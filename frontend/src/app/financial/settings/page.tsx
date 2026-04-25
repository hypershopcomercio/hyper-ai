"use client";

import { FixedCostsManager } from "@/components/financial/FixedCostsManager";
import { Wallet } from "lucide-react";

export default function FinancialSettingsPage() {
    return (
        <div className="p-8 max-w-7xl mx-auto">
            <div className="flex items-center gap-4 mb-8">
                <div className="bg-blue-600/20 p-3 rounded-xl border border-blue-500/30">
                    <Wallet size={32} className="text-blue-400" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Configurações Financeiras</h1>
                    <p className="text-slate-400">Gerencie seus custos fixos para cálculo preciso de ponto de equilíbrio.</p>
                </div>
            </div>

            <FixedCostsManager />
        </div>
    );
}
