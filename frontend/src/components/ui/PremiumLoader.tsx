'use client';

import { useEffect, useState } from 'react';
import { NeuralBackground } from './NeuralBackground';

export function PremiumLoader({ onComplete, duration = 4000 }: { onComplete?: () => void, duration?: number }) {
    const [progress, setProgress] = useState(0);
    const [contentVisible, setContentVisible] = useState(true);

    // Loading Phases Logic - SMOOTH LINEAR
    useEffect(() => {
        let animationFrameId: number;
        let startTime: number | null = null;
        const DURATION = duration; // Use prop

        const animate = (timestamp: number) => {
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;
            const nextProgress = Math.min((elapsed / DURATION) * 100, 100);

            setProgress(nextProgress);

            if (nextProgress < 100) {
                animationFrameId = requestAnimationFrame(animate);
            } else {
                // Complete
                setContentVisible(false);
                if (onComplete) {
                    // Wait for fade out
                    setTimeout(onComplete, 800);
                }
            }
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
        };
    }, [onComplete]);

    // Dynamic Text Generator
    const getLoadingText = (pct: number) => {
        if (pct < 25) return "CARREGANDO HYPER CATALOG...";
        if (pct < 50) return "CARREGANDO HYPER SYNC...";
        if (pct < 75) return "CARREGANDO HYPER PERFORM...";
        return "CARREGANDO HYPER SUPPLY...";
    };

    const loadingText = getLoadingText(progress);

    return (
        <div className={`flex flex-col items-center justify-center w-full h-full fixed inset-0 z-[9999] overflow-hidden bg-[#0f1014] transition-opacity duration-800 ease-in-out ${contentVisible ? 'opacity-100' : 'opacity-0'}`}>
            {/* Background Atmosphere - Neural Network Effect */}
            <NeuralBackground />

            {/* Grid Floor Effect (Tron-like) */}
            <div className="absolute bottom-0 w-full h-[50vh] bg-[linear-gradient(to_bottom,transparent,rgba(16,185,129,0.05)_1px,transparent_1px),linear-gradient(to_right,rgba(16,185,129,0.05)_1px,transparent_1px)] bg-[size:40px_40px] [transform:perspective(500px)_rotateX(60deg)] origin-bottom opacity-30"></div>

            {/* Main Content */}
            <div className="relative z-10 flex flex-col items-center">
                {/* Logo Container - Pure, no box, just glow */}
                <div className="relative group mb-0 -ml-5">
                    <div className="relative">
                        <img
                            src="/logo-ai.png"
                            alt="HyperShop"
                            className="h-20 md:h-28 w-auto relative z-10 drop-shadow-[0_0_20px_rgba(16,185,129,0.85)] animate-pulse"
                        />
                    </div>
                </div>

                {/* Loading Bar & Text - Standard overlap */}
                <div className="mt-0 w-40 text-center relative z-20 flex flex-col items-center">
                    {/* Text Glitch Effect Container */}
                    <div className="flex justify-between items-end mb-2 w-full">
                        <span className="text-[10px] font-mono text-emerald-400 animate-pulse tracking-wider">
                            INICIALIZANDO SISTEMA
                        </span>
                        <span className="text-xs font-mono text-emerald-500/80">
                            {Math.round(progress)}%
                        </span>
                    </div>

                    {/* High-tech Progress Bar */}
                    <div className="h-1 w-full bg-slate-800/50 rounded-full overflow-hidden backdrop-blur-sm border border-white/5">
                        <div
                            className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)] relative"
                            style={{ width: `${progress}%` }}
                        >
                            {/* Inner shimmer of the bar */}
                            <div className="absolute inset-0 bg-white/30 w-full animate-[shimmer_1s_infinite]"></div>
                        </div>
                    </div>

                    {/* Status Messages - Centered */}
                    <div className="mt-2 w-full flex justify-center">
                        <span className="text-[10px] text-slate-500 font-mono h-4 whitespace-nowrap">
                            {loadingText}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
