
import { DashboardMetrics } from "@/types";
import { DollarSign, ShoppingBag, TrendingUp, Eye } from "lucide-react";

interface Props {
    metrics: DashboardMetrics;
}

export function DashboardStats({ metrics }: Props) {
    const cards = [
        {
            label: "Receita Total (Sincronizada)",
            value: `R$ ${metrics.total_revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
            icon: DollarSign,
            color: "text-[#2ECC71]"
        },
        {
            label: "Total de Vendas",
            value: metrics.total_sales,
            icon: ShoppingBag,
            color: "text-[#3498DB]"
        },
        {
            label: "Margem Média",
            value: `${metrics.average_margin.toFixed(1)}%`,
            icon: TrendingUp,
            color: "text-[#F39C12]"
        },
        {
            label: "Total de Visitas",
            value: metrics.total_visits.toLocaleString('pt-BR'),
            icon: Eye,
            color: "text-[#9B59B6]"
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {cards.map((card) => (
                <div key={card.label} className="bg-[#1A1A2E] border border-[#2D2D3A] p-6 rounded-xl flex items-center justify-between">
                    <div>
                        <p className="text-zinc-400 text-xs uppercase tracking-wider font-semibold mb-1">{card.label}</p>
                        <p className="text-2xl font-bold text-white font-mono">{card.value}</p>
                    </div>
                    <div className={`p-3 rounded-lg bg-white/5 ${card.color}`}>
                        <card.icon className="w-6 h-6" />
                    </div>
                </div>
            ))}
        </div>
    );
}
