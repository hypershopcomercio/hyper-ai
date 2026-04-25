import React from 'react';
import { DollarSign, AlertTriangle, TrendingDown, TrendingUp } from 'lucide-react';

interface SimulationData {
    ad_id: string;
    sku: string;
    price: number;
    cost_product: number;
    shipping_cost: number;
    commission_rate: number;
    tax_rate: number;
    financial_metrics: {
        return_rate?: number;
        fixed_cost_share?: number;
        avg_return_cost?: number;
        storage_cost?: number;
        daily_storage_fee?: number;
        inbound_freight_cost?: number;
        storage_risk_cost?: number;
    }
}

interface Props {
    competitorPrice: number;
    data: SimulationData;
}

export function CompetitorMarginSimulator({ competitorPrice, data }: Props) {
    if (!data) return null;

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    // Calculos
    const targetPrice = competitorPrice;

    // Custos Variaveis
    const tax = targetPrice * data.tax_rate;
    const commission = targetPrice * data.commission_rate;
    const shipping = data.shipping_cost;
    const productCost = data.cost_product;

    // Custos Financeiros (Unit Economics)
    const fixedCostShare = data.financial_metrics.fixed_cost_share || 0;
    const storageCostTotal = data.financial_metrics.storage_cost || 0;

    // Split Storage
    const inboundCost = data.financial_metrics.inbound_freight_cost || 0;
    const dailyStorage = (storageCostTotal - inboundCost) > 0 ? (storageCostTotal - inboundCost) : 0; // Approx total daily part

    const riskLongTerm = data.financial_metrics.storage_risk_cost || 0;

    const totalFixed = fixedCostShare + storageCostTotal;

    const returnRate = data.financial_metrics.return_rate || 0.03; // Default 3%
    const avgReturnCost = data.financial_metrics.avg_return_cost || 20.0;
    const riskDevolution = returnRate * avgReturnCost;

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
                Simulação: Cobrir Oferta (Unit Economics)
            </h4>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-slate-900/50 p-3 rounded border border-white/5">
                    <p className="text-[10px] text-slate-500 uppercase">Preço Alvo</p>
                    <p className="text-lg font-bold text-white">{formatCurrency(targetPrice)}</p>
                </div>

                <div className="relative group bg-slate-900/50 p-3 rounded border border-white/5 cursor-help transition-colors hover:bg-slate-900/80">
                    <p className="text-[10px] text-slate-500 uppercase">Custos Variáveis</p>
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
                                <span>Comissão ({(data.commission_rate * 100).toFixed(1)}%)</span>
                                <div>
                                    <span>{formatCurrency(commission)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((commission / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-slate-400">
                                <span>Imposto ({data.tax_rate * 100}%)</span>
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
                            <p className="text-[9px] text-slate-500 italic mt-1 border-t border-white/5 pt-1">
                                Calculado com base no custo fixo total + taxas ML Full.
                            </p>
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
                            {(marginPercent * 100).toFixed(1)}%
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
                                <span>Armazenagem (Inbound + Diária)</span>
                                <div>
                                    <span>- {formatCurrency(storageCostTotal)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((storageCostTotal / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="flex justify-between text-[10px] text-red-400">
                                <span>Riscos (Devolução + Longo Prazo)</span>
                                <div>
                                    <span>- {formatCurrency(totalRisk)}</span>
                                    <span className="text-slate-600 ml-1">({targetPrice ? ((totalRisk / targetPrice) * 100).toFixed(1) : 0}%)</span>
                                </div>
                            </div>
                            <div className="border-t border-white/10 pt-1 mt-1 flex justify-between text-xs font-bold text-white">
                                <span>Resultado Líquido</span>
                                <div>
                                    <span>{formatCurrency(margin)}</span>
                                    <span className={`text-emerald-500 ml-1`}>({(marginPercent * 100).toFixed(1)}%)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detalhamento colapsavel ou tooltip poderia vir aqui */}
            {isNegative && (
                <div className="flex items-center gap-2 text-red-400 text-xs bg-red-500/10 p-2 rounded border border-red-500/20">
                    <AlertTriangle size={14} />
                    <span>Perigo: Cobrir esta oferta resultará em prejuízo operacional real.</span>
                </div>
            )}
            {isTight && (
                <div className="flex items-center gap-2 text-amber-400 text-xs bg-amber-500/10 p-2 rounded border border-amber-500/20">
                    <AlertTriangle size={14} />
                    <span>Atenção: Margem muito apertada (abaixo de 10%). Risco alto.</span>
                </div>
            )}

            {/* ===== SMART COMPENSATION ANALYSIS ===== */}
            {(() => {
                // Current margin at current price
                const currentPrice = data.price;
                const currentMarginValue = currentPrice - (data.cost_product + (currentPrice * data.tax_rate) + (currentPrice * data.commission_rate) + data.shipping_cost + totalFixed + totalRisk);
                const marginLoss = currentMarginValue - margin;

                // Break-even analysis: how many extra units needed?
                const avgMonthlySales = 30; // Estimate - ideally from data
                const extraUnitsNeeded = marginLoss > 0 && margin > 0 ? Math.ceil(marginLoss / margin) : (margin <= 0 ? Infinity : 0);

                // Factors (all normalized to 0-100 score)
                // 1. Faster turnover benefit (less capital tied up)
                const turnoverBenefit = Math.min(100, (targetPrice < currentPrice ? 25 : 0) + (margin > 0 ? 20 : 0));

                // 2. Volume dilutes complaint risk
                const riskDilutionBenefit = Math.min(100, margin > 0 ? 30 : 0);

                // 3. ML Algorithm visibility boost (lower price = better ranking)
                const priceDiffPct = ((currentPrice - targetPrice) / currentPrice) * 100;
                const visibilityBoost = Math.min(100, priceDiffPct > 0 ? Math.min(priceDiffPct * 5, 40) : 0);

                // 4. Structure pressure (negative - more volume = more work)
                const structurePressure = margin > 0 ? Math.min(100, 15 + (priceDiffPct > 10 ? 15 : 0)) : 0;

                // Total score
                const positiveScore = turnoverBenefit + riskDilutionBenefit + visibilityBoost;
                const negativeScore = structurePressure + (isNegative ? 100 : 0);
                const netScore = positiveScore - negativeScore;

                // Recommendation
                let recommendation: { label: string; color: string; icon: React.ReactElement };
                if (isNegative) {
                    recommendation = { label: "NÃO Recomendado", color: "text-red-400", icon: <TrendingDown size={14} /> };
                } else if (netScore >= 50) {
                    recommendation = { label: "Altamente Recomendado", color: "text-emerald-400", icon: <TrendingUp size={14} /> };
                } else if (netScore >= 20) {
                    recommendation = { label: "Pode Compensar", color: "text-amber-400", icon: <TrendingUp size={14} /> };
                } else {
                    recommendation = { label: "Baixo Benefício", color: "text-slate-400", icon: <TrendingDown size={14} /> };
                }

                return (
                    <div className="mt-4 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 rounded-lg border border-indigo-500/20 p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h5 className="text-xs font-bold text-indigo-300 uppercase tracking-wide flex items-center gap-2">
                                📊 Análise de Compensação
                            </h5>
                            <div className="relative group">
                                <span className="text-indigo-400 text-xs cursor-help border-b border-dashed border-indigo-400/50">
                                    ℹ️ Como funciona?
                                </span>
                                {/* Info Tooltip */}
                                <div className="absolute bottom-full right-0 mb-2 w-80 bg-[#0c0d12] border border-indigo-500/30 rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 text-left">
                                    <p className="text-[10px] font-bold text-indigo-300 uppercase mb-2 border-b border-white/10 pb-1">Metodologia de Cálculo</p>
                                    <div className="space-y-2 text-[10px] text-slate-300">
                                        <div>
                                            <span className="text-emerald-400">✅ Giro Mais Rápido:</span> Menos capital empatado = economia de oportunidade (custo do dinheiro parado).
                                        </div>
                                        <div>
                                            <span className="text-emerald-400">✅ Diluição de Risco:</span> Mais vendas = menos impacto de cada reclamação individual na avaliação.
                                        </div>
                                        <div>
                                            <span className="text-emerald-400">✅ Boost no Algoritmo ML:</span> Preço competitivo melhora ranqueamento = mais visitas orgânicas.
                                        </div>
                                        <div>
                                            <span className="text-red-400">❌ Pressão Estrutural:</span> Mais volume = mais trabalho operacional, embalagem, suporte.
                                        </div>
                                        <div className="border-t border-white/10 pt-2 mt-2 text-slate-400 italic">
                                            O score final pondera esses fatores para determinar se a redução de margem compensa.
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Factors Grid */}
                        <div className="grid grid-cols-2 gap-2 mb-3">
                            <div className="bg-emerald-500/10 rounded p-2 border border-emerald-500/20">
                                <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                                    <span>🔄</span> Giro Rápido
                                </div>
                                <div className="text-xs font-bold text-emerald-300">+{turnoverBenefit} pts</div>
                            </div>
                            <div className="bg-emerald-500/10 rounded p-2 border border-emerald-500/20">
                                <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                                    <span>🛡️</span> Diluição Risco
                                </div>
                                <div className="text-xs font-bold text-emerald-300">+{riskDilutionBenefit} pts</div>
                            </div>
                            <div className="bg-emerald-500/10 rounded p-2 border border-emerald-500/20">
                                <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                                    <span>📈</span> Boost Algoritmo
                                </div>
                                <div className="text-xs font-bold text-emerald-300">+{visibilityBoost.toFixed(0)} pts</div>
                            </div>
                            <div className="bg-red-500/10 rounded p-2 border border-red-500/20">
                                <div className="flex items-center gap-1 text-[10px] text-red-400 font-medium">
                                    <span>⚙️</span> Pressão Estrutural
                                </div>
                                <div className="text-xs font-bold text-red-300">-{structurePressure} pts</div>
                            </div>
                        </div>

                        {/* Result */}
                        <div className="flex items-center justify-between bg-black/20 rounded-lg p-3 border border-white/5">
                            <div>
                                <span className="text-[10px] text-slate-500 uppercase">Score Final</span>
                                <div className={`text-lg font-bold ${netScore >= 50 ? 'text-emerald-400' : netScore >= 0 ? 'text-amber-400' : 'text-red-400'}`}>
                                    {netScore >= 0 ? '+' : ''}{netScore} pts
                                </div>
                            </div>
                            <div className="text-right">
                                <div className={`flex items-center gap-1 ${recommendation.color} font-bold text-sm`}>
                                    {recommendation.icon}
                                    {recommendation.label}
                                </div>
                                {margin > 0 && marginLoss > 0 && Number.isFinite(extraUnitsNeeded) && (
                                    <div className="text-[10px] text-slate-400 mt-1">
                                        Break-even: <span className="text-white font-medium">+{extraUnitsNeeded} vendas extras</span> para compensar
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })()}
        </div>
    );
}
