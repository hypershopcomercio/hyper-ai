"""
Hyper Forecast - Main Engine
Combines all multipliers to generate sales predictions
"""
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .data_collector import DataCollector
from .baseline import BaselineCalculator
from .multipliers.calendar import CalendarMultipliers
from .multipliers.momentum import MomentumCalculator

logger = logging.getLogger(__name__)


class HyperForecast:
    """
    Main forecasting engine that combines ALL prediction factors.
    
    Uses DynamicMultipliers to load ALL factors from database.
    No hardcoded factors - everything is configurable.
    
    Formula: PREDICTION = Σ(products) where each product uses:
      base_units × global_multipliers × product_multipliers × stock_factor
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.data_collector = DataCollector(db)
        self.baseline_calc = BaselineCalculator(db)
        self.calendar_mult = CalendarMultipliers()
        self.momentum_calc = MomentumCalculator(db)
        
        # Dynamic multipliers - loads ALL factors from database
        from .multipliers.dynamic import DynamicMultipliers
        self.dynamic_mult = DynamicMultipliers(db)
    
    def predict_hour(
        self,
        target_hour: int,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate prediction for a specific hour using product-based forecasting.
        
        IMPORTANT: This method applies ALL available factors without bias.
        The data collected will determine which factors have the most impact.
        
        Factors applied:
        - Global: day_of_week, period_of_month, event, seasonal, momentum
        - Per-product: trend, category (seasonal), stock (physical constraint)
        
        Args:
            target_hour: Hour (0-23) to predict
            target_date: Date to predict (defaults to today)
            category: Optional product category filter
        
        Returns:
            Dict with prediction, factor breakdown, AND product mix
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        now = datetime.now()
        is_future = (target_date > now.date()) or (target_date == now.date() and target_hour > now.hour)
        
        # ================================================
        # GLOBAL FACTORS - ALL factors from database
        # ================================================
        
        # Get ALL global multipliers from database (28+ types)
        # We need both VALUE (for math) and KEY (for logging/calibration context)
        # dynamic_mult methods now return {type: value} but we need metadata.
        # Ideally dynamic.py should return {type: {value: x, key: y}}.
        
        # For now, let's wrap the dynamic call or just handle momentum manually first since that's the bug.
        raw_multipliers = self.dynamic_mult.get_all_global_multipliers(target_date, target_hour)
        
        all_multipliers = {}
        factor_metadata = {} # To store specific keys like 'segunda', 'alto'
        
        for k, v in raw_multipliers.items():
            all_multipliers[k] = v
            # For standard dynamic factors, we don't easily know the sub-key without changing dynamic.py
            # But the primary issue is Momentum. 
            
        # Add momentum (real-time calculation, not from database)
        if is_future and target_date == now.date():
            momentum_result = self.momentum_calc.calculate_momentum()
            all_multipliers['momentum'] = momentum_result["multiplier"]
            momentum_reason = momentum_result["reason"]
            # Store metadata for logging - USE CATEGORICAL KEY (direction) NOT REASON
            factor_metadata['momentum'] = momentum_result.get("direction", "neutral")
            # Store reason separately if needed, but not as the primary key
            factor_metadata['momentum_reason'] = momentum_reason
        else:
            all_multipliers['momentum'] = 1.0
            momentum_reason = "normal"
            factor_metadata['momentum'] = "neutral"
        
        # Get baseline for fallback
        baseline_result = self.baseline_calc.calculate_baseline(target_hour, target_date)
        baseline = baseline_result["baseline"]
        baseline_confidence = baseline_result["confidence"]
        
        # Calculate combined global multiplier
        global_multiplier = self.dynamic_mult.calculate_combined_multiplier(all_multipliers)
        
        # ================================================
        # PRODUCT-BASED PREDICTION (with stock & category)
        # ================================================
        
        product_based = self._calculate_product_based_hourly(
            target_hour, target_date, global_multiplier, all_multipliers, now
        )
        
        if product_based:
            # Use product-based prediction
            prediction = product_based["total_revenue"]
            potential_prediction = product_based["potential_revenue"]
            product_mix = product_based["product_mix"]
            stock_factor = product_based["stock_factor"]
            
            # Add stock factor to multipliers for logging
            all_multipliers["stock"] = round(stock_factor, 3)
        else:
            # Fallback to baseline if no products
            prediction = baseline * global_multiplier
            potential_prediction = prediction
            product_mix = []
            all_multipliers["stock"] = 1.0
        
        # Recalculate combined multiplier including stock
        combined_multiplier = 1.0
        for mult in all_multipliers.values():
            combined_multiplier *= mult
        
        # ================================================
        # CONFIDENCE CALCULATION
        # ================================================
        
        deviation_factor = sum(abs(m - 1.0) for m in all_multipliers.values())
        
        if deviation_factor < 0.3:
            confidence_range = 0.20
            confidence_level = 0.85
        elif deviation_factor < 0.6:
            confidence_range = 0.30
            confidence_level = 0.70
        elif deviation_factor < 1.0:
            confidence_range = 0.40
            confidence_level = 0.55
        else:
            confidence_range = 0.50
            confidence_level = 0.40
        
        final_confidence = confidence_level * baseline_confidence
        
        min_prediction = prediction * (1 - confidence_range)
        max_prediction = prediction * (1 + confidence_range)
        
        return {
            "hour": target_hour,
            "hour_label": f"{target_hour:02d}h",
            "date": target_date.isoformat(),
            "prediction": round(prediction, 2),
            "prediction_potential": round(potential_prediction, 2),
            "min": round(min_prediction, 2),
            "max": round(max_prediction, 2),
            "confidence": round(final_confidence, 2),
            "baseline": round(baseline, 2),
            "combined_multiplier": round(combined_multiplier, 3),
            "multipliers": all_multipliers,
            "factors": {
                "momentum_reason": momentum_reason,
                "multiplier_types": list(all_multipliers.keys()),
            },
            "product_mix": product_mix[:100],  # Top 100 products to sell
            "is_future": is_future,
        }
    
    def _calculate_product_based_hourly(
        self,
        target_hour: int,
        target_date: date,
        global_multiplier: float,
        global_factors: Dict,
        now: datetime
    ) -> Optional[Dict]:
        """
        Calculate hourly prediction based on individual products.
        Returns total revenue, potential revenue, and product mix.
        """
        try:
            from app.models.product_forecast import ProductForecast
            from app.jobs.category_sync import get_category_multiplier
            
            products = self.db.query(ProductForecast).filter(
                ProductForecast.is_active == True
            ).all()
            
            if not products:
                return None
            
            total_revenue = 0.0
            potential_revenue = 0.0
            product_mix = []
            
            for p in products:
                # Base units per hour (avg_units_7d is daily, divide by 24)
                base_units_daily = float(p.avg_units_7d or 0)
                base_units_hourly = base_units_daily / 24
                price = float(p.price or 0)
                stock = p.stock_current or 0
                
                # STOCK CHECK: Exclude completely from forecast if no stock
                # Must have at least 1 full unit to be included
                if stock < 1.0:
                    continue
                
                # Apply global factors
                units_adjusted = base_units_hourly * global_multiplier
                
                # ================================================
                # PRODUCT-SPECIFIC FACTORS - ALL from database
                # ================================================
                
                # Get ALL product multipliers from database
                product_multipliers = self.dynamic_mult.get_all_product_multipliers(p)
                
                # Calculate combined product multiplier
                product_mult = self.dynamic_mult.calculate_combined_multiplier(product_multipliers)
                
                # Stock factor is special - it's a physical constraint, not just a multiplier
                # If no stock, cannot sell regardless of other factors
                stock_factor = product_multipliers.get('stock_pressure', 1.0)
                if stock == 0:
                    stock_factor = 0.0
                elif p.days_of_coverage and float(p.days_of_coverage) < 1:
                    stock_factor = min(float(p.days_of_coverage), stock_factor)
                
                # Remove stock from product_mult since we apply it separately
                product_mult_no_stock = product_mult / (product_multipliers.get('stock_pressure', 1.0) or 1.0)
                
                # Apply all factors
                units_final = units_adjusted * product_mult_no_stock * stock_factor
                units_potential = units_adjusted * product_mult_no_stock  # Without stock
                
                revenue = units_final * price
                rev_potential = units_potential * price
                
                total_revenue += revenue
                potential_revenue += rev_potential
                
                # Check for realized sales if in past or current hour (repair/backfill/real-time mode)
                realized_units = 0
                if target_date < now.date() or (target_date == now.date() and target_hour <= now.hour):
                     # Quick check from data collector for this specific product/hour
                     # Since we are inside a loop, this could be slow. Better to batch?
                     # For now, let's trust DataCollector is fast or cached.
                     # Actually, to avoid N+1 queries, we should use a bulk result passed in.
                     # But for MVP repair, let's check directly.
                     real_sales = self.data_collector.get_hourly_sales_by_product(p.mlb_id, target_date, target_hour)
                     realized_units = real_sales.get('units', 0)

                if revenue > 0 or rev_potential > 5 or realized_units > 0:  # Include if relevant OR if it sold
                    product_mix.append({
                        "mlb_id": p.mlb_id,
                        "title": p.title or "?",
                        "units_expected": round(units_final, 4),
                        "units_potential": round(units_potential, 4),
                        "revenue_expected": round(revenue, 2),
                        "revenue_potential": round(rev_potential, 2),
                        "base_units": round(base_units_hourly, 4),
                        "realized_units": realized_units,  # New field for UI highlighting
                        "stock": stock,
                        "product_multipliers": product_multipliers,
                        "combined_product_mult": round(product_mult, 3),
                        "curve": p.curve
                    })
            
            # Sort by expected revenue
            product_mix.sort(key=lambda x: x["revenue_expected"], reverse=True)
            
            # Calculate overall stock factor
            overall_stock_factor = total_revenue / potential_revenue if potential_revenue > 0 else 1.0
            
            return {
                "total_revenue": total_revenue,
                "potential_revenue": potential_revenue,
                "stock_factor": overall_stock_factor,
                "product_mix": product_mix
            }
            
        except Exception as e:
            logger.warning(f"[FORECAST] Product-based hourly calculation failed: {e}")
            return None
    
    def _log_prediction(
        self,
        target_date: date,
        target_hour: int,
        prediction: float,
        baseline: float,
        multipliers: Dict,
        product_mix: Optional[List] = None
    ) -> int:
        """
        Log prediction to forecast_logs table for future learning
        
        Returns:
            ID of the created log entry
        """
        try:
            from app.models.forecast_learning import ForecastLog
            
            hora_alvo = datetime.combine(target_date, datetime.min.time()).replace(hour=target_hour)
            
            # Check for existing pending predictions for this hour and replace them
            # Use range check to be robust against microsecond differences
            next_hour = hora_alvo + timedelta(hours=1)
            
            # FIND ALL LOGS (Ignoring valor_real status) to prevent duplicates
            existing_logs = self.db.query(ForecastLog).filter(
                ForecastLog.hora_alvo >= hora_alvo,
                ForecastLog.hora_alvo < next_hour
            ).all()
            
            real_value_to_preserve = None
            
            for old_log in existing_logs:
                # Preserve the actual value if it exists in any of the old logs
                if old_log.valor_real is not None:
                    real_value_to_preserve = old_log.valor_real
                
                # Delete the old log
                self.db.delete(old_log)
            
            # Add product mix to multipliers (stored in JSONB)
            # We use a special key that starts with _ to indicate metadata
            if product_mix:
                # Store top 100 products to capture tail, as requested by user
                multipliers['_product_mix'] = product_mix[:100]
            
            log_entry = ForecastLog(
                timestamp_previsao=datetime.utcnow(),
                hora_alvo=hora_alvo,
                valor_previsto=prediction,
                valor_real=real_value_to_preserve, # Carry over existing actuals
                fatores_usados=multipliers,
                baseline_usado=baseline,
                modelo_versao='heuristic_v1'
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
            logger.debug(f"[FORECAST] Logged prediction for {hora_alvo}: R${prediction:.2f}")
            return log_entry.id
            
        except Exception as e:
            logger.warning(f"[FORECAST] Failed to log prediction: {e}")
            self.db.rollback()
            return -1
    
    def predict_hour_with_logging(
        self,
        target_hour: int,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate prediction AND log it for learning system
        Use this method when you want predictions to be tracked
        """
        result = self.predict_hour(target_hour, target_date, category)
        
        # ALWAYS log if target_date is explicitly provided (manual generation)
        # OR if it's a future prediction
        # This allows filling gaps for past dates
        should_log = target_date is not None or result["is_future"]
        
        if should_log:
            # Inject categorical key names (NOT values) for proper logging
            multipliers_to_log = result["multipliers"].copy()
            
            # Get categorical metadata from dynamic multipliers
            factor_metadata = self.dynamic_mult.get_factor_metadata()
            
            # Inject metadata with _meta_ prefix to distinguish from values
            for factor_name, categorical_key in factor_metadata.items():
                multipliers_to_log[f"_meta_{factor_name}"] = categorical_key
            
            # Also inject momentum metadata if available
            if "factors" in result and "momentum_reason" in result["factors"]:
                multipliers_to_log["_info_momentum_reason"] = result["factors"]["momentum_reason"]
            
            log_id = self._log_prediction(
                target_date=target_date or datetime.now().date(),
                target_hour=target_hour,
                prediction=result["prediction"],
                baseline=result["baseline"],
                multipliers=multipliers_to_log,
                product_mix=result.get("product_mix")  # Pass product mix
            )
            result["log_id"] = log_id
        
        return result
    
    def predict_day(
        self,
        target_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Generate predictions for an entire day (all 24 hours)
        """
        if target_date is None:
            target_date = datetime.now().date()
        
        hourly_predictions = []
        total_predicted = 0
        total_min = 0
        total_max = 0
        avg_confidence = 0
        
        for hour in range(24):
            pred = self.predict_hour(hour, target_date, category)
            hourly_predictions.append(pred)
            total_predicted += pred["prediction"]
            total_min += pred["min"]
            total_max += pred["max"]
            avg_confidence += pred["confidence"]
        
        # Find peak and valley hours
        peak = max(hourly_predictions, key=lambda x: x["prediction"])
        valley = min(hourly_predictions, key=lambda x: x["prediction"])
        
        return {
            "date": target_date.isoformat(),
            "total_predicted": round(total_predicted, 2),
            "total_min": round(total_min, 2),
            "total_max": round(total_max, 2),
            "avg_confidence": round(avg_confidence / 24, 2),
            "hourly": hourly_predictions,
            "peak_hour": {
                "hour": peak["hour_label"],
                "prediction": peak["prediction"]
            },
            "valley_hour": {
                "hour": valley["hour_label"],
                "prediction": valley["prediction"]
            }
        }
    
    def get_today_with_actuals(self) -> Dict:
        """
        Get today's forecast combined with actual sales data
        Perfect for the dashboard chart
        """
        today = datetime.now().date()
        current_hour = datetime.now().hour
        
        # Get predictions for all 24 hours
        day_forecast = self.predict_day(today)
        
        # Get actual sales up to current hour
        actuals = self.data_collector.get_sales_today_so_far()
        actual_total = sum(h["revenue"] for h in actuals)
        
        # Get previous period for comparison
        previous = self.data_collector.get_sales_previous_period(today, "week")
        previous_total = sum(h["revenue"] for h in previous)
        
        # Calculate remaining prediction (future hours only)
        remaining_predicted = sum(
            p["prediction"] 
            for p in day_forecast["hourly"] 
            if p["hour"] > current_hour
        )
        
        # Project end of day
        projected_total = actual_total + remaining_predicted
        
        # Comparison with previous period
        vs_previous_percent = ((projected_total - previous_total) / previous_total * 100) if previous_total > 0 else 0
        
        return {
            "date": today.isoformat(),
            "current_hour": current_hour,
            "actual_total": round(actual_total, 2),
            "remaining_predicted": round(remaining_predicted, 2),
            "projected_total": round(projected_total, 2),
            "projected_min": round(actual_total + sum(p["min"] for p in day_forecast["hourly"] if p["hour"] > current_hour), 2),
            "projected_max": round(actual_total + sum(p["max"] for p in day_forecast["hourly"] if p["hour"] > current_hour), 2),
            "previous_period_total": round(previous_total, 2),
            "vs_previous_percent": round(vs_previous_percent, 1),
            "avg_confidence": day_forecast["avg_confidence"],
            "hourly": {
                "actuals": actuals,
                "predictions": day_forecast["hourly"],
                "previous": previous
            },
            "peak_hour": day_forecast["peak_hour"],
            "valley_hour": day_forecast["valley_hour"]
        }

    def get_product_based_forecast(self, target_date: Optional[date] = None) -> Dict:
        """
        Get forecast based on sum of individual product forecasts.
        
        IMPORTANT: Apply ALL available factors without bias.
        The data collected will determine which factors have the most impact.
        We should NOT cherry-pick factors - let the data speak.
        
        Factors applied per product:
        - Base units (from historical avg_units_7d)
        - ALL calendar multipliers (day_of_week, period_of_month, event, seasonal)
        - Momentum (if available)
        - Stock factor (physical constraint - no stock = no sales)
        - Category factor (when category_mapping is populated)
        - Product trend (up/down based on recent performance)
        
        Formula: units = avg_units × Π(ALL_FACTORS) × stock_factor
        Revenue = units × price
        
        Returns:
            Dict with total forecast, all factors applied, and breakdown by product
        """
        try:
            from app.models.product_forecast import ProductForecast
            
            if target_date is None:
                target_date = datetime.now().date()
            
            # Get all active products with forecasts
            products = self.db.query(ProductForecast).filter(
                ProductForecast.is_active == True
            ).all()
            
            if not products:
                logger.warning("[FORECAST] No products in product_forecast table, falling back to baseline")
                return None
            
            total_forecast = 0.0
            total_if_all_stock = 0.0
            products_with_stock = 0
            products_without_stock = 0
            breakdown = []
            
            # ================================================
            # GET ALL AVAILABLE MULTIPLIERS (NO BIAS)
            # ================================================
            
            # Calendar multipliers - ALL of them
            calendar = self.calendar_mult.get_all_calendar_multipliers(target_date, None)
            
            # Momentum - if available (for current day predictions)
            now = datetime.now()
            if target_date == now.date():
                momentum_result = self.momentum_calc.calculate_momentum()
                momentum_mult = momentum_result["multiplier"]
            else:
                momentum_mult = 1.0
            
            # All global factors to apply
            all_global_factors = {
                "day_of_week": calendar["day_of_week"],
                "period_of_month": calendar["period_of_month"],
                "event": calendar["event"],
                "seasonal": calendar["seasonal"],
                "momentum": momentum_mult
            }
            
            # Combined global multiplier (product of all factors)
            global_multiplier = 1.0
            for factor in all_global_factors.values():
                global_multiplier *= factor
            
            for p in products:
                # ================================================
                # PRODUCT-SPECIFIC FACTORS
                # ================================================
                
                base_units = float(p.avg_units_7d or 0)
                price = float(p.price or 0)
                stock = p.stock_current or 0
                
                # Product-level factors
                product_factors = {}
                
                # 1. Trend factor - based on product's own performance trend
                if p.trend == 'up' and p.trend_pct:
                    # Product trending up - apply boost (capped at 50%)
                    trend_factor = 1.0 + min(float(p.trend_pct) / 100, 0.5)
                elif p.trend == 'down' and p.trend_pct:
                    # Product trending down - apply reduction
                    trend_factor = 1.0 + max(float(p.trend_pct) / 100, -0.5)  # trend_pct is negative
                else:
                    trend_factor = 1.0
                product_factors["trend"] = round(trend_factor, 3)
                
                # 2. Category factor - seasonal multiplier from category_mapping table
                try:
                    from app.jobs.category_sync import get_category_multiplier
                    category_factor = get_category_multiplier(self.db, p.category_ml)
                except Exception:
                    category_factor = 1.0
                product_factors["category"] = round(category_factor, 3)
                
                # 3. Stock factor - PHYSICAL CONSTRAINT (not optional)
                # No stock = no sales, this is a hard limit
                if stock == 0:
                    stock_factor = 0.0
                    products_without_stock += 1
                elif p.days_of_coverage and float(p.days_of_coverage) < 1:
                    stock_factor = float(p.days_of_coverage)
                    products_without_stock += 1
                else:
                    stock_factor = 1.0
                    products_with_stock += 1
                product_factors["stock"] = round(stock_factor, 3)
                
                # ================================================
                # COMBINE ALL FACTORS
                # ================================================
                
                # Product multiplier = all product-specific factors (except stock)
                product_multiplier = trend_factor * category_factor
                
                # Calculate units with ALL factors
                units_adjusted = base_units * global_multiplier * product_multiplier
                
                # Apply stock as final gate (can only sell what we have)
                final_units = units_adjusted * stock_factor
                
                # Calculate revenue
                product_forecast_value = final_units * price
                full_potential = units_adjusted * price  # What we could sell with stock
                
                total_forecast += product_forecast_value
                total_if_all_stock += full_potential
                
                # Include in breakdown
                if product_forecast_value > 0 or full_potential > 50:
                    breakdown.append({
                        "mlb_id": p.mlb_id,
                        "title": p.title[:50] if p.title else "?",
                        "avg_units": round(base_units, 2),
                        "units_adjusted": round(units_adjusted, 2),
                        "final_units": round(final_units, 2),
                        "price": price,
                        "stock": stock,
                        "stock_full": p.stock_full or 0,
                        "stock_local": p.stock_local or 0,
                        "stock_incoming": p.stock_incoming or 0,
                        "days_of_coverage": float(p.days_of_coverage or 0),
                        "global_factors": all_global_factors,
                        "product_factors": product_factors,
                        "forecast_value": round(product_forecast_value, 2),
                        "potential_value": round(full_potential, 2),
                        "lost_revenue": round(full_potential - product_forecast_value, 2),
                        "curve": p.curve
                    })
            
            # Calculate impact metrics
            lost_revenue = total_if_all_stock - total_forecast
            stock_impact_pct = (lost_revenue / total_if_all_stock * 100) if total_if_all_stock > 0 else 0
            
            # Sort breakdown by forecast value desc
            breakdown.sort(key=lambda x: x["forecast_value"], reverse=True)
            
            logger.info(f"[FORECAST] Product-based forecast: R${total_forecast:.2f} (lost R${lost_revenue:.2f} due to stock)")
            
            return {
                "date": target_date.isoformat(),
                "method": "product_based_v2",
                "total_forecast": round(total_forecast, 2),
                "total_potential": round(total_if_all_stock, 2),
                "lost_to_stock": round(lost_revenue, 2),
                "stock_impact_pct": round(stock_impact_pct, 1),
                "global_factors": all_global_factors,
                "global_multiplier": round(global_multiplier, 3),
                "products_with_stock": products_with_stock,
                "products_without_stock": products_without_stock,
                "breakdown": breakdown[:20],
                "_note": "All available factors applied without bias. Data will determine impact over time."
            }
            
        except Exception as e:
            logger.error(f"[FORECAST] Error in product-based forecast: {e}")
            import traceback
            traceback.print_exc()
            return None

    def reconcile_predictions(self) -> Dict:
        """
        Reconcile pending forecast logs with actual sales data
        """
        try:
            from app.models.forecast_learning import ForecastLog
            
            # Find all pending logs for past hours
            now = datetime.now()
            
            pending_logs = self.db.query(ForecastLog).filter(
                ForecastLog.valor_real.is_(None),
                ForecastLog.hora_alvo < now
            ).all()
            
            processed_count = 0
            total_error = 0.0
            
            for log in pending_logs:
                # Get actual sales for that hour
                actual_data = self.data_collector.get_hourly_sales(log.hora_alvo.date(), log.hora_alvo.hour)
                actual_revenue = actual_data["revenue"]
                
                # Update log
                log.valor_real = actual_revenue
                
                # Calculate Error
                if actual_revenue > 0:
                    # error % = (predicted - actual) / actual
                    # Fix TypeError: Convert Decimal to float
                    predicted_val = float(log.valor_previsto or 0)
                    error = ((predicted_val - actual_revenue) / actual_revenue) * 100
                elif float(log.valor_previsto or 0) > 0:
                     # If actual is 0 but we predicted something, error is 100% (or infinite?)
                     # Let's cap at 100% surplus
                     error = 100.0
                else:
                    error = 0.0
                
                # Cap error to fit Numeric(5, 2) i.e., max 999.99
                if error > 999.99:
                    error = 999.99
                elif error < -999.99:
                    error = -999.99
                    
                log.erro_percentual = round(error, 2)
                
                total_error += abs(error)
                processed_count += 1
            
            self.db.commit()
            
            avg_abs_error = (total_error / processed_count) if processed_count > 0 else 0
            
            return {
                "reconciled": processed_count,
                "avg_abs_error": round(avg_abs_error, 2)
            }
            
        except Exception as e:
            logger.error(f"[FORECAST] Errors during reconciliation: {e}")
            self.db.rollback()
            raise e
