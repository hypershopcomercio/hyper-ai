"""
Additional forecast endpoints for specific date generation and incomplete day tracking
"""
from flask import request, jsonify
from app.core.database import SessionLocal
from app.services.forecast.engine import HyperForecast
from app.models.forecast_learning import ForecastLog
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
import logging

logger = logging.getLogger(__name__)


def generate_for_specific_date():
    """
    Generate predictions for a specific date (all 24 hours).
    Accepts a date in YYYY-MM-DD format.
    """
    try:
        data = request.get_json()
        target_date_str = data.get('date')
        
        if not target_date_str:
            return jsonify({"success": False, "error": "Date parameter is required"}), 400
        
        # Parse date
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Don't allow dates too far in the past (e.g., more than 30 days)
        yesterday = (datetime.now() - timedelta(days=1)).date()
        if target_date < (yesterday - timedelta(days=30)):
            return jsonify({"success": False, "error": "Cannot generate for dates older than 30 days"}), 400
        
        # Generate for this specific date
        db = SessionLocal()
        try:
            forecast = HyperForecast(db)
            predictions_made = 0
            
            force = data.get('force', False)
            
            # Generate all 24 hours for this date
            for hour in range(24):
                try:
                    target_dt = datetime.combine(target_date, datetime.min.time()) + timedelta(hours=hour)
                    
                    # Check if exists (unless forced)
                    if not force:
                        existing = db.query(ForecastLog).filter(
                            ForecastLog.hora_alvo == target_dt
                        ).first()
                        
                        if existing:
                            continue
                    
                    # Generate
                    result = forecast.predict_hour_with_logging(hour, target_date)
                    if result and 'prediction' in result:
                        predictions_made += 1
                        
                except Exception as e_hour:
                    logger.error(f"Failed for {target_date} {hour:02d}h: {e_hour}")
                    continue
            
            return jsonify({
                "success": True,
                "data": {
                    "date": target_date_str,
                    "predictions_made": predictions_made,
                    "message": f"Geradas {predictions_made} previsões para {target_date_str}"
                }
            })
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Generate for date error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def get_incomplete_days():
    """
    Get list of days with less than 24 predictions.
    Returns days from yesterday backwards for up to 30 days.
    """
    try:
        db = SessionLocal()
        try:
            yesterday = (datetime.now() - timedelta(days=1)).date()
            # Fixed start date as per user request: Dec 18, 2025
            cutoff_date = datetime(2025, 12, 18).date()
            
            # Query to count predictions per day
            results = db.query(
                cast(ForecastLog.hora_alvo, Date).label('date'),
                func.count(ForecastLog.id).label('count')
            ).filter(
                ForecastLog.hora_alvo >= cutoff_date,
                ForecastLog.hora_alvo < datetime.now()
            ).group_by(
                cast(ForecastLog.hora_alvo, Date)
            ).all()
            
            # Build map of dates to counts
            date_counts = {str(r.date): r.count for r in results}
            
            # Find incomplete days
            incomplete_days = []
            current_check = yesterday
            
            # Check days back until cutoff
            days_diff = (yesterday - cutoff_date).days
            for i in range(days_diff + 1):
                date_str = str(current_check)
                count = date_counts.get(date_str, 0)
                
                if count < 24:
                    incomplete_days.append({
                        "date": date_str,
                        "count": count,
                        "missing": 24 - count
                    })
                
                current_check -= timedelta(days=1)
            
            return jsonify({
                "success": True,
                "data": {
                    "incomplete_days": incomplete_days,
                    "total_incomplete": len(incomplete_days)
                }
            })
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error fetching incomplete days: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def get_allowed_factors():
    """
    Get all allowed factors (whitelisted keys).
    """
    from app.models.forecast_learning import AllowedFactor
    
    db = SessionLocal()
    try:
        factors = db.query(AllowedFactor).filter(AllowedFactor.is_active == 'Y').all()
        
        result = [
            {
                "id": f.id,
                "factor_type": f.factor_type,
                "factor_key": f.factor_key,
                "description": f.description
            }
            for f in factors
        ]
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error fetching allowed factors: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


def add_allowed_factor():
    """
    Add a new allowed factor key to the whitelist.
    """
    from app.models.forecast_learning import AllowedFactor
    
    data = request.json
    factor_type = data.get('factor_type')
    factor_key = data.get('factor_key')
    description = data.get('description')
    
    if not factor_type or not factor_key:
        return jsonify({"status": "error", "message": "Missing type or key"}), 400
        
    # Validation: No spaces in key
    if ' ' in factor_key:
        return jsonify({"status": "error", "message": "Keys cannot contain spaces"}), 400
        
    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(AllowedFactor).filter_by(
            factor_type=factor_type, 
            factor_key=factor_key
        ).first()
        
        if existing:
            if existing.is_active == 'N':
                existing.is_active = 'Y'
                if description: existing.description = description
                db.commit()
                return jsonify({"status": "ok", "message": "Factor reactivated"}), 200
            else:
                return jsonify({"status": "error", "message": "Factor already exists"}), 400
                
        new_factor = AllowedFactor(
            factor_type=factor_type,
            factor_key=factor_key,
            description=description
        )
        db.add(new_factor)
        db.commit()
        
        return jsonify({"status": "ok", "id": new_factor.id}), 201
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding allowed factor: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()


def delete_allowed_factor(factor_id):
    """
    Soft delete an allowed factor.
    """
    from app.models.forecast_learning import AllowedFactor
    
    db = SessionLocal()
    try:
        factor = db.query(AllowedFactor).get(factor_id)
        if not factor:
            return jsonify({"status": "error", "message": "Not found"}), 404
            
        # Soft delete
        factor.is_active = 'N'
        db.commit()
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting allowed factor: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db.close()
