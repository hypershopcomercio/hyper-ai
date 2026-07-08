import React, { useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { 
    AlertCircle, Calculator, RefreshCw, ShieldAlert, CheckCircle2, 
    Lock, Edit3, X, Save, Clock, Info, FileText, UploadCloud, Link as LinkIcon, ChevronDown, ChevronUp 
} from "lucide-react";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

interface Props {
    adId: string;
    pricingResolution: any;
    isResolvingPricing: boolean;
    onSaved?: () => void;
}

export function FiscalParametersTab({ adId, pricingResolution, isResolvingPricing, onSaved }: Props) {
    const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);
    const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
    
    // Override form state
    const [overrideCost, setOverrideCost] = useState("");
    const [overrideNfValue, setOverrideNfValue] = useState("");
    const [overrideReason, setOverrideReason] = useState("");
    const [saving, setSaving] = useState(false);

    if (isResolvingPricing && !pricingResolution) {
        return (
            <div className="flex justify-center items-center h-40">
                <div className="flex flex-col items-center text-slate-500 gap-3">
                    <RefreshCw className="animate-spin" size={20} />
                    <span className="text-[10px] uppercase tracking-widest font-medium">Sincronizando Auditoria Fiscal...</span>
                </div>
            </div>
        );
    }

    if (!pricingResolution) return null;

    const { status, is_usable_for_automation, audit, hard_locks, data_sources, selected_cost_source, selection_status, cost_candidates, comparison } = pricingResolution;
    
    const isBlocked = !is_usable_for_automation;
    const isConflict = hard_locks?.includes("COST_SOURCE_CONFLICT");
    const isMissingData = hard_locks?.includes("MISSING_COST_DATA");

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

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

    const getRecommendation = () => {
        if (isConflict) return "Importe a NF/XML da compra ou revise o override ativo.";
        if (isMissingData) return "Nenhum custo encontrado. Importe a NF/XML ou configure no Tiny.";
        if (isBlocked) return "Resolva as pendências fiscais antes da automação atuar.";
        return "Dados completos. O robô usará essa base para precificação.";
    };

    const renderAuditRow = (label: string, key: string) => {
        const entry = audit?.[key];
        if (!entry) return null;

        return (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2 border-b border-white/[0.03] gap-2">
                <div className="flex flex-col">
                    <span className="text-xs text-slate-300">{label}</span>
                    <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[9px] text-slate-500 uppercase tracking-wider">{entry.source_type}: {entry.source}</span>
                        {entry.confidence === 'high' && <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" title="Alta Confiança" />}
                        {entry.confidence === 'medium' && <span className="w-1.5 h-1.5 rounded-full bg-amber-500" title="Média Confiança" />}
                        {entry.confidence === 'low' && <span className="w-1.5 h-1.5 rounded-full bg-rose-500" title="Baixa Confiança" />}
                    </div>
                    {entry.formula && <span className="text-[9px] text-slate-500 font-mono mt-1"><Calculator size={9} className="inline mr-1" />{entry.formula}</span>}
                </div>
                <div className="text-right">
                    <span className="text-xs font-mono text-white">
                        {typeof entry.value === 'number' ? entry.value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2, maximumFractionDigits: 4 }) : entry.value}
                    </span>
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            {/* TOPO EXECUTIVO */}
            <div className={`p-5 rounded-xl border ${isBlocked ? 'bg-rose-950/20 border-rose-500/20' : 'bg-emerald-950/20 border-emerald-500/20'} flex flex-col md:flex-row gap-5`}>
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        {isBlocked ? <ShieldAlert className="text-rose-400 w-5 h-5" /> : <CheckCircle2 className="text-emerald-400 w-5 h-5" />}
                        <h3 className={`text-base font-medium ${isBlocked ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {isBlocked ? 'Automação Bloqueada: Base Fiscal Conflitante ou Incompleta' : 'Apto para Automação'}
                        </h3>
                    </div>
                    <p className="text-sm text-slate-300 font-light">
                        {isConflict 
                            ? "Existe um override manual ativo que diverge da fonte automática atual. Como ainda não há NF/XML oficial importado para este lote, a automação fica bloqueada até importar a nota ou revisar o override."
                            : getRecommendation()
                        }
                    </p>
                    
                    {hard_locks && hard_locks.length > 0 && (
                        <div className="mt-3 flex gap-2 flex-wrap">
                            {hard_locks.map((hl: string) => (
                                <span key={hl} className="px-2 py-0.5 bg-rose-500/10 text-rose-300 text-[10px] font-medium rounded border border-rose-500/20">
                                    {hl}
                                </span>
                            ))}
                        </div>
                    )}
                </div>

                <div className="w-full md:w-64 flex flex-col gap-2">
                    <h4 className="text-[10px] uppercase tracking-wider text-slate-500 font-medium">Próxima Ação Recomendada</h4>
                    <button className="w-full px-3 py-2 bg-white/5 border border-white/10 text-slate-400 text-xs rounded-md flex items-center justify-center gap-2 opacity-60 cursor-not-allowed transition-all" title="Em breve">
                        <UploadCloud size={14} /> Importar NF/XML (Em Breve)
                    </button>
                    <button className="w-full px-3 py-2 bg-white/5 border border-white/10 text-slate-400 text-xs rounded-md flex items-center justify-center gap-2 opacity-60 cursor-not-allowed transition-all" title="Em breve">
                        <LinkIcon size={14} /> Vincular NF ao Lote (Em Breve)
                    </button>
                    <button 
                        onClick={() => {
                            setOverrideCost(audit?.product_base_cost?.value || "");
                            setOverrideNfValue(audit?.nf_value?.value || "");
                            setOverrideReason("");
                            setIsOverrideModalOpen(true);
                        }}
                        className="w-full px-3 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-300 text-xs rounded-md flex items-center justify-center gap-2 transition-all cursor-pointer"
                    >
                        <Edit3 size={14} /> Criar/Revisar Override
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* BLOCO DE FONTES DE DADOS */}
                <div className="bg-[#111218] rounded-xl border border-white/5 p-5">
                    <h4 className="text-[11px] uppercase tracking-wider text-slate-500 font-medium mb-4 flex items-center gap-2">
                        <FileText size={14} /> Fontes de Dados
                    </h4>
                    
                    <div className="space-y-3">
                        <div className="flex justify-between items-center bg-white/[0.02] p-2 rounded">
                            <span className="text-xs text-slate-400 flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${data_sources?.product_purchase_costs === 'available' ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                                Tiny / ERP
                            </span>
                            <span className="text-xs font-mono text-slate-300">{formatCurrency(cost_candidates?.tiny_ads_cost || 0)}</span>
                        </div>
                        <div className={`flex justify-between items-center p-2 rounded ${cost_candidates?.nfe_confirmed_cost ? 'bg-emerald-500/5 border border-emerald-500/10' : 'bg-white/[0.02]'}`}>
                            <span className="text-xs text-slate-400 flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${cost_candidates?.nfe_confirmed_cost ? 'bg-emerald-500' : cost_candidates?.candidate_nfe_cost ? 'bg-amber-500' : 'bg-slate-600'}`} />
                                NF / XML (SEFAZ)
                                {cost_candidates?.nfe_confirmed_nfe_number && (
                                    <span className="text-[9px] text-emerald-400/70 font-mono">#{cost_candidates.nfe_confirmed_nfe_number}</span>
                                )}
                            </span>
                            {cost_candidates?.nfe_confirmed_cost ? (
                                <span className="text-xs font-mono text-emerald-400">{formatCurrency(cost_candidates.nfe_confirmed_cost)}</span>
                            ) : cost_candidates?.candidate_nfe_cost ? (
                                <span className="text-[10px] text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">Sugerida: {formatCurrency(cost_candidates.candidate_nfe_cost)}</span>
                            ) : (
                                <span className="text-[10px] text-slate-500 bg-black/30 px-1.5 py-0.5 rounded">Pendente</span>
                            )}
                        </div>
                        <div className="flex justify-between items-center bg-indigo-500/5 border border-indigo-500/10 p-2 rounded">
                            <span className="text-xs text-indigo-300 flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${cost_candidates?.override_manual_base ? (isConflict ? 'bg-amber-500' : 'bg-indigo-500') : 'bg-slate-600'}`} />
                                Override Manual
                            </span>
                            <span className="text-xs font-mono text-indigo-300">{cost_candidates?.override_manual_base ? formatCurrency(cost_candidates.override_manual_base) : 'Inativo'}</span>
                        </div>

                        <div className="pt-2 border-t border-white/5 mt-2 flex justify-between items-center">
                            <span className="text-xs text-white font-medium">Custo Final Resolvido:</span>
                            <span className={`text-sm font-mono font-bold ${isConflict ? 'text-amber-400' : 'text-emerald-400'}`}>
                                {formatCurrency(cost_candidates?.resolved_final_cost || 0)}
                            </span>
                        </div>
                        {comparison?.ad_cost_divergence && (
                            <div className="flex justify-between items-center text-[10px]">
                                <span className="text-slate-500">Divergência Automático vs Override:</span>
                                <span className="text-amber-400 font-mono">{formatCurrency(comparison.ad_cost_divergence.diff)}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* CASCATA FISCAL COMPACTA */}
                <div className="bg-[#111218] rounded-xl border border-white/5 p-5">
                    <h4 className="text-[11px] uppercase tracking-wider text-slate-500 font-medium mb-4 flex items-center gap-2">
                        <Calculator size={14} /> Cascata Fiscal
                    </h4>
                    
                    <div className="space-y-1.5 font-mono text-xs">
                        <div className="flex justify-between text-slate-300 pb-2 border-b border-white/5">
                            <span>Custo Base (sem impostos compra)</span>
                            <span>{formatCurrency(cost_candidates?.resolved_base_cost ?? audit?.product_base_cost?.value ?? 0)}</span>
                        </div>

                        <div className="flex justify-between text-slate-400 pt-1">
                            <span>(+) IPI ({(audit?.ipi_rate?.value || 0).toFixed(1)}%)</span>
                            <span>{formatCurrency(audit?.ipi_value?.value || 0)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>(+) Subst. Tributária (ST)</span>
                            <span>{formatCurrency(audit?.st_value?.value || 0)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>(+) DIFAL (ICMS Interestadual)</span>
                            <span>{formatCurrency(audit?.difal_value?.value || 0)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>(+) Custos Extras Compra</span>
                            <span>{formatCurrency(audit?.purchase_extra_costs?.value || 0)}</span>
                        </div>
                        
                        <div className="flex justify-between items-center pt-3 border-t border-white/5 mt-1">
                            <span className="font-sans text-xs text-white font-medium">Custo Final Pós-Impostos</span>
                            <span className="text-sm text-emerald-400 font-bold">
                                {formatCurrency(audit?.final_product_cost?.value || 0)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* DETALHES TÉCNICOS (ACCORDION) */}
            <div className="bg-[#111218] rounded-xl border border-white/5 overflow-hidden">
                <button 
                    onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                    className="w-full px-4 py-3 flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition-colors cursor-pointer bg-white/[0.01] hover:bg-white/[0.03]"
                >
                    <span className="flex items-center gap-2">
                        <Info size={14} />
                        Ver fórmulas e rastreio técnico (Avançado)
                    </span>
                    {showTechnicalDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
                
                {showTechnicalDetails && (
                    <div className="p-4 border-t border-white/5 bg-black/20">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                            {renderAuditRow("Custo Base do Produto", "product_base_cost")}
                            {renderAuditRow("Valor na NF", "nf_value")}
                            {renderAuditRow("IPI (Rate)", "ipi_rate")}
                            {renderAuditRow("IPI (Valor)", "ipi_value")}
                            {renderAuditRow("ST (Valor)", "st_value")}
                            {renderAuditRow("DIFAL (Valor)", "difal_value")}
                            {renderAuditRow("Extras de Compra", "purchase_extra_costs")}
                            {renderAuditRow("DAS/Simples", "sales_tax_rate")}
                            {renderAuditRow("Custo Final", "final_product_cost")}
                        </div>
                        <div className="mt-4 pt-3 border-t border-white/5 flex gap-4">
                            <p className="text-[10px] text-slate-500">
                                <strong>Decisão do Resolver:</strong> {selection_status} ({selected_cost_source})
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* OVERRIDE MODAL */}
            {isOverrideModalOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsOverrideModalOpen(false)}></div>
                    <div className="bg-[#13141b] border border-white/10 rounded-xl p-6 w-full max-w-md relative z-10 shadow-2xl">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-base font-medium text-white flex items-center gap-2">
                                    <Edit3 className="w-4 h-4 text-indigo-400" /> Exceção Manual (Override)
                                </h3>
                                <p className="text-[11px] text-slate-400 mt-1 font-light">Force um custo base em caso de falha de integração ou acordo com fornecedor.</p>
                            </div>
                            <button onClick={() => setIsOverrideModalOpen(false)} className="text-slate-500 hover:text-white"><X size={18}/></button>
                        </div>
                        
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-[10px] uppercase text-slate-400 mb-1">Custo Base R$</label>
                                    <input 
                                        type="number" step="0.01" 
                                        value={overrideCost} onChange={e => setOverrideCost(e.target.value)} 
                                        className="w-full bg-black/30 border border-white/10 rounded-md px-3 py-2 text-sm text-white outline-none focus:border-indigo-500/50" 
                                    />
                                </div>
                                <div>
                                    <label className="block text-[10px] uppercase text-slate-400 mb-1">Valor NF R$</label>
                                    <input 
                                        type="number" step="0.01" 
                                        value={overrideNfValue} onChange={e => setOverrideNfValue(e.target.value)} 
                                        className="w-full bg-black/30 border border-white/10 rounded-md px-3 py-2 text-sm text-white outline-none focus:border-indigo-500/50" 
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-[10px] uppercase text-slate-400 mb-1">
                                    Motivo da Validação <span className="text-rose-400">*</span>
                                </label>
                                <textarea 
                                    rows={2}
                                    value={overrideReason} onChange={e => setOverrideReason(e.target.value)} 
                                    className="w-full bg-black/30 border border-white/10 rounded-md px-3 py-2 text-white text-sm outline-none focus:border-indigo-500/50"
                                    placeholder="Ex: Custo validado com fornecedor via e-mail."
                                />
                            </div>
                            
                            <div className="flex gap-2 pt-2 border-t border-white/5">
                                <button 
                                    onClick={() => {
                                        setOverrideCost("0");
                                        setOverrideNfValue("0");
                                        setOverrideReason("REMOVER_OVERRIDE_PELO_USUARIO");
                                        handleSaveOverride();
                                    }}
                                    disabled={saving}
                                    className="flex-1 bg-white/5 hover:bg-rose-500/10 hover:text-rose-400 text-slate-300 py-2 rounded-md font-medium text-xs transition-colors cursor-pointer"
                                >
                                    Remover Override
                                </button>
                                <button 
                                    onClick={handleSaveOverride}
                                    disabled={saving}
                                    className="flex-[2] bg-indigo-500 hover:bg-indigo-600 text-white py-2 rounded-md font-medium text-xs disabled:opacity-50 transition-colors flex justify-center items-center gap-2 cursor-pointer shadow-sm"
                                >
                                    {saving ? <PremiumLoader /> : <Save size={14} />} Salvar Exceção
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
