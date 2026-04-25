'use client';

import { useState, useEffect } from 'react';

export function DigitalClock() {
    const [mounted, setMounted] = useState(false);
    const [time, setTime] = useState('');

    useEffect(() => {
        setMounted(true);

        const updateTime = () => {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            setTime(`${hours}:${minutes}:${seconds}`);
        };

        updateTime(); // Set initial time
        const interval = setInterval(updateTime, 1000);

        return () => clearInterval(interval);
    }, []);

    // Don't render anything on server or before mount
    if (!mounted) return null;

    const [hm, sec] = [time.slice(0, 5), time.slice(6)];

    return (
        <div className="font-mono text-4xl font-light tracking-widest tabular-nums">
            <span className="text-emerald-400">{hm}</span>
            <span className="text-emerald-400/50 animate-pulse">:</span>
            <span className="text-emerald-400 text-2xl align-middle">{sec}</span>
        </div>
    );
}
