"use client";

import { useEffect, useMemo, useState } from "react";
import { Calculator, CheckCircle2, PackageSearch, Printer, RefreshCw, Save, Search, Tags, TriangleAlert } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

type PricingProduct = {
    sku: string;
    name: string;
    thumbnail?: string | null;
    stock_available: number;
    calculated_cost: number;
    tax_rate_percent: number;
    target_margin_percent: number;
    selling_price: number;
    suggested_price: number;
    status: string;
    is_manual_price: boolean;
    warnings: string[];
};

const money = (value: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value || 0);

export default function LocalPricingPage() {
    const [products, setProducts] = useState<PricingProduct[]>([]);
    const [margin, setMargin] = useState("10");
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [savingAll, setSavingAll] = useState(false);
    const [edits, setEdits] = useState<Record<string, string>>({});

    const numericMargin = Math.max(0, Number(margin) || 0);
    const loadProducts = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ margin: String(numericMargin) });
            if (search.trim()) params.set("q", search.trim());
            const response = await api.get(`/local/products?${params.toString()}`);
            setProducts(response.data.data || []);
            setEdits({});
        } catch (error) {
            console.error(error);
            toast.error("Não foi possível carregar a tabela de preços.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { void loadProducts(); }, []);

    const displayed = useMemo(() => products, [products]);
    const readyCount = displayed.filter(product => product.status === "ready" && product.selling_price > 0).length;
    const pendingCount = displayed.length - readyCount;

    const applyBulkPricing = async () => {
        if (numericMargin >= 100) {
            toast.error("A margem deve ser menor que 100%.");
            return;
        }
        setSavingAll(true);
        try {
            const response = await api.post("/local/pricing/bulk", {
                target_margin_percent: numericMargin,
                skus: displayed.map(product => product.sku),
            });
            toast.success(`${response.data.updated} preços locais atualizados${response.data.pending ? ` · ${response.data.pending} pendentes` : ""}.`);
            await loadProducts();
        } catch (error: any) {
            toast.error(error?.response?.data?.error || "Não foi possível aplicar a precificação.");
        } finally {
            setSavingAll(false);
        }
    };

    const saveManualPrice = async (product: PricingProduct) => {
        const value = Number(edits[product.sku]);
        if (!value || value <= 0) {
            toast.error("Informe um preço maior que zero.");
            return;
        }
        try {
            await api.put(`/local/pricing/${encodeURIComponent(product.sku)}`, { selling_price: value, target_margin_percent: numericMargin });
            toast.success(`Preço local de ${product.name} salvo.`);
            await loadProducts();
        } catch (error: any) {
            toast.error(error?.response?.data?.error || "Não foi possível salvar o preço.");
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white p-5 md:p-8 print:bg-white print:text-black print:p-0">
            <style jsx global>{`@media print { aside, header, footer, .no-print { display: none !important; } main { margin: 0 !important; background: white !important; } .print-table { font-size: 10px; } .print-table th, .print-table td { color: #111827 !important; border-color: #d1d5db !important; } }`}</style>
            <div className="max-w-7xl mx-auto space-y-6">
                <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between no-print">
                    <div>
                        <p className="text-xs uppercase tracking-[0.22em] text-violet-400 font-semibold">Operação</p>
                        <h1 className="text-3xl font-bold tracking-tight">Precificação Local</h1>
                        <p className="text-sm text-slate-400 mt-1">Tabela independente do Mercado Livre, calculada sobre custo fiscal e alíquota mensal.</p>
                    </div>
                    <button onClick={() => window.print()} className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm hover:bg-white/5 flex items-center justify-center gap-2"><Printer className="w-4 h-4" /> Imprimir tabela</button>
                </header>

                <section className="rounded-2xl border border-violet-500/15 bg-gradient-to-r from-violet-950/25 to-[#111218] p-5 no-print">
                    <div className="grid grid-cols-1 lg:grid-cols-[auto_1fr_auto] gap-4 items-end">
                        <label className="text-xs text-slate-400">Margem desejada (%)<div className="mt-1.5 flex items-center rounded-lg border border-violet-500/30 bg-black/20 px-3"><Calculator className="w-4 h-4 text-violet-300" /><input type="number" min="0" max="99" step="0.1" value={margin} onChange={event => setMargin(event.target.value)} className="w-24 bg-transparent px-2 py-2.5 outline-none text-white" /><button onClick={() => void loadProducts()} className="text-xs text-violet-300 hover:text-violet-100">Simular</button></div></label>
                        <div className="flex flex-col sm:flex-row gap-3"><div className="flex-1 flex items-center rounded-lg border border-slate-700 bg-black/20 px-3"><Search className="w-4 h-4 text-slate-500" /><input value={search} onChange={event => setSearch(event.target.value)} onKeyDown={event => { if (event.key === "Enter") void loadProducts(); }} placeholder="Filtrar por produto ou SKU" className="w-full bg-transparent px-2 py-2.5 text-sm outline-none" /></div></div>
                        <button disabled={savingAll || !displayed.length} onClick={() => void applyBulkPricing()} className="rounded-xl bg-violet-500 px-5 py-3 text-sm font-bold text-white hover:bg-violet-400 disabled:opacity-50 flex items-center justify-center gap-2"><Tags className="w-4 h-4" /> {savingAll ? "Aplicando..." : "Aplicar à tabela"}</button>
                    </div>
                    <p className="mt-3 text-xs text-slate-400">Fórmula: custo final ÷ (1 − margem − DAS). Comissão e frete de marketplace não entram no preço local.</p>
                </section>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 no-print">
                    <div className="rounded-xl border border-white/10 bg-[#111218] p-4"><p className="text-xs text-slate-500">Produtos exibidos</p><p className="mt-1 text-2xl font-bold">{displayed.length}</p></div>
                    <div className="rounded-xl border border-emerald-500/15 bg-emerald-500/5 p-4"><p className="text-xs text-emerald-200/70">Prontos para venda</p><p className="mt-1 text-2xl font-bold text-emerald-300">{readyCount}</p></div>
                    <div className="rounded-xl border border-amber-500/15 bg-amber-500/5 p-4"><p className="text-xs text-amber-200/70">Pendências</p><p className="mt-1 text-2xl font-bold text-amber-300">{pendingCount}</p></div>
                    <div className="rounded-xl border border-white/10 bg-[#111218] p-4"><p className="text-xs text-slate-500">Margem simulada</p><p className="mt-1 text-2xl font-bold text-violet-300">{numericMargin.toLocaleString("pt-BR")}%</p></div>
                </div>

                <section className="overflow-hidden rounded-2xl border border-white/10 bg-[#111218]">
                    <div className="hidden print:block p-5 border-b border-slate-300"><h1 className="text-xl font-bold">Tabela de Preços — Loja Física</h1><p>Margem alvo: {numericMargin}% · Gerada em {new Date().toLocaleDateString("pt-BR")}</p></div>
                    <div className="overflow-x-auto">
                        <table className="w-full min-w-[950px] text-left print-table">
                            <thead className="bg-white/[0.03] text-[11px] uppercase tracking-wider text-slate-500"><tr><th className="px-4 py-3">Produto / SKU</th><th className="px-3 py-3 text-right">Estoque</th><th className="px-3 py-3 text-right">Custo final</th><th className="px-3 py-3 text-right">DAS</th><th className="px-3 py-3 text-right">Margem</th><th className="px-4 py-3 text-right">Preço local</th><th className="px-4 py-3 no-print">Situação</th></tr></thead>
                            <tbody className="divide-y divide-white/5">
                                {displayed.map(product => {
                                    const editableValue = edits[product.sku] ?? String(product.selling_price || product.suggested_price || "");
                                    return <tr key={product.sku} className="hover:bg-white/[0.02]"><td className="px-4 py-3"><div className="flex items-center gap-3"><span className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg border border-white/10 bg-white/5 flex items-center justify-center print:border-slate-300"><PackageSearch className="w-5 h-5 text-slate-500" />{product.thumbnail && <img src={product.thumbnail} alt="" className="absolute inset-0 h-full w-full object-cover" onError={event => { event.currentTarget.style.display = "none"; }} />}</span><span className="min-w-0"><p className="text-sm font-medium">{product.name}</p><p className="mt-0.5 font-mono text-[11px] text-slate-500">{product.sku}</p></span></div></td><td className={`px-3 py-3 text-right font-mono ${product.stock_available <= 0 ? "text-rose-300" : "text-slate-300"}`}>{product.stock_available}</td><td className="px-3 py-3 text-right font-mono text-slate-300">{money(product.calculated_cost)}</td><td className="px-3 py-3 text-right font-mono text-slate-300">{product.tax_rate_percent.toFixed(2)}%</td><td className="px-3 py-3 text-right font-mono text-slate-300">{product.target_margin_percent.toFixed(1)}%</td><td className="px-4 py-3 text-right"><span className="print:inline hidden font-bold">{money(product.selling_price)}</span><div className="no-print flex items-center justify-end gap-2"><span className="font-bold text-cyan-300">{money(product.selling_price)}</span><input value={editableValue} onChange={event => setEdits(current => ({ ...current, [product.sku]: event.target.value }))} className="w-20 rounded border border-slate-700 bg-black/20 px-2 py-1.5 text-xs outline-none focus:border-violet-500" /><button title="Salvar preço manual" onClick={() => void saveManualPrice(product)} className="rounded p-1.5 text-violet-300 hover:bg-violet-500/15"><Save className="w-4 h-4" /></button></div></td><td className="px-4 py-3 no-print">{product.status === "ready" ? <span className="inline-flex items-center gap-1 text-xs text-emerald-300"><CheckCircle2 className="w-3.5 h-3.5" /> {product.is_manual_price ? "Manual" : "Pronto"}</span> : <span title={product.warnings?.join(" ")} className="inline-flex items-center gap-1 text-xs text-amber-300"><TriangleAlert className="w-3.5 h-3.5" /> {product.status === "cost_pending" ? "Sem custo" : "Fiscal pendente"}</span>}</td></tr>;
                                })}
                                {!displayed.length && <tr><td colSpan={7} className="px-4 py-16 text-center text-sm text-slate-500">{loading ? <span className="inline-flex items-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" /> Carregando tabela...</span> : "Nenhum produto encontrado."}</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </div>
    );
}
