'use client';

import { useEffect, useRef, useState } from 'react';

export function SalesFireworks({ onComplete, productName }: { onComplete: () => void, productName?: string }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        // Play sale sound
        const audio = new Audio('/sale-sound.mp3');
        audio.volume = 0.7;
        audio.play().catch(e => console.log('Audio play failed:', e));

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;


        // --- WARP SPEED EFFECT (No Gravity) ---

        class DataStream {
            x: number;
            y: number;
            z: number; // Depth for 3D feel
            angle: number;
            speed: number;
            length: number;
            color: string;
            thickness: number;

            constructor() {
                this.angle = Math.random() * Math.PI * 2;
                // Start near center
                this.x = canvas!.width / 2 + Math.cos(this.angle) * (Math.random() * 50);
                this.y = canvas!.height / 2 + Math.sin(this.angle) * (Math.random() * 50);
                this.z = Math.random() * 0.5 + 0.1;
                this.speed = Math.random() * 15 + 10;
                this.length = Math.random() * 50 + 20;
                this.color = Math.random() > 0.5 ? '#10b981' : '#06b6d4'; // Emerald/Cyan
                this.thickness = Math.random() * 2 + 1;
            }

            update() {
                // Move radially outward
                this.x += Math.cos(this.angle) * this.speed * this.z;
                this.y += Math.sin(this.angle) * this.speed * this.z;

                // Accelerate (Warp effect)
                this.speed *= 1.05;
                this.length *= 1.05;
            }

            draw(ctx: CanvasRenderingContext2D) {
                ctx.save();
                ctx.strokeStyle = this.color;
                ctx.lineWidth = this.thickness * this.z;
                ctx.lineCap = 'round';
                ctx.globalAlpha = Math.min(1, this.speed / 50); // Fade in as they speed up

                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                // Draw tail
                const tailX = this.x - Math.cos(this.angle) * this.length;
                const tailY = this.y - Math.sin(this.angle) * this.length;
                ctx.lineTo(tailX, tailY);
                ctx.stroke();
                ctx.restore();
            }
        }

        class HexagonRing {
            radius: number;
            rotation: number;
            rotationSpeed: number;
            color: string;
            alpha: number;

            constructor(reverse: boolean = false) {
                this.radius = 50;
                this.rotation = 0;
                this.rotationSpeed = reverse ? -0.02 : 0.02;
                this.color = '#10b981';
                this.alpha = 0.8;
            }

            update() {
                this.radius += 5; // Expand
                this.rotation += this.rotationSpeed;
                this.alpha -= 0.01;
            }

            draw(ctx: CanvasRenderingContext2D) {
                if (this.alpha <= 0) return;
                ctx.save();
                ctx.translate(canvas!.width / 2, canvas!.height / 2);
                ctx.rotate(this.rotation);
                ctx.globalAlpha = this.alpha;
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 2;

                ctx.beginPath();
                for (let i = 0; i < 6; i++) {
                    const angle = (Math.PI / 3) * i;
                    const x = Math.cos(angle) * this.radius;
                    const y = Math.sin(angle) * this.radius;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                ctx.stroke();
                ctx.restore();
            }
        }

        const streams: DataStream[] = [];
        const rings: HexagonRing[] = [];

        // Initial Burst of Streams
        for (let i = 0; i < 100; i++) {
            streams.push(new DataStream());
        }

        // Add rings periodically
        rings.push(new HexagonRing(false));
        setTimeout(() => rings.push(new HexagonRing(true)), 200);
        setTimeout(() => rings.push(new HexagonRing(false)), 400);

        let animationId: number;
        let frames = 0;

        const animate = () => {
            frames++;
            // Clear with slight trail for motion blur feel
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(0, 0, canvas!.width, canvas!.height);

            // Add new streams occasionally (60 frames for longer effect)
            if (frames < 60 && Math.random() > 0.5) {
                streams.push(new DataStream());
            }

            // Update & Draw Streams
            for (let i = streams.length - 1; i >= 0; i--) {
                const s = streams[i];
                s.update();
                s.draw(ctx);

                // Remove if off screen
                const dist = Math.hypot(s.x - canvas!.width / 2, s.y - canvas!.height / 2);
                if (dist > Math.max(canvas!.width, canvas!.height)) {
                    streams.splice(i, 1);
                }
            }

            // Update & Draw Rings
            for (let i = rings.length - 1; i >= 0; i--) {
                const r = rings[i];
                r.update();
                r.draw(ctx);
                if (r.alpha <= 0) rings.splice(i, 1);
            }

            // Continue or End (max 200 frames = ~3.3s)
            if ((streams.length > 0 || rings.length > 0) && frames < 200) {
                animationId = requestAnimationFrame(animate);
            } else {
                setIsExiting(true);
                setTimeout(() => {
                    if (onComplete) onComplete();
                }, 2500); // 2.5s to read product name
            }
        };

        animate();

        const handleResize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener('resize', handleResize);
        return () => {
            cancelAnimationFrame(animationId);
            window.removeEventListener('resize', handleResize);
        };
    }, [onComplete]);

    return (
        <div className={`fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-[2px] transition-opacity duration-1000 ease-in-out ${isExiting ? 'opacity-0' : 'animate-in fade-in duration-300'}`}>
            <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none mix-blend-screen" />

            {/* V2-style Text Overlay (No Box) */}
            <div className={`relative z-10 flex flex-col items-center justify-center transition-all duration-700 ${isExiting ? 'scale-150 opacity-0' : 'animate-[zoomIn_0.4s_ease-out_forwards]'}`}>
                <h1 className="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-emerald-400 tracking-tighter drop-shadow-[0_0_35px_rgba(16,185,129,0.6)] animate-pulse">
                    NOVA VENDA
                </h1>
                <div className="mt-4 text-emerald-300 text-sm font-bold tracking-[0.5em] uppercase glow-text">
                    Parabéns!
                </div>

                {productName && (
                    <div className="mt-10 relative w-full flex justify-center animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 fill-mode-both">
                        {/* Infinite Beam Background */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-950/40 to-transparent"></div>

                        {/* Holographic Border Lines (Top/Bottom only, fading out) */}
                        <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"></div>
                        <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"></div>

                        <div className="relative px-20 py-2">
                            <span className="text-emerald-200/80 font-light text-sm md:text-base tracking-[0.2em] uppercase drop-shadow-lg text-center whitespace-nowrap">
                                {productName}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
