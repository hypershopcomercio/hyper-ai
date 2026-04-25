"use client";

import { useEffect, useRef, useState, useCallback } from 'react';

interface SSEEvent {
    type: string;
    data: any;
    timestamp: number;
}

interface UseSSEOptions {
    url: string;
    onEvent?: (event: SSEEvent) => void;
    onConnect?: () => void;
    onDisconnect?: () => void;
    reconnectDelay?: number;
}

export function useSSE({
    url,
    onEvent,
    onConnect,
    onDisconnect,
    reconnectDelay = 5000
}: UseSSEOptions) {
    const [isConnected, setIsConnected] = useState(false);
    const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const mountedRef = useRef(true);

    // Store callbacks in refs to avoid recreating connect function
    const onEventRef = useRef(onEvent);
    const onConnectRef = useRef(onConnect);
    const onDisconnectRef = useRef(onDisconnect);

    useEffect(() => {
        onEventRef.current = onEvent;
        onConnectRef.current = onConnect;
        onDisconnectRef.current = onDisconnect;
    }, [onEvent, onConnect, onDisconnect]);

    useEffect(() => {
        mountedRef.current = true;

        const connect = () => {
            if (!mountedRef.current) return;

            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }

            const eventSource = new EventSource(url);
            eventSourceRef.current = eventSource;

            eventSource.onopen = () => {
                if (!mountedRef.current) return;
                console.log('[SSE] Connected');
                setIsConnected(true);
                onConnectRef.current?.();
            };

            eventSource.onerror = () => {
                if (!mountedRef.current) return;
                console.log('[SSE] Connection lost, will reconnect...');
                setIsConnected(false);
                onDisconnectRef.current?.();

                // Attempt reconnect
                if (reconnectTimeoutRef.current) {
                    clearTimeout(reconnectTimeoutRef.current);
                }
                reconnectTimeoutRef.current = setTimeout(() => {
                    if (mountedRef.current) {
                        console.log('[SSE] Reconnecting...');
                        connect();
                    }
                }, reconnectDelay);
            };

            // Handle custom events
            eventSource.addEventListener('connected', () => {
                console.log('[SSE] Connection confirmed');
            });

            eventSource.addEventListener('heartbeat', () => {
                // Heartbeat received, connection is alive
            });

            eventSource.addEventListener('webhook_processed', (e) => {
                try {
                    const data = JSON.parse(e.data);
                    const event: SSEEvent = {
                        type: 'webhook_processed',
                        data,
                        timestamp: Date.now()
                    };
                    setLastEvent(event);
                    onEventRef.current?.(event);
                } catch (err) {
                    console.error('[SSE] Parse error:', err);
                }
            });

            eventSource.addEventListener('order_update', (e) => {
                try {
                    const data = JSON.parse(e.data);
                    const event: SSEEvent = {
                        type: 'order_update',
                        data,
                        timestamp: Date.now()
                    };
                    setLastEvent(event);
                    onEventRef.current?.(event);
                } catch (err) {
                    console.error('[SSE] Parse error:', err);
                }
            });
        };

        connect();

        return () => {
            mountedRef.current = false;
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [url, reconnectDelay]);

    const reconnect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }
        // Trigger reconnect by dispatching error
        setIsConnected(false);
    }, []);

    return {
        isConnected,
        lastEvent,
        reconnect,
        disconnect: reconnect
    };
}
