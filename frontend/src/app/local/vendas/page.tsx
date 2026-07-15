"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, History, Minus, PackageSearch, Plus, Search, ShoppingCart, Trash2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

type Product = {
    sku: string;
    name: string;
    stock_available: number;
    selling_price: number;
    status: string;
};

type CartItem = Product & { quantity: number; unit_price: number };

type Sale = {
    id: string;
    customer_name?: string;
    payment_method?: string;
    total_amount: number;
    status: string;
    completed_at?: string;
    items: Array<{ sku: string; product_name: string; quantity: number; line_total: number }>;
};

const money = (value: number) => new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value || 0);

export default function LocalSalesPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [cart, setCart] = useState<CartItem[]>([]);
    const [search, setSearch] = useState("");
    const [customerName, setCustomerName] = useState("");
    const [paymentMethod, setPaymentMethod] = useState("Pix");
    const [discount, setDiscount] = useState("0");
    const [notes, setNotes] = useState("");
    const [loading, setLoading] = useState(true);
    const [finishing, setFinishing] = useState(false);
    const [sales, setSales] = useState<Sale[]>([]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [productsResponse, salesResponse] = await Promise.all([
                api.get("/local/products"),
                api.get("/local/sales?limit=12"),
            ]);
            setProducts(productsResponse.data.data || []);
            setSales(salesResponse.data.data || []);
        } catch (error) {
            console.error(error);
            toast.error("Não foi possível carregar o catálogo local.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { void loadData(); }, []);

    const matches = useMemo(() => {
        const term = search.trim().toLowerCase();
        if (!term) return [];
        return products.filter(product => `${product.sku} ${product.name}`.toLowerCase().includes(term)).slice(0, 8);
    }, [products, search]);

    const subtotal = cart.reduce((total, item) => total + item.quantity * item.unit_price, 0);
    const discountAmount = Math.max(0, Number(discount) || 0);
    const total = Math.max(0, subtotal - discountAmount);

    const addProduct = (product: Product) => {
        if (product.selling_price <= 0) {
            toast.error("Este produto ainda não possui um preço local válido.");
            return;
        }
        setCart(current => {
            const existing = current.find(item => item.sku === product.sku);
            if (existing) {
                if (existing.quantity >= product.stock_available) {
                    toast.error("Quantidade máxima disponível em estoque atingida.");
                    return current;
                }
                return current.map(item => item.sku === product.sku ? { ...item, quantity: item.quantity + 1 } : item);
            }
            if (product.stock_available <= 0) {
                toast.error("Produto sem estoque disponível.");
                return current;
            }
            return [...current, { ...product, quantity: 1, unit_price: product.selling_price }];
        });
        setSearch("");
    };

    const changeQuantity = (sku: string, nextQuantity: number) => {
        setCart(current => current.flatMap(item => {
            if (item.sku !== sku) return [item];
            if (nextQuantity <= 0) return [];
            if (nextQuantity > item.stock_available) {
                toast.error(`Estoque disponível: ${item.stock_available} un.`);
                return [item];
            }
            return [{ ...item, quantity: nextQuantity }];
        }));
    };

    const finishSale = async () => {
        if (!cart.length) {
            toast.error("Adicione produtos ao carrinho antes de finalizar.");
            return;
        }
        if (discountAmount > subtotal) {
            toast.error("O desconto não pode ser maior que o subtotal.");
            return;
        }
        setFinishing(true);
        try {
            const response = await api.post("/local/sales", {
                customer_name: customerName,
                payment_method: paymentMethod,
                discount_amount: discountAmount,
                notes,
                items: cart.map(item => ({ sku: item.sku, quantity: item.quantity, unit_price: item.unit_price })),
            });
            toast.success(`Venda ${response.data.data.id} finalizada: ${money(response.data.data.total_amount)}.`);
            setCart([]);
            setCustomerName("");
            setPaymentMethod("Pix");
            setDiscount("0");
            setNotes("");
            await loadData();
        } catch (error: any) {
            toast.error(error?.response?.data?.error || "Não foi possível finalizar a venda.");
        } finally {
            setFinishing(false);
        }
    };

    const cancelSale = async (sale: Sale) => {
        if (!window.confirm(`Cancelar a venda ${sale.id}? O estoque dos itens será estornado.`)) return;
        try {
            await api.post(`/local/sales/${sale.id}/cancel`);
            toast.success("Venda cancelada e estoque estornado.");
            await loadData();
        } catch (error: any) {
            toast.error(error?.response?.data?.error || "Não foi possível cancelar a venda.");
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white p-5 md:p-8">
            <div className="max-w-7xl mx-auto space-y-6">
                <header className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                    <div>
                        <p className="text-xs uppercase tracking-[0.22em] text-cyan-400 font-semibold">Operação</p>
                        <h1 className="text-3xl font-bold tracking-tight">Venda Local</h1>
                        <p className="text-sm text-slate-400 mt-1">Venda rápida, sem dados obrigatórios, com baixa imediata no estoque do Hyper AI.</p>
                    </div>
                    <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-200">
                        As baixas aguardam integração de escrita com o Tiny.
                    </div>
                </header>

                <div className="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-6">
                    <section className="rounded-2xl border border-white/10 bg-[#111218] p-5 shadow-2xl shadow-black/20">
                        <div className="relative">
                            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Adicionar produto</label>
                            <div className="mt-2 flex items-center gap-3 rounded-xl border border-slate-700 bg-black/20 px-4 py-3 focus-within:border-cyan-500/60">
                                <Search className="w-5 h-5 text-slate-500" />
                                <input
                                    autoFocus
                                    value={search}
                                    onChange={event => setSearch(event.target.value)}
                                    placeholder="Digite nome, SKU ou código de barras"
                                    className="w-full bg-transparent outline-none text-white placeholder:text-slate-600"
                                />
                            </div>
                            {search && (
                                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-xl border border-slate-700 bg-[#181923] shadow-2xl">
                                    {matches.length ? matches.map(product => (
                                        <button key={product.sku} onClick={() => addProduct(product)} className="w-full flex items-center justify-between gap-4 px-4 py-3 text-left hover:bg-cyan-500/10 border-b border-white/5 last:border-0">
                                            <span className="min-w-0"><span className="block text-sm font-medium truncate">{product.name}</span><span className="text-xs text-slate-500">{product.sku} · Estoque {product.stock_available}</span></span>
                                            <span className="font-semibold text-cyan-300 whitespace-nowrap">{money(product.selling_price)}</span>
                                        </button>
                                    )) : <p className="px-4 py-4 text-sm text-slate-400">Nenhum produto encontrado.</p>}
                                </div>
                            )}
                        </div>

                        <div className="mt-7 flex items-center justify-between">
                            <h2 className="font-semibold flex items-center gap-2"><ShoppingCart className="w-5 h-5 text-cyan-400" /> Carrinho</h2>
                            <span className="text-xs text-slate-500">{cart.length} {cart.length === 1 ? "item" : "itens"}</span>
                        </div>
                        <div className="mt-3 divide-y divide-white/5 rounded-xl border border-white/5 bg-black/10">
                            {cart.length ? cart.map(item => (
                                <div key={item.sku} className="p-4 flex gap-3 items-center">
                                    <div className="min-w-0 flex-1">
                                        <p className="text-sm font-medium truncate">{item.name}</p>
                                        <p className="text-xs text-slate-500">{item.sku} · {money(item.unit_price)} un.</p>
                                    </div>
                                    <div className="flex items-center gap-2 rounded-lg bg-white/5 p-1">
                                        <button onClick={() => changeQuantity(item.sku, item.quantity - 1)} className="p-1.5 rounded hover:bg-white/10"><Minus className="w-3.5 h-3.5" /></button>
                                        <span className="w-6 text-center text-sm font-semibold">{item.quantity}</span>
                                        <button onClick={() => changeQuantity(item.sku, item.quantity + 1)} className="p-1.5 rounded hover:bg-white/10"><Plus className="w-3.5 h-3.5" /></button>
                                    </div>
                                    <span className="w-24 text-right text-sm font-semibold">{money(item.quantity * item.unit_price)}</span>
                                    <button onClick={() => changeQuantity(item.sku, 0)} className="p-2 text-slate-500 hover:text-rose-400"><Trash2 className="w-4 h-4" /></button>
                                </div>
                            )) : (
                                <div className="py-14 text-center text-slate-500"><PackageSearch className="w-8 h-8 mx-auto mb-3 opacity-50" /><p className="text-sm">Busque um produto para iniciar a venda.</p></div>
                            )}
                        </div>
                    </section>

                    <section className="rounded-2xl border border-cyan-500/15 bg-gradient-to-b from-cyan-950/20 to-[#111218] p-5">
                        <h2 className="font-semibold">Finalizar venda</h2>
                        <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <label className="text-xs text-slate-400">Cliente (opcional)<input value={customerName} onChange={event => setCustomerName(event.target.value)} placeholder="Nome da pessoa" className="mt-1.5 w-full rounded-lg border border-slate-700 bg-black/20 px-3 py-2.5 text-sm outline-none focus:border-cyan-500" /></label>
                            <label className="text-xs text-slate-400">Pagamento (opcional)<select value={paymentMethod} onChange={event => setPaymentMethod(event.target.value)} className="mt-1.5 w-full rounded-lg border border-slate-700 bg-black/20 px-3 py-2.5 text-sm outline-none focus:border-cyan-500"><option>Pix</option><option>Dinheiro</option><option>Cartão</option><option>Não informado</option></select></label>
                            <label className="text-xs text-slate-400">Desconto total<input type="number" min="0" step="0.01" value={discount} onChange={event => setDiscount(event.target.value)} className="mt-1.5 w-full rounded-lg border border-slate-700 bg-black/20 px-3 py-2.5 text-sm outline-none focus:border-cyan-500" /></label>
                            <label className="text-xs text-slate-400">Observação (opcional)<input value={notes} onChange={event => setNotes(event.target.value)} placeholder="Ex.: retirada balcão" className="mt-1.5 w-full rounded-lg border border-slate-700 bg-black/20 px-3 py-2.5 text-sm outline-none focus:border-cyan-500" /></label>
                        </div>
                        <div className="mt-7 space-y-3 border-t border-white/10 pt-5 text-sm">
                            <div className="flex justify-between text-slate-400"><span>Subtotal</span><span>{money(subtotal)}</span></div>
                            <div className="flex justify-between text-slate-400"><span>Desconto</span><span>- {money(discountAmount)}</span></div>
                            <div className="flex justify-between items-end pt-2"><span className="text-base font-semibold">Total</span><span className="text-3xl font-bold text-cyan-300">{money(total)}</span></div>
                        </div>
                        <button disabled={!cart.length || finishing || loading} onClick={() => void finishSale()} className="mt-6 w-full rounded-xl bg-cyan-500 py-4 text-sm font-bold text-slate-950 hover:bg-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2">
                            <CheckCircle2 className="w-5 h-5" /> {finishing ? "Finalizando..." : "Finalizar e baixar estoque"}
                        </button>
                    </section>
                </div>

                <section className="rounded-2xl border border-white/10 bg-[#111218] p-5">
                    <h2 className="font-semibold flex items-center gap-2"><History className="w-5 h-5 text-slate-400" /> Últimas vendas locais</h2>
                    <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
                        {sales.map(sale => <article key={sale.id} className="rounded-xl border border-white/5 bg-black/10 p-4 flex gap-3 justify-between">
                            <div className="min-w-0"><p className="font-mono text-xs text-cyan-300">{sale.id}</p><p className="text-sm mt-1">{sale.customer_name || "Cliente não informado"} · {sale.payment_method || "Pagamento não informado"}</p><p className="text-xs text-slate-500 mt-1 truncate">{sale.items.map(item => `${item.quantity}× ${item.product_name}`).join(" · ")}</p></div>
                            <div className="text-right shrink-0"><p className="font-semibold">{money(sale.total_amount)}</p><p className="text-xs text-slate-500 mt-1">{sale.completed_at ? new Date(sale.completed_at).toLocaleString("pt-BR") : ""}</p>{sale.status === "completed" ? <button onClick={() => void cancelSale(sale)} className="mt-2 text-xs text-rose-300 hover:text-rose-200 flex items-center gap-1 ml-auto"><XCircle className="w-3.5 h-3.5" /> Cancelar</button> : <span className="mt-2 inline-block text-xs text-slate-500">Cancelada</span>}</div>
                        </article>)}
                        {!sales.length && !loading && <p className="text-sm text-slate-500">Ainda não há vendas locais registradas.</p>}
                    </div>
                </section>
            </div>
        </div>
    );
}
