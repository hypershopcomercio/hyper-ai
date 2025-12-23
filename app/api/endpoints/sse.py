"""
Server-Sent Events (SSE) endpoint for real-time dashboard updates.
"""
from flask import Response, stream_with_context
import json
import time
import logging
from queue import Queue, Empty
from threading import Lock

from app.api import api_bp

logger = logging.getLogger(__name__)

# Global SSE subscribers (thread-safe)
_sse_queues = []
_sse_lock = Lock()


def broadcast_event(event_type: str, data: dict):
    """
    Broadcast an event to all connected SSE clients.
    Called by WebhookProcessor when orders are synced.
    """
    event_data = {
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    }
    
    with _sse_lock:
        dead_queues = []
        for q in _sse_queues:
            try:
                q.put_nowait(event_data)
            except:
                dead_queues.append(q)
        
        # Clean up dead queues
        for q in dead_queues:
            _sse_queues.remove(q)
    
    logger.info(f"[SSE] Broadcast: {event_type} to {len(_sse_queues)} clients")


def _generate_events(client_queue: Queue):
    """Generator that yields SSE events."""
    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"
        
        while True:
            try:
                # Wait for events with timeout (keeps connection alive)
                event = client_queue.get(timeout=30)
                
                event_type = event.get('type', 'update')
                event_data = json.dumps(event.get('data', {}))
                
                yield f"event: {event_type}\ndata: {event_data}\n\n"
                
            except Empty:
                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"
                
    except GeneratorExit:
        logger.info("[SSE] Client disconnected")
    finally:
        # Clean up
        with _sse_lock:
            if client_queue in _sse_queues:
                _sse_queues.remove(client_queue)


@api_bp.route('/sse/updates', methods=['GET'])
def sse_updates():
    """
    SSE endpoint for real-time updates.
    
    Events:
    - connected: Initial connection confirmation
    - order_update: New order synced
    - item_update: Item/Ad synced
    - sync_status: Sync job status change
    """
    # Create a queue for this client
    client_queue = Queue(maxsize=100)
    
    with _sse_lock:
        _sse_queues.append(client_queue)
    
    logger.info(f"[SSE] New client connected. Total: {len(_sse_queues)}")
    
    response = Response(
        stream_with_context(_generate_events(client_queue)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            'Access-Control-Allow-Origin': '*'
        }
    )
    
    return response


@api_bp.route('/sse/status', methods=['GET'])
def sse_status():
    """Get SSE connection status."""
    from flask import jsonify
    return jsonify({
        'connected_clients': len(_sse_queues)
    })
