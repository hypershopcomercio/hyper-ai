import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';

interface TooltipProps {
    title?: string;
    content: React.ReactNode;
    children: React.ReactNode;
    position?: 'top' | 'bottom' | 'right' | 'left';
}

export const Tooltip: React.FC<TooltipProps> = ({ title, content, children, position = 'top' }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [coords, setCoords] = useState({ top: 0, left: 0 });
    const triggerRef = useRef<HTMLDivElement>(null);

    const updatePosition = () => {
        if (triggerRef.current) {
            const rect = triggerRef.current.getBoundingClientRect();

            let top = 0;
            let left = 0;
            const gap = 6;

            switch (position) {
                case 'top':
                    top = rect.top - gap;
                    left = rect.left + rect.width / 2;
                    break;
                case 'bottom':
                    top = rect.bottom + gap;
                    left = rect.left + rect.width / 2;
                    break;
                case 'left':
                    top = rect.top + rect.height / 2;
                    left = rect.left - gap;
                    break;
                case 'right':
                    top = rect.top + rect.height / 2;
                    left = rect.right + gap;
                    break;
            }

            setCoords({ top, left });
        }
    };

    const handleMouseEnter = () => {
        updatePosition();
        setIsVisible(true);
    };

    const handleMouseLeave = () => {
        setIsVisible(false);
    };

    // Portal Content
    const tooltipContent = isVisible && (
        <div
            className="fixed z-[9999] pointer-events-none"
            style={{
                top: coords.top,
                left: coords.left,
                transform: position === 'top' ? 'translate(-50%, -100%)' :
                    position === 'bottom' ? 'translate(-50%, 0)' :
                        position === 'left' ? 'translate(-100%, -50%)' :
                            'translate(0, -50%)'
            }}
        >
            <div className="bg-[#0e0f14] text-slate-200 text-xs rounded-md border border-slate-600/80 shadow-2xl shadow-black/60 min-w-[280px] animate-in fade-in zoom-in-95 duration-150">
                {title && (
                    <div className="px-3 py-1.5 bg-slate-800/80 border-b border-slate-700/50 flex items-center gap-2">
                        <div className="w-1 h-1 rounded-sm bg-cyan-400" />
                        <span className="font-bold text-white text-[10px] uppercase tracking-wider">{title}</span>
                    </div>
                )}
                <div className="px-3 py-2 leading-relaxed text-slate-300 text-[11px]">
                    {content}
                </div>
            </div>
        </div>
    );

    // Only render portal on client
    const [mounted, setMounted] = useState(false);
    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <>
            <div
                ref={triggerRef}
                className="group/tooltip inline-block"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
            >
                {children}
            </div>
            {mounted && isVisible && createPortal(tooltipContent, document.body)}
        </>
    );
};
