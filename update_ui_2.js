const fs = require('fs');
let adModalPath = 'frontend/src/components/AdDetailsModal.tsx';
let adModalContent = fs.readFileSync(adModalPath, 'utf-8');

// 1. Fixing the badges
let oldBadges = `{fiscalResult?.is_mocked ? (
                                                                                    <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] uppercase rounded border border-indigo-500/30 font-bold">
                                                                                        Modo Simulação — Dados Fiscais Estimados
                                                                                    </span>
                                                                                ) : (
                                                                                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] uppercase rounded border border-emerald-500/30 font-bold flex items-center gap-1">
                                                                                        <CheckCircle2 size={12} /> Dados Fiscais Reais
                                                                                    </span>
                                                                                )}`;

let newBadges = `{fiscalResult?.is_mocked ? (
                                                                                    <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-[10px] uppercase rounded border border-amber-500/30 font-bold flex items-center gap-1">
                                                                                        <AlertTriangle size={12} /> Dados Estimados
                                                                                    </span>
                                                                                ) : (
                                                                                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] uppercase rounded border border-emerald-500/30 font-bold flex items-center gap-1">
                                                                                        <CheckCircle2 size={12} /> Dados Fiscais Reais
                                                                                    </span>
                                                                                )}`;

if (adModalContent.includes(oldBadges)) {
    adModalContent = adModalContent.replace(oldBadges, newBadges);
}

// 2. The block reason UI
let oldWarningsBlock = `{fiscalResult.status === 'blocked' && (
                                                                        <div className="mb-5 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                                                                            <p className="text-xs font-bold text-rose-400 mb-1">Motivo do Bloqueio: {fiscalResult.block_reason}</p>
                                                                            <ul className="list-disc pl-4 text-[11px] text-rose-300 mb-3">
                                                                                {fiscalResult.hard_locks?.map((lk: string) => <li key={lk}>{lk}</li>)}
                                                                                {fiscalResult.warnings?.map((w: string) => <li key={w} className="text-amber-300">{w}</li>)}
                                                                            </ul>
                                                                            {(fiscalResult.block_reason?.includes('MISSING') || fiscalResult.hard_locks?.some((lk: string) => lk.includes('MISSING'))) && (
                                                                                <button onClick={() => setActiveTab('fiscal')} className="px-4 py-1.5 bg-rose-500 hover:bg-rose-600 text-white text-[11px] font-bold rounded shadow-sm transition-colors uppercase">
                                                                                    Preencher Ficha Fiscal
                                                                                </button>
                                                                            )}
                                                                        </div>
                                                                    )}`;

// But the file ACTUALLY HAS THIS version right now:
let oldWarningsBlockFallback = `{fiscalResult.status === 'blocked' && (
                                                                        <div className="mb-5 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                                                                            <p className="text-xs font-bold text-rose-400 mb-1">Motivo do Bloqueio: {fiscalResult.block_reason}</p>
                                                                            <ul className="list-disc pl-4 text-[11px] text-rose-300">
                                                                                {fiscalResult.hard_locks?.map((lk: string) => <li key={lk}>{lk}</li>)}
                                                                                {fiscalResult.warnings?.map((w: string) => <li key={w} className="text-amber-300">{w}</li>)}
                                                                            </ul>
                                                                            {(fiscalResult.block_reason?.includes('MISSING') || fiscalResult.hard_locks?.some((lk: string) => lk.includes('MISSING'))) && (
                                                                                <button onClick={() => setActiveTab('fiscal')} className="px-4 py-1.5 bg-rose-500 hover:bg-rose-600 text-white text-[11px] font-bold rounded shadow-sm transition-colors uppercase">
                                                                                    Preencher Ficha Fiscal
                                                                                </button>
                                                                            )}
                                                                        </div>
                                                                    )}`;

// Wait, the file actually ONLY has this because my earlier script failed to add the button?
// Let's check what it has by reading a small chunk.

// I will just use regex to match the blocked div safely
let blockedRegex = /{fiscalResult\.status === 'blocked' && \([\s\S]*?<\/div>\s*\)\s*}/;

let newWarnings = `{fiscalResult.status === 'blocked' && (
                                                                        <>
                                                                        {(fiscalResult.block_reason === 'ZERO_PROFIT_VIOLATION' || fiscalResult.hard_locks?.includes('NEGATIVE_PROFIT')) ? (
                                                                            <div className="mb-5 p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg">
                                                                                <div className="flex items-center gap-2 mb-2">
                                                                                    <AlertTriangle className="w-5 h-5 text-rose-500" />
                                                                                    <h4 className="text-sm font-bold text-rose-400 uppercase">Preço bloqueado por prejuízo</h4>
                                                                                </div>
                                                                                <p className="text-xs text-rose-300 mb-4">O preço atual/simulado gera lucro líquido negativo com os dados fiscais reais cadastrados.</p>
                                                                                
                                                                                <div className="grid grid-cols-2 gap-3 mb-4">
                                                                                    <div className="bg-[#0B1120] p-2 rounded border border-rose-500/20">
                                                                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Lucro Líquido</p>
                                                                                        <p className="text-sm font-mono font-bold text-rose-400">{(fiscalResult.profit_amount || 0).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</p>
                                                                                    </div>
                                                                                    <div className="bg-[#0B1120] p-2 rounded border border-rose-500/20">
                                                                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Margem</p>
                                                                                        <p className="text-sm font-mono font-bold text-rose-400">{(fiscalResult.contribution_margin_percent || 0).toFixed(2)}%</p>
                                                                                    </div>
                                                                                    <div className="bg-[#0B1120] p-2 rounded border border-white/5">
                                                                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Mínimo (Lucro Zero)</p>
                                                                                        <p className="text-sm font-mono font-bold text-slate-300">{(fiscalResult.minimum_price_zero_profit || 0).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</p>
                                                                                    </div>
                                                                                    <div className="bg-[#0B1120] p-2 rounded border border-indigo-500/20">
                                                                                        <p className="text-[10px] text-slate-500 uppercase font-bold">Sugerido (Margem Alvo)</p>
                                                                                        <p className="text-sm font-mono font-bold text-indigo-400">{(fiscalResult.minimum_price_target_margin || 0).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</p>
                                                                                    </div>
                                                                                </div>
                                                                                
                                                                                <div className="text-[10px] text-rose-400/80 italic flex flex-col gap-1">
                                                                                    <span>• O sistema está usando Dados Fiscais Reais.</span>
                                                                                    <span>• O preço não está aprovado (bloqueio de segurança).</span>
                                                                                    <span>• Nenhuma alteração foi enviada ao Mercado Livre.</span>
                                                                                </div>
                                                                            </div>
                                                                        ) : (
                                                                            <div className="mb-5 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                                                                                <p className="text-xs font-bold text-amber-400 mb-1">Motivo do Bloqueio: Pendência Fiscal</p>
                                                                                <ul className="list-disc pl-4 text-[11px] text-amber-300 mb-3">
                                                                                    {fiscalResult.hard_locks?.map((lk: string) => {
                                                                                        const ptMsg = lk.replace('MISSING_PRODUCT_TAX_PROFILE', 'Ficha fiscal não cadastrada')
                                                                                                      .replace('MISSING_PURCHASE_COST', 'Custo de compra não cadastrado')
                                                                                                      .replace('MISSING_MONTHLY_TAX_CONFIG', 'Configuração mensal do Simples Nacional ausente')
                                                                                                      .replace('MISSING_ST_DATA', 'Dados de Substituição Tributária (ST) incompletos')
                                                                                                      .replace('MISSING_IPI_DATA', 'Dados de IPI incompletos')
                                                                                                      .replace('MISSING_NF_VALUE', 'Valor da NF ausente no custo de compra');
                                                                                        return <li key={lk}>{ptMsg}</li>
                                                                                    })}
                                                                                    {fiscalResult.warnings?.map((w: string) => <li key={w} className="text-slate-400">{w}</li>)}
                                                                                </ul>
                                                                                {(fiscalResult.block_reason?.includes('MISSING') || fiscalResult.hard_locks?.some((lk: string) => lk.includes('MISSING'))) && (
                                                                                    <button onClick={() => setActiveTab('fiscal')} className="px-4 py-1.5 bg-amber-500 hover:bg-amber-600 text-slate-900 text-[11px] font-bold rounded shadow-sm transition-colors uppercase mt-1">
                                                                                        Preencher Ficha Fiscal
                                                                                    </button>
                                                                                )}
                                                                            </div>
                                                                        )}
                                                                        </>
                                                                    )}`;

adModalContent = adModalContent.replace(blockedRegex, newWarnings);

fs.writeFileSync(adModalPath, adModalContent, 'utf-8');
console.log('Done!');
