import React from 'react';
import { Calculator, ShieldAlert, CheckCircle2, Info, AlertTriangle } from 'lucide-react';
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

    const { status, is_usable_for_automation, calculator_inputs, comparison, cost_candidates, hard_locks, warnings, selection_status } = pricingResolution;

    const targetPrice = simulatedPrice > 0 ? simulatedPrice : ad.price;

    const mkp_rate = calculator_inputs?.marketplace_costs?.commission_rate || 0;
    const mkp_shipping = calculator_inputs?.marketplace_costs?.shipping_cost || 0;
    const das_rate = calculator_inputs?.sales_tax_rate || 0;
    const final_product_cost = calculator_inputs?.final_product_cost || 0;

    const mkp_commission = targetPrice * mkp_rate;
    const das_value = targetPrice * (das_rate / 100);
    
    const riskLongTerm = ad.storage_risk_cost || 0;
    const riskDevolution = ad.return_risk_cost || 0;
    const fixedCostShare = ad.fixed_cost_share || 0;
    const storageCostTotal = ad.storage_cost || 0;
    
    const extra_costs = riskLongTerm + riskDevolution + fixedCostShare + storageCostTotal;
    const total_cost = final_product_cost + mkp_commission + mkp_shipping + das_value + extra_costs;
    const profit = targetPrice - total_cost;
    const margin = targetPrice > 0 ? profit / targetPrice : 0;
    const min_price_zero_profit = (final_product_cost + mkp_shipping + extra_costs) / (1 - mkp_rate - (das_rate / 100));

    const isBlocked = !is_usable_for_automation;
    const isConflict = hard_locks?.includes("COST_SOURCE_CONFLICT");

    return (
        <div className="space-y-4">
            {/* Status Panel */}
            <div className={`p-4 rounded-xl border ${isBlocked ? 'bg-rose-500/10 border-rose-500/30' : 'bg-emerald-500/10 border-emerald-500/30'} flex flex-col gap-3`}>
                <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                        {isBlocked ? <ShieldAlert className="text-rose-400 w-6 h-6" /> : <CheckCircle2 className="text-emerald-400 w-6 h-6" />}
                    </div>
                    <div className="flex-1">
                        <h3 className={`text-lg font-bold ${isBlocked ? 'text-rose-400' : 'text-emerald-400'}`}>
                            {isBlocked ? 'Automação Bloqueada: Revisão Necessária' : 'Apto para Automação'}
                        </h3>
                        {isConflict && (
                            <p className="text-sm text-rose-300 font-bold mt-1 uppercase tracking-wider">
                                Conflito de Custo Detectado
                            </p>
                        )}
                        <p className="text-xs text-slate-300 mt-1">
                            {isBlocked 
                                ? 'O robô de precificação não executará ações automáticas enquanto existirem divergências bloqueantes.' 
                                : 'Os parâmetros fiscais e de custo foram validados com sucesso pela auditoria sistêmica.'}
                        </p>
                        
                        {hard_locks && hard_locks.length > 0 && (
                            <div className="mt-3 flex gap-2 flex-wrap">
                                {hard_locks.map((hl: string) => (
                                    <span key={hl} className="px-2 py-1 bg-rose-500/20 text-rose-300 text-xs font-bold rounded uppercase border border-rose-500/30">
                                        BLOQUEIO CRÍTICO: {hl}
                                    </span>
                                ))}
                            </div>
                        )}
                        {warnings && warnings.length > 0 && (
                            <div className="mt-2 space-y-1">
                                {warnings.map((w: string, idx: number) => (
                                    <p key={idx} className="text-xs text-amber-400 flex items-center gap-1.5">
                                        <AlertTriangle size={12} /> {w}
                                    </p>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {isConflict && (
                    <div className="mt-2 bg-rose-500/10 border border-rose-500/20 rounded p-3 text-xs text-rose-200">
                        <strong className="block text-rose-400 mb-1">Recomendação:</strong>
                        Existe um Override Manual ativo que diverge significativamente da fonte automática confiável. Você deve revisar a Auditoria Fiscal e Validar o override, Remover o override, ou Usar a fonte automática antes de reativar o robô.
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Cost Comparison Panel */}
                <div className="bg-[#13141b] rounded-xl border border-white/5 p-5">
                    <h4 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                        <Info size={16} className="text-indigo-400" /> Diagnóstico de Custos
                    </h4>
                    
                    <div className="space-y-3">
                        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                            <span className="text-slate-400">Custo Tiny / Ads (Automático):</span>
                            <span className="font-mono text-slate-300">{formatCurrency(cost_candidates?.tiny_ads_cost || 0)}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
                            <span className="text-slate-400">Override Manual Base:</span>
                            <span className="font-mono text-indigo-400 font-bold">{formatCurrency(cost_candidates?.override_manual_base || 0)}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm pt-2">
                            <span className="text-slate-300 font-bold">Custo Final Resolvido (usado no cálculo):</span>
                            <span className="font-mono text-white font-bold">{formatCurrency(cost_candidates?.resolved_final_cost || 0)}</span>
                        </div>
                        
                        {comparison?.ad_cost_divergence && (
                            <div className={`mt-4 p-3 rounded-lg border flex justify-between items-center ${isConflict ? 'bg-rose-500/10 border-rose-500/20' : 'bg-black/30 border-white/5'}`}>
                                <span className={`text-xs uppercase font-bold tracking-wider ${isConflict ? 'text-rose-400' : 'text-slate-400'}`}>
                                    Divergência
                                </span>
                                <span className={`text-sm font-mono font-bold ${isConflict ? 'text-rose-400' : 'text-amber-400'}`}>
                                    {formatCurrency(comparison.ad_cost_divergence.diff)} 
                                    <span className="text-xs ml-1 opacity-70">({comparison.ad_cost_divergence.diff_percent.toFixed(1)}%)</span>
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Calculation Cascade */}
                <div className="bg-[#13141b] rounded-xl border border-white/5 p-5">
                    <h4 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                        <Calculator size={16} className="text-emerald-400" /> Cascata de Cálculo Real
                    </h4>
                    
                    <div className="space-y-2 font-mono text-sm">
                        <div className="flex justify-between text-emerald-400 font-bold mb-2 pb-2 border-b border-white/10">
                            <span>Preço de Venda Analisado</span>
                            <span>{formatCurrency(targetPrice)}</span>
                        </div>
                        
                        <div className="flex justify-between text-slate-400">
                            <span>(-) Comissão ML ({(mkp_rate * 100).toFixed(1)}%)</span>
                            <span className="text-rose-400">-{formatCurrency(mkp_commission)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>(-) Frete ML</span>
                            <span className="text-rose-400">-{formatCurrency(mkp_shipping)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>(-) Imposto DAS ({das_rate.toFixed(2)}%)</span>
                            <span className="text-rose-400">-{formatCurrency(das_value)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400 pb-2 border-b border-white/10">
                            <span>(-) Custo Final Resolvido</span>
                            <span className="text-rose-400">-{formatCurrency(final_product_cost)}</span>
                        </div>
                        
                        <div className="flex justify-between items-center pt-2">
                            <span className="font-bold text-white tracking-wider">LUCRO LÍQUIDO</span>
                            <div className="flex flex-col items-end">
                                <span className={`text-lg font-bold ${profit < 0 ? 'text-rose-500' : 'text-emerald-400'}`}>
                                    {formatCurrency(profit)}
                                </span>
                                <span className={`text-xs px-1.5 py-0.5 rounded ${profit < 0 ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'}`}>
                                    {(margin * 100).toFixed(1)}% Margem
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
