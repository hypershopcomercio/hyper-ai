import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Plus, Trash2, ExternalLink, AlertTriangle, CheckCircle, Search, ChevronDown, ChevronUp } from 'lucide-react';
import { CompetitorImpactChart } from './CompetitorImpactChart';
import { CompetitorMarginSimulator } from './CompetitorMarginSimulator';
import { toast } from 'sonner';

interface Competitor {
    id: string;
    title: string;
    price: number;
    original_price?: number;
    permalink: string;
    status: 'active' | 'paused' | 'closed';
    added_at: string;
}

interface CompetitorManagerProps {
    adId: string;
}

export function CompetitorManager({ adId }: CompetitorManagerProps) {
    const [competitors, setCompetitors] = useState<Competitor[]>([]);
    const [newUrl, setNewUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [expandedCompetitorId, setExpandedCompetitorId] = useState<string | null>(null);
    const [simulationData, setSimulationData] = useState<any>(null);

    useEffect(() => {
        if (adId) {
            loadCompetitors();
            loadSimulationData();
        }
    }, [adId]);

    const loadCompetitors = async () => {
        try {
            const res = await api.get(`/ads/${adId}/competitors`);
            setCompetitors(res.data);
        } catch (err) {
            console.error('Erro ao carregar concorrentes:', err);
            toast.error('Erro ao carregar concorrentes');
        }
    };

    const loadSimulationData = async () => {
        try {
            const res = await api.get(`/financial/ads/${adId}/simulation`);
            setSimulationData(res.data);
        } catch (err) {
            console.error('Erro ao carregar dados financeiros:', err);
        }
    };

    const handleAddCompetitor = async () => {
        if (!newUrl.trim()) return;

        setLoading(true);
        try {
            await api.post(`/ads/${adId}/competitors`, { url: newUrl });
            setNewUrl('');
            toast.success('Concorrente adicionado');
            await loadCompetitors();
        } catch (err) {
            console.error('Erro ao adicionar concorrente:', err);
            toast.error('Erro ao adicionar concorrente');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteCompetitor = async (competitorId: string) => {
        if (!confirm('Remover este concorrente do monitoramento?')) return;

        try {
            await api.delete(`/ads/${adId}/competitors/${competitorId}`);
            toast.success('Concorrente removido');
            await loadCompetitors();
        } catch (err) {
            console.error('Erro ao remover concorrente:', err);
            toast.error('Erro ao remover');
        }
    };

    const handleSyncAll = async () => {
        try {
            setLoading(true);
            await api.post(`/ads/${adId}/competitors/sync`);
            toast.success('Sincronização iniciada');
            await loadCompetitors();
        } catch (err) {
            console.error('Erro ao sincronizar:', err);
            toast.error('Erro ao sincronizar');
        } finally {
            setLoading(false);
        }
    };

    const filteredCompetitors = competitors.filter(comp =>
        comp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        comp.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="space-y-4">
            {/* Add Competitor Input */}
            <div className="flex gap-2">
                <div className="relative flex-1">
                    <input
                        type="text"
                        value={newUrl}
                        onChange={(e) => setNewUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAddCompetitor()}
                        placeholder="Cole a URL do concorrente (Mercado Livre)..."
                        className="w-full bg-[#09090b] border border-white/10 rounded-lg px-4 py-2.5 text-sm text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50 transition-colors"
                        disabled={loading}
                    />
                </div>
                <button
                    onClick={handleAddCompetitor}
                    disabled={loading || !newUrl.trim()}
                    className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-700 disabled:bg-slate-800 disabled:text-slate-600 rounded-lg font-medium text-sm text-white transition-colors flex items-center gap-2 cursor-pointer disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <Plus size={16} />
                    )}
                    {loading ? 'Adicionando...' : 'Adicionar'}
                </button>
                <button
                    onClick={handleSyncAll}
                    disabled={loading || competitors.length === 0}
                    className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 rounded-lg font-medium text-sm text-white transition-colors flex items-center gap-2 cursor-pointer disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <Search size={16} />
                    )}
                    {loading ? 'Sincronizando...' : 'Sincronizar Todos'}
                </button>
            </div>

            {/* Competitors List */}
            <div className="bg-[#13141b] rounded-xl border border-white/5 overflow-hidden">
                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <AlertTriangle size={16} className="text-amber-500" />
                        <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wide">
                            CONCORRENTES MONITORADOS
                        </h3>
                        <span className="px-2 py-0.5 bg-cyan-500/10 rounded text-xs font-bold text-cyan-400">
                            {competitors.length}
                        </span>
                    </div>
                </div>

                <div className="p-4">
                    {competitors.length === 0 ? (
                        <div className="text-center py-12">
                            <AlertTriangle size={32} className="mx-auto text-slate-600 mb-3" />
                            <p className="text-sm text-slate-500">Nenhum concorrente monitorado</p>
                            <p className="text-xs text-slate-600 mt-1">Adicione URLs do Mercado Livre acima</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {filteredCompetitors.map((comp) => {
                                const isExpanded = expandedCompetitorId === comp.id;

                                return (
                                    <div key={comp.id} className="bg-[#09090b] rounded-lg border border-white/5">
                                        {/* Competitor Header */}
                                        <div className="p-4 flex items-center justify-between">
                                            <div className="flex items-center gap-3 flex-1">
                                                <div className="flex items-center gap-2 bg-amber-500/10 px-2 py-1 rounded text-[10px] font-mono text-amber-400">
                                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                                                    ML
                                                </div>
                                                <div className="flex-1">
                                                    <p className="text-xs text-slate-400 line-clamp-1">{comp.title}</p>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <span className="text-[10px] font-mono text-blue-400">
                                                            {comp.id}
                                                        </span>
                                                        <span className="text-[10px] text-slate-600">•</span>
                                                        <div className="flex items-baseline gap-1.5">
                                                            {comp.original_price && comp.original_price > comp.price && (
                                                                <span className="text-xs text-slate-500 line-through">
                                                                    R$ {comp.original_price.toFixed(2)}
                                                                </span>
                                                            )}
                                                            <span className="text-sm font-bold text-emerald-400">R$ {comp.price.toFixed(2)}</span>
                                                        </div>
                                                        {comp.status === 'active' ? (
                                                            <CheckCircle size={12} className="text-emerald-500" />
                                                        ) : (
                                                            <AlertTriangle size={12} className="text-amber-500" />
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => setExpandedCompetitorId(isExpanded ? null : comp.id)}
                                                    className="p-2 hover:bg-white/5 rounded-lg transition-colors cursor-pointer text-slate-400 hover:text-cyan-400"
                                                    title={isExpanded ? "Ocultar análise" : "Ver análise de impacto"}
                                                >
                                                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                                </button>
                                                <a
                                                    href={comp.permalink}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="p-2 hover:bg-white/5 rounded-lg transition-colors cursor-pointer text-slate-400 hover:text-cyan-400"
                                                    title="Abrir no ML"
                                                >
                                                    <ExternalLink size={14} />
                                                </a>
                                                <button
                                                    onClick={() => handleDeleteCompetitor(comp.id)}
                                                    className="p-2 hover:bg-white/5 rounded-lg transition-colors cursor-pointer text-slate-400 hover:text-red-400"
                                                    title="Remover"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        </div>

                                        {/* Expanded Section with Impact Chart & Simulation */}
                                        {isExpanded && (
                                            <div className="px-4 pb-4 border-t border-white/5 space-y-4 pt-4">
                                                {simulationData && (
                                                    <div className="animate-in slide-in-from-top-2 fade-in duration-300">
                                                        <CompetitorMarginSimulator
                                                            competitorPrice={comp.price}
                                                            data={simulationData}
                                                        />
                                                    </div>
                                                )}

                                                <div>
                                                    <CompetitorImpactChart
                                                        adId={adId}
                                                        competitorId={comp.id}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
