'use client';

import { useEffect, useRef, useState } from 'react';

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    baseSize: number; // Store original size for scaling
}

export function NeuralBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let particles: Particle[] = [];
        let w = 0;
        let h = 0;

        // Configuration
        // Configuration
        const particleCount = 130;
        const connectionDistance = 160;
        const moveSpeed = 0.8;

        // Mouse State
        let mouse = { x: -1000, y: -1000 };
        const mouseRadius = 250;

        const resize = () => {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
            initParticles();
        };

        const initParticles = () => {
            particles = [];
            for (let i = 0; i < particleCount; i++) {
                // User requested "menores" (smaller) particles
                const s = Math.random() * 1.5 + 0.5; // Range 0.5px to 2.0px
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    vx: (Math.random() - 0.5) * moveSpeed,
                    vy: (Math.random() - 0.5) * moveSpeed,
                    size: s,
                    baseSize: s
                });
            }
        };

        const handleMouseMove = (e: MouseEvent) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };

        const draw = () => {
            ctx.clearRect(0, 0, w, h);

            // 1. Update & Draw Particles
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0 || p.x > w) p.vx *= -1;
                if (p.y < 0 || p.y > h) p.vy *= -1;

                const dxMouse = p.x - mouse.x;
                const dyMouse = p.y - mouse.y;
                const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);

                let isRadiant = false;

                if (distMouse < mouseRadius) {
                    isRadiant = true;
                    // Radiant: ONLY luminous/glow increases, size stays mostly same (maybe tiny bump)
                    // User said: "tamanho não"
                    p.size = p.baseSize * 1.2;
                } else {
                    p.size = p.baseSize;
                }

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);

                if (isRadiant) {
                    // Strong Glow
                    ctx.shadowBlur = 20; // High luminosity
                    ctx.shadowColor = '#fff'; // White core glow for maximum brightness
                    ctx.fillStyle = '#10B981'; // Emerald center
                } else {
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = `rgba(52, 211, 153, 0.6)`;
                }

                ctx.fill();
                ctx.shadowBlur = 0;

                // 2. Connections
                for (let j = 0; j < particles.length; j++) {
                    const p2 = particles[j];
                    if (p === p2) continue;

                    const dx = p.x - p2.x;
                    const dy = p.y - p2.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < connectionDistance) {
                        ctx.beginPath();
                        const opacity = 1 - (dist / connectionDistance);
                        // Thinner lines for high definition
                        ctx.lineWidth = 0.8;
                        ctx.strokeStyle = `rgba(16, 185, 129, ${opacity * 0.35})`; // Slightly more visible alpha for thinner line
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }

                // 3. Mouse Connection
                if (distMouse < mouseRadius) {
                    ctx.beginPath();
                    const alpha = (1 - distMouse / mouseRadius) * 0.8; // Higher opacity for definition
                    ctx.lineWidth = 1.0; // Thinner for quality
                    ctx.strokeStyle = `rgba(52, 211, 153, ${alpha})`;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            });

            animationFrameId = requestAnimationFrame(draw);
        };

        window.addEventListener('resize', resize);
        window.addEventListener('mousemove', handleMouseMove);
        resize();
        draw();

        return () => {
            window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', handleMouseMove);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    const [opacityClass, setOpacityClass] = useState('opacity-0');

    useEffect(() => {
        // Trigger fade-in after mount
        const timer = setTimeout(() => {
            setOpacityClass('opacity-60');
        }, 100);
        return () => clearTimeout(timer);
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className={`absolute inset-0 z-0 transition-opacity duration-2000 ease-in-out pointer-events-none ${opacityClass}`}
        />
    );
}
