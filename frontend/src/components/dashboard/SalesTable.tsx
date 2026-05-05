import { useState, useMemo } from 'react';
import {
    ChevronDown,
    ChevronRight,
    Search,
    Package,
    ArrowUpRight,
    ArrowDownRight,
    Filter,
    Layers,
    List,
    Radio,
    Zap,
    RefreshCw
} from "lucide-react";
import { api } from '@/lib/api';

interface SalesItem {
    order_id: string;
    date: string;
    sku: string;
    title: string;
    thumbnail: string | null;
    quantity: number;
    unit_price: number;
    total_revenue: number;
    costs: {
        product: number;
        tax: number;
        fee: number;
        shipping: number;
        ads: number;
    };
    total_cost: number;
    net_margin: number;
    margin_percent: number;
    status?: string;
    buyer_name?: string;
    logistic_type?: string;
    ml_item_id?: string;
}

interface SalesTableProps {
    data: SalesItem[];
    isLoading?: boolean;
}

export function SalesTable({ data, isLoading }: SalesTableProps) {
    const [viewMode, setViewMode] = useState<'list' | 'grouped'>('list');
    const [searchTerm, setSearchTerm] = useState('');
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState<string>('');
    const [isSaving, setIsSaving] = useState(false);

    const handleSaveCost = async (mlItemId: string, sku: string) => {
        if (!mlItemId) return;
        setIsSaving(true);
        try {
            await api.patch(`/ads/${mlItemId}/cost`, { cost: parseFloat(editValue) });
            // For real-time feel, we should ideally trigger a dashboard refresh
            // DashboardPage has refetchMetrics, but we are in a child component.
            // For now, reload the page or rely on the user to refresh.
            window.location.reload(); 
        } catch (error) {
            console.error("Erro ao salvar custo:", error);
            alert("Erro ao salvar custo. Tente novamente.");
        } finally {
            setIsSaving(false);
            setEditingId(null);
        }
    };

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

    const formatPercent = (val: number | undefined | null) =>
        `${(val || 0).toFixed(1)}%`;

    const filteredData = useMemo(() => {
        if (!searchTerm) return data;
        const lower = searchTerm.toLowerCase();
        return data.filter(item =>
            item.title.toLowerCase().includes(lower) ||
            item.sku?.toLowerCase().includes(lower) ||
            item.order_id.includes(lower)
        );
    }, [data, searchTerm]);

    const groupedData = useMemo(() => {
        if (viewMode === 'list') return [];

        const groups: Record<string, any> = {};

        filteredData.forEach(item => {
            if (item.status === 'cancelled') return; // Exclude cancelled from analytical grouping

            // Group by SKU or Title if SKU missing
            const key = item.sku || item.title;

            if (!groups[key]) {
                groups[key] = {
                    key,
                    title: item.title,
                    thumbnail: item.thumbnail,
                    sku: item.sku,
                    ml_item_id: item.ml_item_id,
                    quantity: 0,
                    revenue: 0,
                    total_cost: 0,
                    net_margin: 0,
                    costs: { product: 0, tax: 0, fee: 0, shipping: 0, ads: 0 },
                    count: 0
                };
            }

            const g = groups[key];
            g.quantity += item.quantity;
            g.revenue += item.total_revenue;
            g.total_cost += item.total_cost;
            g.net_margin += item.net_margin;
        });

        return Object.values(groups).sort((a: any, b: any) => b.revenue - a.revenue);
    }, [filteredData, viewMode]);


    if (isLoading) return <div className="p-10 text-center text-slate-500">Carregando vendas...</div>;

    if (!data || data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-12 bg-[#151520] border border-slate-800/60 rounded-2xl text-slate-500 gap-3">
                <Package size={32} className="opacity-20" />
                <p className="text-sm">Nenhuma venda registrada neste período.</p>
            </div>
        );
    }

    return (
        <div className="w-full">
            {/* Table Header */}
            <div className="pb-2 flex flex-col sm:flex-row justify-between items-end gap-4 mt-2">
                <div className="flex items-center gap-3">
                    <div className="ml-1 p-1.5 bg-emerald-500/10 rounded-lg relative overflow-hidden group">
                        <div className="absolute inset-0 bg-emerald-500/20 blur-xl group-hover:bg-emerald-500/30 transition-all duration-500"></div>
                        <Zap size={16} className="text-emerald-500 relative z-10 animate-[pulse_3s_ease-in-out_infinite]" />
                    </div>
                    <div className="flex flex-col">
                        <p className="text-[10px] uppercase font-bold text-slate-500 flex gap-2 tracking-wider">
                            <span>{data.length} Pedidos</span>
                            {data.some(x => x.status === 'cancelled') && (
                                <span className="text-rose-500/70 flex items-center gap-1">
                                    <span>• {data.filter(x => x.status === 'cancelled').length} cancelados</span>
                                </span>
                            )}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* View Toggle */}
                    <div className="flex bg-[#1A1A2E] p-1 rounded-lg border border-slate-700/50">
                        <button
                            onClick={() => setViewMode('list')}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1.5 transition-all cursor-pointer ${viewMode === 'list'
                                ? 'bg-slate-700 text-white shadow-sm'
                                : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            <List size={14} />
                            Lista
                        </button>
                        <button
                            onClick={() => setViewMode('grouped')}
                            className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1.5 transition-all cursor-pointer ${viewMode === 'grouped'
                                ? 'bg-slate-700 text-white shadow-sm'
                                : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            <Layers size={14} />
                            Agrupado
                        </button>
                    </div>

                    {/* Search */}
                    <div className="relative group">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                        <input
                            type="text"
                            placeholder="Buscar produto, SKU..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-[#1A1A2E] border border-slate-700/50 rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 w-48 transition-all"
                        />
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
                <table className="w-full text-left border-collapse">
                    <thead className="text-[10px] uppercase font-semibold text-slate-500 border-b border-slate-800">
                        <tr className="whitespace-nowrap">
                            <th className="px-4 py-3 pl-6">Produto</th>
                            <th className="px-4 py-3 text-right">Qtd</th>
                            <th className="px-4 py-3 text-right text-slate-300">Venda</th>
                            <th className="px-4 py-3 text-right text-rose-400/70">Custo Prod.</th>
                            <th className="px-4 py-3 text-right text-rose-400/70">Taxa ML</th>
                            <th className="px-4 py-3 text-right text-rose-400/70">Imposto</th>
                            <th className="px-4 py-3 text-right text-rose-400/70">Frete</th>
                            <th className="px-4 py-3 text-right text-cyan-400">Mg. Contrib.</th>
                            <th className="px-4 py-3 text-right text-amber-500/80">Ads</th>
                            <th className="px-4 py-3 text-right text-emerald-400 pr-6">Mg. Final</th>
                        </tr>
                    </thead>
                    <tbody className="text-xs text-slate-300 divide-y divide-slate-800/50">
                        {viewMode === 'list' ? (
                            filteredData.map((item, idx) => {
                                const mgContrib = item.total_revenue - (item.costs.product + item.costs.tax + item.costs.fee + item.costs.shipping);
                                const mgContribPercent = item.total_revenue > 0 ? (mgContrib / item.total_revenue) * 100 : 0;
                                const isCancelled = item.status === 'cancelled';

                                return (
                                    <tr key={`${item.order_id}-${idx}`} className={`border-b border-slate-800/50 hover:bg-slate-800/60 even:bg-slate-900/30 transition-all duration-200 group ${isCancelled ? 'opacity-60 grayscale' : ''}`}>
                                        <td className="px-4 py-3 pl-6">
                                            <div className="flex items-center gap-3">
                                                <div
                                                    className="w-8 h-8 bg-slate-800 rounded flex items-center justify-center shrink-0 overflow-hidden border border-slate-700/30 cursor-help"
                                                    title={`Comprador: ${item.buyer_name || 'Desconhecido'}`}
                                                >
                                                    {item.thumbnail ? (
                                                        <img src={item.thumbnail} alt="" className={`w-full h-full object-cover ${isCancelled ? 'grayscale' : ''}`} />
                                                    ) : (
                                                        <Package size={14} className="opacity-30" />
                                                    )}
                                                </div>
                                                <div className="flex flex-col">
                                                    <div className="flex flex-col gap-1">
                                                        <span
                                                            className={`font-medium min-w-[180px] flex items-center gap-2 cursor-help ${isCancelled ? 'text-slate-500/80 line-through decoration-slate-600' : 'text-slate-200'}`}
                                                            title={`Comprador: ${item.buyer_name || 'Desconhecido'}`}
                                                        >
                                                            {item.logistic_type?.toLowerCase() === 'fulfillment' && (
                                                                <span className="bg-emerald-500 text-white text-[9px] font-black uppercase px-1 rounded flex items-center gap-0.5 shadow-[0_0_8px_rgba(16,185,129,0.4)] shrink-0 mt-0.5">
                                                                    <Zap size={8} fill="currentColor" /> FULL
                                                                </span>
                                                            )}
                                                            {item.title}
                                                            {isCancelled && (
                                                                <span className="text-[9px] font-bold text-slate-500 border border-slate-700/50 px-1 rounded-sm bg-slate-800 uppercase tracking-tighter ml-1">
                                                                    Cancelado
                                                                </span>
                                                            )}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-right font-medium text-slate-400 whitespace-nowrap">{item.quantity}</td>
                                        <td className="px-4 py-3 text-right font-medium text-white whitespace-nowrap">{formatCurrency(item.total_revenue)}</td>

                                        {/* Costs Breakdown */}
                                        <td className="px-4 py-3 text-right whitespace-nowrap">
                                            {editingId === `${item.order_id}-${idx}` ? (
                                                <div className="flex items-center justify-end relative">
                                                    <input
                                                        autoFocus
                                                        type="text"
                                                        value={editValue}
                                                        onChange={(e) => setEditValue(e.target.value.replace(/[^0-9.]/g, ''))}
                                                        onBlur={() => handleSaveCost(item.ml_item_id || '', item.sku)}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') handleSaveCost(item.ml_item_id || '', item.sku);
                                                            if (e.key === 'Escape') setEditingId(null);
                                                        }}
                                                        className="w-24 bg-[#0F172A]/90 border-2 border-emerald-500/40 rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 transition-all shadow-xl shadow-emerald-500/5 font-medium text-right"
                                                    />
                                                    {isSaving && (
                                                        <div className="absolute left-2 top-1/2 -translate-y-1/2">
                                                            <RefreshCw size={10} className="animate-spin text-emerald-400" />
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                <div 
                                                    className="cursor-pointer hover:bg-slate-700/50 rounded px-1 -mx-1 transition-colors"
                                                    onClick={() => {
                                                        setEditingId(`${item.order_id}-${idx}`);
                                                        setEditValue(item.costs.product.toString());
                                                    }}
                                                >
                                                    {item.costs.product === 0 ? (
                                                        <span className="text-rose-500 font-bold flex items-center justify-end gap-1" title="Clique para editar custo">
                                                            <span className="text-rose-500 animate-pulse text-[10px]">⚠</span>
                                                            {formatCurrency(item.costs.product)}
                                                        </span>
                                                    ) : (
                                                        <span className="text-slate-500 group-hover:text-slate-300 transition-colors" title="Clique para editar custo">{formatCurrency(item.costs.product)}</span>
                                                    )}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-right text-slate-500 whitespace-nowrap">{formatCurrency(item.costs.fee)}</td>
                                        <td className="px-4 py-3 text-right text-slate-500 whitespace-nowrap">{formatCurrency(item.costs.tax)}</td>
                                        <td className="px-4 py-3 text-right text-slate-500 whitespace-nowrap">{formatCurrency(item.costs.shipping)}</td>

                                        {/* Contribution Margin */}
                                        <td className="px-4 py-3 text-right whitespace-nowrap">
                                            <div className="flex items-baseline justify-end gap-1.5">
                                                <span className="font-semibold text-cyan-500">{formatCurrency(mgContrib)}</span>
                                                <span className="text-[10px] text-cyan-500/70">({formatPercent(mgContribPercent)})</span>
                                            </div>
                                        </td>

                                        <td className="px-4 py-3 text-right text-amber-500/80 whitespace-nowrap">{formatCurrency(item.costs.ads)}</td>

                                        {/* Net Margin */}
                                        <td className="px-4 py-3 text-right pr-6 whitespace-nowrap">
                                            <div className="flex items-baseline justify-end gap-1.5">
                                                <span className={`font-bold ${item.net_margin >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {formatCurrency(item.net_margin)}
                                                </span>
                                                <span className={`text-[10px] ${item.margin_percent >= 15 ? 'text-emerald-500/70' :
                                                    item.margin_percent >= 0 ? 'text-amber-500/70' :
                                                        'text-rose-500/70'
                                                    }`}>
                                                    ({formatPercent(item.margin_percent)})
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        ) : (
                            groupedData.map((group, idx) => {
                                const mgContrib = group.revenue - (group.costs.product + group.costs.tax + group.costs.fee + group.costs.shipping);
                                const mgContribPercent = group.revenue > 0 ? (mgContrib / group.revenue) * 100 : 0;
                                const avgMargin = group.revenue > 0 ? (group.net_margin / group.revenue) * 100 : 0;

                                return (
                                    <tr key={idx} className="hover:bg-slate-800/20 transition-colors">
                                        <td className="p-4 pl-6">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 bg-slate-800 rounded flex items-center justify-center shrink-0 overflow-hidden border border-slate-700/30">
                                                    {group.thumbnail ? (
                                                        <img src={group.thumbnail} alt="" className="w-full h-full object-cover" />
                                                    ) : (
                                                        <Package size={14} className="opacity-30" />
                                                    )}
                                                </div>
                                                <div className="flex flex-col justify-center">
                                                    <span className="font-medium text-slate-200 line-clamp-1 max-w-[200px]" title={group.title}>{group.title}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-4 text-right font-medium text-slate-400">{group.quantity}</td>
                                        <td className="p-4 text-right font-medium text-white">{formatCurrency(group.revenue)}</td>

                                        <td className="p-4 text-right whitespace-nowrap">
                                            {editingId === `group-${idx}` ? (
                                                <div className="flex items-center justify-end relative">
                                                    <input
                                                        autoFocus
                                                        type="text"
                                                        value={editValue}
                                                        onChange={(e) => setEditValue(e.target.value.replace(/[^0-9.]/g, ''))}
                                                        onBlur={() => handleSaveCost(group.ml_item_id || '', group.sku)}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') handleSaveCost(group.ml_item_id || '', group.sku);
                                                            if (e.key === 'Escape') setEditingId(null);
                                                        }}
                                                        className="w-24 bg-[#0F172A]/90 border-2 border-emerald-500/40 rounded-lg px-2 py-1 text-[11px] text-white focus:outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-500/10 transition-all shadow-xl shadow-emerald-500/5 font-medium text-right"
                                                    />
                                                    {isSaving && (
                                                        <div className="absolute left-2 top-1/2 -translate-y-1/2">
                                                            <RefreshCw size={10} className="animate-spin text-emerald-400" />
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                <div 
                                                    className="group/cost relative cursor-pointer hover:bg-emerald-500/5 rounded-md px-2 py-1 -mx-2 transition-all duration-300"
                                                    onClick={() => {
                                                        setEditingId(`group-${idx}`);
                                                        setEditValue((group.costs.product / group.quantity).toString());
                                                    }}
                                                >
                                                    <div className="flex items-center justify-end gap-2">
                                                        <span className="text-slate-400 group-hover/cost:text-emerald-400 transition-colors font-medium text-[11px]">{formatCurrency(group.costs.product)}</span>
                                                        <div className="opacity-0 group-hover/cost:opacity-100 transition-opacity">
                                                            <Zap size={10} className="text-emerald-500/50" />
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </td>
                                        <td className="p-4 text-right text-slate-500">{formatCurrency(group.costs.fee)}</td>
                                        <td className="p-4 text-right text-slate-500">{formatCurrency(group.costs.tax)}</td>
                                        <td className="p-4 text-right text-slate-500">{formatCurrency(group.costs.shipping)}</td>

                                        {/* Contrib Margin */}
                                        <td className="p-4 text-right">
                                            <div className="flex items-baseline justify-end gap-1.5">
                                                <span className="font-semibold text-cyan-500">{formatCurrency(mgContrib)}</span>
                                                <span className="text-[10px] text-cyan-500/70">({formatPercent(mgContribPercent)})</span>
                                            </div>
                                        </td>

                                        <td className="p-4 text-right text-amber-500/80">{formatCurrency(group.costs.ads)}</td>

                                        {/* Net Margin */}
                                        <td className="p-4 text-right pr-6">
                                            <div className="flex items-baseline justify-end gap-1.5">
                                                <span className={`font-bold ${group.net_margin >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {formatCurrency(group.net_margin)}
                                                </span>
                                                <span className={`text-[10px] ${avgMargin >= 15 ? 'text-emerald-500/70' :
                                                    avgMargin >= 0 ? 'text-amber-500/70' :
                                                        'text-rose-500/70'
                                                    }`}>
                                                    ({formatPercent(avgMargin)})
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>

            <div className="p-3 border-t border-slate-800/50 bg-[#1A1A2E]/30 text-center text-[10px] text-slate-500">
                * Ads referente a esta venda específico ainda não disponível (em breve). Taxa de Imposto estimada em 5.6%.
            </div>
        </div>
    );
}
