import React, { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { AlertCircle, Calculator, RefreshCw, ShieldAlert, CheckCircle2, Lock, Edit3, X, Save, Clock, Info, ArrowRight } from "lucide-react";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

interface Props {
    adId: string;
    pricingResolution: any;
    isResolvingPricing: boolean;
    onSaved?: () => void;
}

export function FiscalParametersTab({ adId, pricingResolution, isResolvingPricing, onSaved }: Props) {
    const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);
    
    // Override form state
    const [overrideCost, setOverrideCost] = useState("");
    const [overrideNfValue, setOverrideNfValue] = useState("");
    const [overrideReason, setOverrideReason] = useState("");
    const [saving, setSaving] = useState(false);

    if (isResolvingPricing && !pricingResolution) {
        return (
            <div className="flex justify-center items-center h-40">
                <div className="flex flex-col items-center text-slate-500 gap-3">
                    <RefreshCw className="animate-spin" size={24} />
                    <span className="text-xs uppercase font-bold tracking-widest">Sincronizando Auditoria Fiscal...</span>
                </div>
            </div>
        );
    }

    if (!pricingResolution) return null;

    const { status, is_usable_for_automation, audit, missing_fields, hard_locks, data_sources, confidence_summary, selected_cost_source, selection_status, cost_candidates, comparison } = pricingResolution;
    
    const isBlocked = !is_usable_for_automation;
    const isConflict = hard_locks?.includes("COST_SOURCE_CONFLICT");

    const handleSaveOverride = async () => {
        if (!overrideReason || overrideReason.length < 5) {
            toast.error("Motivo do override é obrigatório e deve ser claro.");
            return;
        }

        const isTest = overrideReason.toLowerCase().includes("teste") || overrideReason.toLowerCase().includes("correção") || overrideReason.toLowerCase().includes("temporário");

        setSaving(true);
        try {
            const payload = {
                purchase_cost: {
                    real_cost: overrideCost ? Number(overrideCost) : 0,
                    nf_value: overrideNfValue ? Number(overrideNfValue) : 0,
                    data_source: "manual",
                    notes: overrideReason,
                    is_active: true
                }
            };
            await api.put(`/ads/${adId}/fiscal-profile`, payload);
            toast.success("Exceção registrada com sucesso!");
            if (isTest) {
                toast.warning("Como o motivo indica 'teste' ou 'correção', a automação permanecerá bloqueada por segurança.");
            }
            setIsOverrideModalOpen(false);
            if (onSaved) onSaved();
        } catch (err) {
            console.error(err);
            toast.error("Erro ao salvar exceção fiscal.");
        } finally {
            setSaving(false);
        }
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const renderConfidenceBadge = (conf: string) => {
        if (conf === 'high') return <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Alta Confiança</span>;
        if (conf === 'medium') return <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30">Média Confiança</span>;
        return <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">Baixa Confiança</span>;
    };

    const renderAuditRow = (label: string, key: string) => {
        const entry = audit?.[key];
        if (!entry) return null;

        return (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3 border-b border-white/5 hover:bg-white/[0.02] transition-colors gap-3">
                <div className="flex flex-col gap-1">
                    <span className="text-xs font-bold text-slate-300">{label}</span>
                    <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase ${entry.source_type === 'override' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' : entry.source_type === 'automatic' ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                            {entry.source_type}: {entry.source}
                        </span>
                        {renderConfidenceBadge(entry.confidence)}
                    </div>
                    {entry.formula && <span className="text-[10px] text-slate-500 font-mono mt-1 flex items-center gap-1"><Calculator size={10} /> {entry.formula}</span>}
                    {entry.warnings && entry.warnings.map((w: string, i: number) => (
                        <span key={i} className="text-[9px] text-amber-400 flex items-center gap-1 mt-0.5"><AlertCircle size={9}/> {w}</span>
                    ))}
                </div>
                <div className="flex flex-col sm:items-end">
                    <span className="text-sm font-mono font-bold text-white">
                        {typeof entry.value === 'number' ? entry.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2, maximumFractionDigits: 4 }) : entry.value}
                    </span>
                    {entry.updated_at && (
                        <span className="text-[9px] text-slate-500 flex items-center gap-1 mt-1">
                            <Clock size={9} /> {new Date(entry.updated_at).toLocaleString('pt-BR')}
                        </span>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <ShieldAlert className="w-5 h-5 text-indigo-400" />
                        Auditoria Fiscal (Read-Only)
                        {isResolvingPricing && <RefreshCw size={14} className="animate-spin text-slate-500 ml-2" />}
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Esta tela não é um formulário de preenchimento. O sistema utiliza os dados oficiais do Tiny ERP por padrão. Use as opções de exceção apenas em casos de bloqueio ou correção necessária.
                    </p>
                </div>
            </div>

            {/* STATUS ROW */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#13141b] rounded-xl border border-white/5 p-4 flex flex-col justify-center">
                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Status de Automação</span>
                    <div className="flex items-center gap-2">
                        {isBlocked ? <Lock size={16} className="text-rose-400" /> : <CheckCircle2 size={16} className="text-emerald-400" />}
                        <span className={`text-sm font-bold uppercase ${isBlocked ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {status === 'needs_review' ? 'Revisão Pendente' : isBlocked ? 'Bloqueado' : 'Aprovado'}
                        </span>
                    </div>
                </div>

                <div className="bg-[#13141b] rounded-xl border border-white/5 p-4 flex flex-col justify-center">
                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Decisão de Custo Base</span>
                    <span className={`text-sm font-bold uppercase ${selection_status === 'conflict_detected' ? 'text-rose-400' : 'text-indigo-400'}`}>
                        {selection_status.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] text-slate-500 mt-1 font-mono">{selected_cost_source}</span>
                </div>

                <div className="bg-[#13141b] rounded-xl border border-white/5 p-4 col-span-1 md:col-span-2 flex flex-col justify-center">
                    <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Fontes Identificadas</span>
                    <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                            <span className="text-xs text-slate-400">Tiny / Automático:</span>
                            <span className="font-mono text-slate-200">{formatCurrency(cost_candidates?.tiny_ads_cost || 0)}</span>
                        </div>
                        <ArrowRight size={14} className="text-slate-600 mx-2" />
                        <div className="flex flex-col">
                            <span className="text-xs text-slate-400">Override Manual:</span>
                            <span className="font-mono text-indigo-400">{cost_candidates?.override_manual_base ? formatCurrency(cost_candidates.override_manual_base) : 'Nenhum'}</span>
                        </div>
                        <ArrowRight size={14} className="text-slate-600 mx-2" />
                        <div className="flex flex-col">
                            <span className="text-xs font-bold text-white">Custo Resolvido:</span>
                            <span className={`font-mono font-bold ${isConflict ? 'text-rose-400' : 'text-emerald-400'}`}>{formatCurrency(cost_candidates?.resolved_final_cost || 0)}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* ACTIONS PANEL */}
            <div className="bg-indigo-950/20 border border-indigo-500/20 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                    <h4 className="text-sm font-bold text-indigo-300">Gestão de Exceções</h4>
                    <p className="text-xs text-indigo-200/70 mt-1">
                        Use overrides manuais apenas para corrigir falhas de integração ou acordos pontuais com fornecedores.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => {
                            setOverrideCost(audit?.product_base_cost?.value || "");
                            setOverrideNfValue(audit?.nf_value?.value || "");
                            setOverrideReason("");
                            setIsOverrideModalOpen(true);
                        }}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold uppercase rounded-md transition-colors flex items-center gap-2 shadow-sm"
                    >
                        <Edit3 className="w-4 h-4" />
                        Criar / Revisar Override Manual
                    </button>
                </div>
            </div>

            {/* AUDIT LIST */}
            <div className="bg-[#13141b] border border-white/5 rounded-xl overflow-hidden mt-6">
                <div className="px-4 py-3 bg-white/[0.02] border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <AlertCircle size={14} className="text-slate-400" />
                        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-widest">Rastreio de Variáveis Fiscais e Custos</h4>
                    </div>
                    {audit?.product_base_cost?.updated_at && (
                        <span className="text-[10px] text-slate-500">Última atualização: {new Date(audit.product_base_cost.updated_at).toLocaleString()}</span>
                    )}
                </div>
                <div className="flex flex-col">
                    {renderAuditRow("Custo Base do Produto", "product_base_cost")}
                    {renderAuditRow("Valor na Nota Fiscal (NF)", "nf_value")}
                    {renderAuditRow("Alíquota IPI", "ipi_rate")}
                    {renderAuditRow("Valor IPI", "ipi_value")}
                    {renderAuditRow("Substituição Tributária (ST)", "st_value")}
                    {renderAuditRow("Custos Extras de Compra", "purchase_extra_costs")}
                    {renderAuditRow("Alíquota DAS (Simples)", "sales_tax_rate")}
                    {renderAuditRow("Custo Fiscal e Reposição Total Resolvido", "final_product_cost")}
                </div>
            </div>

            {/* OVERRIDE MODAL */}
            {isOverrideModalOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsOverrideModalOpen(false)}></div>
                    <div className="bg-[#0f111a] border border-indigo-500/30 rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                    <Edit3 className="w-5 h-5 text-indigo-400" /> Registrar Exceção Manual
                                </h3>
                                <p className="text-xs text-slate-400 mt-1">Forçar um custo base ou NF manual para este anúncio em caso de exceção.</p>
                            </div>
                            <button onClick={() => setIsOverrideModalOpen(false)} className="text-slate-500 hover:text-white"><X size={20}/></button>
                        </div>
                        
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-slate-300 mb-1">Custo Base Override R$</label>
                                <input 
                                    type="number" step="0.01" 
                                    value={overrideCost} onChange={e => setOverrideCost(e.target.value)} 
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-indigo-500" 
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-300 mb-1">Valor na NF Override R$</label>
                                <input 
                                    type="number" step="0.01" 
                                    value={overrideNfValue} onChange={e => setOverrideNfValue(e.target.value)} 
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-indigo-500" 
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-300 mb-1">
                                    Motivo da Exceção / Validação <span className="text-rose-400">*</span>
                                </label>
                                <textarea 
                                    rows={3}
                                    value={overrideReason} onChange={e => setOverrideReason(e.target.value)} 
                                    className="w-full bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-white text-sm outline-none focus:border-indigo-500"
                                    placeholder="Ex: Custo do Tiny está incorreto. Custo acordado com o fornecedor validado."
                                />
                                <div className="flex items-start gap-1 mt-1">
                                    <Info size={12} className="text-amber-400 mt-0.5 shrink-0" />
                                    <p className="text-[10px] text-amber-400/80 leading-tight">
                                        Palavras como "teste", "temporário" ou "correção" manterão a automação bloqueada (COST_SOURCE_CONFLICT). Forneça um motivo validado para liberar o robô.
                                    </p>
                                </div>
                            </div>
                            
                            <div className="flex gap-2 mt-4">
                                <button 
                                    onClick={() => {
                                        setOverrideCost("0");
                                        setOverrideNfValue("0");
                                        setOverrideReason("REMOVER_OVERRIDE");
                                        handleSaveOverride();
                                    }}
                                    disabled={saving}
                                    className="flex-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 py-2 rounded-lg font-bold uppercase text-xs tracking-wider transition-colors"
                                >
                                    Remover Override
                                </button>
                                <button 
                                    onClick={handleSaveOverride}
                                    disabled={saving}
                                    className="flex-[2] bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded-lg font-bold uppercase text-xs tracking-wider disabled:opacity-50 transition-colors flex justify-center items-center gap-2"
                                >
                                    {saving ? <PremiumLoader /> : <Save size={14} />} Salvar / Validar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
