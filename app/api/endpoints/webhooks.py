"""
Webhook endpoint for Mercado Livre notifications.
Receives real-time order updates and queues them for processing.
"""
from flask import request, jsonify
import logging
from queue import Queue
from datetime import datetime

from app.api import api_bp

logger = logging.getLogger(__name__)

# In-memory queue for webhook events (MVP - use Redis for production)
webhook_queue = Queue()

# Track processed events to avoid duplicates
processed_events = set()
MAX_PROCESSED_CACHE = 10000


@api_bp.route('/webhooks/ml', methods=['POST'])
def receive_ml_webhook():
    """
    Receive Mercado Livre webhook notification.
    Must respond within 500ms to avoid retries.
    
    Expected payload:
    {
        "resource": "/orders/2000014403184862",
        "user_id": 123456789,
        "topic": "orders_v2",
        "application_id": 7890123456789012,
        "attempts": 1,
        "sent": "2025-12-23T12:00:00.000-03:00",
        "received": "2025-12-23T12:00:00.500-03:00"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        resource = data.get('resource', '')
        topic = data.get('topic', '')
        user_id = data.get('user_id')
        attempts = data.get('attempts', 1)
        sent = data.get('sent', '')
        
        # Create unique event ID to prevent duplicate processing
        event_id = f"{topic}:{resource}:{sent}"
        
        if event_id in processed_events:
            logger.info(f"[WEBHOOK] Duplicate event ignored: {event_id}")
            return jsonify({"status": "duplicate"}), 200
        
        # Log the incoming webhook
        logger.info(f"[WEBHOOK] Received: topic={topic}, resource={resource}, attempts={attempts}")
        
        # Validate topic
        supported_topics = ['orders_v2', 'items', 'questions', 'messages', 'payments']
        if topic not in supported_topics:
            logger.warning(f"[WEBHOOK] Unsupported topic: {topic}")
            return jsonify({"status": "unsupported_topic"}), 200
        
        # Queue the event for async processing
        webhook_queue.put({
            'resource': resource,
            'topic': topic,
            'user_id': user_id,
            'attempts': attempts,
            'sent': sent,
            'received_at': datetime.utcnow().isoformat()
        })
        
        # Mark as processed
        processed_events.add(event_id)
        
        # Prune cache if too large
        if len(processed_events) > MAX_PROCESSED_CACHE:
            # Remove oldest half
            to_remove = list(processed_events)[:MAX_PROCESSED_CACHE // 2]
            for item in to_remove:
                processed_events.discard(item)
        
        return jsonify({"status": "queued"}), 200
        
    except Exception as e:
        logger.error(f"[WEBHOOK] Error processing webhook: {e}")
        # Still return 200 to prevent ML from retrying
        return jsonify({"status": "error", "message": str(e)}), 200


@api_bp.route('/webhooks/status', methods=['GET'])
def webhook_status():
    """Get webhook processing status."""
    return jsonify({
        "queue_size": webhook_queue.qsize(),
        "processed_count": len(processed_events)
    })
