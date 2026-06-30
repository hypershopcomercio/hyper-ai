import React, { useState, useEffect, useCallback, useMemo } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
    TrendingUp, PauseCircle, PlayCircle, RefreshCw, AlertTriangle, Info,
    Zap, History, Target
} from "lucide-react";
import { Tooltip } from "@/components/ui/Tooltip";
import { Ad } from "@/types";

interface Props {
    ad: Ad;
    requestConfirm: (cfg: { title: string; message: string; type: 'danger' | 'warning' | 'info'; onConfirm: () => void }) => void;
    onAdUpdate: (patch: Partial<Ad>) => void;
}

interface StrategyData {
    is_active: boolean;
    is_paused: boolean;
    current_price: number;
    target_price: number | null;
    target_margin: number | null;
    current_step_number: number;
    conversion: { current: number; threshold: number; method: string; break_even_at_target: number };
    reversion_status: { triggered: boolean; reason: string };
    elasticity: { score: number | null; label: string; suggestion: string; action?: string };
    price_steps: Array<{ step: number; date_display: string; price: number; increase_pct: number }>;
    step_mode: 'fixed' | 'percent';
    step_value: number;
    is_low_ticket: boolean;
    estimated_days: number;
}

interface RepricerConfig {
    low_ticket_threshold: number;
    low_ticket_step_value: number;
    step_pct_elastic: number;
    step_pct_unitary: number;
    step_pct_inelastic: number;
    max_step_percent: number;
}

interface PriceLog {
    id: number;
    old_price: number;
    new_price: number;
    executed_at: string;
    status: string;
}

const formatCurrency = (v: number | null | undefined) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0);

// Mirrors the backend's PricingEngine.calculate_safe_price_steps — used ONLY for
// instant client-side preview while the user drags the slider. The authoritative
// plan always comes from the server (price_steps in StrategyData).
function computeLocalPlan(currentPrice: number, targetPrice: number, elasticityScore: number | null, config: RepricerConfig) {
    if (targetPrice <= currentPrice || !config) return [];
    const isLowTicket = currentPrice < config.low_ticket_threshold;
    let stepMode: 'fixed' | 'percent' = 'fixed';
    let stepValue = config.low_ticket_step_value;

    if (!isLowTicket) {
        stepMode = 'percent';
        if (elasticityScore === null) stepValue = config.step_pct_unitary;
        else if (elasticityScore > 1.5) stepValue = config.step_pct_elastic;
        else if (elasticityScore < 0.8) stepValue = config.step_pct_inelastic;
        else stepValue = config.step_pct_unitary;
        stepValue = Math.min(stepValue, config.max_step_percent);
    }

    const steps: Array<{ step: number; date_display: string; price: number; increase_pct: number }> = [];
    let price = currentPrice;
    let stepNum = 0;
    const baseDate = new Date();
    while (price < targetPrice && stepNum < 200) {
        stepNum++;
        let newPrice = stepMode === 'fixed' ? price + stepValue : price * (1 + stepValue / 100);
        if (newPrice >= targetPrice - 0.005) newPrice = targetPrice;
        const d = new Date(baseDate);
        d.setDate(baseDate.getDate() + stepNum);
        steps.push({
            step: stepNum,
            date_display: d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
            price: Math.round(newPrice * 100) / 100,
            increase_pct: Math.round(((newPrice - currentPrice) / currentPrice) * 1000) / 10
        });
        price = newPrice;
        if (price >= targetPrice) break;
    }
    return steps;
}

export function RepricerStrategyPanel({ ad, requestConfirm, onAdUpdate }: Props) {
    const [data, setData] = useState<StrategyData | null>(null);
    const [config, setConfig] = useState<RepricerConfig | null>(null);
    const [history, setHistory] = useState<PriceLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);
    const [sliderIdx, setSliderIdx] = useState(0);

    const fetchAll = useCallback(async () => {
        try {
            const [stratRes, cfgRes, histRes] = await Promise.all([
                api.get(`/pricing/strategy/${ad.id}`),
                api.get(`/settings/repricer`),
                api.get(`/ads/${ad.id}/price-history`)
            ]);
            setData(stratRes.data);
            setConfig(cfgRes.data.data);
            setHistory(histRes.data || []);
        } catch (err) {
            console.error("Erro ao carregar repricer:", err);
        } finally {
            setLoading(false);
        }
    }, [ad.id]);

    useEffect(() => { fetchAll(); }, [fetchAll]);

    const effectivePrice = (ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price) ? ad.promotion_price : ad.price;

    // Discrete psychological-price candidates in a [-3%, +25%] band around current price
    const candidates = useMemo(() => {
        const minPrice = effectivePrice * 0.97;
        const maxPrice = effectivePrice * 1.25;
        const list: number[] = [parseFloat(effectivePrice.toFixed(2))];
        const lowInt = Math.floor(minPrice);
        const highInt = Math.ceil(maxPrice);
        for (let i = lowInt; i <= highInt; i++) {
            for (const end of [0.40, 0.74, 0.90]) {
                const p = i + end;
                if (p >= minPrice && p <= maxPrice && Math.abs(p - effectivePrice) > 0.005) list.push(p);
            }
        }
        return list.sort((a, b) => a - b);
    }, [effectivePrice]);

    const targetPrice = candidates[sliderIdx] ?? effectivePrice;

    const localPlan = useMemo(() => {
        if (!config || !data) return [];
        return computeLocalPlan(effectivePrice, targetPrice, data.elasticity.score, config);
    }, [config, data, effectivePrice, targetPrice]);

    const isActive = !!data?.is_active;
    const displaySteps = isActive ? (data?.price_steps || []) : localPlan;
    const currentStepIdx = ad.current_step_number || 0;
    const progress = isActive && displaySteps.length > 0 ? Math.min((currentStepIdx / displaySteps.length) * 100, 100) : 0;

    const handleActivate = () => {
        if (localPlan.length === 0) {
            toast.error("Arraste o controle para definir uma meta acima do preço atual.");
            return;
        }
        const finalTarget = localPlan[localPlan.length - 1].price;
        const reqMarginDec = 1 - ((effectivePrice * (1 - ((ad.financials as any)?.net_margin_percent || ad.margin_percent || 0) / 100)) / finalTarget);
        requestConfirm({
            title: 'Ativar Estratégia',
            message: `Deseja ativar a subida gradual até ${formatCurrency(finalTarget)} (~${displaySteps.length} dias)? Modo simulação — nenhum preço real será alterado até autorização expressa.`,
            type: 'info',
            onConfirm: async () => {
                setBusy(true);
                try {
                    await api.patch(`/ads/${ad.id}/target-margin`, { target_margin: reqMarginDec, suggested_price: finalTarget });
                    onAdUpdate({ target_margin: reqMarginDec, suggested_price: finalTarget, strategy_start_price: ad.price, current_step_number: 0 });
                    toast.success("Estratégia ativada (simulação).");
                    await fetchAll();
                } catch {
                    toast.error("Erro ao ativar estratégia.");
                } finally {
                    setBusy(false);
                }
            }
        });
    };

    const handlePauseResume = async () => {
        setBusy(true);
        try {
            await api.post(`/ads/${ad.id}/pause-strategy`, { paused: !data?.is_paused });
            toast.success(data?.is_paused ? "Estratégia retomada." : "Estratégia pausada.");
            await fetchAll();
        } catch {
            toast.error("Erro ao alterar estratégia.");
        } finally {
            setBusy(false);
        }
    };

    const handleReset = () => {
        requestConfirm({
            title: 'Gerar Nova Estratégia',
            message: 'A estratégia atual será encerrada. Deseja continuar?',
            type: 'warning',
            onConfirm: async () => {
                setBusy(true);
                try {
                    await api.patch(`/ads/${ad.id}/target-margin`, { target_margin: 0, suggested_price: null, force_update: true });
                    onAdUpdate({ target_margin: 0, suggested_price: undefined, strategy_start_price: 0, current_step_number: 0 });
                    toast.success("Estratégia resetada.");
                    await fetchAll();
                } catch {
                    toast.error("Erro ao resetar estratégia.");
                } finally {
                    setBusy(false);
                }
            }
        });
    };

    const handleSendNow = (stepPrice: number) => {
        requestConfirm({
            title: 'Enviar Preço Agora',
            message: `Enviar ${formatCurrency(stepPrice)} para o Mercado Livre agora, furando a fila do próximo ciclo automático?`,
            type: 'info',
            onConfirm: async () => {
                setBusy(true);
                try {
                    const res = await api.post(`/ads/${ad.id}/execute-price-step`, { target_price: stepPrice });
                    if (res.data.success) {
                        onAdUpdate({ price: res.data.new_price, current_step_number: (ad.current_step_number || 0) + 1 });
                        toast.success("Comando enviado ao Mercado Livre.");
                    } else if (res.data.status === 'locked') {
                        toast.info("Bloqueado: escrita real no ML está desativada (modo simulação).");
                    } else {
                        toast.error(res.data.message || "Falha ao enviar.");
                    }
                    await fetchAll();
                } catch {
                    toast.error("Erro ao enviar comando.");
                } finally {
                    setBusy(false);
                }
            }
        });
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-32 text-slate-500 gap-2">
                <RefreshCw className="animate-spin" size={16} />
                <span className="text-[10px] uppercase tracking-widest">Calculando estratégia...</span>
            </div>
        );
    }
    if (!data || !config) return null;

    const elasticityColor = data.elasticity.action === 'RAISE' ? 'text-emerald-400'
        : data.elasticity.action === 'HOLD_OR_LOWER' ? 'text-red-400' : 'text-amber-400';

    return (
        <div className="bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-slate-900/50 rounded-xl border border-white/5 p-6 relative overflow-hidden">
            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 bg-indigo-500/20 rounded-xl border border-indigo-500/30">
                            <TrendingUp size={20} className="text-indigo-400" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h3 className="text-sm font-bold text-white">Estratégia de Precificação</h3>
                                <Tooltip
                                    title="Piloto Automático"
                                    content={
                                        <div className="space-y-2 w-60 text-xs">
                                            <p>Roda diariamente às <strong>04:00</strong>. Ticket baixo sobe R$ fixo/dia; ticket alto sobe % conforme a elasticidade do produto.</p>
                                            <p className="text-rose-300">Se a conversão cair, a estratégia pausa sozinha.</p>
                                        </div>
                                    }
                                >
                                    <Info size={14} className="text-slate-500 hover:text-indigo-400 cursor-help" />
                                </Tooltip>
                            </div>
                            <p className="text-[10px] text-slate-400">
                                {isActive ? (data.reversion_status.triggered ? 'Pausado por segurança' : 'Piloto automático ativo') : 'Defina uma meta para ativar'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        {isActive ? (
                            <>
                                <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase border ${data.reversion_status.triggered ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'}`}>
                                    <span className={`w-2 h-2 rounded-full ${data.reversion_status.triggered ? 'bg-red-400' : 'bg-emerald-400 animate-pulse'}`} />
                                    {data.reversion_status.triggered ? 'Pausado' : 'Ativo'}
                                </span>
                                <button onClick={handlePauseResume} disabled={busy} className="p-1.5 rounded-lg bg-slate-700/50 hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition-all cursor-pointer disabled:opacity-50">
                                    {data.is_paused ? <PlayCircle size={14} /> : <PauseCircle size={14} />}
                                </button>
                            </>
                        ) : (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 text-slate-500 rounded-full text-[10px] font-bold uppercase border border-slate-700/50">
                                <span className="w-2 h-2 bg-slate-600 rounded-full" /> Inativo
                            </span>
                        )}
                    </div>
                </div>

                {data.reversion_status.triggered && (
                    <div className="mb-5 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-2">
                        <AlertTriangle className="text-red-400 mt-0.5" size={14} />
                        <span className="text-xs text-red-300">{data.reversion_status.reason}</span>
                    </div>
                )}

                {/* Timeline */}
                {displaySteps.length > 0 && (
                    <div className="relative w-full pb-6 px-4 pt-8 mb-6 bg-[#0c0d12] rounded-xl border border-white/5 overflow-x-auto">
                        <div className="flex items-center justify-between mb-3 px-1">
                            <span className="text-[10px] text-slate-500">Timeline ({displaySteps.length} etapas, ~{displaySteps.length} dias)</span>
                            {isActive && <span className="text-[10px] font-mono text-indigo-400">{Math.round(progress)}%</span>}
                        </div>
                        <div className="relative min-w-[480px]">
                            <div className="absolute top-[13px] left-0 w-full h-[4px] bg-[#1a1c23] rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-cyan-500 via-indigo-600 to-emerald-500 rounded-full transition-all duration-700" style={{ width: `${progress}%` }} />
                            </div>
                            <div className="relative z-10 flex justify-between w-full">
                                {displaySteps.slice(0, 12).map((step, idx) => {
                                    const isDone = isActive && idx < currentStepIdx;
                                    const isCurrent = isActive && idx === currentStepIdx;
                                    return (
                                        <div key={step.step} className="flex flex-col items-center group relative">
                                            <span className="absolute -top-5 text-[8px] font-mono text-slate-600">{step.date_display}</span>
                                            <div className={`w-3 h-3 rounded-full border-2 ${isDone ? 'bg-emerald-500 border-emerald-500' : isCurrent ? 'bg-indigo-500 border-indigo-300 scale-125' : 'bg-[#1a1c23] border-slate-700'}`} />
                                            <span className="mt-1 text-[9px] font-mono text-slate-400">{formatCurrency(step.price)}</span>
                                            {isActive && idx === currentStepIdx && (
                                                <button
                                                    onClick={() => handleSendNow(step.price)}
                                                    disabled={busy}
                                                    className="mt-1 px-2 py-0.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full text-[8px] font-bold uppercase cursor-pointer disabled:opacity-50"
                                                >
                                                    Enviar agora
                                                </button>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                )}

                {/* Elasticity + conversion */}
                <div className="grid grid-cols-3 gap-3 mb-5">
                    <div className="bg-[#13141b] rounded-lg p-3 border border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase mb-1">Elasticidade</p>
                        <p className={`text-sm font-bold ${elasticityColor}`}>{data.elasticity.label}</p>
                    </div>
                    <div className="bg-[#13141b] rounded-lg p-3 border border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase mb-1">Conversão Atual</p>
                        <p className="text-sm font-bold text-white">{data.conversion.current}%</p>
                    </div>
                    <div className="bg-[#13141b] rounded-lg p-3 border border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase mb-1">Ritmo do Step</p>
                        <p className="text-sm font-bold text-indigo-400">
                            {isActive
                                ? (data.step_mode === 'fixed' ? `+${formatCurrency(data.step_value)}/dia` : `+${data.step_value}%/dia`)
                                : (localPlan.length > 0 ? (config && effectivePrice < config.low_ticket_threshold ? `+${formatCurrency(config.low_ticket_step_value)}/dia` : 'variável %/dia') : '—')
                            }
                        </p>
                    </div>
                </div>

                {/* Slider (only when not active) */}
                {!isActive && (
                    <div className="bg-black/40 rounded-xl p-5 border border-white/5">
                        <div className="flex items-center justify-between mb-2">
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-wide flex items-center gap-2">
                                <Target size={12} /> Meta de Preço
                            </label>
                            <span className="text-xl font-bold font-mono text-emerald-400">{formatCurrency(targetPrice)}</span>
                        </div>

                        <div className="relative mb-4 group h-10 flex items-center">
                            <div className="absolute inset-x-0 h-2 bg-slate-700/50 rounded-full top-1/2 -translate-y-1/2 overflow-hidden">
                                <div className="h-full opacity-70" style={{ background: 'linear-gradient(to right, #6366f1 0%, #10b981 100%)', width: '100%' }} />
                            </div>
                            <input
                                type="range"
                                min={0}
                                max={candidates.length - 1}
                                step={1}
                                value={sliderIdx}
                                onChange={(e) => setSliderIdx(parseInt(e.target.value))}
                                className="absolute inset-x-0 w-full h-full opacity-0 cursor-pointer z-50"
                            />
                            <div
                                className="absolute w-4 h-4 bg-white border-2 border-indigo-500 rounded-full shadow-lg pointer-events-none z-10 transition-all"
                                style={{ left: `${(sliderIdx / Math.max(candidates.length - 1, 1)) * 100}%`, transform: 'translateX(-50%)' }}
                            />
                        </div>

                        <div className="flex justify-between text-[10px] text-slate-500 font-mono mb-5">
                            <span>{formatCurrency(effectivePrice)} (atual)</span>
                            <span>{targetPrice > effectivePrice ? `+${(((targetPrice / effectivePrice) - 1) * 100).toFixed(1)}%` : 'sem alteração'}</span>
                        </div>

                        <button
                            onClick={handleActivate}
                            disabled={busy || localPlan.length === 0}
                            className="w-full px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold text-xs shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer uppercase tracking-wider disabled:opacity-50"
                        >
                            <Zap size={16} /> Ativar Subida Gradual
                        </button>
                    </div>
                )}

                {isActive && (
                    <button
                        onClick={handleReset}
                        disabled={busy}
                        className="px-6 py-2 bg-[#13141b] border border-indigo-500/30 hover:border-indigo-500 hover:bg-indigo-500/10 text-indigo-400 hover:text-white rounded-lg font-bold text-xs transition-all flex items-center gap-2 cursor-pointer uppercase tracking-wider disabled:opacity-50"
                    >
                        <RefreshCw size={14} /> Gerar Nova Estratégia
                    </button>
                )}

                {/* History */}
                {history.length > 0 && (
                    <div className="mt-5 pt-5 border-t border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase mb-2 flex items-center gap-2"><History size={12} /> Histórico</p>
                        <div className="space-y-1 max-h-32 overflow-y-auto">
                            {history.slice(0, 8).map((log) => (
                                <div key={log.id} className="flex items-center justify-between text-[10px] py-1 text-slate-500">
                                    <span>{new Date(log.executed_at).toLocaleDateString('pt-BR')}</span>
                                    <span>{formatCurrency(log.old_price)} → {formatCurrency(log.new_price)}</span>
                                    <span className={log.status === 'success' ? 'text-emerald-400' : log.status === 'failed' ? 'text-red-400' : 'text-slate-400'}>{log.status}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
