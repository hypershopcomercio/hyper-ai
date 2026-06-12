const fs = require('fs');

const filePath = 'frontend/src/components/AdDetailsModal.tsx';
let content = fs.readFileSync(filePath, 'utf-8');

const oldPayload = `                    const payload = {
                        ad_id: ad.id,
                        simulate_price: priceToSimulate,
                        target_margin_percent: targetMargin,
                        product_cost: {
                            real_cost: ad.cost || 0,
                            valor_nf: ad.cost ? ad.cost * 0.5 : 0,
                            ipi_rate: 0.0,
                            difal_value: 0.0,
                            other_purchase_costs: 0.0,
                            product_origin: "nacional"
                        },
                        tax_profile: {
                            full_das_rate: 10.0,
                            das_without_icms_rate: 4.83,
                            has_st: false,
                            has_ipi: false,
                            has_difal: false,
                            mva_rate: 0.0,
                            origin_icms_rate: 12.0,
                            destination_icms_rate: 18.0
                        },
                        marketplace: {
                            fee_rate: ad.commission_percent || 10.0,
                            fixed_fee: priceToSimulate < 79.90 ? 6.0 : 0.0,
                            freight_cost: ad.shipping_cost || 0.0,
                            other_variable_costs: 0.0
                        }
                    };`;

const newPayload = `                    const payload = {
                        ad_id: ad.id,
                        simulate_price: priceToSimulate,
                        target_margin_percent: targetMargin
                    };`;

if (content.includes(oldPayload)) {
    content = content.replace(oldPayload, newPayload);
}

const oldHeader = `                                                                                <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] uppercase rounded border border-indigo-500/30 font-bold">
                                                                                    Modo Simulação — Dados Fiscais Estimados
                                                                                </span>
                                                                            </h3>
                                                                            <p className="text-[10px] text-slate-400 mt-1">
                                                                                Os impostos exibidos usam parâmetros temporários até a configuração fiscal do produto ser cadastrada.
                                                                            </p>`;

const newHeader = `                                                                                {fiscalResult?.is_mocked ? (
                                                                                    <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-[10px] uppercase rounded border border-indigo-500/30 font-bold">
                                                                                        Modo Simulação — Dados Fiscais Estimados
                                                                                    </span>
                                                                                ) : (
                                                                                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] uppercase rounded border border-emerald-500/30 font-bold flex items-center gap-1">
                                                                                        <CheckCircle2 size={12} /> Dados Fiscais Reais
                                                                                    </span>
                                                                                )}
                                                                            </h3>
                                                                            {fiscalResult?.is_mocked && (
                                                                                <p className="text-[10px] text-slate-400 mt-1">
                                                                                    Os impostos exibidos usam parâmetros temporários até a configuração fiscal do produto ser cadastrada.
                                                                                </p>
                                                                            )}`;

if (content.includes(oldHeader)) {
    content = content.replace(oldHeader, newHeader);
}

const oldWarnings = `                                                                        <div className="mb-5 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                                                                            <p className="text-xs font-bold text-rose-400 mb-1">Motivo do Bloqueio: {fiscalResult.block_reason}</p>
                                                                            <ul className="list-disc pl-4 text-[11px] text-rose-300">
                                                                                {fiscalResult.hard_locks?.map((lk: string) => <li key={lk}>{lk}</li>)}
                                                                                {fiscalResult.warnings?.map((w: string) => <li key={w} className="text-amber-300">{w}</li>)}
                                                                            </ul>
                                                                        </div>`;

const newWarnings = `                                                                        <div className="mb-5 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg">
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
                                                                        </div>`;

if (content.includes(oldWarnings)) {
    content = content.replace(oldWarnings, newWarnings);
}

const oldDataTitle = `<h4 className="text-[10px] font-bold text-amber-500/70 uppercase tracking-wider border-b border-white/5 pb-2 mb-3">Dados Fiscais Mockados</h4>`;

const newDataTitle = `<h4 className={\`text-[10px] font-bold uppercase tracking-wider border-b border-white/5 pb-2 mb-3 \${fiscalResult.is_mocked ? 'text-amber-500/70' : 'text-emerald-500/70'}\`}>
                                                                                {fiscalResult.is_mocked ? 'Dados Fiscais Estimados' : 'Base de Cálculo (Ficha Real)'}
                                                                            </h4>`;

if (content.includes(oldDataTitle)) {
    content = content.replace(oldDataTitle, newDataTitle);
}

fs.writeFileSync(filePath, content, 'utf-8');
console.log('Frontend updated.');
