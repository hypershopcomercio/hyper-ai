"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";
import { AlertTriangle, BadgeDollarSign, CalendarDays, Landmark, TrendingUp, Wallet } from "lucide-react";
import { Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface PanelData {
    generated_at: string;
    period_days: number;
    margin: {
        revenue: number; contribution: number; ads_spend: number; operating_fixed: number;
        operating_profit: number; net_margin_pct: number | null; coverage_pct: number; status: string;
    };
    cash: {
        projected_inflow: number; projected_outflow: number; operating_fixed_due: number;
        debt_service_due: number; purchase_commitments: number; cash_before_debt: number;
        projected_net_change: number; minimum_accumulated_change: number;
        debt_coverage_ratio: number | null; status: string;
    };
    obligations: { monthly_debt_service: number; debt_items: { id: number; name: string; amount: number; day_of_month: number }[] };
    timeline: { date: string; inflow: number; operating_fixed: number; debt_service: number; purchases: number; accumulated_change: number }[];
    audit: { sources: string[]; warnings: string[] };
}

const money = (value: number) => value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export default function CashflowPanelPage() {
    const [data, setData] = useState<PanelData | null>(null);
    const [days, setDays] = useState(30);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;
        setError("");
        api.get(`/financial/cashflow-panel?days=${days}`)
            .then(response => active && setData(response.data))
            .catch(() => active && setError("Não foi possível carregar o painel financeiro."));
        return () => { active = false; };
    }, [days]);

    if (!data && !error) return <div className="p-8 text-slate-300">Carregando fluxo de caixa...</div>;
    if (error) return <div className="p-8 text-rose-300">{error}</div>;
    if (!data) return null;

    const marginComplete = data.margin.status === "complete";
    const coverageOk = data.cash.status === "covered_in_projection";

    return (
        <main className="min-h-screen bg-[#09090b] text-slate-100 p-6 md:p-8 space-y-6">
            <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-3"><Wallet className="text-emerald-400" /> Margem & Caixa</h1>
                    <p className="text-sm text-slate-400 mt-1">A operação dá margem? O caixa projetado cobre as parcelas e compromissos?</p>
                </div>
                <div className="flex bg-slate-800/60 border border-white/5 rounded-lg p-1 w-fit">
                    {[30, 60, 90].map(value => <button key={value} onClick={() => setDays(value)} className={`px-4 py-1.5 text-xs font-bold rounded-md ${days === value ? "bg-emerald-500 text-white" : "text-slate-400 hover:text-white"}`}>{value} dias</button>)}
                </div>
            </header>

            <div className="grid gap-6 lg:grid-cols-2">
                <section className="rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.04] p-6">
                    <div className="flex items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-widest text-emerald-300">Mundo 1: operação</p><h2 className="text-lg font-bold mt-1">Margem líquida operacional</h2></div><TrendingUp className="text-emerald-400" /></div>
                    <p className={`font-mono text-4xl font-black mt-6 ${data.margin.net_margin_pct !== null && data.margin.net_margin_pct >= 0 ? "text-emerald-300" : "text-rose-300"}`}>{data.margin.net_margin_pct === null ? "--" : `${data.margin.net_margin_pct.toFixed(1)}%`}</p>
                    <p className="text-xs text-slate-400 mt-2">{marginComplete ? "Base completa dos SKUs vendidos no período." : `Estimativa parcial: ${data.margin.coverage_pct.toFixed(1)}% da receita tem margem vinculada.`}</p>
                    <dl className="mt-6 space-y-3 text-sm border-t border-white/10 pt-4">
                        <Row label="Receita (30d)" value={money(data.margin.revenue)} />
                        <Row label="Contribuição dos SKUs" value={money(data.margin.contribution)} />
                        <Row label="Ads reais (DB)" value={`- ${money(data.margin.ads_spend)}`} negative />
                        <Row label="Fixos operacionais" value={`- ${money(data.margin.operating_fixed)}`} negative />
                        <Row label="Resultado operacional" value={money(data.margin.operating_profit)} strong />
                    </dl>
                </section>

                <section className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.04] p-6">
                    <div className="flex items-start justify-between gap-4"><div><p className="text-xs uppercase tracking-widest text-amber-300">Mundo 2: caixa</p><h2 className="text-lg font-bold mt-1">Cobertura do serviço da dívida</h2></div><Landmark className="text-amber-400" /></div>
                    <p className={`font-mono text-4xl font-black mt-6 ${coverageOk ? "text-emerald-300" : "text-amber-300"}`}>{data.cash.debt_coverage_ratio === null ? "N/C" : `${data.cash.debt_coverage_ratio.toFixed(2)}x`}</p>
                    <p className="text-xs text-slate-400 mt-2">{coverageOk ? "A projeção cobre as parcelas no horizonte selecionado." : data.cash.status === "not_configured" ? "Ainda não há parcelas classificadas para medir cobertura." : "A projeção indica pressão antes de cobrir as parcelas."}</p>
                    <dl className="mt-6 space-y-3 text-sm border-t border-white/10 pt-4">
                        <Row label="Caixa projetado antes da dívida" value={money(data.cash.cash_before_debt)} />
                        <Row label="Parcelas no período" value={`- ${money(data.cash.debt_service_due)}`} negative />
                        <Row label="Compras abertas" value={`- ${money(data.cash.purchase_commitments)}`} negative />
                        <Row label="Variação projetada" value={money(data.cash.projected_net_change)} strong />
                    </dl>
                </section>
            </div>

            <section className="rounded-xl border border-white/10 bg-[#121217] p-4 flex gap-3 text-sm text-slate-300">
                <AlertTriangle className="shrink-0 text-amber-400 mt-0.5" size={18} />
                <p>O painel não confunde margem com caixa: parcelas ficam fora da margem operacional, mas entram no fluxo no vencimento. Como o saldo bancário inicial não está integrado, a linha representa <strong>variação projetada</strong>, não saldo final confirmado.</p>
            </section>

            <section className="rounded-2xl border border-white/5 bg-[#121217] p-6">
                <h2 className="font-bold flex items-center gap-2"><CalendarDays size={18} className="text-blue-400" /> Calendário de caixa projetado</h2>
                <div className="h-[350px] mt-5"><ResponsiveContainer width="100%" height="100%"><ComposedChart data={data.timeline}><CartesianGrid stroke="#ffffff10" vertical={false} /><XAxis dataKey="date" tickFormatter={value => { const [year, month, day] = value.split("-"); return `${day}/${month}`; }} stroke="#64748b" fontSize={10} /><YAxis yAxisId="money" tickFormatter={value => `R$ ${value / 1000}k`} stroke="#64748b" fontSize={10} /><YAxis yAxisId="change" orientation="right" tickFormatter={value => `R$ ${value / 1000}k`} stroke="#64748b" fontSize={10} /><Tooltip contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8 }} formatter={(value: number) => money(value)} /><Bar yAxisId="money" dataKey="inflow" name="Entradas projetadas" fill="#10b981" stackId="out" /><Bar yAxisId="money" dataKey="operating_fixed" name="Fixos operacionais" fill="#64748b" stackId="out" /><Bar yAxisId="money" dataKey="purchases" name="Compras" fill="#f97316" stackId="out" /><Bar yAxisId="money" dataKey="debt_service" name="Parcelas" fill="#f43f5e" stackId="out" /><Line yAxisId="change" type="monotone" dataKey="accumulated_change" name="Variação acumulada" stroke="#60a5fa" strokeWidth={2} dot={false} /></ComposedChart></ResponsiveContainer></div>
            </section>

            <div className="grid gap-6 lg:grid-cols-2">
                <section className="rounded-2xl border border-white/5 bg-[#121217] p-6"><h2 className="font-bold flex gap-2 items-center"><BadgeDollarSign size={18} className="text-amber-400" /> Obrigações classificadas</h2>{data.obligations.debt_items.length ? <div className="mt-4 space-y-3">{data.obligations.debt_items.map(item => <div key={item.id} className="flex justify-between border-b border-white/5 pb-3 text-sm"><span>{item.name}<small className="block text-slate-500">Vencimento: dia {item.day_of_month}</small></span><strong className="font-mono text-amber-300">{money(item.amount)}</strong></div>)}</div> : <p className="text-sm text-slate-400 mt-4">Cadastre as parcelas em <Link href="/financial/settings" className="text-blue-400 underline">Custos Fixos</Link> com a categoria <strong>Serviço da dívida / Parcelas</strong>.</p>}</section>
                <section className="rounded-2xl border border-white/5 bg-[#121217] p-6"><h2 className="font-bold">Auditoria e limites</h2><ul className="mt-4 space-y-2 text-sm text-slate-400">{data.audit.sources.map(source => <li key={source}>• {source}</li>)}{data.audit.warnings.map(warning => <li key={warning} className="text-amber-300">• {warning}</li>)}</ul></section>
            </div>
        </main>
    );
}

function Row({ label, value, negative = false, strong = false }: { label: string; value: string; negative?: boolean; strong?: boolean }) {
    return <div className={`flex justify-between gap-4 ${strong ? "pt-2 border-t border-white/10 font-bold text-white" : "text-slate-300"}`}><dt>{label}</dt><dd className={`font-mono ${negative ? "text-rose-300" : ""}`}>{value}</dd></div>;
}
