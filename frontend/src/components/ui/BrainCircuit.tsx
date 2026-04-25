import React from 'react';
import { Brain } from 'lucide-react';

export const BrainCircuit = () => {
    return (
        <div className="relative w-full h-full flex items-center justify-center">
            {/* Background Glow */}
            <div className="absolute inset-0 bg-cyan-500/5 blur-3xl rounded-full" />

            {/* Brain Icon (Static Base) */}
            <div className="relative z-10 text-cyan-400 opacity-20 w-[60%] h-[60%] flex items-center justify-center">
                <Brain className="w-full h-full" strokeWidth={1.5} />
            </div>

            {/* Circuit Overlay */}
            <svg
                className="absolute inset-0 w-full h-full pointer-events-none z-20"
                viewBox="0 0 100 100"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Circuit Path 1: Top Left to Center */}
                <path
                    d="M 10 10 Q 30 10 35 35 L 40 40"
                    stroke="url(#circuit-gradient)"
                    strokeWidth="0.5"
                    strokeOpacity="0.3"
                />
                <circle r="1" fill="#22d3ee">
                    <animateMotion
                        dur="3s"
                        repeatCount="indefinite"
                        path="M 10 10 Q 30 10 35 35 L 40 40"
                        keyPoints="0;1"
                        keyTimes="0;1"
                        calcMode="linear"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="3s"
                        repeatCount="indefinite"
                    />
                </circle>

                {/* Circuit Path 2: Bottom Right to Center */}
                <path
                    d="M 90 90 Q 70 90 65 65 L 60 60"
                    stroke="url(#circuit-gradient)"
                    strokeWidth="0.5"
                    strokeOpacity="0.3"
                />
                <circle r="1" fill="#22d3ee">
                    <animateMotion
                        dur="4s"
                        repeatCount="indefinite"
                        path="M 90 90 Q 70 90 65 65 L 60 60"
                        keyPoints="0;1"
                        keyTimes="0;1"
                        calcMode="linear"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="4s"
                        repeatCount="indefinite"
                    />
                </circle>

                {/* Circuit Path 3: Top Right to Center */}
                <path
                    d="M 90 10 Q 90 30 65 35 L 60 40"
                    stroke="url(#circuit-gradient)"
                    strokeWidth="0.5"
                    strokeOpacity="0.3"
                />
                <circle r="1" fill="#22d3ee">
                    <animateMotion
                        dur="2.5s"
                        repeatCount="indefinite"
                        path="M 90 10 Q 90 30 65 35 L 60 40"
                        keyPoints="0;1"
                        keyTimes="0;1"
                        calcMode="linear"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="2.5s"
                        repeatCount="indefinite"
                    />
                </circle>

                {/* Circuit Path 4: Bottom Left to Center */}
                <path
                    d="M 10 90 Q 10 70 35 65 L 40 60"
                    stroke="url(#circuit-gradient)"
                    strokeWidth="0.5"
                    strokeOpacity="0.3"
                />
                <circle r="1" fill="#22d3ee">
                    <animateMotion
                        dur="3.5s"
                        repeatCount="indefinite"
                        path="M 10 90 Q 10 70 35 65 L 40 60"
                        keyPoints="0;1"
                        keyTimes="0;1"
                        calcMode="linear"
                    />
                    <animate
                        attributeName="opacity"
                        values="0;1;0"
                        dur="3.5s"
                        repeatCount="indefinite"
                    />
                </circle>


                <defs>
                    <linearGradient id="circuit-gradient" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity="0" />
                        <stop offset="50%" stopColor="#22d3ee" stopOpacity="0.5" />
                        <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
                    </linearGradient>
                </defs>
            </svg>
        </div>
    );
};
