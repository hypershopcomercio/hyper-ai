from flask import jsonify, request
from sqlalchemy import desc, asc
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.ml_metrics_daily import MlMetricsDaily
from app.services.pricing_engine import PricingEngine
from app.services.stock_engine import StockEngine
from app.services.stock_engine import StockEngine
from app.services.ad_quality_service import AdQualityService
from app.services.margin_calculator import MarginCalculatorService
from app.models.system_config import SystemConfig
import logging

def _calculate_health_safely(ad):
    try:
        service = AdQualityService()
        return service.analyze({
            'title': ad.title,
            'pictures': ad.pictures,
            'video_id': getattr(ad, 'video_id', None),
            'short_description': getattr(ad, 'short_description', None),
            'manual_video_verified': getattr(ad, 'manual_video_verified', False),
            'attributes': ad.attributes
        })
    except Exception as e:
        logging.error(f"Health Check Failed for {ad.id}: {e}")
        return {
            "score": 0,
            "label": "Erro",
            "sections": {
                "title": {"score": 0, "issues": ["Erro na análise"]},
                "media": {"score": 0, "issues": []},
                "attributes": {"score": 0, "issues": []}
            }
        }

@api_bp.route('/ads', methods=['GET'])
def get_ads():
    db = SessionLocal()
    try:
        from app.models.financial import ProductFinancialMetric
        from app.models.product_forecast import ProductForecast
        
        query = db.query(Ad)
        
        # Filters
        status = request.args.get('status')
        if status:
            query = query.filter(Ad.status == status)
            
        search = request.args.get('search')
        if search:
            query = query.filter(Ad.title.ilike(f"%{search}%"))
            
        # Decision Filters
        filter_type = request.args.get('filter_type')
        if filter_type == 'stock_critical':
            # Critical Stock: Days of stock < 15 or Quantity < 5
            # Ideally use ProductForecast here, but Ad.days_of_stock is indexed/available on Ad
            query = query.filter((Ad.days_of_stock < 15) | (Ad.available_quantity < 5))
            query = query.filter(Ad.status == 'active') # Only active ads
        elif filter_type == 'low_margin':
            # Low Margin: Less than 15%
            query = query.filter(Ad.margin_percent < 15)
            query = query.filter(Ad.status == 'active')
        elif filter_type == 'no_sales':
            # No Sales: Sales 30d is 0 or null
            query = query.filter((Ad.sales_30d == 0) | (Ad.sales_30d == None))
            query = query.filter(Ad.status == 'active')

            
        # Sorting
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        sort_column = getattr(Ad, sort_by, Ad.updated_at)
        if sort_order == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
            
        # Pagination
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        ads = query.offset(offset).limit(limit).all()
        
        # Batch fetch financial metrics to avoid N+1
        ad_skus = [ad.sku for ad in ads if ad.sku]
        metrics_map = {}
        if ad_skus:
            metrics = db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku.in_(ad_skus)).all()
            metrics_map = {m.sku: m for m in metrics}
            
        # Batch fetch ProductForecast (for correct stock days)
        ad_ids = [ad.id for ad in ads]
        forecast_map = {}
        if ad_ids:
            forecasts = db.query(ProductForecast).filter(ProductForecast.mlb_id.in_(ad_ids)).all()
            forecast_map = {f.mlb_id: f for f in forecasts}

        results = []
        for ad in ads:
            # 1. Determine Effective Price (Promotion vs Normal)
            effective_price = float(ad.price or 0)
            if ad.promotion_price and ad.promotion_price > 0 and ad.promotion_price < effective_price:
                effective_price = float(ad.promotion_price)

            # 2. Get Stock Info from ProductForecast (Unified with Supply)
            days_of_stock = ad.days_of_stock # Fallback
            stock_status = None
            if ad.id in forecast_map:
                pf = forecast_map[ad.id]
                if pf.days_of_coverage:
                    days_of_stock = float(pf.days_of_coverage)
                stock_status = pf.stock_status

            # 3. Calculate financials using SHARED logic
            metric = None
            if ad.sku and ad.sku in metrics_map:
                metric = metrics_map[ad.sku]
                
            fin_data = _compute_shared_financials(ad, metric, days_of_stock, effective_price)
            
            # Map back for result construction
            fixed_share = fin_data['fixed_cost_share']
            risk_cost = fin_data['return_risk_cost']
            storage_cost = fin_data['storage_cost']
            inbound_freight_cost = fin_data['inbound_freight_cost']
            daily_storage_fee = fin_data['daily_storage_fee']
            storage_risk_cost = fin_data['storage_risk_cost']
            net_margin_percent = fin_data['net_margin_percent']
            net_margin_value = fin_data['net_margin_value']

            results.append({
                "id": ad.id,
                "title": ad.title,
                "price": ad.price,
                "available_quantity": ad.available_quantity,
                "sold_quantity": ad.sold_quantity,
                "status": ad.status,
                "thumbnail": ad.thumbnail,
                "permalink": ad.permalink,
                "sku": ad.sku,
                
                # New Fields
                "listing_type_id": ad.listing_type_id,
                "shipping_mode": ad.shipping_mode,
                "is_full": ad.is_full,
                "total_visits": ad.total_visits,

                # Costs for Tooltip
                "tax_cost": ad.tax_cost,
                "commission_cost": ad.commission_cost,
                "shipping_cost": ad.shipping_cost,
                "ads_spend_30d": ad.ads_spend_30d,
                "fixed_cost_share": fixed_share,
                "return_risk_cost": risk_cost,
                "storage_cost": storage_cost,
                "inbound_freight_cost": inbound_freight_cost,
                "daily_storage_fee": daily_storage_fee,
                "storage_risk_cost": storage_risk_cost,

                # Metrics
                "visits_30d": ad.visits_30d,
                "sales_30d": ad.sales_30d,
                "visits_7d_change": ad.visits_7d_change,
                "sales_7d_change": ad.sales_7d_change,
                "days_of_stock": days_of_stock, # Unified
                "stock_status": stock_status,   # Unified
                "stock_incoming": ad.stock_incoming,
                
                # Financials (Use Recalculated Net)
                "cost": ad.cost,
                "margin_percent": net_margin_percent,
                "margin_value": net_margin_value,
                "is_margin_alert": ad.is_margin_alert,
                "updated_at": ad.updated_at.isoformat() if ad.updated_at else None,
                "pictures": ad.pictures,
                "manual_video_verified": getattr(ad, 'manual_video_verified', False),
                "original_price": ad.original_price,
                "promotion_price": ad.promotion_price, # Send to frontend
                "effective_price": effective_price,    # Send for calculation display
                "target_margin": ad.target_margin,
                "suggested_price": ad.suggested_price,
                "strategy_start_price": ad.strategy_start_price,
                "current_step_number": ad.current_step_number or 0
            })
            
        return jsonify({
            "total": total,
            "data": results,
            "limit": limit,
            "offset": offset
        })
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>', methods=['GET'])
def get_ad_details(ad_id):
    db = SessionLocal()
    try:
        from app.models.product_forecast import ProductForecast
        
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        # Intelligence
        pricing_engine = PricingEngine(db)
        stock_engine = StockEngine()
        
        # Calculate Velocity (simple 30d avg for now)
        velocity = (ad.sales_30d or 0) / 30.0
            
        # Get metrics history (last 30 days) from MlMetricsDaily
        metrics = db.query(MlMetricsDaily).filter(MlMetricsDaily.item_id == ad_id).order_by(MlMetricsDaily.date.asc()).limit(400).all()
        
        # Calculate fresh total visits from recent metrics (same source as dashboard)
        fresh_total_visits = sum(m.visits or 0 for m in metrics)
        
        history = []
        for m in metrics:
            history.append({
                "date": m.date.isoformat(),
                "visits": m.visits,
                "sales": m.sales_qty,
                # conversion rate? m.conversion_rate or calc
                "revenue": m.sales_revenue
            })
            
        # Fetch ProductForecast for unified stock data
        days_of_stock = ad.days_of_stock
        stock_status = None
        pf = db.query(ProductForecast).filter(ProductForecast.mlb_id == ad_id).first()
        if pf:
            if pf.days_of_coverage:
                days_of_stock = float(pf.days_of_coverage)
            stock_status = pf.stock_status
            
        return jsonify({
            "id": ad.id,
            "title": ad.title,
            "price": ad.price,
            "status": ad.status,
            "thumbnail": ad.thumbnail,
            "available_quantity": ad.available_quantity,
            "stock_incoming": ad.stock_incoming,
            "sold_quantity": ad.sold_quantity,
            # Prioritize ad.total_visits (lifetime from ML API sync) over metrics sum (30d)
            "total_visits": ad.total_visits if ad.total_visits and ad.total_visits > 0 else fresh_total_visits,
            "permalink": ad.permalink,
            "sku": ad.sku,
            "history": history,
            
            "metrics": {
                "visits_30d": ad.visits_30d,
                "visits_7d_change": ad.visits_7d_change,
                "sales_7d_change": ad.sales_7d_change,
                "days_of_stock": days_of_stock # Unified
            },
            
            "intelligence": {
                "pricing": pricing_engine.calculate_elasticity(ad_id),
                "stock": stock_engine.analyze_stock(ad, velocity), # Keep for comparison or legacy?
                "health": _calculate_health_safely(ad)
            },
            
            # Root level fields for UI compatibility
            "cost": ad.cost,
            "margin_percent": ad.margin_percent,
            "margin_value": ad.margin_value,
            "is_margin_alert": ad.is_margin_alert,
            "sales_30d": ad.sales_30d, 
            "visits_30d": ad.visits_30d,
            "days_of_stock": days_of_stock,
            "stock_status": stock_status, # Send status
            "sales_7d_change": ad.sales_7d_change,
            "visits_7d_change": ad.visits_7d_change,
            
            "shipping_mode": ad.shipping_mode,
            "is_full": ad.is_full,
            
            "financials": _calculate_detailed_financials(db, ad, days_of_stock=days_of_stock),
            
            "pictures": ad.pictures,
            "manual_video_verified": getattr(ad, 'manual_video_verified', False),
            "video_id": getattr(ad, 'video_id', None),
            "original_price": ad.original_price,
            "promotion_price": ad.promotion_price,
            "target_margin": ad.target_margin,
            "suggested_price": ad.suggested_price,
            "strategy_start_price": ad.strategy_start_price,
            "current_step_number": ad.current_step_number or 0,
            
            # Strategy Data (for pricing strategy panel with real data)
            "strategy_data": pricing_engine.get_strategy_data(
                ad_id, 
                float(ad.price or 0), 
                float(ad.suggested_price or ad.price * 1.05)
            ) if ad.target_margin and ad.target_margin > 0 else None
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

def _compute_shared_financials(ad, metric, days_of_stock, effective_price):
    """
    Centralized logic for financial costs and margin calculation.
    Used by both get_ads (List) and get_ad_details (Detail).
    """
    # 1. Base Costs from Ad/DB
    cost = float(ad.cost or 0)
    commission = float(ad.commission_cost or 0)
    shipping = float(ad.shipping_cost or 0)
    tax = float(ad.tax_cost or 0)
    ads_spend = float(ad.ads_spend_30d or 0)
    
    # 2. Dimensions & Defaults
    l_mm = float(ad.length_mm or 0)
    w_mm = float(ad.width_mm or 0)
    h_mm = float(ad.height_mm or 0)
    dims = sorted([l_mm/10, w_mm/10, h_mm/10]) # cm

    # Default Rates (ML 2024 Base)
    daily_fee = 0.007
    inbound_est = 0.50 

    if dims[2] <= 25 and dims[1] <= 15 and dims[0] <= 12:
        daily_fee = 0.007
        inbound_est = 0.80
    elif dims[2] <= 51 and dims[1] <= 36 and dims[0] <= 28:
        daily_fee = 0.013
        inbound_est = 1.50
    elif dims[2] <= 70 and dims[1] <= 60 and dims[0] <= 60:
        daily_fee = 0.047
        inbound_est = 4.00
    else:
        daily_fee = 0.107
        inbound_est = 9.00
        
    # 3. Dynamic Costs (Fixed Share, Risk, Storage)
    fixed_share = 0.0
    return_risk = 0.0
    storage_total = 0.0
    storage_risk = 0.0
    
    inbound_final = inbound_est
    daily_final = daily_fee
    
    if metric:
        fixed_share = float(metric.calculated_fixed_cost_share or 0)
        
        # Return Risk
        risk_rate = metric.return_rate_90d or 0.03
        avg_return_cost = float(metric.avg_return_cost or 20.0)
        return_risk = risk_rate * avg_return_cost
        
        # Storage Rates
        inbound_final = float(metric.inbound_freight_cost or inbound_est)
        daily_final = float(metric.daily_storage_fee or daily_fee)
        storage_risk = float(metric.storage_risk_cost or 0)
        
        # DB Storage Value vs Calc
        db_storage = float(metric.storage_cost or 0)
        if db_storage > 0:
             # Trust DB if populated? 
             # For consistency, if we want dynamic update based on days_stock, we should recalc.
             # But if DB has accurate snapshot, use it?
             # User reported DB was 0.
             # The issue is "Calculo igual". If we ignore DB and always calc, it's consistent.
             # Let's Always Calc to be safe and consistent with List View Fix.
             pass

    # Calculate Storage
    curr_days = float(days_of_stock or 30)
    avg_days_stock = curr_days / 2
    
    storage_total = (daily_final * avg_days_stock) + inbound_final
    
    if curr_days > 120:
        storage_risk += (curr_days - 120) * (daily_final * 3)

    # 4. Net Margin Calc
    # NOTE: ads_spend_30d is intentionally EXCLUDED from margin calculation
    # It's a marketing cost, not a product unit cost
    total_cost = (
        cost + 
        commission + 
        shipping + 
        tax + 
        fixed_share + 
        return_risk + 
        storage_total + 
        storage_risk
    )
    
    margin_value = effective_price - total_cost
    margin_percent = (margin_value / effective_price * 100) if effective_price > 0 else 0
    
    return {
        "cost": cost,
        "commission_cost": commission,
        "shipping_cost": shipping,
        "tax_cost": tax,
        "ads_spend_30d": ads_spend,
        
        "fixed_cost_share": fixed_share,
        "return_risk_cost": return_risk,
        "storage_cost": storage_total,
        
        "inbound_freight_cost": inbound_final,
        "daily_storage_fee": daily_final,
        "storage_risk_cost": storage_risk,
        
        "net_margin_value": margin_value,
        "net_margin_percent": margin_percent,
        "effective_price": effective_price
    }

def _calculate_detailed_financials(db, ad, days_of_stock=None):
    """
    Calcula financials incluindo custos fixos e risco de devolução.
    Wraps _compute_shared_financials.
    """
    from app.models.financial import ProductFinancialMetric
    
    # Fetch Metric
    metric = None
    if ad.sku:
        metric = db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku == ad.sku).first()

    # Determine Effective Price
    effective_price = float(ad.price or 0)
    if ad.promotion_price and ad.promotion_price > 0 and ad.promotion_price < effective_price:
        effective_price = float(ad.promotion_price)

    final_days = days_of_stock if days_of_stock is not None else ad.days_of_stock
    return _compute_shared_financials(ad, metric, final_days, effective_price)

@api_bp.route('/ads/<ad_id>/verify-video', methods=['PATCH'])
def verify_ad_video_manual(ad_id):
    db: Session = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        ad.manual_video_verified = True
        db.commit()
        
        return jsonify({"success": True, "message": "Video verified manually"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>/verify-video', methods=['DELETE'])
def unverify_ad_video_manual(ad_id):
    db: Session = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
        ad.manual_video_verified = False
        db.commit()
        
        return jsonify({"success": True, "message": "Video verification removed"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>/target-margin', methods=['PATCH'])
def update_target_margin(ad_id):
    db = SessionLocal()
    try:
        data = request.json
        if 'target_margin' not in data:
            return jsonify({"error": "Missing target_margin"}), 400
            
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
            
                # Update Target
        try:
            val = float(data['target_margin'])
            ad.target_margin = val
            
            # FIX: If target_margin is 0, explicitly DISABLE strategy
            if val == 0:
                ad.strategy_start_price = 0
                ad.current_step_number = 0
                ad.suggested_price = None # Clear suggestion
                
        except ValueError:
             return jsonify({"error": "Invalid target_margin"}), 400
        
        # If frontend sent the calculated suggested_price, use it directly (ensures consistency)
        if 'suggested_price' in data and data['suggested_price']:
            try:
                new_suggested = float(data['suggested_price'])
                
                # Check if this is a NEW strategy or EXPLICIT RESET
                # A strategy is "new" if strategy_start_price is not set
                is_new_strategy = (not ad.strategy_start_price or ad.strategy_start_price == 0) and val > 0
                force_update = data.get('force_update', False)  # Frontend can force update if needed
                
                if is_new_strategy:
                    # First time setting strategy - save starting point
                    ad.strategy_start_price = ad.price
                    ad.current_step_number = 0
                    ad.suggested_price = new_suggested
                elif force_update:
                    # Explicit reset requested - update suggested_price
                    ad.suggested_price = new_suggested
                # else: Strategy exists, DO NOT overwrite suggested_price
                # This prevents the simulator from corrupting saved strategy data
                
                db.commit()
                return jsonify({
                    "id": ad.id,
                    "target_margin": ad.target_margin,
                    "suggested_price": ad.suggested_price,
                    "strategy_start_price": ad.strategy_start_price,
                    "current_step_number": ad.current_step_number,
                    "margin_percent": ad.margin_percent
                })
            except ValueError:
                pass  # Fall through to recalculation
             
        tax_config = db.query(SystemConfig).filter(SystemConfig.key == "aliquota_simples").first()
        tax_rate = float(tax_config.value) if tax_config and tax_config.value else 12.5 # Default fallback
        
        fixed_pkg_config = db.query(SystemConfig).filter(SystemConfig.key == "fixed_packaging_cost").first()
        fixed_cost = float(fixed_pkg_config.value) if fixed_pkg_config and fixed_pkg_config.value else 0.0
        
        inbound_cost = 0.0
        if ad.is_full:
             sc_inbound = db.query(SystemConfig).filter(SystemConfig.key == 'avg_inbound_cost').first()
             inbound_cost = float(sc_inbound.value) if sc_inbound else 0.0
             
        # Fetch Financial Metric for Unit Economics (Storage, Risk, Fixed Share)
        from app.models.financial import ProductFinancialMetric
        financial_metric = db.query(ProductFinancialMetric).filter(ProductFinancialMetric.sku == ad.sku).first()
        
        extra_fixed_cost = 0.0
        extra_inbound_cost = 0.0 # From metric if available
        
        if financial_metric:
            # 1. Fixed Share (Rateio)
            extra_fixed_cost += float(financial_metric.calculated_fixed_cost_share or 0)
            
            # 2. Return Risk
            risk_rate = financial_metric.return_rate_90d or 0.03
            avg_return_cost = float(financial_metric.avg_return_cost or 20.0)
            extra_fixed_cost += (risk_rate * avg_return_cost)
            
            # 3. Storage Cost (Total Unit Economics)
            # Use logic from _calculate_detailed_financials or simple metric access
            # Ideally verify if storage_cost is pre-calculated or needs dynamic calc
            # For robustness, we use dynamic logic if values missing
            
            daily_fee = float(financial_metric.daily_storage_fee or 0.007)
            inbound_est = float(financial_metric.inbound_freight_cost or 0.50)
            
            days_stock = float(ad.days_of_stock or 30)
            avg_days_stock = days_stock / 2
            
            calc_storage = (daily_fee * avg_days_stock)
            
            # Add to costs
            # We treat Inbound from metric as Inbound Cost
            extra_inbound_cost = inbound_est
            
            # We treat Daily Storage as Fixed Cost per Unit (simplified)
            extra_fixed_cost += calc_storage
            
            # 4. Storage Risk (Long Term)
            extra_fixed_cost += float(financial_metric.storage_risk_cost or 0)

        # Merge Costs
        total_fixed_cost = fixed_cost + extra_fixed_cost
        total_inbound_cost = inbound_cost + extra_inbound_cost # Use metric inbound preference? Or system? 
        # Usually system inbound is generic, metric inbound is dimension-based. Use metric if exists.
        if extra_inbound_cost > 0:
            total_inbound_cost = extra_inbound_cost
             
        calc_service = MarginCalculatorService()
        # We pass None for tiny_product so it uses ad.cost stored in DB
        calc_service.calculate_margin(ad, tiny_product=None, tax_rate=tax_rate, fixed_cost=total_fixed_cost, inbound_cost=total_inbound_cost)
        
        db.commit()
        
        return jsonify({
            "id": ad.id,
            "target_margin": ad.target_margin,
            "suggested_price": ad.suggested_price,
            "margin_percent": ad.margin_percent
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@api_bp.route('/ads/<ad_id>/logs', methods=['GET'])
def get_ad_logs(ad_id):
    """
    Retorna logs do sistema relacionados a este anúncio.
    Busca por logs onde o ad_id aparece na mensagem ou nos detalhes.
    """
    from app.models.system_log import SystemLog
    from sqlalchemy import or_, desc
    
    db = SessionLocal()
    try:
        # Search heuristic: logs referring to this ID in message or details (JSON)
        # Also filter by relevant modules (optional, but keep broad for now)
        search_term = f"%{ad_id}%"
        
        logs = db.query(SystemLog).filter(
            or_(
                SystemLog.message.ilike(search_term),
                SystemLog.details.ilike(search_term)
            )
        ).order_by(desc(SystemLog.timestamp)).limit(50).all()
        
        return jsonify([{
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "module": log.module,
            "message": log.message,
            "details": log.details,
            "status": log.status
        } for log in logs])
    except Exception as e:
        logger.error(f"Error fetching logs for ad {ad_id}: {e}")
        return jsonify([]), 500
    finally:
        db.close()


@api_bp.route('/ads/<ad_id>/execute-price-step', methods=['POST'])
def execute_price_step(ad_id):
    """
    Manually execute a pricing step for a specific ad.
    
    Body (optional):
        target_price: float - If provided, jumps directly to this price.
                              If not, calculates the next step automatically.
    """
    from app.jobs.pricing_job import execute_single_ad_step
    
    data = request.get_json() or {}
    target_price = data.get('target_price')
    
    # Validate target_price if provided
    if target_price is not None:
        try:
            target_price = float(target_price)
            if target_price <= 0:
                return jsonify({"error": "target_price must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid target_price"}), 400
    
    result = execute_single_ad_step(ad_id, target_price)
    
    if result.get("success"):
        return jsonify(result)
    else:
        return jsonify(result), 500


@api_bp.route('/ads/<ad_id>/pause-strategy', methods=['POST'])
def pause_strategy(ad_id):
    """
    Pause or resume the pricing strategy for an ad.
    
    Body:
        paused: bool - True to pause, False to resume
    """
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"error": "Ad not found"}), 404
        
        data = request.get_json() or {}
        paused = data.get('paused', True)
        
        # We use target_margin = 0 to indicate paused
        # Could also add a separate 'strategy_paused' column if needed
        if paused:
            # Store current target_margin temporarily and set to 0
            ad.paused_target_margin = ad.target_margin
            ad.target_margin = 0
            message = "Strategy paused"
        else:
            # Restore target_margin
            if hasattr(ad, 'paused_target_margin') and ad.paused_target_margin:
                ad.target_margin = ad.paused_target_margin
            message = "Strategy resumed"
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": message,
            "paused": paused
        })
    except Exception as e:
        db.rollback()
        logger.error(f"Error pausing strategy for {ad_id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/ads/<ad_id>/price-history', methods=['GET'])
def get_price_history(ad_id):
    """
    Get the price adjustment history for an ad.
    """
    from app.models.pricing_log import PriceAdjustmentLog
    
    db = SessionLocal()
    try:
        logs = db.query(PriceAdjustmentLog).filter(
            PriceAdjustmentLog.ad_id == ad_id
        ).order_by(PriceAdjustmentLog.executed_at.desc()).limit(20).all()
        
        return jsonify([{
            "id": log.id,
            "old_price": float(log.old_price),
            "new_price": float(log.new_price),
            "target_price": float(log.target_price) if log.target_price else None,
            "step_number": log.step_number,
            "total_steps": log.total_steps,
            "trigger_type": log.trigger_type,
            "executed_at": log.executed_at.isoformat() if log.executed_at else None,
            "status": log.status,
            "error_message": log.error_message
        } for log in logs])
    except Exception as e:
        logger.error(f"Error fetching price history for {ad_id}: {e}")
        return jsonify([]), 500
    finally:
        db.close()


@api_bp.route('/ads/<ad_id>/promotions', methods=['GET'])
def get_ad_promotions(ad_id):
    """
    Get promotions for an ad - both active and available deals.
    """
    from app.services.promo_service import PromoService
    
    db = SessionLocal()
    try:
        promo_service = PromoService(db)
        
        # Get current promotions
        current = promo_service.get_item_promotions(ad_id)
        
        # Get available deal types
        available = promo_service.get_available_deals(ad_id)
        
        return jsonify({
            "has_promotions": current.get("has_promotions", False),
            "current_promotions": current.get("promotions", []),
            "available_deals": available.get("deals", []),
            "error": current.get("error") or available.get("error")
        })
    except Exception as e:
        logger.error(f"Error fetching promotions for {ad_id}: {e}")
        return jsonify({
            "has_promotions": False,
            "current_promotions": [],
            "available_deals": [],
            "error": str(e)
        }), 500
    finally:
        db.close()


@api_bp.route('/ads/<ad_id>/promotions', methods=['POST'])
def apply_ad_promotion(ad_id):
    """
    Apply a PRICE_DISCOUNT promotion to an ad.
    
    Body:
        deal_price: float - The discounted price
        days: int - Duration (max 14, default 14)
    """
    from app.services.promo_service import PromoService
    
    db = SessionLocal()
    try:
        data = request.get_json() or {}
        
        deal_price = data.get('deal_price')
        if not deal_price:
            return jsonify({"error": "deal_price is required"}), 400
        
        try:
            deal_price = float(deal_price)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid deal_price"}), 400
        
        days = int(data.get('days', 14))
        
        promo_service = PromoService(db)
        result = promo_service.apply_promotion(ad_id, deal_price, days)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error applying promotion to {ad_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route('/ads/<ad_id>/promotions', methods=['DELETE'])
def remove_ad_promotion(ad_id):
    """
    Remove active PRICE_DISCOUNT promotion from an ad.
    """
    from app.services.promo_service import PromoService
    
    db = SessionLocal()
    try:
        promo_service = PromoService(db)
        result = promo_service.remove_promotion(ad_id)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Error removing promotion from {ad_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
