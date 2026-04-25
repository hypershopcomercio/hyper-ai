"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Brain } from 'lucide-react';

export default function HomePage() {
    const router = useRouter();

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('token');

        if (token) {
            // Redirect to dashboard
            router.push('/perform/analytics');
        } else {
            // Redirect to login
            router.push('/login');
        }
    }, [router]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0d0d14] to-[#0a0a0f] flex items-center justify-center">
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
            </div>

            <div className="relative z-10 text-center">
                <div className="inline-flex items-center justify-center p-4 rounded-2xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-purple-500/30 mb-4 animate-pulse">
                    <Brain className="w-12 h-12 text-cyan-400" />
                </div>
                <h1 className="text-2xl font-bold text-white">Carregando...</h1>
            </div>
        </div>
    );
}
