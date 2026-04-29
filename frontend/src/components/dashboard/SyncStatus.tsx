"use client";

import { useSSE } from '@/hooks/useSSE';
import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';

interface SyncStatusProps {
    onDataRefresh?: () => void; // Refreshes dashboard data
    onNewSale?: (productName?: string) => void; // Celebration - ONLY from real SSE order_update
}

export function SyncStatus({ onDataRefresh, onNewSale }: SyncStatusProps) {
    const [lastSync, setLastSync] = useState<Date | null>(null);
    const [showPulse, setShowPulse] = useState(false);
    const [isSyncing, setIsSyncing] = useState(false);
    const lastProcessedRef = useRef<string | null>(null);
    const isInitializedRef = useRef(false);

    // SSE for instant updates when available
    const { isConnected } = useSSE({
        url: '/api/sse/updates',
        onEvent: (event) => {
            console.log('[SyncStatus] SSE event received:', event.type);

            // ONLY trigger celebration for order_update (real new sale from webhook)
            if (event.type === 'order_update') {
                console.log('[SyncStatus] 🎉 REAL NEW SALE from SSE webhook!');
                const productName = event.data?.title || event.data?.product_name || 'Novo Pedido';
                onNewSale?.(productName);
                // Data refresh happens in SalesFireworks onComplete callback
            } else if (event.type === 'webhook_processed') {
                // Other webhook events - just refresh data, no celebration
                refreshData();
            }
        }
    });

    // Polling fallback - check for new webhooks every 10 seconds
    useEffect(() => {
        const checkForUpdates = async () => {
            try {
                const res = await api.get('/webhooks/status');
                const newTimestamp = res.data.last_processed_at;

                // First check: just store the timestamp, don't trigger
                if (!isInitializedRef.current) {
                    lastProcessedRef.current = newTimestamp;
                    isInitializedRef.current = true;
                    return;
                }

                // Subsequent checks: only refresh if timestamp changed
                if (newTimestamp && newTimestamp !== lastProcessedRef.current) {
                    console.log('[SyncStatus] Polling detected new data:', newTimestamp);
                    lastProcessedRef.current = newTimestamp;
                    refreshData();
                }
            } catch (err) {
                // Silent fail for polling
            }
        };

        // Check immediately (to get initial timestamp) then every 10 seconds
        checkForUpdates();
        const interval = setInterval(checkForUpdates, 10000);
        return () => clearInterval(interval);
    }, []);

    // Only refresh data - NO celebration here
    const refreshData = () => {
        setLastSync(new Date());
        setShowPulse(true);
        onDataRefresh?.(); // Just refresh, no fireworks
        setTimeout(() => setShowPulse(false), 2000);
    };

    // Manual sync when clicking on Live indicator
    const handleManualSync = async () => {
        if (isSyncing) return;

        setIsSyncing(true);
        console.log('[SyncStatus] Manual sync triggered');

        try {
            await api.post('/jobs/trigger', { job_type: 'quick_sync' });
            await new Promise(resolve => setTimeout(resolve, 3000));
            refreshData();
        } catch (err) {
            console.error('[SyncStatus] Manual sync failed:', err);
            refreshData();
        } finally {
            setIsSyncing(false);
        }
    };

    return (
        <div className="flex items-center gap-2 text-sm relative z-10">
            {/* Live Indicator - Clickable for manual sync */}
            <div
                className="flex items-center gap-1.5 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={handleManualSync}
                title="Clique para atualizar dados"
            >
                <div className="relative flex h-2.5 w-2.5 items-center justify-center">
                    {isConnected && !isSyncing && (
                        <span className="animate-ping absolute inset-0 block h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    )}
                    {isSyncing && (
                        <span className="animate-spin absolute inset-0 block h-full w-full rounded-full border-2 border-green-400 border-t-transparent"></span>
                    )}
                    <span className={`relative block rounded-full h-2.5 w-2.5 ${isSyncing ? 'bg-yellow-500' : isConnected ? 'bg-green-500' : 'bg-gray-400'
                        }`}></span>
                </div>
                <span className={`font-medium ${isSyncing ? 'text-yellow-500' : isConnected ? 'text-green-500' : 'text-gray-400'
                    }`}>
                    {isSyncing ? 'Sincronizando...' : isConnected ? 'Live' : 'Offline'}
                </span>
            </div>

            {/* Last Sync Time */}
            {lastSync && (
                <span className="text-gray-400 text-xs">
                    Última atualização: {lastSync.toLocaleTimeString('pt-BR')}
                </span>
            )}

            {/* New Order Pulse */}
            {showPulse && (
                <span className="text-green-400 text-xs animate-pulse">
                    ✓ Atualizado!
                </span>
            )}
        </div>
    );
}
