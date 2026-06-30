import React, { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
    TrendingUp, TrendingDown, PauseCircle, PlayCircle, RefreshCw, AlertTriangle,
    CheckCircle2, Target, Calendar, Info, History, Settings as SettingsIcon
} from "lucide-react";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

interface Props {
    adId: string;
}

interface StrategyData {
    ad_id: string;
    is_active: boolean;
    is_paused: boolean;
    current_price: number;
    target_price: number | null;
    target_margin: number | null;
    current_step_number: number;
    conversion: {
        current: number;
        threshold: number;
        method: string;
        explanation: string;
        break_even_at_target: number;
    };
    reversion_status: {
        triggered: boolean;
        reason: string;
        avg_7d: number;
        current: number;
        drop_pct: number;
    };
    elasticity: {
        score: number | null;
        label: string;
        suggestion: string;
        action?: string;
        analysis?: string;
    };
    price_steps: Array<{
        step: number;
        date: string;
        date_display: string;
        price: number;
        increase_pct: number;
        reason: string;
    }>;
    step_size_pct: number;
    estimated_days: number;
    tooltips: Record<string, string>;
}

interface PriceLog {
    id: number;
    old_price: number;
    new_price: number;
    target_price: number | null;
    step_number: number;
    total_steps: number;
    trigger_type: string;
    executed_at: string;
    status: string;
    error_message: string | null;
}

const formatCurrency = (value: number | null | undefined) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);

export function RepricerTab({ adId }: Props) {
    const [data, setData] = useState<StrategyData | null>(null);
    const [history, setHistory] = useState<PriceLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [marginInput, setMarginInput] = useState("");

    const fetchData = useCallback(async () => {
        try {
            const [stratRes, histRes] = await Promise.all([
                api.get(`/pricing/strategy/${adId}`),
                api.get(`/ads/${adId}/price-history`)
            ]);
            setData(stratRes.data);
            setHistory(histRes.data || []);
            if (stratRes.data?.target_margin) {
                setMarginInput((stratRes.data.target_margin * 100).toFixed(1));
            }
        } catch (err) {
            console.error("Erro ao carregar estratégia de repricer:", err);
            toast.error("Erro ao carregar dados do repricer.");
        } finally {
            setLoading(false);
        }
    }, [adId]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleStartStrategy = async () => {
        const pct = parseFloat(marginInput);
        if (isNaN(pct) || pct <= 0) {
            toast.error("Informe uma margem alvo válida (%).");
            return;
        }
        setActionLoading(true);
        try {
            await api.patch(`/ads/${adId}/target-margin`, { target_margin: pct / 100 });
            toast.success("Estratégia configurada.");
            await fetchData();
        } catch (err) {
            toast.error("Erro ao configurar estratégia.");
        } finally {
            setActionLoading(false);
        }
    };

    const handlePauseResume = async () => {
        setActionLoading(true);
        try {
            await api.post(`/ads/${adId}/pause-strategy`, { paused: !data?.is_paused });
            toast.success(data?.is_paused ? "Estratégia retomada." : "Estratégia pausada.");
            await fetchData();
        } catch (err) {
            toast.error("Erro ao alterar status da estratégia.");
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-40">
                <div className="flex flex-col items-center text-slate-500 gap-3">
                    <RefreshCw className="animate-spin" size={20} />
                    <span className="text-[10px] uppercase tracking-widest font-medium">Calculando estratégia...</span>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const elasticityColor = data.elasticity.action === 'RAISE' ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/5'
        : data.elasticity.action === 'HOLD_OR_LOWER' ? 'text-red-400 border-red-500/30 bg-red-500/5'
        : 'text-amber-400 border-amber-500/30 bg-amber-500/5';

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-4 text-xs text-indigo-300 flex items-start gap-2">
                <Info size={14} className="mt-0.5 flex-shrink-0" />
                <span>
                    Modo simulação — a escrita real de preço no Mercado Livre está bloqueada por segurança até autorização expressa.
                    Os parâmetros do motor (steps, limites, reversão) ficam em <strong>Configurações &gt; Repricer</strong>.
                </span>
            </div>

            {/* Status header */}
            <div className="bg-[#13141b] rounded-xl border border-white/5 p-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${data.is_active ? (data.reversion_status.triggered ? 'bg-red-500' : 'bg-emerald-500') : 'bg-slate-600'}`} />
                    <div>
                        <div className="text-white font-semibold">
                            {data.is_active ? (data.reversion_status.triggered ? 'Pausado por segurança' : 'Estratégia ativa') : 'Sem estratégia ativa'}
                        </div>
                        <div className="text-xs text-slate-500">
                            Preço atual: {formatCurrency(data.current_price)}
                            {data.is_active && data.target_price && ` → Alvo: ${formatCurrency(data.target_price)}`}
                        </div>
                    </div>
                </div>
                {data.is_active && (
                    <button
                        onClick={handlePauseResume}
                        disabled={actionLoading}
                        className="px-4 py-2 rounded-lg text-xs font-medium flex items-center gap-2 bg-white/5 hover:bg-white/10 text-slate-300 cursor-pointer disabled:opacity-50"
                    >
                        {data.is_paused ? <PlayCircle size={14} /> : <PauseCircle size={14} />}
                        {data.is_paused ? 'Retomar' : 'Pausar'}
                    </button>
                )}
            </div>

            {/* Reversion alert */}
            {data.reversion_status.triggered && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-start gap-3">
                    <AlertTriangle className="text-red-400 mt-0.5" size={18} />
                    <div>
                        <div className="text-red-400 font-semibold text-sm">Reversão automática acionada</div>
                        <div className="text-xs text-slate-400 mt-1">{data.reversion_status.reason}</div>
                    </div>
                </div>
            )}

            {/* Start strategy form (if inactive) */}
            {!data.is_active && (
                <div className="bg-[#13141b] rounded-xl border border-white/5 p-5">
                    <div className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <Target size={14} /> Configurar Estratégia
                    </div>
                    <div className="flex items-center gap-3">
                        <input
                            type="number"
                            value={marginInput}
                            onChange={(e) => setMarginInput(e.target.value)}
                            placeholder="Margem alvo (%)"
                            className="bg-slate-800 border border-slate-600 text-white rounded px-3 py-2 w-40 focus:ring-1 focus:ring-indigo-500"
                        />
                        <button
                            onClick={handleStartStrategy}
                            disabled={actionLoading}
                            className="px-4 py-2 rounded-lg text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white cursor-pointer disabled:opacity-50"
                        >
                            Iniciar subida gradual
                        </button>
                    </div>
                </div>
            )}

            {/* Elasticity + conversion */}
            <div className="grid grid-cols-2 gap-4">
                <div className={`rounded-xl border p-4 ${elasticityColor}`}>
                    <div className="text-[10px] uppercase tracking-widest font-bold opacity-70 mb-1">Elasticidade</div>
                    <div className="text-sm font-semibold">{data.elasticity.label}</div>
                    <div className="text-xs mt-1 opacity-80">{data.elasticity.suggestion}</div>
                </div>
                <div className="rounded-xl border border-white/5 bg-[#13141b] p-4">
                    <div className="text-[10px] uppercase tracking-widest font-bold text-slate-500 mb-1">Conversão Atual</div>
                    <div className="text-sm font-semibold text-white">{data.conversion.current}% <span className="text-slate-500 font-normal">/ limite {data.conversion.threshold}%</span></div>
                    <div className="text-xs mt-1 text-slate-500">{data.conversion.method === 'historical' ? 'Calculado do histórico' : 'Benchmark Mercado Livre'}</div>
                </div>
            </div>

            {/* Steps preview */}
            {data.is_active && data.price_steps.length > 0 && (
                <div className="bg-[#13141b] rounded-xl border border-white/5 p-5">
                    <div className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <Calendar size={14} /> Próximos Steps ({data.estimated_days} dias estimados)
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-1">
                        {data.price_steps.slice(0, 10).map((step) => (
                            <div key={step.step} className="flex items-center justify-between text-xs py-1.5 px-2 rounded hover:bg-white/[0.02]">
                                <span className="text-slate-500">{step.date_display} — Step {step.step}</span>
                                <span className="text-slate-300 font-mono">{formatCurrency(step.price)}</span>
                                <span className="text-emerald-400/70">+{step.increase_pct}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* History */}
            <div className="bg-[#13141b] rounded-xl border border-white/5 p-5">
                <div className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                    <History size={14} /> Histórico de Ajustes
                </div>
                {history.length === 0 ? (
                    <div className="text-xs text-slate-500">Nenhum ajuste executado ainda.</div>
                ) : (
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                        {history.map((log) => (
                            <div key={log.id} className="flex items-center justify-between text-xs py-1.5 px-2 rounded hover:bg-white/[0.02]">
                                <span className="text-slate-500">{new Date(log.executed_at).toLocaleDateString('pt-BR')}</span>
                                <span className="text-slate-400">{formatCurrency(log.old_price)} → {formatCurrency(log.new_price)}</span>
                                <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                                    log.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' :
                                    log.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                                    'bg-slate-500/10 text-slate-400'
                                }`}>{log.status}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
