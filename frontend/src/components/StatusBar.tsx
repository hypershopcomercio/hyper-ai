
"use client";
import { CheckCircle2, XCircle } from "lucide-react";

export function StatusBar({ isCollapsed }: { isCollapsed: boolean }) {
    // Ideally this comes from health check API
    const isConnected = true;

    return (
        <div className={`h-[40px] bg-[#1A1A2E] border-t border-[#2D2D3A] flex items-center justify-between px-6 text-xs fixed bottom-0 right-0 z-40 text-zinc-400 transition-all duration-300 ${isCollapsed ? 'left-[80px]' : 'left-[260px]'}`}>
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    {isConnected ? (
                        <>
                            <div className="w-2 h-2 rounded-full bg-[#2ECC71] animate-pulse" />
                            <span className="text-zinc-300">ML: Conectado</span>
                        </>
                    ) : (
                        <>
                            <div className="w-2 h-2 rounded-full bg-[#E74C3C]" />
                            <span className="text-[#E74C3C]">ML: Desconectado</span>
                        </>
                    )}
                </div>
            </div>
            <div>
                v1.0.0
            </div>
        </div>
    );
}
