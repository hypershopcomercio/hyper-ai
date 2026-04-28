"use client";
import { useState, useEffect, useRef } from "react";
import { CheckCircle2, AlertCircle, ShoppingBag, Database, RefreshCw, Key, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

export default function IntegrationsPage() {
    const [tinyToken, setTinyToken] = useState("");
    const [loading, setLoading] = useState(true);

    const [mlStatus, setMlStatus] = useState<any>(null);
    const [tinyStatus, setTinyStatus] = useState<any>(null);

    // OpenWeather state
    const [weatherApiKey, setWeatherApiKey] = useState("");
    const [weatherCidade, setWeatherCidade] = useState("Votorantim,BR");
    const [savingWeather, setSavingWeather] = useState(false);

    // Google Trends state
    const [trendsKeywords, setTrendsKeywords] = useState("piscina\naquecedor\nventilador");
    const [savingTrends, setSavingTrends] = useState(false);

    // Polling Ref to avoid closure stale state
    const pollingRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        loadStatus();
        return () => {
            if (pollingRef.current) clearTimeout(pollingRef.current);
        };
    }, []);

    useEffect(() => {
        // If syncing, poll more frequently
        if (mlStatus?.syncing || tinyStatus?.syncing) {
            pollingRef.current = setTimeout(loadStatus, 3000);
        } else if (pollingRef.current) {
            // Stop aggressive polling if not syncing, but we might want to poll casually?
            // For now, stop.
            clearTimeout(pollingRef.current);
            pollingRef.current = null;
        }
    }, [mlStatus?.syncing, tinyStatus?.syncing]);

    const loadStatus = async () => {
        try {
            const res = await api.get("/sync/status");
            console.log("Full Status Response:", res.data); // DEBUG
            const ml = res.data.ml;
            const ts = res.data.tiny;
            setMlStatus(ml);
            setTinyStatus(ts);

            if (ts?.has_token && !tinyToken) {
                setTinyToken("••••••••••••••••");
            }

            // Load integration settings
            try {
                const settingsRes = await api.get("/settings/integracoes");
                const settings = settingsRes.data.data || {};
                if (settings.openweather_api_key) {
                    setWeatherApiKey(settings.openweather_api_key);
                }
                if (settings.openweather_cidade) {
                    setWeatherCidade(settings.openweather_cidade);
                }
                if (settings.google_trends_keywords && Array.isArray(settings.google_trends_keywords)) {
                    setTrendsKeywords(settings.google_trends_keywords.join('\n'));
                }
            } catch (e) {
                console.error("Error loading integration settings:", e);
            }

        } catch (error) {
            console.error("Erro ao carregar status:", error);
            // toast.error("Erro ao carregar status das integrações");
        } finally {
            // Enforce minimum 4000ms loader ONLY for initial load
            if (loading) {
                setTimeout(() => setLoading(false), 4000);
            } else {
                setLoading(false);
            }
        }
    };

    const handleConnectTiny = async () => {
        if (!tinyToken || tinyToken === "••••••••••••••••") return toast.info("Token já salvo ou inválido");

        const toastId = toast.loading("Salvando token...");
        try {
            await api.put("/settings/integracoes", {
                "tiny_api_token": tinyToken
            });

            toast.success("Token do Tiny salvo com sucesso!", { id: toastId });
            loadStatus();
        } catch (error) {
            console.error(error);
            toast.error("Erro ao salvar token", { id: toastId });
        }
    }

    const [isSyncingTiny, setIsSyncingTiny] = useState(false);

    const handleSyncTiny = async () => {
        setIsSyncingTiny(true);
        const toastId = toast.loading('Sincronizando Tiny (Estoque/Custos)...');
        try {
            await api.post("/sync/tiny");
            toast.success('Sincronização do Tiny iniciada!', { id: toastId });
            // Immediate reload to catch running state
            setTimeout(loadStatus, 500);
        } catch (error) {
            console.error(error);
            toast.error('Erro ao sincronizar Tiny', { id: toastId });
            setIsSyncingTiny(false); // Only reset on error, otherwise let polling handle it or timeout
        } finally {
            // Safety timeout to reset button if polling doesn't pick it up
            setTimeout(() => setIsSyncingTiny(false), 5000);
        }
    }

    const handleSyncML = async () => {
        const toastId = toast.loading('Iniciando sincronização...');
        try {
            await api.post("/jobs/trigger-sync");
            toast.success('Sincronização ML iniciada!', { id: toastId, description: 'Isso pode levar alguns minutos.' });

            // Immediate reload
            setTimeout(loadStatus, 500);
        } catch (error) {
            console.error(error);
            toast.error('Erro ao iniciar sincronização', { id: toastId });
        }
    }

    const handleSaveWeather = async () => {
        if (!weatherApiKey) {
            toast.error("Digite uma API Key válida");
            return;
        }
        setSavingWeather(true);
        const toastId = toast.loading('Salvando configuração do OpenWeather...');
        try {
            await api.put("/settings/integracoes", {
                openweather_api_key: weatherApiKey,
                openweather_cidade: weatherCidade,
                openweather_enabled: true
            });
            toast.success('OpenWeather configurado com sucesso!', { id: toastId });
        } catch (error) {
            console.error(error);
            toast.error('Erro ao salvar configuração', { id: toastId });
        } finally {
            setSavingWeather(false);
        }
    }

    const handleSaveTrends = async () => {
        setSavingTrends(true);
        const toastId = toast.loading('Salvando Google Trends...');
        try {
            const keywords = trendsKeywords.split('\n').filter(k => k.trim());
            await api.put("/settings/integracoes", {
                google_trends_enabled: true,
                google_trends_keywords: keywords
            });
            toast.success('Google Trends habilitado!', { id: toastId });
        } catch (error) {
            console.error(error);
            toast.error('Erro ao salvar configuração', { id: toastId });
        } finally {
            setSavingTrends(false);
        }
    }

    if (loading) {
        return <PremiumLoader />; // Standard speed
    }

    return (
        <div className="container mx-auto px-6 py-6 max-w-7xl space-y-8">
            <div className="mb-6">
                <h2 className="text-2xl font-bold text-[#1E3A5F] dark:text-white">Integrações marketplace</h2>
                <p className="text-zinc-500 text-sm">Gerencie suas conexões com plataformas de venda e ERPs.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
                {/* Mercado Livre */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full">
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-[#FFE600] p-3 rounded-lg text-black font-bold">ML</div>
                            <div className="flex gap-2">
                                {mlStatus?.syncing && (
                                    <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs font-semibold rounded-full border border-blue-500/20 flex items-center gap-1">
                                        <Loader2 className="w-3 h-3 animate-spin" /> Sincronizando
                                    </span>
                                )}
                                {mlStatus?.connected ? (
                                    <span className="px-2 py-1 bg-[#2ECC71]/10 text-[#2ECC71] text-xs font-semibold rounded-full border border-[#2ECC71]/20 flex items-center gap-1">
                                        <CheckCircle2 className="w-3 h-3" /> Conectado
                                    </span>
                                ) : (
                                    <span className="px-2 py-1 bg-[#E74C3C]/10 text-[#E74C3C] text-xs font-semibold rounded-full border border-[#E74C3C]/20 flex items-center gap-1">
                                        <AlertCircle className="w-3 h-3" /> Desconectado
                                    </span>
                                )}
                            </div>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Mercado Livre</h3>
                        <p className="text-zinc-400 text-sm">Sincronização de anúncios, vendas, visitas e perguntas.</p>

                        <div className="mt-4 text-xs text-zinc-500 space-y-1">
                            <p>Último sync: {mlStatus?.last_sync ? new Date(mlStatus.last_sync).toLocaleString() : 'Nunca'}</p>
                            <p>Anúncios Ativos: {mlStatus?.ads_count || 0}</p>
                            {mlStatus?.seller_id && <p>Seller ID: {mlStatus.seller_id}</p>}
                            <p className={mlStatus?.syncing ? "text-blue-400 animate-pulse" : ""}>
                                Status: {mlStatus?.syncing ? "Sincronizando dados..." : "Aguardando comando"}
                            </p>
                        </div>
                    </div>

                    <div className="flex flex-col gap-3 mt-4">
                        <button
                            onClick={() => { window.location.href = "/api/auth/ml" }}
                            className="w-full h-10 text-black text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap bg-[#FFE600] hover:bg-[#F3CE00] cursor-pointer"
                        >
                            <Key size={14} />
                            {mlStatus?.connected ? 'Re-autenticar Conta' : 'Conectar Mercado Livre'}
                        </button>

                        <button
                            onClick={handleSyncML}
                            disabled={mlStatus?.syncing}
                            className={`w-full h-10 text-white text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap ${mlStatus?.syncing
                                ? 'bg-zinc-700 cursor-not-allowed opacity-70'
                                : 'bg-[#2ECC71] hover:bg-[#27ae60] cursor-pointer'
                                }`}
                        >
                            {mlStatus?.syncing ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                            {mlStatus?.syncing ? 'Rodando...' : 'Sincronizar Tudo'}
                        </button>

                        <button
                            onClick={async () => {
                                const toastId = toast.loading('Atualizando Estoque Full...');
                                try {
                                    await api.post("/sync/stock/ml");
                                    toast.success('Sincronização de Estoque iniciada!', { id: toastId });
                                    setTimeout(loadStatus, 2000);
                                } catch (error) {
                                    console.error(error);
                                    toast.error('Erro ao atualizar estoque', { id: toastId });
                                }
                            }}
                            disabled={mlStatus?.syncing}
                            className={`w-full h-10 text-white text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap ${mlStatus?.syncing
                                ? 'bg-zinc-700 cursor-not-allowed opacity-70'
                                : 'bg-[#1E3A5F] hover:bg-[#2c5282] cursor-pointer'
                                }`}
                            title="Verifica API de estoque (Full) e atualiza quantidades"
                        >
                            {mlStatus?.syncing ? <Loader2 size={14} className="animate-spin" /> : <Database size={14} />}
                            Atualizar Estoque Full
                        </button>
                    </div>
                </div>

                {/* Tiny ERP */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full">
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-blue-600 p-3 rounded-lg text-white font-bold"><Database className="w-6 h-6" /></div>
                            <div className="flex gap-2">
                                {tinyStatus?.syncing && (
                                    <span className="px-2 py-1 bg-blue-500/10 text-blue-400 text-xs font-semibold rounded-full border border-blue-500/20 flex items-center gap-1">
                                        <Loader2 className="w-3 h-3 animate-spin" /> Sincronizando
                                    </span>
                                )}
                                {tinyStatus?.connected || tinyStatus?.has_token ? (
                                    <span className="px-2 py-1 bg-[#2ECC71]/10 text-[#2ECC71] text-xs font-semibold rounded-full border border-[#2ECC71]/20 flex items-center gap-1">
                                        <CheckCircle2 className="w-3 h-3" /> Ativo
                                    </span>
                                ) : (
                                    <span className="px-2 py-1 bg-[#F39C12]/10 text-[#F39C12] text-xs font-semibold rounded-full border border-[#F39C12]/20 flex items-center gap-1">
                                        <AlertCircle className="w-3 h-3" /> Configurar
                                    </span>
                                )}
                            </div>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Tiny ERP</h3>
                        <p className="text-zinc-400 text-sm">Importação de custos, estoque e dados fiscais.</p>

                        <div className="mt-4 space-y-2">
                            <label className="text-xs text-slate-400">Token da API</label>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Token da API"
                                    value={tinyToken}
                                    onChange={e => setTinyToken(e.target.value)}
                                    className="flex-1 bg-[#0D0D14] border border-[#2D2D3A] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-[#1E3A5F]"
                                />
                                <button
                                    onClick={handleConnectTiny}
                                    title="Salvar Token"
                                    disabled={!tinyToken || tinyToken === "••••••••••••••••"}
                                    className="bg-[#1E3A5F] hover:bg-[#2c5282] text-white px-3 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <Key size={16} />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col gap-2 mt-4">
                        {/* Tiny Sync Button */}
                        <button
                            onClick={handleSyncTiny}
                            disabled={(!tinyStatus?.has_token && !tinyToken) || tinyStatus?.syncing || isSyncingTiny}
                            className={`w-full py-2 text-white text-sm font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 ${(!tinyStatus?.has_token && !tinyToken) || tinyStatus?.syncing || isSyncingTiny
                                ? 'bg-zinc-700 text-zinc-500 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-500 cursor-pointer'
                                }`}
                        >
                            {tinyStatus?.syncing || isSyncingTiny ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                            {tinyStatus?.syncing || isSyncingTiny ? 'Sincronizando...' : 'Sincronizar Estoque e Custos'}
                        </button>
                    </div>
                </div>

                {/* OpenWeather API */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full">
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-gradient-to-br from-orange-500 to-yellow-500 p-3 rounded-lg text-white font-bold">🌤️</div>
                            <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-semibold rounded-full border border-purple-500/20">
                                Hyper AI
                            </span>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">OpenWeather</h3>
                        <p className="text-zinc-400 text-sm">Clima influencia vendas. Dias quentes = mais piscinas.</p>

                        <div className="mt-4 space-y-2">
                            <label className="text-xs text-slate-400">API Key (gratuita em openweathermap.org)</label>
                            <input
                                type="text"
                                placeholder="Sua API Key"
                                value={weatherApiKey}
                                onChange={e => setWeatherApiKey(e.target.value)}
                                className="w-full bg-[#0D0D14] border border-[#2D2D3A] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                            />
                            <label className="text-xs text-slate-400 mt-2 block">Cidade (ex: Votorantim,BR)</label>
                            <input
                                type="text"
                                value={weatherCidade}
                                onChange={e => setWeatherCidade(e.target.value)}
                                className="w-full bg-[#0D0D14] border border-[#2D2D3A] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                            />
                        </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                        <button
                            onClick={handleSaveWeather}
                            disabled={savingWeather}
                            className="flex-1 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold rounded-lg cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {savingWeather && <Loader2 className="w-4 h-4 animate-spin" />}
                            Salvar e Testar
                        </button>
                    </div>
                </div>

                {/* Google Trends */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full">
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-gradient-to-br from-blue-500 to-green-500 p-3 rounded-lg text-white font-bold">📈</div>
                            <span className="px-2 py-1 bg-purple-500/10 text-purple-400 text-xs font-semibold rounded-full border border-purple-500/20">
                                Hyper AI
                            </span>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Google Trends</h3>
                        <p className="text-zinc-400 text-sm">Detecta tendências de busca para seus produtos.</p>

                        <div className="mt-4 space-y-2">
                            <label className="text-xs text-slate-400">Palavras-chave (uma por linha)</label>
                            <textarea
                                rows={3}
                                value={trendsKeywords}
                                onChange={e => setTrendsKeywords(e.target.value)}
                                className="w-full bg-[#0D0D14] border border-[#2D2D3A] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 resize-none"
                            />
                            <p className="text-xs text-zinc-500">Não requer API key. Usa pytrends (gratuito).</p>
                        </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                        <button
                            onClick={handleSaveTrends}
                            disabled={savingTrends}
                            className="flex-1 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold rounded-lg cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {savingTrends && <Loader2 className="w-4 h-4 animate-spin" />}
                            Habilitar Trends
                        </button>
                    </div>
                </div>


                {/* Amazon (Disabled) */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full opacity-60 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[#0D0D14]/50 flex items-center justify-center z-10">
                        <span className="px-3 py-1 bg-zinc-800 text-zinc-400 text-xs font-bold rounded-full uppercase tracking-widest">Em breve</span>
                    </div>
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-white p-3 rounded-lg text-black font-bold"><ShoppingBag className="w-6 h-6" /></div>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Amazon</h3>
                        <p className="text-zinc-400 text-sm">Integração completa com Amazon Seller Central.</p>
                    </div>
                    <div className="flex gap-2 mt-4">
                        <button disabled className="flex-1 py-2 bg-zinc-700 text-zinc-400 text-sm font-semibold rounded-lg cursor-not-allowed">
                            Conectar
                        </button>
                    </div>
                </div>

                {/* Shopee (Disabled) */}
                <div className="bg-[#1A1A2E] border border-[#2D2D3A] rounded-xl p-6 flex flex-col justify-between h-full opacity-60 relative overflow-hidden">
                    <div className="absolute inset-0 bg-[#0D0D14]/50 flex items-center justify-center z-10">
                        <span className="px-3 py-1 bg-zinc-800 text-zinc-400 text-xs font-bold rounded-full uppercase tracking-widest">Em breve</span>
                    </div>
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <div className="bg-[#EE4D2D] p-3 rounded-lg text-white font-bold"><ShoppingBag className="w-6 h-6" /></div>
                        </div>
                        <h3 className="text-lg font-bold text-white mb-2">Shopee</h3>
                        <p className="text-zinc-400 text-sm">Sincronização de pedidos e etiquetas Shopee.</p>
                    </div>
                    <div className="flex gap-2 mt-4">
                        <button disabled className="flex-1 py-2 bg-zinc-700 text-zinc-400 text-sm font-semibold rounded-lg cursor-not-allowed">
                            Conectar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
