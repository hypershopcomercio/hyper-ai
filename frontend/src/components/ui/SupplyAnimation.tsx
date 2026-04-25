"use client";

import React from 'react';

export const SupplyAnimation: React.FC = () => {
    return (
        <svg
            className="w-full h-full text-cyan-400 group-hover:text-cyan-300 transition-colors duration-500"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            {/* Box Icon (Static Base) */}
            <path
                d="M21 8L12 3L3 8V16L12 21L21 16V8Z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            <path
                d="M3 8L12 13L21 8"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
            <path
                d="M12 13V21"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
            />

            {/* Moving "Data/Flow" lines */}
            <circle r="0.8" fill="currentColor">
                <animateMotion
                    dur="3s"
                    repeatCount="indefinite"
                    path="M 12 6 L 12 11"
                    calcMode="linear"
                />
                <animate
                    attributeName="opacity"
                    values="0;1;0"
                    dur="3s"
                    repeatCount="indefinite"
                />
            </circle>

            <circle r="0.8" fill="currentColor">
                <animateMotion
                    dur="2.5s"
                    repeatCount="indefinite"
                    path="M 6 10 L 10 12"
                    calcMode="linear"
                />
                <animate
                    attributeName="opacity"
                    values="0;1;0"
                    dur="2.5s"
                    repeatCount="indefinite"
                />
            </circle>

            <circle r="0.8" fill="currentColor">
                <animateMotion
                    dur="2s"
                    repeatCount="indefinite"
                    path="M 18 10 L 14 12"
                    calcMode="linear"
                />
                <animate
                    attributeName="opacity"
                    values="0;1;0"
                    dur="2s"
                    repeatCount="indefinite"
                />
            </circle>

            {/* Glowing effect points */}
            <circle cx="12" cy="13" r="1.5" fill="currentColor" fillOpacity="0.2">
                <animate
                    attributeName="r"
                    values="1.5;2.5;1.5"
                    dur="2s"
                    repeatCount="indefinite"
                />
            </circle>
        </svg>
    );
};
