
"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { RefreshCw, User, LogOut, Settings, ChevronDown } from "lucide-react";
import { toast } from "sonner";

export function Header({ isCollapsed }: { isCollapsed: boolean }) {
    const router = useRouter();
    const [isSyncing, setIsSyncing] = useState(false);
    const [lastSync, setLastSync] = useState<string | null>(null);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [user, setUser] = useState<{ name?: string; email?: string; role?: string } | null>(null);
    const menuRef = useRef<HTMLDivElement>(null);

    // Load user from localStorage
    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (userData) {
            try {
                setUser(JSON.parse(userData));
            } catch (e) {
                console.error("Error parsing user data:", e);
            }
        }
    }, []);

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setUserMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Poll sync status to keep spinner alive if backend is working
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await api.get("/sync/status");
                const mlSyncing = res.data?.ml?.syncing;
                const tinySyncing = res.data?.tiny?.syncing;
                const syncing = mlSyncing || tinySyncing;

                setIsSyncing(syncing);

                // Update last sync text from ML as reference
                if (res.data?.ml?.last_sync) {
                    setLastSync(new Date(res.data.ml.last_sync).toLocaleString('pt-BR'));
                }
            } catch (error) {
                console.error("Erro ao verificar status de sync:", error);
            }
        };

        // Check immediately
        checkStatus();

        // Poll every 3s
        const interval = setInterval(checkStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    async function handleSync() {
        // Optimistic UI update
        setIsSyncing(true);
        const toastId = toast.loading("Iniciando sincronização global...", {
            description: "Mercado Livre e Tiny ERP."
        });

        try {
            // Trigger BOTH syncs parallelly
            await Promise.allSettled([
                api.post("/jobs/trigger-sync"), // ML
                api.post("/sync/tiny")          // Tiny
            ]);

            toast.success("Comandos de sincronização enviados!", {
                id: toastId,
                description: "O processamento continuará em segundo plano."
            });

        } catch (error) {
            console.error(error);
            toast.error("Erro ao disparar sincronização", {
                id: toastId
            });
            setIsSyncing(false);
        }
    }

    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        toast.success("Logout realizado com sucesso!");
        router.push('/login');
    }

    // Get user initials for avatar
    const getUserInitials = () => {
        if (user?.name) {
            return user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
        }
        if (user?.email) {
            return user.email.slice(0, 2).toUpperCase();
        }
        return 'U';
    };

    return (
        <header
            className={`h-[64px] bg-[#1A1A2E] border-b border-[#2D2D3A] flex items-center justify-between px-8 text-white z-40 fixed top-0 right-0 shadow-sm transition-all duration-300 ${isCollapsed ? 'left-[80px]' : 'left-[260px]'}`}
        >
            <div>
                <h1 className="text-xl font-bold tracking-tight">HyPerform</h1>
            </div>

            <div className="flex items-center gap-4">
                {lastSync && (
                    <span className="text-xs text-blue-200 hidden md:block">
                        Última sincronização: {lastSync}
                    </span>
                )}

                <button
                    onClick={handleSync}
                    disabled={isSyncing}
                    className={`flex items-center gap-2 px-4 py-1 text-white text-xs font-bold rounded-lg transition-all shadow-md active:scale-95 cursor-pointer 
                        ${isSyncing
                            ? "bg-emerald-500/50 cursor-not-allowed opacity-80"
                            : "bg-emerald-500 hover:bg-emerald-600 hover:shadow-[0_0_15px_rgba(16,185,129,0.5)]"
                        }`}
                >
                    <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? "animate-spin" : ""}`} />
                    {isSyncing ? "Sincronizando..." : "Sincronizar Agora"}
                </button>

                {/* User Menu */}
                <div className="relative" ref={menuRef}>
                    <button
                        onClick={() => setUserMenuOpen(!userMenuOpen)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 transition-all cursor-pointer"
                    >
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shadow-md">
                            {getUserInitials()}
                        </div>
                        <span className="text-sm text-slate-300 hidden md:block max-w-[120px] truncate">
                            {user?.name || user?.email?.split('@')[0] || 'Usuário'}
                        </span>
                        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown Menu */}
                    {userMenuOpen && (
                        <div className="absolute right-0 top-full mt-2 w-56 bg-[#1a1c2e] border border-slate-700/50 rounded-xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
                            {/* User Info */}
                            <div className="px-4 py-3 border-b border-slate-800/50 bg-slate-900/30">
                                <p className="text-sm font-medium text-white truncate">{user?.name || 'Usuário'}</p>
                                <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                                <span className="inline-block mt-1 px-2 py-0.5 text-[10px] font-bold rounded-full bg-indigo-500/20 text-indigo-400 uppercase">
                                    {user?.role || 'admin'}
                                </span>
                            </div>

                            {/* Menu Items */}
                            <div className="py-1">
                                <button
                                    onClick={() => { router.push('/settings/profile'); setUserMenuOpen(false); }}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors cursor-pointer"
                                >
                                    <User className="w-4 h-4" />
                                    Meu Perfil
                                </button>
                                <button
                                    onClick={() => { router.push('/settings'); setUserMenuOpen(false); }}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors cursor-pointer"
                                >
                                    <Settings className="w-4 h-4" />
                                    Configurações
                                </button>
                            </div>

                            {/* Logout */}
                            <div className="border-t border-slate-800/50 py-1">
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-colors cursor-pointer"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sair
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}

