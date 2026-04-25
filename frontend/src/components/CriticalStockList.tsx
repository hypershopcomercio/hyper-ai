"use client";

import { Ad } from "@/types";
import { CheckCircle, AlertTriangle, Truck, ShoppingCart, Info } from "lucide-react";
import axios from "axios";

interface Props {
    ads: Ad[];
    loading: boolean;
    pendingPurchases: any;
    onPurchase: (ad: Ad) => void;
    onMarkArrived: (purchaseId: number) => void;
}

export function CriticalStockList({ ads, loading, pendingPurchases, onPurchase, onMarkArrived }: Props) {
    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center text-slate-500">
                <div className="flex flex-col items-center gap-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-red-500"></div>
                    <span>Analisando riscos de estoque...</span>
                </div>
            </div>
        );
    }

    if (ads.length === 0) {
        return (
            <div className="p-12 text-center border-2 border-dashed border-slate-800 rounded-xl">
                <div className="inline-flex p-4 rounded-full bg-slate-800/50 mb-4">
                    <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
                <h3 className="text-lg font-medium text-white">Tudo sob controle!</h3>
                <p className="text-slate-500 mt-1">Não há produtos com risco iminente de ruptura.</p>
            </div>
        );
    }

    // Grouping Logic
    const critical = ads.filter(ad => (ad.days_to_run_out || 999) <= 0); // Already out
    const urgent = ads.filter(ad => (ad.days_to_run_out || 999) > 0 && (ad.days_to_run_out || 999) <= 3);
    const attention = ads.filter(ad => (ad.days_to_run_out || 999) > 3 && (ad.days_to_run_out || 999) <= 7);
    const others = ads.filter(ad => (ad.days_to_run_out || 999) > 7);

    const renderGroup = (title: string, items: Ad[], colorClass: string, icon: any) => {
        if (items.length === 0) return null;
        const Icon = icon;

        return (
            <div className="mb-8">
                <div className={`flex items-center gap-2 mb-4 px-2 ${colorClass}`}>
                    <Icon size={18} />
                    <h3 className="font-bold text-sm tracking-wide uppercase">{title} ({items.length})</h3>
                </div>

                <div className="space-y-3">
                    {items.map(ad => {
                        const pending = pendingPurchases[ad.id];

                        return (
                            <div key={ad.id} className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-lg p-4 flex flex-col md:flex-row items-start md:items-center gap-6 hover:border-slate-600 transition-colors">
                                {/* Image & Title */}
                                <div className="flex items-start gap-4 flex-1 min-w-0">
                                    <img src={ad.thumbnail} alt="" className="w-16 h-16 rounded object-contain bg-white shrink-0" />
                                    <div className="min-w-0">
                                        <h4 className="font-medium text-slate-200 truncate pr-4 text-base" title={ad.title}>{ad.title}</h4>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-xs bg-[#0D0D14] px-1.5 py-0.5 rounded text-slate-500 font-mono">{ad.id}</span>
                                        </div>
                                        <div className="mt-2 text-xs text-slate-400 flex items-center gap-4">
                                            <span>Full: <b className="text-slate-200">{ad.available_quantity}</b></span>
                                            <span>Local: <b className="text-slate-200">{ad.stock_local || 0}</b></span>
                                            <span>Venda Média: <b className="text-slate-200">{((ad.sales_30d || 0) / 30).toFixed(1)}/dia</b></span>
                                        </div>
                                    </div>
                                </div>

                                {/* Risk Info */}
                                <div className="flex flex-col items-end md:items-start min-w-[140px] border-l border-[#2D2D3A] pl-6 h-full justify-center">
                                    <div className="text-xs text-slate-500 uppercase font-semibold mb-1">Risco Estimado</div>
                                    <div className="text-base text-slate-200 font-bold">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(ad.risk_value || 0)}
                                    </div>
                                    <div className={`text-xs mt-1 font-bold ${(ad.days_to_run_out || 0) <= 0 ? 'text-red-500' :
                                        (ad.days_to_run_out || 0) <= 3 ? 'text-orange-500' : 'text-yellow-500'
                                        }`}>
                                        Zera em {(ad.days_to_run_out || 0).toFixed(1)} dias
                                    </div>
                                </div>

                                {/* Purchase Action */}
                                <div className="flex flex-col gap-2 min-w-[180px]">
                                    {pending ? (
                                        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="text-xs font-bold text-blue-400">Chegando</span>
                                                <span className="text-[10px] text-blue-300 bg-blue-500/20 px-1.5 rounded">
                                                    {pending.quantity} un
                                                </span>
                                            </div>
                                            <p className="text-[10px] text-slate-400">
                                                Previsão: {new Date(pending.nextArrival).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                                            </p>

                                            {/* Logic to mark as arrived if close? For now simple button */}
                                            <button
                                                onClick={() => pending.purchaseIds?.[0] && onMarkArrived(pending.purchaseIds[0])}
                                                className="mt-2 w-full py-1 text-[10px] bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors"
                                            >
                                                Confirmar Chegada
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="text-xs text-slate-500 mb-1">Status de Reposição</div>
                                            <button
                                                onClick={() => onPurchase(ad)}
                                                className="w-full py-2 bg-red-600 hover:bg-red-500 text-white font-bold text-sm rounded-lg shadow-lg shadow-red-900/20 transition-all flex items-center justify-center gap-2"
                                            >
                                                <ShoppingCart size={16} />
                                                Comprar
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }

    return (
        <div>
            {renderGroup("Crítico - Zera Hoje / Já Zerou", critical, "text-red-500", AlertTriangle)}
            {renderGroup("Alerta - Zera em 1-3 dias", urgent, "text-orange-500", AlertTriangle)}
            {renderGroup("Atenção - Zera em 3-7 dias", attention, "text-yellow-500", Info)}
            {renderGroup("Monitoramento - +7 dias", others, "text-slate-500", Info)}
        </div>
    );
}
