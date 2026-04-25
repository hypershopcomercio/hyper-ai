import React from 'react';
import { Package } from 'lucide-react';

export const SupplyCircuit = () => {
    return (
        <div className="relative w-full h-full flex items-center justify-center">
            {/* Background Glow */}
            <div className="absolute inset-0 bg-blue-500/5 blur-2xl rounded-full animate-pulse" />

            {/* Icon Base */}
            <div className="relative z-10 text-cyan-400 group-hover:text-cyan-300 transition-colors w-[65%] h-[65%] flex items-center justify-center">
                <Package className="w-full h-full drop-shadow-[0_0_8px_rgba(34,211,238,0.4)]" strokeWidth={1.5} />
            </div>

            {/* Animated Flow Overlay */}
            <svg
                className="absolute inset-0 w-full h-full pointer-events-none z-20"
                viewBox="0 0 100 100"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Orbital Paths */}
                <circle cx="50" cy="50" r="35" stroke="url(#supply-gradient)" strokeWidth="0.5" strokeDasharray="4 8" className="opacity-20" />

                {/* Moving Particles */}
                <circle r="1" fill="#22d3ee">
                    <animateMotion
                        dur="4s"
                        repeatCount="indefinite"
                        path="M 50,15 A 35,35 0 1,1 49.9,15 Z"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="4s"
                        repeatCount="indefinite"
                    />
                </circle>

                <circle r="1.2" fill="#3b82f6">
                    <animateMotion
                        dur="3s"
                        begin="1s"
                        repeatCount="indefinite"
                        path="M 50,85 A 35,35 0 1,0 50.1,85 Z"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="3s"
                        repeatCount="indefinite"
                    />
                </circle>

                {/* Diagonal Pulse */}
                <path
                    d="M 20 20 L 40 40 M 80 80 L 60 60"
                    stroke="url(#supply-gradient)"
                    strokeWidth="0.5"
                    strokeOpacity="0.4"
                />

                <defs>
                    <linearGradient id="supply-gradient" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
                        <stop offset="50%" stopColor="#3b82f6" stopOpacity="0.8" />
                        <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
                    </linearGradient>
                </defs>
            </svg>
        </div>
    );
};
