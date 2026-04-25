'use client';

import React from 'react';
import ProductForecastDashboard from '@/components/hyper-ai/ProductForecastDashboard';
import { SupplyCircuit } from '@/components/ui/SupplyCircuit';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import Link from 'next/link';

export default function EstoquePage() {
    const dashboardRef = React.useRef<any>(null);
    const [isSyncing, setIsSyncing] = React.useState(false);

    const handleRefresh = async () => {
        if (dashboardRef.current) {
            setIsSyncing(true);
            try {
                await dashboardRef.current.handleSync();
            } finally {
                setIsSyncing(false);
            }
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white p-6 md:p-10 space-y-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8 group">
                    <div className="flex items-center gap-4">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 shadow-[0_0_20px_rgba(34,211,238,0.1)] group-hover:shadow-[0_0_30px_rgba(34,211,238,0.2)] transition-all duration-500">
                            <div className="w-8 h-8">
                                <SupplyCircuit />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white tracking-tight">
                                Forecast <span className="text-slate-500 font-medium">de Suprimentos</span>
                            </h1>
                            <p className="text-slate-400 text-sm mt-1">Inteligência preditiva para reposição e saúde de estoque</p>
                        </div>
                    </div>

                    <button
                        onClick={handleRefresh}
                        disabled={isSyncing}
                        className={`p-2.5 rounded-xl bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800/50 transition-all duration-300 ${isSyncing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-cyan-500/30 shadow-lg'}`}
                        title="Atualizar Dados"
                    >
                        <RefreshCw className={`w-5 h-5 text-slate-400 ${isSyncing ? 'animate-spin text-cyan-400' : 'group-hover:text-cyan-400'}`} />
                    </button>
                </div>

                {/* Product Forecast Dashboard */}
                <ProductForecastDashboard ref={dashboardRef} />
            </div>
        </div>
    );
}
