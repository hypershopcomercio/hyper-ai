import React from 'react';
import { DollarSign, AlertTriangle, TrendingDown, TrendingUp, Info } from 'lucide-react';
import { Ad } from '@/types';

interface MarginSimulatorProps {
    ad: Ad;
    simulatedPrice: number;
}

export function MarginSimulator({ ad, simulatedPrice }: MarginSimulatorProps) {
    if (!ad) return null;

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    // Calculos
    const targetPrice = simulatedPrice;

    // Custos Variaveis
    // Infer rates from current ad data if possible, or use absolute values scaled
    const currentPrice = ad.price || 1;

    // Tax Rate inference
    const taxRate = ad.tax_cost ? (ad.tax_cost / currentPrice) : 0;
    const tax = targetPrice * taxRate;

    // Commission Rate inference
    const commissionRate = ad.commission_cost ? (ad.commission_cost / currentPrice) : 0;
    const commission = targetPrice * commissionRate;

    const shipping = ad.shipping_cost || 0;
    const productCost = ad.cost || 0;

    // Custos Financeiros (Unit Economics)
    // Using flat fields from Ad interface
    const fixedCostShare = ad.fixed_cost_share || 0;
    const storageCostTotal = ad.storage_cost || 0;

    // Split Storage inferido (similar ao CompetitorMarginSimulator)
    const inboundCost = ad.inbound_freight_cost || 0;
    const dailyStorage = (storageCostTotal - inboundCost) > 0 ? (storageCostTotal - inboundCost) : 0;

    const riskLongTerm = ad.storage_risk_cost || 0;
    const riskDevolution = ad.return_risk_cost || 0;

    const totalFixed = fixedCostShare + storageCostTotal;
    const totalRisk = riskDevolution + riskLongTerm;

    const totalCost = productCost + tax + commission + shipping + totalFixed + totalRisk;
    const margin = targetPrice - totalCost;
    const marginPercent = targetPrice > 0 ? (margin / targetPrice) : 0;

    const isNegative = margin < 0;
    const isTight = marginPercent < 0.10 && !isNegative; // Margem < 10%

    return (
        <div className="bg-[#13141b] rounded-lg border border-white/5 p-4 mt-4">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3 flex items-center gap-2">
                <DollarSign size={14} />
                Simulação de Margem (Unit Economics)
            </h4>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-slate-900/50 p-3 rounded border border-white/5">
                    <p className="text-[10px] text-slate-500 uppercase">Preço Simulado</p>
                    <p className="text-lg font-bold text-white">{formatCurrency(targetPrice)}</p>
                </div>

                <div className="relative group bg-slate-900/50 p-3 rounded border border-white/5 cursor-help transition-colors hover:bg-slate-900/80">
                    <p className="text-[10px] text-slate-500 uppercase">Custos Variáveis <span className="text-[9px] opacity-70 normal-case">(incl. CMV)</span></p>
                    <p className="text-sm font-medium text-red-400">
                        - {formatCurrency(tax + commission + shipping + productCost + totalRisk)}
                    </p>
                    <p className="text-[10px] text-slate-600">Com + Imp + Frete + Risco</p>

                    {/* Tooltip Variable */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-80 bg-[#0c0d12] border border-white/10 rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                        <div className="space-y-1">
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Produto (CMV)</span>
                                <div>
                                    <span>{formatCurrency(productCost)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((productCost / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Comissão ML ({(commissionRate * 100).toFixed(2)}%)</span>
                                <div>
                                    <span>{formatCurrency(commission)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((commission / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Imposto ({(taxRate * 100).toFixed(2)}%)</span>
                                <div>
                                    <span>{formatCurrency(tax)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((tax / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Frete</span>
                                <div>
                                    <span>{formatCurrency(shipping)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((shipping / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="border-t border-white/5 my-1" />
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Risco Devolução</span>
                                <div>
                                    <span>{formatCurrency(riskDevolution)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((riskDevolution / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Risco Est. Longo Prazo</span>
                                <div>
                                    <span>{formatCurrency(riskLongTerm)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((riskLongTerm / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="border-t border-white/10 pt-1 mt-1 flex justify-between text-[10px] font-bold text-red-400">
                                <span>Total Variável + Riscos</span>
                                <div>
                                    <span>{formatCurrency(tax + commission + shipping + productCost + totalRisk)}</span>
                                    <span className="text-red-400/70 ml-1">({targetPrice ? (((tax + commission + shipping + productCost + totalRisk) / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                        </div>
                        {/* Arrow */}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-[#0c0d12] border-l-transparent border-r-transparent"></div>
                    </div>
                </div>

                <div className="relative group bg-slate-900/50 p-3 rounded border border-white/5 cursor-help transition-colors hover:bg-slate-900/80">
                    <p className="text-[10px] text-slate-500 uppercase">Custos Fixos (Rateio)</p>
                    <p className="text-sm font-medium text-red-400">
                        - {formatCurrency(totalFixed)}
                    </p>
                    <p className="text-[10px] text-slate-600">Operacional + Armaz.</p>

                    {/* Tooltip Fixed */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-80 bg-[#0c0d12] border border-white/10 rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                        <div className="space-y-1">
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Rateio por SKU</span>
                                <div>
                                    <span>{formatCurrency(fixedCostShare)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((fixedCostShare / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="border-t border-white/5 my-1" />
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Armazenagem (Total)</span>
                                <div>
                                    <span>{formatCurrency(storageCostTotal)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((storageCostTotal / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="ml-2 flex justify-between text-[9px] text-slate-500">
                                <span>↳ Envio Full (Inbound)</span>
                                <div>
                                    <span>{formatCurrency(inboundCost)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((inboundCost / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="ml-2 flex justify-between text-[9px] text-slate-500">
                                <span>↳ Diária (Est.)</span>
                                <div>
                                    <span>{formatCurrency(dailyStorage)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((dailyStorage / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                        </div>
                        {/* Arrow */}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-[#0c0d12] border-l-transparent border-r-transparent"></div>
                    </div>
                </div>

                <div className={`relative group p-3 rounded border cursor-help ${isNegative ? 'bg-red-500/10 border-red-500/30' : isTight ? 'bg-amber-500/10 border-amber-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
                    <p className="text-[10px] uppercase opacity-70">Margem Líquida Est.</p>
                    <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-lg font-bold ${(() => {
                            const pct = marginPercent * 100;
                            if (pct < 5) return 'text-rose-500';
                            if (pct < 10) return 'text-orange-400';
                            if (pct <= 15) return 'text-yellow-400';
                            if (pct <= 20) return 'text-emerald-400';
                            return 'text-emerald-600';
                        })()}`}>
                            {formatCurrency(margin)}
                        </span>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded whitespace-nowrap ${(() => {
                            const pct = marginPercent * 100;
                            if (pct < 5) return 'bg-rose-500/20 text-rose-300';
                            if (pct < 10) return 'bg-orange-500/20 text-orange-300';
                            if (pct <= 15) return 'bg-yellow-500/20 text-yellow-300';
                            if (pct <= 20) return 'bg-emerald-500/20 text-emerald-300';
                            return 'bg-emerald-600/20 text-emerald-400';
                        })()}`}>
                            {(marginPercent * 100).toFixed(2)}%
                        </span>
                    </div>

                    {/* Tooltip Margin Detailed */}
                    <div className="absolute bottom-full right-0 mb-2 w-80 bg-[#0c0d12] border border-white/10 rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-left">
                        <p className="text-[10px] font-bold text-slate-300 uppercase mb-2 border-b border-white/10 pb-1">Cálculo Final Detalhado</p>
                        <div className="space-y-1">
                            <div className="flex justify-between text-[10px] text-emerald-400">
                                <span>Preço Venda</span>
                                <span>+ {formatCurrency(targetPrice)}</span>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Custos ML</span>
                                <div>
                                    <span>- {formatCurrency(tax + commission + shipping)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? (((tax + commission + shipping) / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Custo Produto</span>
                                <div>
                                    <span>- {formatCurrency(productCost)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((productCost / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Custo Fixo (Rateio)</span>
                                <div>
                                    <span>- {formatCurrency(fixedCostShare)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((fixedCostShare / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Armazenagem</span>
                                <div>
                                    <span>- {formatCurrency(storageCostTotal)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((storageCostTotal / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Riscos (Devolução + LP)</span>
                                <div>
                                    <span>- {formatCurrency(totalRisk)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((totalRisk / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="border-t border-white/10 pt-1 mt-1 flex justify-between text-xs font-bold text-white">
                                <span>Resultado Líquido</span>
                                <div>
                                    <span>{formatCurrency(margin)}</span>
                                    <span className={`text-emerald-500 ml-1`}>({(marginPercent * 100).toFixed(2)}%)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {isNegative && (
                <div className="flex items-center gap-2 text-red-400 text-xs bg-red-500/10 p-2 rounded border border-red-500/20">
                    <AlertTriangle size={14} />
                    <span>Prejuízo operacional estimado com este preço.Revisão necessária.</span>
                </div>
            )}
            {isTight && (
                <div className="flex items-center gap-2 text-amber-400 text-xs bg-amber-500/10 p-2 rounded border border-amber-500/20">
                    <AlertTriangle size={14} />
                    <span>Margem apertada (abaixo de 10%). Acompanhe de perto.</span>
                </div>
            )}
        </div>
    );
}
