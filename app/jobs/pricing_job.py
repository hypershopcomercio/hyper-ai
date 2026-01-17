"""
Hyper Pricing Job
Executes automated pricing strategies on Fridays at 22h (Brazil time).
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.pricing_log import PriceAdjustmentLog
from app.services.meli_api import MeliApiService

logger = logging.getLogger(__name__)

# Constants
MAX_STEP_PERCENT = 5.0  # Maximum price change per step (5%)
MAX_RETRIES = 3


def execute_pricing_strategies():
    """
    Main job function. Finds ads with active pricing strategies and executes
    the next step of price adjustment.
    
    Returns:
        dict with execution summary
    """
    logger.info("=" * 50)
    logger.info("PRICING JOB: Starting execution...")
    logger.info("=" * 50)
    
    db = SessionLocal()
    meli_api = MeliApiService(db)
    
    results = {
        "total_ads": 0,
        "executed": 0,
        "skipped": 0,
        "failed": 0,
        "details": []
    }
    
    try:
        # Find ads with active pricing strategies
        # Criteria: target_margin > 0 AND (suggested_price != price OR target_margin != current margin)
        ads_with_strategies = db.query(Ad).filter(
            Ad.target_margin > 0,
            Ad.suggested_price.isnot(None),
            Ad.status == 'active'
        ).all()
        
        results["total_ads"] = len(ads_with_strategies)
        logger.info(f"Found {len(ads_with_strategies)} ads with active pricing strategies")
        
        for ad in ads_with_strategies:
            result = _execute_single_strategy(db, meli_api, ad)
            results["details"].append(result)
            
            if result["status"] == "success":
                results["executed"] += 1
            elif result["status"] == "skipped":
                results["skipped"] += 1
            else:
                results["failed"] += 1
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Pricing job failed: {e}")
        db.rollback()
    finally:
        db.close()
    
    logger.info(f"PRICING JOB COMPLETED: {results['executed']} executed, {results['skipped']} skipped, {results['failed']} failed")
    return results


def _execute_single_strategy(db: Session, meli_api: MeliApiService, ad: Ad) -> dict:
    """
    Executes a single pricing strategy for one ad.
    """
    result = {
        "ad_id": ad.id,
        "title": ad.title[:50] if ad.title else "",
        "status": "pending",
        "old_price": float(ad.price or 0),
        "new_price": None,
        "message": ""
    }
    
    current_price = float(ad.price or 0)
    target_price = float(ad.suggested_price or 0)
    
    # Skip if no meaningful difference
    if abs(current_price - target_price) < 0.01:
        result["status"] = "skipped"
        result["message"] = "Already at target price"
        logger.info(f"[{ad.id}] Skipped - already at target price")
        return result
    
    # Calculate the step price
    step_price = _calculate_step_price(current_price, target_price)
    result["new_price"] = step_price
    
    # Determine step number (count previous logs)
    previous_logs = db.query(PriceAdjustmentLog).filter(
        PriceAdjustmentLog.ad_id == ad.id,
        PriceAdjustmentLog.status == 'success'
    ).count()
    step_number = previous_logs + 1
    
    # Calculate total steps needed
    total_steps = _calculate_total_steps(current_price, target_price)
    
    # Create log entry before execution
    log_entry = PriceAdjustmentLog(
        ad_id=ad.id,
        old_price=Decimal(str(current_price)),
        new_price=Decimal(str(step_price)),
        target_price=Decimal(str(target_price)),
        target_margin=ad.target_margin,
        step_number=step_number,
        total_steps=total_steps,
        trigger_type='scheduled',
        status='pending'
    )
    db.add(log_entry)
    db.flush()  # Get ID for reference
    
    # Execute the price update on ML
    api_result = meli_api.update_item_price(ad.id, step_price)
    
    if api_result["success"]:
        # Update local ad record
        ad.price = step_price
        
        # Update log
        log_entry.status = 'success'
        
        result["status"] = "success"
        result["message"] = f"Price updated: {current_price:.2f} -> {step_price:.2f}"
        logger.info(f"[{ad.id}] SUCCESS: {current_price:.2f} -> {step_price:.2f}")
    else:
        log_entry.status = 'failed'
        log_entry.error_message = api_result.get("error", "Unknown error")
        
        result["status"] = "failed"
        result["message"] = api_result.get("error", "Unknown error")
        logger.error(f"[{ad.id}] FAILED: {api_result.get('error')}")
    
    return result


def _calculate_step_price(current_price: float, target_price: float) -> float:
    """
    Calculate the next step price, respecting max 5% change per step
    and distributing evenly across remaining steps.
    """
    if current_price <= 0:
        return target_price
    
    # Calculate total change percentage
    total_change_percent = ((target_price / current_price) - 1) * 100
    
    # If change is tiny, just go to target
    if abs(total_change_percent) < 1:
        return target_price
    
    # Number of steps needed
    num_steps = max(1, int(abs(total_change_percent) / MAX_STEP_PERCENT) + (1 if abs(total_change_percent) % MAX_STEP_PERCENT > 0.5 else 0))
    
    # Even distribution per step
    step_percent = total_change_percent / num_steps
    
    # Calculate new price
    new_price = current_price * (1 + step_percent / 100)
    
    # Round to 2 decimal places
    return round(new_price, 2)


def _calculate_total_steps(current_price: float, target_price: float) -> int:
    """Calculate total number of steps needed."""
    if current_price <= 0:
        return 1
    
    total_change_percent = ((target_price / current_price) - 1) * 100
    
    if abs(total_change_percent) < 1:
        return 1
    
    return max(1, int(abs(total_change_percent) / MAX_STEP_PERCENT) + (1 if abs(total_change_percent) % MAX_STEP_PERCENT > 0.5 else 0))


def execute_single_ad_step(ad_id: str, target_price: float = None) -> dict:
    """
    Manual execution for a single ad. Used by the UI "jump to step" button.
    
    Args:
        ad_id: The MLB item ID
        target_price: Optional specific price to set. If None, uses next calculated step.
    """
    db = SessionLocal()
    meli_api = MeliApiService(db)
    
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return {"success": False, "error": "Ad not found"}
        
        # If target_price provided, use it directly (manual jump)
        if target_price:
            step_price = round(float(target_price), 2)  # Ensure 2 decimal places
        else:
            # Calculate next step
            current_price = float(ad.price or 0)
            final_target = float(ad.suggested_price or current_price)
            step_price = _calculate_step_price(current_price, final_target)
        
        # CRITICAL: ML API requires exactly 2 decimal places for BRL
        step_price = round(step_price, 2)
        
        # Create log entry
        log_entry = PriceAdjustmentLog(
            ad_id=ad.id,
            old_price=Decimal(str(round(float(ad.price or 0), 2))),
            new_price=Decimal(str(step_price)),
            target_price=Decimal(str(round(float(ad.suggested_price or step_price), 2))),
            target_margin=ad.target_margin,
            step_number=1,  # Manual doesn't track steps
            total_steps=1,
            trigger_type='manual',
            status='pending'
        )
        db.add(log_entry)
        db.flush()
        
        # Execute
        api_result = meli_api.update_item_price(ad_id, step_price)
        
        if api_result["success"]:
            # Initialize strategy if it was inactive
            if not ad.strategy_start_price or ad.strategy_start_price <= 0:
                ad.strategy_start_price = float(ad.price or 0) # Store the OLD price as start point
            
            ad.price = step_price
            # Increment step counter for timeline progress tracking
            ad.current_step_number = (ad.current_step_number or 0) + 1
            log_entry.status = 'success'
            db.commit()
            return {
                "success": True,
                "old_price": api_result["old_price"],
                "new_price": step_price,
                "current_step": ad.current_step_number,
                "message": "Price updated successfully"
            }
        else:
            log_entry.status = 'failed'
            log_entry.error_message = api_result.get("error")
            db.commit()
            return {
                "success": False,
                "error": api_result.get("error")
            }
            
    except Exception as e:
        db.rollback()
        logger.error(f"Manual execution failed for {ad_id}: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def retry_failed_adjustments():
    """
    Retry all failed price adjustments that haven't exceeded max retries.
    Called by scheduler if there were failures.
    """
    db = SessionLocal()
    meli_api = MeliApiService(db)
    
    try:
        failed_logs = db.query(PriceAdjustmentLog).filter(
            PriceAdjustmentLog.status == 'failed',
            PriceAdjustmentLog.retry_count < MAX_RETRIES
        ).all()
        
        logger.info(f"Found {len(failed_logs)} failed adjustments to retry")
        
        for log in failed_logs:
            # Update retry info
            log.retry_count += 1
            log.last_retry_at = datetime.utcnow()
            log.trigger_type = 'retry'
            
            # Execute
            api_result = meli_api.update_item_price(log.ad_id, float(log.new_price))
            
            if api_result["success"]:
                log.status = 'success'
                # Update ad record
                ad = db.query(Ad).filter(Ad.id == log.ad_id).first()
                if ad:
                    ad.price = float(log.new_price)
                logger.info(f"[{log.ad_id}] Retry SUCCESS")
            else:
                log.error_message = api_result.get("error")
                logger.error(f"[{log.ad_id}] Retry FAILED: {api_result.get('error')}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Retry job failed: {e}")
    finally:
        db.close()



def verify_recent_price_changes(db: Session = None):
    """
    Verifies if recent price changes were actually applied on Mercado Livre.
    Logs tagged as 'success' in the last 2 hours are checked against the live API.
    """
    logger.info("VERIFICATION JOB: Checking recent price consistency...")
    
    local_session = False
    if not db:
        db = SessionLocal()
        local_session = True
        
    meli_api = MeliApiService(db)
    
    try:
        # Check logs from last 2 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=2)
        
        # Find logs that are 'success' but not yet 'verified'
        # Since we don't have 'verified' status yet, we process 'success' and update them.
        recent_logs = db.query(PriceAdjustmentLog).filter(
            PriceAdjustmentLog.status == 'success',
            PriceAdjustmentLog.executed_at >= cutoff_time
        ).all()
        
        verified_count = 0
        mismatch_count = 0
        
        for log in recent_logs:
            # 1. Get Live Price
            # We use get_item_pricing or simpler get_item details
            # get_item_details takes a list
            details = meli_api.get_item_details([log.ad_id])
            
            if not details:
                continue
                
            item_data = details[0]
            live_price = float(item_data.get("price", 0))
            expected_price = float(log.new_price)
            
            # 2. Compare
            # Allow tiny floating point diff
            if abs(live_price - expected_price) < 0.02:
                log.status = 'verified'
                verified_count += 1
            else:
                log.status = 'mismatch'
                log.error_message = f"MISMATCH: Expected {expected_price}, Found {live_price}"
                mismatch_count += 1
                logger.warning(f"[{log.ad_id}] Price MISMATCH! Expected R$ {expected_price}, Found R$ {live_price}")
        
        db.commit()
        logger.info(f"VERIFICATION COMPLETED: {verified_count} verified, {mismatch_count} mismatches.")
        
    except Exception as e:
        logger.error(f"Verification job failed: {e}")
        db.rollback()
    finally:
        if local_session:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = execute_pricing_strategies()
    print(f"Result: {result}")
