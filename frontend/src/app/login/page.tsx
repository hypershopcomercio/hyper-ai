"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Brain, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const res = await api.post('/auth/login', { email, password });

            if (res.data.success) {
                // Save token and user info
                localStorage.setItem('token', res.data.data.token);
                localStorage.setItem('user', JSON.stringify(res.data.data.user));

                // Redirect to dashboard
                router.push('/perform/analytics');
            } else {
                setError(res.data.error || 'Erro ao fazer login');
            }
        } catch (err: any) {
            setError(err.response?.data?.error || 'Erro ao conectar com o servidor');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0d0d14] to-[#0a0a0f] flex items-center justify-center p-4">
            {/* Background effects */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
            </div>

            <div className="relative z-10 w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center mb-4 relative">
                        <img
                            src="/logo-ai.png"
                            alt="HyperAI"
                            className="h-20 w-auto drop-shadow-[0_0_20px_rgba(16,185,129,0.75)]"
                        />
                    </div>
                    <p className="text-slate-400">Sistema de Gestão Inteligente</p>
                </div>

                {/* Login Form */}
                <form onSubmit={handleLogin} className="bg-[#12121a]/80 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-8 shadow-2xl">
                    <h2 className="text-xl font-semibold text-white mb-6 text-center">Acessar Sistema</h2>

                    {error && (
                        <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                            <span className="text-red-400 text-sm">{error}</span>
                        </div>
                    )}

                    <div className="space-y-5">
                        <div>
                            <label className="block text-slate-400 text-sm mb-2">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="seu@email.com"
                                required
                                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-slate-400 text-sm mb-2">Senha</label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    <LogIn className="w-5 h-5" />
                                    Entrar
                                </>
                            )}
                        </button>
                    </div>

                    <div className="mt-6 text-center">
                        <p className="text-slate-500 text-sm">
                            © 2025 HyperShop Comércio
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}
