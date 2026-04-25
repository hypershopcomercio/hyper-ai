"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Settings, DollarSign, Package, Brain, Link2, Building2, Tag, Users, FileText, Save, RefreshCw, Check } from 'lucide-react';
import { PremiumLoader } from '@/components/ui/PremiumLoader';

type SettingsTab = 'financeiro' | 'estoque' | 'hyper_ai' | 'integracoes' | 'geral';

interface SettingsData {
    [key: string]: any;
}

export default function ConfiguracoesPage() {
    const [activeTab, setActiveTab] = useState<SettingsTab>('financeiro');
    const [settings, setSettings] = useState<Record<string, SettingsData>>({});
    const [factors, setFactors] = useState<Record<string, boolean>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);

    const tabs = [
        { key: 'financeiro' as SettingsTab, label: 'Financeiro', icon: DollarSign, priority: 'Alta' },
        { key: 'estoque' as SettingsTab, label: 'Estoque', icon: Package, priority: 'Média' },
        { key: 'hyper_ai' as SettingsTab, label: 'Hyper AI', icon: Brain, priority: 'Média' },
        { key: 'integracoes' as SettingsTab, label: 'Integrações', icon: Link2, priority: 'Alta' },
        { key: 'geral' as SettingsTab, label: 'Geral', icon: Building2, priority: 'Baixa' },
    ];

    const fetchSettings = async () => {
        setIsLoading(true);
        try {
            const [settingsRes, factorsRes] = await Promise.all([
                api.get('/settings'),
                api.get('/factors')
            ]);
            setSettings(settingsRes.data.data || {});

            // Extract enabled states from factors  
            const factorData = factorsRes.data.data || {};
            const factorStates: Record<string, boolean> = {};
            Object.keys(factorData).forEach(key => {
                factorStates[key] = !!factorData[key]?.enabled;
            });
            setFactors(factorStates);
        } catch (error) {
            console.error('Error fetching settings:', error);
        } finally {
            // Enforce minimum 4000ms loader
            if (activeTab === 'financeiro' && isLoading) { // Initial load check roughly
                setTimeout(() => setIsLoading(false), 4000);
            } else {
                setIsLoading(false);
            }
        }
    };

    useEffect(() => {
        fetchSettings();
    }, []);

    const updateSetting = (group: string, key: string, value: any) => {
        setSettings(prev => ({
            ...prev,
            [group]: {
                ...prev[group],
                [key]: value
            }
        }));
    };

    const saveSettings = async () => {
        setIsSaving(true);
        setSaveSuccess(false);
        console.log('[DEBUG] Saving settings for tab:', activeTab);
        console.log('[DEBUG] Data being saved:', JSON.stringify(settings[activeTab], null, 2));
        try {
            const response = await api.put(`/settings/${activeTab}`, settings[activeTab]);
            console.log('[DEBUG] Save response:', response.data);
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (error) {
            console.error('[DEBUG] Error saving settings:', error);
            alert('Erro ao salvar: ' + (error as any)?.message);
        } finally {
            // Enforce minimum 4000ms loader
            if (isLoading) {
                setTimeout(() => setIsLoading(false), 4000);
            } else {
                setIsLoading(false);
            }
        }
    };

    const renderInput = (key: string, value: any, type: 'text' | 'number' | 'checkbox' | 'select', options?: string[]) => {
        if (type === 'checkbox') {
            return (
                <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => updateSetting(activeTab, key, e.target.checked)}
                    className="w-5 h-5 rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-cyan-500 cursor-pointer"
                />
            );
        }
        if (type === 'select' && options) {
            return (
                <select
                    value={value}
                    onChange={(e) => updateSetting(activeTab, key, e.target.value)}
                    className="bg-slate-800 border border-slate-600 text-white rounded px-3 py-2 w-full focus:ring-1 focus:ring-cyan-500"
                >
                    {options.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>
            );
        }
        return (
            <input
                type={type}
                value={value || ''}
                onChange={(e) => updateSetting(activeTab, key, e.target.value)}
                className="bg-slate-800 border border-slate-600 text-white rounded px-3 py-2 w-full focus:ring-1 focus:ring-cyan-500"
            />
        );
    };

    const renderFinanceiro = () => {
        const data = settings.financeiro || {};
        return (
            <div className="space-y-6">
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Margens e Metas</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Margem líquida mínima desejada (%)</label>
                            {renderInput('margem_minima', data.margem_minima, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Meta de faturamento mensal (R$)</label>
                            {renderInput('meta_faturamento_mensal', data.meta_faturamento_mensal, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Meta de lucro líquido mensal (R$)</label>
                            {renderInput('meta_lucro_mensal', data.meta_lucro_mensal, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Comissões por Marketplace</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Mercado Livre - Comissão (%)</label>
                            {renderInput('comissao_ml', data.comissao_ml, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Mercado Livre - Taxa Fixa (R$)</label>
                            {renderInput('taxa_fixa_ml', data.taxa_fixa_ml, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Amazon - Comissão (%)</label>
                            {renderInput('comissao_amazon', data.comissao_amazon, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Shopee - Comissão (%)</label>
                            {renderInput('comissao_shopee', data.comissao_shopee, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Configurações de DIFAL</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('calcular_difal', data.calcular_difal, 'checkbox')}
                            <label className="text-slate-300">Calcular DIFAL automaticamente nas vendas interestaduais</label>
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">UF Origem</label>
                            {renderInput('uf_origem', data.uf_origem, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Alíquota Interna (%)</label>
                            {renderInput('aliquota_interna', data.aliquota_interna, 'number')}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderEstoque = () => {
        const data = settings.estoque || {};
        return (
            <div className="space-y-6">
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Alertas de Estoque</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('usar_dias_estoque', data.usar_dias_estoque, 'checkbox')}
                            <label className="text-slate-300">Usar dias de estoque em vez de unidades fixas</label>
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Nível CRÍTICO (vermelho) - dias</label>
                            {renderInput('dias_critico', data.dias_critico, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Nível BAIXO (amarelo) - dias</label>
                            {renderInput('dias_baixo', data.dias_baixo, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Estoque de Segurança</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Multiplicador de segurança (x lead time)</label>
                            {renderInput('multiplicador_seguranca', data.multiplicador_seguranca, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Lead time padrão (dias)</label>
                            {renderInput('lead_time_padrao', data.lead_time_padrao, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Ponto de Pedido</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('calcular_ponto_pedido', data.calcular_ponto_pedido, 'checkbox')}
                            <label className="text-slate-300">Calcular ponto de pedido automaticamente</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('alertar_ponto_pedido', data.alertar_ponto_pedido, 'checkbox')}
                            <label className="text-slate-300">Alertar quando atingir ponto de pedido</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('sugerir_qtd_compra', data.sugerir_qtd_compra, 'checkbox')}
                            <label className="text-slate-300">Sugerir quantidade de compra baseado em previsão</label>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderHyperAI = () => {
        const data = settings.hyper_ai || {};

        // Group multipliers by category
        const multCategories = {
            "Temporais": ["mult_day_of_week", "mult_hourly_pattern", "mult_period_of_month", "mult_payment_day", "mult_week_of_month"],
            "Eventos": ["mult_event", "mult_post_feriado", "mult_seasonal"],
            "Tendência": ["mult_momentum", "mult_visits_trend", "mult_velocity_score"],
            "Conversão/Produto": ["mult_conversion_rate", "mult_top_sellers", "mult_promo_active", "mult_catalog_boost", "mult_listing_health"],
            "Estoque": ["mult_stock_pressure", "mult_shipping_advantage"],
            "Comportamento": ["mult_impulse_hours", "mult_mobile_hours"],
            "Marketplace": ["mult_search_position", "mult_gold_medal", "mult_listing_type", "mult_free_shipping"],
            "Externos": ["mult_weather", "mult_google_trends", "mult_competitor_stockout"]
        };

        const toggleMult = async (key: string) => {
            // Update UI immediately  
            setFactors(prev => ({ ...prev, [key]: !prev[key] }));

            // Call dedicated toggle endpoint
            try {
                const res = await api.post(`/factors/${key}/toggle`);
                if (res.data.success) {
                    setFactors(prev => ({ ...prev, [key]: res.data.enabled }));
                }
            } catch (e) {
                console.error('Erro ao salvar:', e);
                // Revert on error
                setFactors(prev => ({ ...prev, [key]: !prev[key] }));
            }
        };

        return (
            <div className="space-y-6">
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Ciclo de Aprendizado</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('reconciliacao_habilitada', data.reconciliacao_habilitada, 'checkbox')}
                            <label className="text-slate-300">Reconciliação automática habilitada</label>
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Horário da reconciliação</label>
                            {renderInput('reconciliacao_horario', data.reconciliacao_horario, 'text')}
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('calibracao_habilitada', data.calibracao_habilitada, 'checkbox')}
                            <label className="text-slate-300">Calibração automática habilitada</label>
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Ajuste máximo por ciclo (%)</label>
                            {renderInput('ajuste_maximo', data.ajuste_maximo, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">🎯 Fatores de Previsão</h3>
                    <p className="text-slate-500 text-sm mb-4">Clique para ativar/desativar. Salva automaticamente.</p>

                    <div className="space-y-6">
                        {Object.entries(multCategories).map(([category, keys]) => (
                            <div key={category}>
                                <h4 className="text-sm font-medium text-cyan-400 mb-3">{category}</h4>
                                <div className="grid grid-cols-2 gap-2">
                                    {keys.map(key => {
                                        const isEnabled = factors[key] ?? false;
                                        const mult = data[key] || {};
                                        return (
                                            <div
                                                key={key}
                                                onClick={() => toggleMult(key)}
                                                className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all ${isEnabled
                                                    ? 'bg-emerald-500/10 border border-emerald-500/30'
                                                    : 'bg-slate-800/30 border border-slate-700/30 opacity-60'
                                                    }`}
                                            >
                                                <div className={`w-3 h-3 rounded-full ${isEnabled ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                                                <span className="text-sm text-slate-300">{mult.desc || key.replace('mult_', '').replace(/_/g, ' ')}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Limites de Confiança</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Mínimo de amostras para calibrar</label>
                            {renderInput('min_amostras_calibrar', data.min_amostras_calibrar, 'number')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Erro máximo tolerável (%)</label>
                            {renderInput('erro_max_toleravel', data.erro_max_toleravel, 'number')}
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('alertar_erro_alto', data.alertar_erro_alto, 'checkbox')}
                            <label className="text-slate-300">Alertar quando erro for alto</label>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderIntegracoes = () => {
        const data = settings.integracoes || {};
        return (
            <div className="space-y-6">
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                        Mercado Livre
                    </h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('ml_sync_estoque', data.ml_sync_estoque, 'checkbox')}
                            <label className="text-slate-300">Sincronizar estoque automaticamente</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('ml_sync_precos', data.ml_sync_precos, 'checkbox')}
                            <label className="text-slate-300">Sincronizar preços automaticamente</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('ml_importar_pedidos', data.ml_importar_pedidos, 'checkbox')}
                            <label className="text-slate-300">Importar pedidos em tempo real</label>
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Intervalo de sync (minutos)</label>
                            {renderInput('ml_intervalo_sync', data.ml_intervalo_sync, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                        Tiny ERP
                    </h3>
                    <div className="grid gap-4">
                        <div className="flex items-center gap-3">
                            {renderInput('tiny_importar_custos', data.tiny_importar_custos, 'checkbox')}
                            <label className="text-slate-300">Importar custos dos produtos</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('tiny_sync_bidirecional', data.tiny_sync_bidirecional, 'checkbox')}
                            <label className="text-slate-300">Sincronizar estoque bidirecional</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('tiny_criar_produtos_auto', data.tiny_criar_produtos_auto, 'checkbox')}
                            <label className="text-slate-300">Criar produtos automaticamente no Tiny</label>
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-slate-500"></span>
                        API de Clima (OpenWeatherMap)
                    </h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">API Key</label>
                            {renderInput('clima_api_key', data.clima_api_key, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Cidade padrão</label>
                            {renderInput('clima_cidade', data.clima_cidade, 'text')}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderGeral = () => {
        const data = settings.geral || {};
        return (
            <div className="space-y-6">
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Informações da Empresa</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Nome da Empresa</label>
                            {renderInput('empresa_nome', data.empresa_nome, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">CNPJ</label>
                            {renderInput('empresa_cnpj', data.empresa_cnpj, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Estado (UF)</label>
                            {renderInput('empresa_uf', data.empresa_uf, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Alíquota Simples Nacional (%)</label>
                            {renderInput('aliquota_simples', data.aliquota_simples, 'number')}
                        </div>
                    </div>
                </div>

                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Notificações</h3>
                    <div className="grid gap-4">
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">Email para alertas</label>
                            {renderInput('email_alertas', data.email_alertas, 'text')}
                        </div>
                        <div className="flex items-center justify-between">
                            <label className="text-slate-300">WhatsApp (opcional)</label>
                            {renderInput('whatsapp_alertas', data.whatsapp_alertas, 'text')}
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('alerta_estoque_critico', data.alerta_estoque_critico, 'checkbox')}
                            <label className="text-slate-300">Receber alerta de estoque crítico</label>
                        </div>
                        <div className="flex items-center gap-3">
                            {renderInput('alerta_resumo_diario', data.alerta_resumo_diario, 'checkbox')}
                            <label className="text-slate-300">Receber resumo diário de vendas</label>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    if (isLoading) {
        return <PremiumLoader />;
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0d0d14] to-[#0a0a0f] p-6 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300 ease-out fill-mode-both">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-slate-500/20 to-slate-600/20 border border-slate-500/30">
                            <Settings className="w-8 h-8 text-slate-300" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Configurações</h1>
                            <p className="text-slate-400 text-sm">Personalize o comportamento do sistema</p>
                        </div>
                    </div>
                    <button
                        onClick={saveSettings}
                        disabled={isSaving}
                        className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all cursor-pointer ${saveSuccess
                            ? 'bg-emerald-600 text-white'
                            : 'bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-500 hover:to-cyan-600 text-white'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {isSaving ? (
                            <RefreshCw className="w-5 h-5 animate-spin" />
                        ) : saveSuccess ? (
                            <Check className="w-5 h-5" />
                        ) : (
                            <Save className="w-5 h-5" />
                        )}
                        {saveSuccess ? 'Salvo!' : 'Salvar Alterações'}
                    </button>
                </div>

                <div className="flex gap-6">
                    {/* Sidebar Tabs */}
                    <div className="w-64 flex-shrink-0">
                        <nav className="bg-[#12121a] rounded-xl border border-slate-800/50 p-2">
                            {tabs.map(tab => (
                                <button
                                    key={tab.key}
                                    onClick={() => setActiveTab(tab.key)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all cursor-pointer ${activeTab === tab.key
                                        ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/30'
                                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                                        }`}
                                >
                                    <tab.icon className="w-5 h-5" />
                                    <div>
                                        <div className="font-medium">{tab.label}</div>
                                        <div className={`text-xs ${tab.priority === 'Alta' ? 'text-red-400' :
                                            tab.priority === 'Média' ? 'text-yellow-400' :
                                                'text-slate-500'
                                            }`}>
                                            {tab.priority}
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </nav>
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                        {activeTab === 'financeiro' && renderFinanceiro()}
                        {activeTab === 'estoque' && renderEstoque()}
                        {activeTab === 'hyper_ai' && renderHyperAI()}
                        {activeTab === 'integracoes' && renderIntegracoes()}
                        {activeTab === 'geral' && renderGeral()}
                    </div>
                </div>
            </div>
        </div>
    );
}
