'use client';

import { useEffect, useState, useRef } from 'react';

interface AnimatedNumberProps {
    value: number;
    duration?: number; // in ms
    formatFn?: (value: number) => string;
    className?: string;
    animationKey?: number; // Change this to force replay animation
}

export function AnimatedNumber({
    value,
    duration = 800,
    formatFn,
    className = '',
    animationKey = 0
}: AnimatedNumberProps) {
    const [displayValue, setDisplayValue] = useState(value);
    const previousValue = useRef(0); // Start from 0 to ensure entrance animation
    const animationRef = useRef<number | null>(null);
    const lastAnimationKey = useRef(animationKey);

    useEffect(() => {
        // Cancel any existing animation
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
        }

        // If animationKey changed, reset previousValue to force animation
        if (animationKey !== lastAnimationKey.current) {
            previousValue.current = 0;
            lastAnimationKey.current = animationKey;
        }

        const startValue = previousValue.current;
        const endValue = value;
        const startTime = performance.now();

        const animate = (currentTime: number) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease-out cubic)
            const easeProgress = 1 - Math.pow(1 - progress, 3);

            const currentValue = startValue + (endValue - startValue) * easeProgress;
            setDisplayValue(currentValue);

            if (progress < 1) {
                animationRef.current = requestAnimationFrame(animate);
            } else {
                previousValue.current = endValue;
            }
        };

        animationRef.current = requestAnimationFrame(animate);

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [value, duration, animationKey]);

    const formatted = formatFn ? formatFn(displayValue) : displayValue.toFixed(0);

    return <span className={className}>{formatted}</span>;
}

// Currency formatted animated number
interface AnimatedCurrencyProps {
    value: number;
    duration?: number;
    className?: string;
}

export function AnimatedCurrency({ value, duration = 800, className = '' }: AnimatedCurrencyProps) {
    return (
        <AnimatedNumber
            value={value}
            duration={duration}
            className={className}
            formatFn={(v) => new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(v)}
        />
    );
}

// Percentage formatted animated number
interface AnimatedPercentProps {
    value: number;
    duration?: number;
    className?: string;
    decimals?: number;
}

export function AnimatedPercent({ value, duration = 800, className = '', decimals = 2 }: AnimatedPercentProps) {
    return (
        <AnimatedNumber
            value={value}
            duration={duration}
            className={className}
            formatFn={(v) => `${v.toFixed(decimals)}%`}
        />
    );
}

// Integer formatted animated number
interface AnimatedIntProps {
    value: number;
    duration?: number;
    className?: string;
    locale?: string;
}

export function AnimatedInt({ value, duration = 800, className = '', locale = 'pt-BR' }: AnimatedIntProps) {
    return (
        <AnimatedNumber
            value={value}
            duration={duration}
            className={className}
            formatFn={(v) => Math.round(v).toLocaleString(locale)}
        />
    );
}
