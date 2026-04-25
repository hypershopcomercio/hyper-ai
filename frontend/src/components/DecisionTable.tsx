
import { ArrowLeft, HelpCircle, TrendingUp, TrendingDown, DollarSign, ArrowDown, ArrowUp, ArrowUpDown, Truck, CheckCircle, Info, AlertCircle } from 'lucide-react';
import { Ad } from '../types';
import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import PurchaseModal from './PurchaseModal';
import { Tooltip } from './ui/Tooltip';

interface DecisionTableProps {
    ads: Ad[];
    loading: boolean;
    sort: string;
    onSort: (field: string) => void;
    filterType?: string;
    sortOrder?: string;
    onRefresh?: () => void;
}

export function DecisionTable({ ads, loading, onSort, filterType, sort, sortOrder, onRefresh }: DecisionTableProps) {
    const [modalOpen, setModalOpen] = useState(false);
    const [selectedAd, setSelectedAd] = useState<Ad | null>(null);
    const [pendingPurchases, setPendingPurchases] = useState<any>({});

    const isRisk = filterType === 'stock_risk';
    const isMargin = filterType === 'low_margin';
    const isDefault = !filterType;
    const showStockRisk = isRisk || isDefault;
    const showMargin = isMargin || isDefault;

    // Helper for currency
    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

    const loadPendingPurchases = async () => {
        try {
            const res = await axios.get('http://localhost:5000/api/purchases/pending');
            setPendingPurchases(res.data.pending || {});
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (showStockRisk) {
            loadPendingPurchases();
        }
    }, [showStockRisk]);

    const handleOpenPurchase = (ad: Ad) => {
        setSelectedAd(ad);
        setModalOpen(true);
    };

    const handlePurchaseSuccess = (purchase: any) => {
        loadPendingPurchases();
        if (onRefresh) onRefresh();
    };

    const handleMarkArrived = async (purchaseId: number) => {
        if (!confirm('Confirma que a compra chegou no galpão?')) return;
        try {
            await axios.put(`http://localhost:5000/api/purchases/${purchaseId}/status`, { status: 'arrived' });
            loadPendingPurchases();
            if (onRefresh) onRefresh();
        } catch (e) {
            alert('Erro ao atualizar status');
        }
    };

    // Calculate Stats for Summary Cards
    const stats = useMemo(() => {
        if (!isRisk) return null;
        const totalRisk = ads.reduce((sum, ad) => sum + (ad.risk_value || 0), 0);
        const criticalCount = ads.length;
        const zeroToday = ads.filter(ad => (ad.days_to_run_out || 999) <= 1).length;
        const zeroIn7Days = ads.filter(ad => (ad.days_to_run_out || 999) <= 7).length;
        const pendingCount = Object.keys(pendingPurchases).length;

        return { totalRisk, criticalCount, zeroToday, zeroIn7Days, pendingCount };
    }, [ads, pendingPurchases, isRisk]);


    const renderActionButton = (ad: Ad) => {
        const pending = pendingPurchases[ad.id];

        if (pending) {
            const nextArrival = new Date(pending.nextArrival);
            const today = new Date();
            const daysToArrival = Math.ceil((nextArrival.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

            if (daysToArrival <= 0) {
                const pid = pending.purchaseIds?.[0];
                return (
                    <button
                        onClick={() => pid && handleMarkArrived(pid)}
                        className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded flex items-center gap-1 mx-auto transition-colors whitespace-nowrap"
                    >
                        <CheckCircle size={14} className="mr-1" /> Chegou?
                    </button>
                );
            }

            return (
                <div className="px-3 py-1.5 bg-blue-500/20 text-blue-400 text-xs font-medium rounded-lg border border-blue-500/30 flex flex-col items-center whitespace-nowrap">
                    <span>Chegando</span>
                    <span className="text-[10px] opacity-75">({daysToArrival}d)</span>
                </div>
            );
        }

        const days = ad.days_to_run_out || 999;
        const isUrgent = days <= 1;

        return (
            <button
                onClick={() => handleOpenPurchase(ad)}
                className={`px-3 py-1.5 text-xs font-bold rounded transition-colors whitespace-nowrap shadow-sm ${isUrgent
                    ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse'
                    : 'bg-emerald-600 hover:bg-emerald-500 text-white'
                    }`}
            >
                {isUrgent ? 'Comprar Urgente!' : 'Comprar Estoque'}
            </button>
        );
    };

    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center text-slate-500">
                <div className="flex flex-col items-center gap-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-500"></div>
                    <span>Carregando dados estratégicos...</span>
                </div>
            </div>
        );
    }

    if (ads.length === 0) {
        return <div className="p-8 text-center text-slate-500">Nenhum anúncio encontrado com os filtros atuais.</div>;
    }

    const SortIcon = ({ column }: { column: string }) => {
        if (sort !== column) return <ArrowUpDown size={14} className="text-slate-600 opacity-50" />;
        return sortOrder === 'asc'
            ? <ArrowUp size={14} className="text-white" />
            : <ArrowDown size={14} className="text-white" />;
    };

    const SortableHeader = ({ label, sortKey }: { label: string, sortKey: string }) => {
        const isActive = sort === sortKey;
        return (
            <th
                className={`px-4 py-3 text-center cursor-pointer transition-all duration-300 select-none text-[10px] uppercase tracking-widest font-bold border-r border-slate-800/30 last:border-r-0 ${isActive ? 'bg-slate-800/50 text-white shadow-[inset_0_-2px_0_0_#22d3ee]' : 'text-slate-500 hover:bg-slate-800/30 hover:text-slate-300'}`}
                onClick={() => onSort(sortKey)}
            >
                <div className="flex items-center justify-center gap-1.5">
                    {label}
                    {isActive ? (
                        <span className="text-cyan-400">
                            {sortOrder === 'asc' ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                        </span>
                    ) : (
                        <ArrowUpDown size={12} className="text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                    )}
                </div>
            </th>
        );
    };

    // --- RENDER CRITICAL TAB (isRisk) ---
    if (isRisk) {
        return (
            <div className="flex flex-col gap-6">
                <PurchaseModal
                    isOpen={modalOpen}
                    onClose={() => setModalOpen(false)}
                    product={selectedAd}
                    onSuccess={handlePurchaseSuccess}
                />

                {/* SUMMARY CARDS */}
                {stats && (
                    <div className="grid grid-cols-4 gap-4">
                        <div className="premium-border-container group/card">
                            <div className="premium-border-beam" />
                            <div className="premium-card rounded-xl p-4 h-full relative">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium mb-1">
                                    Total em Risco
                                    <Tooltip
                                        title="Capital em Risco"
                                        content="Valor total em estoque de produtos que podem entrar em ruptura nos próximos 30 dias se não houver reposição."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-red-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <p className="text-2xl font-bold text-red-400">
                                    {formatCurrency(stats.totalRisk)}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">
                                    {stats.criticalCount} produtos críticos
                                </p>
                            </div>
                        </div>
                        <div className="premium-border-container group/card">
                            <div className="premium-border-beam" />
                            <div className="premium-card rounded-xl p-4 h-full relative">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium mb-1">
                                    Zeram Hoje
                                    <Tooltip
                                        title="Atenção Imediata"
                                        content="Produtos que já atingiram o estoque crítico (0 ou próximo de zero) e precisam de ação urgente."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-red-500 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <p className="text-2xl font-bold text-red-500">
                                    {stats.zeroToday}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">produtos</p>
                            </div>
                        </div>
                        <div className="premium-border-container group/card">
                            <div className="premium-border-beam" />
                            <div className="premium-card rounded-xl p-4 h-full relative">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium mb-1">
                                    Zeram em 7 dias
                                    <Tooltip
                                        title="Planejamento Curto Prazo"
                                        content="Produtos cujo estoque atual deve durar menos de uma semana baseado na média de vendas."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-yellow-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <p className="text-2xl font-bold text-yellow-400">
                                    {stats.zeroIn7Days}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">produtos</p>
                            </div>
                        </div>
                        <div className="premium-border-container group/card">
                            <div className="premium-border-beam" />
                            <div className="premium-card rounded-xl p-4 h-full relative">
                                <div className="text-slate-400 text-sm flex items-center gap-1.5 font-medium mb-1">
                                    Compras Pendentes
                                    <Tooltip
                                        title="Estoque em Trânsito"
                                        content="Quantidade de ordens de compra emitidas que ainda não foram recebidas no estoque central."
                                    >
                                        <Info className="w-3.5 h-3.5 text-slate-600 group-hover/card:text-blue-400 transition-colors cursor-help" />
                                    </Tooltip>
                                </div>
                                <p className="text-2xl font-bold text-blue-400">
                                    {stats.pendingCount}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">aguardando chegada</p>
                            </div>
                        </div>
                    </div>
                )}

                <div className="premium-border-container shadow-2xl">
                    <div className="premium-border-beam" />
                    <div className="premium-card rounded-xl overflow-hidden relative">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead className="text-[10px] uppercase tracking-widest text-slate-500 font-bold sticky top-0 z-10 bg-[#0a0a0f] border-t border-slate-800/50">
                                    <tr className="border-b border-slate-800/50">
                                        <th className="px-4 py-3 w-[300px] border-r border-slate-800/30">Anúncio</th>
                                        <SortableHeader label="DIAS P/ ZERAR" sortKey="days_to_run_out" />
                                        <th className="px-4 py-3 text-center whitespace-nowrap border-r border-slate-800/30">ESTOQUE (FULL/LOCAL)</th>
                                        <th className="px-4 py-3 text-center whitespace-nowrap border-r border-slate-800/30">COMPRA PENDENTE</th>
                                        <SortableHeader label="RISCO TOTAL" sortKey="risk_value" />
                                        <th className="px-4 py-3 text-center whitespace-nowrap border-r border-slate-800/30">VENDAS</th>
                                        <th className="px-4 py-3 text-center whitespace-nowrap border-r border-slate-800/30">PREÇO</th>
                                        <th className="px-4 py-3 text-center w-[140px] text-white bg-slate-800/40 font-black">AÇÃO</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {ads.map((ad) => {
                                        const pending = pendingPurchases[ad.id];
                                        return (
                                            <tr key={ad.id} className="group hover:bg-slate-800/30 transition-all odd:bg-slate-900/20">
                                                {/* 1. ANÚNCIO */}
                                                <td className="px-4 py-3">
                                                    <div className="flex items-start gap-3">
                                                        <div className="relative shrink-0">
                                                            <img src={ad.thumbnail} className="w-12 h-12 rounded object-contain bg-white border border-slate-800/50" loading="lazy" />
                                                        </div>
                                                        <div className="min-w-0">
                                                            <p className="text-sm font-bold text-slate-200 truncate pr-4 group-hover:text-cyan-400 transition-colors" title={ad.title}>
                                                                {ad.title}
                                                            </p>
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <a href={ad.permalink} target="_blank" rel="noreferrer" className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 hover:text-cyan-300 font-mono transition-colors cursor-pointer">
                                                                    {ad.id}
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </td>

                                                {/* 2. DIAS P/ ZERAR */}
                                                <td className="px-4 py-3 text-center">
                                                    <span className={`text-lg font-bold ${(ad.days_to_run_out || 999) <= 1 ? 'text-red-500' :
                                                        (ad.days_to_run_out || 999) <= 3 ? 'text-orange-500' :
                                                            (ad.days_to_run_out || 999) <= 7 ? 'text-yellow-500' :
                                                                'text-emerald-500'
                                                        }`}>
                                                        {(ad.days_to_run_out || 0).toFixed(1)}d
                                                    </span>
                                                </td>

                                                {/* 3. ESTOQUE */}
                                                <td className="px-4 py-3">
                                                    <div className="flex flex-col text-xs items-center">
                                                        <div className="flex justify-between w-24">
                                                            <span className="text-slate-500">Full:</span>
                                                            <span className="text-slate-200 font-medium">{ad.available_quantity || 0} un</span>
                                                        </div>
                                                        <div className="flex justify-between w-24 mt-1">
                                                            <span className="text-slate-500">Local:</span>
                                                            <span className="text-slate-400">{ad.stock_local || 0} un</span>
                                                        </div>
                                                    </div>
                                                </td>

                                                {/* 4. COMPRA PENDENTE (NEW) */}
                                                <td className="px-4 py-3 text-center">
                                                    {pending ? (
                                                        <div className="text-sm">
                                                            <span className="text-green-400 font-medium block">
                                                                {pending.quantity} un
                                                            </span>
                                                            <span className="text-slate-400 text-xs text-[10px]">
                                                                Chega {new Date(pending.nextArrival).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                                                            </span>
                                                        </div>
                                                    ) : (
                                                        <span className="text-slate-600">--</span>
                                                    )}
                                                </td>

                                                {/* 5. RISCO TOTAL */}
                                                <td className="px-4 py-3 text-center">
                                                    <div>
                                                        <p className="text-slate-200 font-bold">
                                                            {formatCurrency(ad.risk_value || 0)}
                                                        </p>
                                                        {(ad.risk_value || 0) > 0 && (
                                                            <span className="text-[10px] px-1.5 py-0.5 bg-red-500/10 text-red-400 rounded border border-red-500/20">
                                                                EM RISCO
                                                            </span>
                                                        )}
                                                    </div>
                                                </td>

                                                {/* 6. VENDAS */}
                                                <td className="px-4 py-3 text-center">
                                                    <div>
                                                        <p className="text-slate-200 font-medium">{ad.sales_30d || 0} un</p>
                                                        {ad.sales_7d_change !== null && ad.sales_7d_change !== undefined && (
                                                            <span className={`text-[10px] ${ad.sales_7d_change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                                {ad.sales_7d_change >= 0 ? '↑' : '↓'} {Math.abs(ad.sales_7d_change)}%
                                                            </span>
                                                        )}
                                                    </div>
                                                </td>

                                                {/* 7. PREÇO */}
                                                <td className="px-4 py-3 text-center">
                                                    <span className="text-slate-300 font-mono text-xs">
                                                        {formatCurrency(ad.price)}
                                                    </span>
                                                </td>

                                                {/* 8. AÇÃO */}
                                                <td className="px-4 py-3 text-center border-l border-slate-700 bg-slate-800/20">
                                                    {renderActionButton(ad)}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Default Layout for other Tabs (Todos, Baixa Margem, etc.)
    return (
        <div className="flex flex-col gap-6">
            <PurchaseModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                product={selectedAd}
                onSuccess={handlePurchaseSuccess}
            />
            <div className="premium-border-container shadow-2xl">
                <div className="premium-border-beam" />
                <div className="premium-card rounded-xl overflow-hidden relative">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="text-[10px] uppercase tracking-widest text-slate-500 font-bold sticky top-0 z-10 bg-[#0a0a0f] border-t border-slate-800/50">
                                <tr className="border-b border-slate-800/50">
                                    <th className="px-4 py-3 w-[300px] border-r border-slate-800/30 cursor-default">Anúncio</th>

                                    <th className="px-4 py-3 text-center cursor-pointer hover:bg-slate-800/50 transition-colors border-r border-slate-800/30" onClick={() => onSort('days_to_run_out')}>
                                        <div className="flex items-center justify-center gap-1.5">
                                            DIAS P/ ZERAR <SortIcon column="days_to_run_out" />
                                        </div>
                                    </th>

                                    <th className="px-4 py-3 text-center border-r border-slate-800/30 font-bold uppercase tracking-widest text-[10px]">
                                        Estoque (Full/Local)
                                    </th>

                                    {/* Standard Financial Columns */}
                                    {isMargin && (
                                        <th className="px-4 py-2 text-right text-red-400/80 uppercase tracking-widest text-[10px]">Custos</th>
                                    )}

                                    {showMargin && (
                                        <th className="px-4 py-2 text-right cursor-pointer hover:text-white transition-colors uppercase tracking-widest text-[10px]" onClick={() => onSort('margin_percent')}>
                                            <div className="flex items-center justify-end gap-1.5">
                                                <span className="text-emerald-400">Margem</span> <SortIcon column="margin_percent" />
                                            </div>
                                        </th>
                                    )}

                                    <th className="px-4 py-2 text-center w-[140px] font-bold text-white bg-slate-800/60 border-l border-slate-700">AÇÃO</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {/* Using standard ads for non-risk tabs */}
                                {ads.map((ad) => {
                                    return (
                                        <tr key={ad.id} className="group hover:bg-slate-800/30 transition-all odd:bg-slate-900/20">

                                            {/* PRODUCT */}
                                            <td className="px-4 py-3">
                                                <div className="flex items-start gap-3">
                                                    <div className="relative shrink-0">
                                                        <img src={ad.thumbnail} className="w-12 h-12 rounded object-contain bg-white border border-slate-800/50" loading="lazy" />
                                                    </div>
                                                    <div className="min-w-0">
                                                        <p className="text-sm font-bold text-slate-200 truncate pr-4 group-hover:text-cyan-400 transition-colors" title={ad.title}>
                                                            {ad.title}
                                                        </p>
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 font-mono">{ad.id}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>

                                            <td className="px-4 py-3 text-center bg-orange-500/5 border-l border-orange-500/10">
                                                <div className={`font-bold text-lg ${(ad.days_to_run_out || 999) <= 3 ? 'text-red-500' :
                                                    (ad.days_to_run_out || 999) <= 7 ? 'text-yellow-500' : 'text-orange-400'
                                                    }`}>
                                                    {ad.days_to_run_out ? ad.days_to_run_out.toFixed(1) : '?'}d
                                                </div>
                                            </td>

                                            <td className="px-4 py-3">
                                                <div className="flex flex-col text-xs">
                                                    <div className="flex justify-between gap-2">
                                                        <span className="text-slate-500">Full:</span>
                                                        <span className="text-slate-200 font-medium">{ad.available_quantity || 0} un</span>
                                                    </div>
                                                    <div className="flex justify-between gap-2">
                                                        <span className="text-slate-500">Local:</span>
                                                        <span className="text-slate-400 bg-slate-800/50 px-1 rounded">{ad.stock_local || 0} un</span>
                                                    </div>
                                                </div>
                                            </td>

                                            {isMargin && (
                                                <td className="px-4 py-3 text-right text-red-400/80">
                                                    R$ {((ad.cost || 0) + (ad.financials?.tax_cost || 0) + (ad.financials?.commission_cost || 0) + (ad.financials?.shipping_cost || 0)).toFixed(2)}
                                                </td>
                                            )}

                                            {showMargin && (
                                                <td className="px-4 py-3 text-right">
                                                    <div className={`font-bold ${ad.margin_percent && ad.margin_percent < 15 ? 'text-red-400' : 'text-emerald-400'}`}>
                                                        {ad.margin_percent ? `${ad.margin_percent.toFixed(1)}%` : '-'}
                                                    </div>
                                                </td>
                                            )}

                                            {/* ACTION COLUMN */}
                                            <td className="px-4 py-3 text-center border-l border-slate-700 bg-slate-800/20">
                                                {renderActionButton(ad)}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
