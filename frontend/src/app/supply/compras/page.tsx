"use client";
import { PremiumLoader } from "@/components/ui/PremiumLoader";
import { useState, useEffect } from "react";

export default function PurchasesPage() {
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Simulate loading for now since it's in development
        const timer = setTimeout(() => {
            setLoading(false);
        }, 4000);
        return () => clearTimeout(timer);
    }, []);

    if (loading) return <PremiumLoader />;

    return (
        <div className="p-8 text-center text-slate-500 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300 ease-out fill-mode-both">
            <h1 className="text-2xl font-bold text-white mb-2">Gestão de Compras</h1>
            <p>Módulo em desenvolvimento...</p>
        </div>
    )
}
