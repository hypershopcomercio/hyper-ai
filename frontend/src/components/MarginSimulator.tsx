import React from 'react';
import { Calculator, ShieldAlert, CheckCircle2, Info, AlertTriangle, ArrowRight } from 'lucide-react';
import { Ad } from '@/types';

interface MarginSimulatorProps {
    ad: Ad;
    simulatedPrice: number;
    pricingResolution: any;
}

export function MarginSimulator({ ad, simulatedPrice, pricingResolution }: MarginSimulatorProps) {
    if (!ad) return null;

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    if (!pricingResolution) {
        return (
            <div className="bg-[#13141b] rounded-lg border border-white/5 p-4 mt-4 animate-pulse">
                <div className="h-4 bg-white/10 rounded w-1/4 mb-4"></div>
                <div className="h-20 bg-white/5 rounded"></div>
            </div>
        );
    }

    const { is_usable_for_automation, calculator_inputs, comparison, cost_candidates, hard_locks, warnings } = pricingResolution;

    const targetPrice = simulatedPrice > 0 ? simulatedPrice : ad.price;

    const mkp_rate = calculator_inputs?.marketplace_costs?.commission_rate || 0;
    const mkp_shipping = calculator_inputs?.marketplace_costs?.shipping_cost || 0;
    const das_rate = calculator_inputs?.sales_tax_rate || 0;
    const final_product_cost = calculator_inputs?.final_product_cost || 0;

    const mkp_commission = targetPrice * mkp_rate;
    const das_value = targetPrice * (das_rate / 100);
    
    // Custos operacionais vêm de ad.financials (payload de detalhe), não da raiz
    // (que só existe na listagem) — senão a simulação subconta custo e infla o lucro.
    const fin = ad.financials;
    const riskLongTerm = fin?.storage_risk_cost ?? ad.storage_risk_cost ?? 0;
    const riskDevolution = fin?.return_risk_cost ?? ad.return_risk_cost ?? 0;
    const fixedCostShare = fin?.fixed_cost_share ?? ad.fixed_cost_share ?? 0;
    const storageCostTotal = fin?.storage_cost ?? ad.storage_cost ?? 0;
    
    const extra_costs = riskLongTerm + riskDevolution + fixedCostShare + storageCostTotal;
    const total_cost = final_product_cost + mkp_commission + mkp_shipping + das_value + extra_costs;
    const profit = targetPrice - total_cost;
    const margin = targetPrice > 0 ? profit / targetPrice : 0;

    const isBlocked = !is_usable_for_automation;
    const isConflict = hard_locks?.includes("COST_SOURCE_CONFLICT");
    const isMissingData = hard_locks?.includes("MISSING_COST_DATA");

    return (
        <div className="space-y-6">
            {/* Status Panel */}
            <div className={`p-5 rounded-xl border ${isBlocked ? 'bg-rose-950/20 border-rose-500/20' : 'bg-emerald-950/20 border-emerald-500/20'} flex flex-col gap-3`}>
                <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                        {isBlocked ? <ShieldAlert className="text-rose-400 w-5 h-5" /> : <CheckCircle2 className="text-emerald-400 w-5 h-5" />}
                    </div>
                    <div className="flex-1">
                        <h3 className={`text-base font-medium ${isBlocked ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {isBlocked ? 'Automação Bloqueada' : 'Apto para Automação'}
                            {isConflict && <span className="ml-2 font-normal text-rose-300">— Base fiscal conflitante</span>}
                            {isMissingData && <span className="ml-2 font-normal text-rose-300">— Dados de custo ausentes</span>}
                        </h3>
                        
                        <p className="text-sm text-slate-300 font-light mt-1">
                            {isBlocked 
                                ? 'Importe a NF/XML ou revise o override antes de ativar estratégias automáticas para este produto.' 
                                : 'Os parâmetros fiscais e de custo foram validados com sucesso pela auditoria sistêmica e o robô está liberado para operar.'}
                        </p>
                        
                        {hard_locks && hard_locks.length > 0 && (
                            <div className="mt-3 flex gap-2 flex-wrap">
                                {hard_locks.map((hl: string) => (
                                    <span key={hl} className="px-2 py-0.5 bg-rose-500/10 text-rose-300 text-[10px] font-medium rounded border border-rose-500/20">
                                        BLOQUEIO: {hl}
                                    </span>
                                ))}
                            </div>
                        )}
                        {warnings && warnings.length > 0 && (
                            <div className="mt-2 space-y-1">
                                {warnings.map((w: string, idx: number) => (
                                    <p key={idx} className="text-[11px] text-amber-400 flex items-center gap-1.5 font-light">
                                        <AlertTriangle size={10} /> {w}
                                    </p>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Cost Comparison Panel */}
                <div className="bg-[#111218] rounded-xl border border-white/5 p-5">
                    <h4 className="text-[11px] uppercase tracking-wider text-slate-500 font-medium mb-4 flex items-center gap-2">
                        <Info size={14} className="text-indigo-400" /> Diagnóstico de Custos
                    </h4>
                    
                    <div className="space-y-4">
                        <div className="flex items-center justify-between text-xs text-slate-400 px-2">
                            <span>Tiny / Ads</span>
                            <span>Override</span>
                            <span>Resolvido</span>
                        </div>
                        <div className="flex items-center justify-between bg-white/[0.02] p-3 rounded-lg border border-white/[0.05]">
                            <span className="font-mono text-slate-300">{formatCurrency(cost_candidates?.tiny_ads_cost || 0)}</span>
                            <ArrowRight size={14} className="text-slate-600" />
                            <span className="font-mono text-indigo-400">{cost_candidates?.override_manual_base ? formatCurrency(cost_candidates.override_manual_base) : '---'}</span>
                            <ArrowRight size={14} className="text-slate-600" />
                            <span className={`font-mono font-bold ${isConflict ? 'text-amber-400' : 'text-emerald-400'}`}>{formatCurrency(cost_candidates?.resolved_final_cost || 0)}</span>
                        </div>
                        
                        {comparison?.ad_cost_divergence && (
                            <div className={`mt-2 p-3 rounded-lg border flex justify-between items-center ${isConflict ? 'bg-amber-500/5 border-amber-500/10' : 'bg-black/30 border-white/5'}`}>
                                <span className={`text-[11px] font-medium ${isConflict ? 'text-amber-400/80' : 'text-slate-500'}`}>
                                    Divergência
                                </span>
                                <span className={`text-sm font-mono font-bold ${isConflict ? 'text-amber-400' : 'text-emerald-400'}`}>
                                    {formatCurrency(comparison.ad_cost_divergence.diff)} 
                                    <span className="text-[10px] ml-1 opacity-70 font-sans">({comparison.ad_cost_divergence.diff_percent.toFixed(1)}%)</span>
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Calculation Cascade */}
                <div className="bg-[#111218] rounded-xl border border-white/5 p-5">
                    <h4 className="text-[11px] uppercase tracking-wider text-slate-500 font-medium mb-4 flex items-center gap-2">
                        <Calculator size={14} className="text-emerald-400" /> Cascata de Cálculo Real
                    </h4>
                    
                    <div className="space-y-1.5 font-mono text-xs">
                        <div className="flex justify-between text-emerald-400/80 font-medium mb-3 pb-3 border-b border-white/5">
                            <span className="font-sans">Preço de Venda Analisado</span>
                            <span>{formatCurrency(targetPrice)}</span>
                        </div>
                        
                        <div className="flex justify-between text-slate-400">
                            <span className="font-sans">(-) Comissão ML ({(mkp_rate * 100).toFixed(1)}%)</span>
                            <span className="text-rose-400/80">-{formatCurrency(mkp_commission)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span className="font-sans">(-) Frete ML</span>
                            <span className="text-rose-400/80">-{formatCurrency(mkp_shipping)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span className="font-sans">(-) Imposto DAS ({das_rate.toFixed(2)}%)</span>
                            <span className="text-rose-400/80">-{formatCurrency(das_value)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span className="font-sans">(-) Custo Final Resolvido</span>
                            <span className="text-rose-400/80">-{formatCurrency(final_product_cost)}</span>
                        </div>
                        {extra_costs > 0 && (
                            <div className="flex justify-between text-slate-400" title="Armazenagem + risco de devolução + risco long-term + rateio de custo fixo">
                                <span className="font-sans">(-) Custos operacionais</span>
                                <span className="text-rose-400/80">-{formatCurrency(extra_costs)}</span>
                            </div>
                        )}
                        <div className="pb-3 border-b border-white/5"></div>

                        <div className="flex justify-between items-center pt-2">
                            <span className="font-medium text-white font-sans">LUCRO LÍQUIDO</span>
                            <div className="flex items-center gap-3">
                                <span className={`text-[10px] px-2 py-1 rounded-md font-sans font-medium ${profit < 0 ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                                    {(margin * 100).toFixed(1)}% Margem
                                </span>
                                <span className={`text-base font-bold ${profit < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                    {formatCurrency(profit)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
