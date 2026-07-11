"use client";

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
    Truck, Package, PackageCheck, PackageX, Warehouse, AlertTriangle,
    Clock, Boxes, RefreshCw, Loader2, Settings2, Trash2, Plus, Pencil, X, ExternalLink, DollarSign
} from 'lucide-react';

const fmtBRL = (v: number | null | undefined) =>
    v == null ? '—' : v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const fmtInt = (v: number | null | undefined) =>
    v == null ? '—' : v.toLocaleString('pt-BR');

interface Summary {
    products_count: number;
    inventories_count: number;
    units_available: number;
    units_in_transit: number;
    units_not_available: number;
    immobilized_value: number;
}
interface Alerts { low_coverage: number; aged_stock: number; stranded: number; }
interface Overview { has_data: boolean; message?: string; summary: Summary; alerts: Alerts; }

interface InvItem {
    inventory_id: string;
    ad_id: string | null;
    sku: string | null;
    title: string | null;
    thumbnail: string | null;
    permalink: string | null;
    available_qty: number;
    in_transit_qty: number;
    not_available_qty: number;
    total_qty: number;
    days_of_stock: number | null;
    oldest_stock_days: number | null;
    storage_cost_unit: number | null;
    storage_risk_unit: number | null;
    is_aged: boolean;
    is_low_coverage: boolean;
}

interface Tariff {
    id: number;
    name: string | null;
    min_volume_l: number;
    max_volume_l: number | null;
    daily_fee: number | null;
    inbound_fee: number | null;
    aged_days_threshold: number;
    aged_daily_factor: number;
    active: boolean;
}

interface ReplenishmentItem {
    ad_id: string;
    sku: string;
    title: string | null;
    full_available: number;
    local_available: number;
    coverage_days: number;
    quantity_suggested: number;
    status: 'ready' | 'no_local_stock';
}

export default function FullPage() {
    const [overview, setOverview] = useState<Overview | null>(null);
    const [items, setItems] = useState<InvItem[]>([]);
    const [tariffs, setTariffs] = useState<Tariff[]>([]);
    const [replenishment, setReplenishment] = useState<ReplenishmentItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);
    const [sortBy, setSortBy] = useState<'coverage' | 'aged' | 'available'>('coverage');
    const [onlyAlerts, setOnlyAlerts] = useState(false);
    const [showTariffs, setShowTariffs] = useState(false);
    const [feedback, setFeedback] = useState<string | null>(null);

    const load = useCallback(() => {
        setLoading(true);
        Promise.all([
            api.get('/full/overview'),
            api.get(`/full/inventory?sort_by=${sortBy}${onlyAlerts ? '&alerts=1' : ''}`),
            api.get('/full/tariffs'),
            api.get('/full/replenishment'),
        ])
            .then(([ov, inv, tf, rp]) => {
                setOverview(ov.data);
                setItems(inv.data.items || []);
                setTariffs(tf.data.tariffs || []);
                setReplenishment(rp.data.items || []);
            })
            .catch(err => console.error('Erro ao carregar Full', err))
            .finally(() => setLoading(false));
    }, [sortBy, onlyAlerts]);

    useEffect(() => { load(); }, [load]);

    const runSync = async () => {
        setSyncing(true);
        setFeedback(null);
        try {
            const res = await api.post('/full/sync');
            setFeedback(`Sync concluído: ${res.data?.stock?.inventories ?? 0} unidades de inventário, custo real em ${res.data?.cost?.updated ?? 0} SKUs.`);
            load();
        } catch (err: any) {
            setFeedback(err?.response?.data?.error || 'Falha no sync.');
        } finally {
            setSyncing(false);
        }
    };

    const coverageColor = (d: number | null) =>
        d == null ? 'text-slate-500' : d < 14 ? 'text-red-400' : d < 30 ? 'text-amber-400' : 'text-emerald-400';
    const agedColor = (d: number | null) =>
        d == null ? 'text-slate-500' : d > 90 ? 'text-red-400' : d > 60 ? 'text-amber-400' : 'text-slate-300';

    if (loading && !overview) {
        return <div className="p-8 text-white flex items-center gap-2"><Loader2 className="animate-spin" size={18} /> Carregando Full...</div>;
    }

    const s = overview?.summary;
    const a = overview?.alerts;

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Truck className="text-sky-400" /> Envio Full
                    </h1>
                    <p className="text-slate-400 mt-1">Estoque real nos CDs do Mercado Livre — cobertura, estoque antigo e custo real de armazenagem</p>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowTariffs(v => !v)}
                        className="px-3 py-2 rounded-lg text-xs font-bold border border-white/10 text-slate-300 hover:text-white hover:bg-white/5 flex items-center gap-2"
                    >
                        <Settings2 size={14} /> Tarifas ({tariffs.length})
                    </button>
                    <button
                        onClick={runSync}
                        disabled={syncing}
                        className="px-4 py-2 rounded-lg text-xs font-bold bg-sky-500 hover:bg-sky-400 text-white flex items-center gap-2 disabled:opacity-60"
                    >
                        {syncing ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                        {syncing ? 'Sincronizando...' : 'Sincronizar'}
                    </button>
                </div>
            </div>

            {feedback && (
                <div className="bg-sky-500/10 border border-sky-500/20 rounded-xl px-4 py-3 text-sm text-sky-200">{feedback}</div>
            )}

            {/* Tariffs panel */}
            {showTariffs && <TariffsPanel tariffs={tariffs} onChange={load} />}

            {!overview?.has_data ? (
                <div className="bg-[#121217] border border-white/5 rounded-2xl p-8 text-slate-400">
                    Sem dados de Full ainda. {overview?.message || 'Clique em "Sincronizar" ou rode: python -m app.scripts.backfill_full_stock'}
                    {tariffs.length === 0 && (
                        <div className="mt-3 text-amber-300/90 text-sm flex items-start gap-2">
                            <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                            Cadastre a <b>tabela de tarifas do Full</b> (botão Tarifas) para que o custo real de armazenagem alimente o financeiro e o modal do produto.
                        </div>
                    )}
                </div>
            ) : (
                <>
                    {/* Summary cards */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <Card icon={<Boxes size={12} />} label="Produtos no Full" value={fmtInt(s!.products_count)} sub={`${fmtInt(s!.inventories_count)} inventários`} />
                        <Card icon={<PackageCheck size={12} />} label="Disponível" value={fmtInt(s!.units_available)} sub="unidades vendáveis" valueClass="text-emerald-400" />
                        <Card icon={<Package size={12} />} label="Em trânsito" value={fmtInt(s!.units_in_transit)} sub="a caminho do CD" valueClass="text-sky-400" />
                        <Card icon={<PackageX size={12} />} label="Indisponível" value={fmtInt(s!.units_not_available)} sub="retido / avariado" valueClass={s!.units_not_available > 0 ? 'text-amber-400' : 'text-white'} />
                        <Card icon={<DollarSign size={12} />} label="Valor imobilizado" value={fmtBRL(s!.immobilized_value)} sub="custo × disponível" />
                    </div>

                    {/* Alert chips */}
                    <div className="flex flex-wrap gap-3">
                        <AlertChip active={(a?.low_coverage ?? 0) > 0} icon={<AlertTriangle size={14} />} count={a?.low_coverage ?? 0} label="cobertura < 14 dias" tone="red" />
                        <AlertChip active={(a?.aged_stock ?? 0) > 0} icon={<Clock size={14} />} count={a?.aged_stock ?? 0} label="estoque antigo (>90d)" tone="amber" />
                        <AlertChip active={(a?.stranded ?? 0) > 0} icon={<Warehouse size={14} />} count={a?.stranded ?? 0} label="parado / sem giro" tone="slate" />
                    </div>

                    <section className="bg-[#121217] border border-white/5 rounded-2xl overflow-hidden">
                        <div className="p-5 border-b border-white/5 flex items-start justify-between gap-4">
                            <div>
                                <h2 className="text-sm font-bold text-white">Reposicao sugerida para o Full</h2>
                                <p className="text-xs text-slate-500 mt-1">Sugestao apenas: Full e local sao dados reais; a velocidade usa as vendas dos ultimos 30 dias.</p>
                            </div>
                            <span className="text-xs font-mono text-sky-300 shrink-0">{replenishment.length} alerta(s)</span>
                        </div>
                        {replenishment.length === 0 ? (
                            <p className="p-5 text-sm text-slate-500">Nenhuma reposicao urgente com giro registrado.</p>
                        ) : (
                            <div className="overflow-x-auto"><table className="w-full text-sm">
                                <thead><tr className="text-[10px] uppercase tracking-widest text-slate-500 border-b border-white/5">
                                    <th className="text-left px-5 py-3">Produto</th><th className="text-right px-3 py-3">Full</th><th className="text-right px-3 py-3">Local</th><th className="text-right px-3 py-3">Cobertura</th><th className="text-right px-5 py-3">Sugestao</th>
                                </tr></thead>
                                <tbody>{replenishment.slice(0, 12).map(item => <tr key={item.sku} className="border-b border-white/5">
                                    <td className="px-5 py-3"><div className="text-slate-200">{item.title || item.sku}</div><div className="text-[11px] text-slate-500 font-mono">{item.sku}</div></td>
                                    <td className="px-3 py-3 text-right font-mono text-sky-300">{fmtInt(item.full_available)}</td>
                                    <td className="px-3 py-3 text-right font-mono text-emerald-300">{fmtInt(item.local_available)}</td>
                                    <td className={`px-3 py-3 text-right font-mono ${coverageColor(item.coverage_days)}`}>{`${item.coverage_days.toFixed(0)}d`}</td>
                                    <td className={`px-5 py-3 text-right font-mono font-bold ${item.status === 'ready' ? 'text-amber-300' : 'text-rose-300'}`}>{item.status === 'ready' ? `${fmtInt(item.quantity_suggested)} un` : 'Sem local'}</td>
                                </tr>)}</tbody>
                            </table></div>
                        )}
                    </section>

                    {/* Filters */}
                    <div className="flex items-center gap-3 flex-wrap">
                        <div className="flex bg-slate-800/50 rounded-lg p-1 border border-white/5">
                            {([['coverage', 'Cobertura'], ['aged', 'Antiguidade'], ['available', 'Estoque']] as const).map(([key, lbl]) => (
                                <button key={key} onClick={() => setSortBy(key)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${sortBy === key ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}>
                                    {lbl}
                                </button>
                            ))}
                        </div>
                        <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                            <input type="checkbox" checked={onlyAlerts} onChange={e => setOnlyAlerts(e.target.checked)} className="accent-sky-500" />
                            só alertas
                        </label>
                        <span className="text-xs text-slate-500 ml-auto">{items.length} anúncios</span>
                    </div>

                    {/* Inventory table */}
                    <div className="bg-[#121217] border border-white/5 rounded-2xl overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-[10px] uppercase tracking-widest text-slate-500 border-b border-white/5">
                                        <th className="text-left font-semibold px-4 py-3">Produto</th>
                                        <th className="text-right font-semibold px-3 py-3">Disp.</th>
                                        <th className="text-right font-semibold px-3 py-3">Trânsito</th>
                                        <th className="text-right font-semibold px-3 py-3">Indisp.</th>
                                        <th className="text-right font-semibold px-3 py-3">Cobertura</th>
                                        <th className="text-right font-semibold px-3 py-3">Antiguidade</th>
                                        <th className="text-right font-semibold px-4 py-3">Armaz./un</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items.map(it => (
                                        <tr key={it.inventory_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-3">
                                                    {it.thumbnail
                                                        ? <img src={it.thumbnail} alt="" className="w-9 h-9 rounded object-cover bg-slate-800 shrink-0" />
                                                        : <div className="w-9 h-9 rounded bg-slate-800 shrink-0" />}
                                                    <div className="min-w-0">
                                                        <div className="text-slate-200 truncate max-w-[320px] flex items-center gap-1.5">
                                                            {it.title || it.ad_id}
                                                            {it.permalink && <a href={it.permalink} target="_blank" rel="noreferrer" className="text-slate-500 hover:text-sky-400"><ExternalLink size={12} /></a>}
                                                        </div>
                                                        <div className="text-[11px] text-slate-500 font-mono">{it.sku || it.ad_id}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-3 py-3 text-right font-mono text-emerald-400">{fmtInt(it.available_qty)}</td>
                                            <td className="px-3 py-3 text-right font-mono text-sky-400/90">{it.in_transit_qty > 0 ? fmtInt(it.in_transit_qty) : '—'}</td>
                                            <td className="px-3 py-3 text-right font-mono text-slate-400">{it.not_available_qty > 0 ? fmtInt(it.not_available_qty) : '—'}</td>
                                            <td className={`px-3 py-3 text-right font-mono ${coverageColor(it.days_of_stock)}`}>
                                                {it.days_of_stock != null ? `${it.days_of_stock.toFixed(0)}d` : '—'}
                                            </td>
                                            <td className={`px-3 py-3 text-right font-mono ${agedColor(it.oldest_stock_days)}`}>
                                                {it.oldest_stock_days != null ? `${it.oldest_stock_days}d` : '—'}
                                            </td>
                                            <td className="px-4 py-3 text-right font-mono text-slate-200">
                                                {fmtBRL(it.storage_cost_unit)}
                                                {it.storage_risk_unit ? <span className="text-red-400/80 text-[11px] ml-1">+{fmtBRL(it.storage_risk_unit)}</span> : null}
                                            </td>
                                        </tr>
                                    ))}
                                    {items.length === 0 && (
                                        <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500">Nenhum item no filtro atual.</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

function Card({ icon, label, value, sub, valueClass = 'text-white' }: {
    icon: React.ReactNode; label: string; value: string; sub?: string; valueClass?: string;
}) {
    return (
        <div className="bg-[#121217] border border-white/5 rounded-2xl p-5">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center gap-1.5 mb-2">{icon} {label}</div>
            <div className={`text-2xl font-black font-mono ${valueClass}`}>{value}</div>
            {sub && <div className="text-[11px] text-slate-500 mt-1">{sub}</div>}
        </div>
    );
}

function AlertChip({ active, icon, count, label, tone }: {
    active: boolean; icon: React.ReactNode; count: number; label: string; tone: 'red' | 'amber' | 'slate';
}) {
    const tones: Record<string, string> = {
        red: active ? 'bg-red-500/10 border-red-500/20 text-red-300' : 'bg-[#121217] border-white/5 text-slate-500',
        amber: active ? 'bg-amber-500/10 border-amber-500/20 text-amber-300' : 'bg-[#121217] border-white/5 text-slate-500',
        slate: active ? 'bg-slate-500/10 border-slate-400/20 text-slate-300' : 'bg-[#121217] border-white/5 text-slate-500',
    };
    return (
        <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-xs font-semibold ${tones[tone]}`}>
            {icon} <span className="font-mono text-sm">{count}</span> {label}
        </div>
    );
}

function TariffsPanel({ tariffs, onChange }: { tariffs: Tariff[]; onChange: () => void }) {
    const empty = { name: '', min_volume_l: '', max_volume_l: '', daily_fee: '', inbound_fee: '', aged_days_threshold: '90', aged_daily_factor: '3' };
    const [form, setForm] = useState<Record<string, string>>(empty);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [saving, setSaving] = useState(false);
    const [err, setErr] = useState<string | null>(null);

    const save = async () => {
        setSaving(true); setErr(null);
        try {
            const payload = {
                name: form.name || null,
                min_volume_l: parseFloat(form.min_volume_l || '0'),
                max_volume_l: form.max_volume_l === '' ? null : parseFloat(form.max_volume_l),
                daily_fee: parseFloat(form.daily_fee || '0'),
                inbound_fee: parseFloat(form.inbound_fee || '0'),
                aged_days_threshold: parseInt(form.aged_days_threshold || '90'),
                aged_daily_factor: parseFloat(form.aged_daily_factor || '3'),
            };
            if (editingId == null) await api.post('/full/tariffs', payload);
            else await api.put(`/full/tariffs/${editingId}`, payload);
            setForm(empty);
            setEditingId(null);
            onChange();
        } catch (e: any) {
            setErr(e?.response?.data?.error || 'Erro ao salvar tarifa.');
        } finally { setSaving(false); }
    };

    const del = async (id: number) => {
        if (!confirm('Remover esta faixa de tarifa?')) return;
        await api.delete(`/full/tariffs/${id}`);
        onChange();
    };

    const edit = (t: Tariff) => {
        setEditingId(t.id);
        setErr(null);
        setForm({
            name: t.name || '', min_volume_l: String(t.min_volume_l),
            max_volume_l: t.max_volume_l == null ? '' : String(t.max_volume_l),
            daily_fee: String(t.daily_fee ?? 0), inbound_fee: String(t.inbound_fee ?? 0),
            aged_days_threshold: String(t.aged_days_threshold), aged_daily_factor: String(t.aged_daily_factor),
        });
    };

    const cancelEdit = () => { setEditingId(null); setForm(empty); setErr(null); };

    const field = (k: string, ph: string, w = 'w-24') => (
        <input value={form[k]} onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))}
            placeholder={ph} className={`${w} bg-slate-900 border border-white/10 rounded px-2 py-1.5 text-xs text-slate-200 placeholder:text-slate-600`} />
    );

    return (
        <div className="bg-[#121217] border border-white/5 rounded-2xl p-5 space-y-4">
            <div className="text-sm font-bold text-white flex items-center gap-2"><Settings2 size={15} /> Tabela de tarifas do Full</div>
            <p className="text-xs text-slate-500">
                Faixas por volume (litros = C×L×A em mm ÷ 1.000.000). <b>Diária</b> = R$/unidade/dia de armazenagem; <b>Inbound</b> = R$/un de envio ao CD;
                a sobretaxa de <b>estoque antigo</b> aplica a diária × fator após o limiar de dias.
            </p>

            {tariffs.length > 0 && (
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead><tr className="text-[10px] uppercase tracking-widest text-slate-500 border-b border-white/5">
                            <th className="text-left py-2 px-2">Faixa</th><th className="text-right px-2">Vol. min (L)</th><th className="text-right px-2">Vol. máx (L)</th>
                            <th className="text-right px-2">Diária</th><th className="text-right px-2">Inbound</th><th className="text-right px-2">Antigo</th><th></th>
                        </tr></thead>
                        <tbody>
                            {tariffs.map(t => (
                                <tr key={t.id} className={`border-b border-white/5 ${t.active ? '' : 'opacity-40'}`}>
                                    <td className="py-2 px-2 text-slate-300">{t.name || `#${t.id}`}</td>
                                    <td className="text-right px-2 font-mono">{t.min_volume_l}</td>
                                    <td className="text-right px-2 font-mono">{t.max_volume_l ?? '∞'}</td>
                                    <td className="text-right px-2 font-mono">{fmtBRL(t.daily_fee)}</td>
                                    <td className="text-right px-2 font-mono">{fmtBRL(t.inbound_fee)}</td>
                                    <td className="text-right px-2 font-mono text-slate-400">&gt;{t.aged_days_threshold}d ×{t.aged_daily_factor}</td>
                                    <td className="text-right px-2 whitespace-nowrap">
                                        <button onClick={() => edit(t)} className="text-slate-500 hover:text-sky-400 mr-2" aria-label={`Editar ${t.name || `tarifa ${t.id}`}`}><Pencil size={14} /></button>
                                        <button onClick={() => del(t.id)} className="text-slate-500 hover:text-red-400" aria-label={`Remover ${t.name || `tarifa ${t.id}`}`}><Trash2 size={14} /></button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <div className="flex flex-wrap items-end gap-2 pt-2 border-t border-white/5">
                {field('name', 'Nome', 'w-28')}
                {field('min_volume_l', 'Vol min')}
                {field('max_volume_l', 'Vol máx')}
                {field('daily_fee', 'Diária R$')}
                {field('inbound_fee', 'Inbound R$')}
                {field('aged_days_threshold', 'Antigo d', 'w-20')}
                {field('aged_daily_factor', 'Fator', 'w-16')}
                <button onClick={save} disabled={saving}
                    className="px-3 py-1.5 rounded-lg text-xs font-bold bg-sky-500 hover:bg-sky-400 text-white flex items-center gap-1.5 disabled:opacity-60">
                    {saving ? <Loader2 size={13} className="animate-spin" /> : editingId == null ? <Plus size={13} /> : <Pencil size={13} />} {editingId == null ? 'Adicionar' : 'Salvar'}
                </button>
                {editingId != null && <button onClick={cancelEdit} className="px-3 py-1.5 rounded-lg text-xs font-bold border border-white/10 text-slate-300 hover:text-white flex items-center gap-1.5"><X size={13} /> Cancelar</button>}
            </div>
            {err && <div className="text-xs text-red-400">{err}</div>}
        </div>
    );
}
