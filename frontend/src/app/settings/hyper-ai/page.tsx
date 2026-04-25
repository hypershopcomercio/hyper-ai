"use client";

import React, { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import {
    Activity, ArrowUpRight, ArrowDownRight, ArrowRight, TrendingUp, TrendingDown, History,
    CheckCircle2, AlertCircle, RefreshCw, Filter,
    Lightbulb, Target, Settings2, BarChart3, CloudRain, Calculator,
    Plus, Lock, Unlock, PlayCircle, Eye, AlertTriangle, Calendar, Info,
    X, Check, Search, Trash2, Sliders, Clock, BrainCircuit, Zap, ArrowUp, ArrowDown, Save,
    ChevronLeft, ChevronRight, ChevronDown, ChevronsLeft, ChevronsRight, ShoppingCart
} from "lucide-react";
import { PremiumLoader } from '@/components/ui/PremiumLoader';
import { ConfirmModal } from '@/components/ui/ConfirmModal';
import { ModernDatePicker } from '@/components/ui/ModernDatePicker';
import { Tooltip } from '@/components/ui/Tooltip';
import { BrainCircuit as BrainHub } from '@/components/ui/BrainCircuit';
import LearningAnalytics from '@/components/hyper-ai/LearningAnalytics';
import { translateFactorType, translateFactorKey, getFactorLabel } from '@/lib/translations';

interface LearningStatus {
    total_predictions_logged: number;
    predictions_reconciled: number;
    pending_reconciliation: number;
    avg_error_7d: number;
    today_summary?: {
        projected: number;
        realized: number;
        accuracy: number;
    };
}

interface LogEntry {
    id: number;
    timestamp_previsao: string;
    hora_alvo: string;
    valor_previsto: number;
    valor_real: number | null;
    erro_percentual: number | null;
    status: 'pending' | 'awaiting' | 'reconciled' | 'high_error';
    baseline: number | null;
    modelo_versao: string;
    fatores_usados: Record<string, any>;
    calibrated?: 'Y' | 'N' | null;
    calibration_impact?: {
        factor_type: string;
        factor_key: string;
        old_value: number;
        new_value: number;
        avg_error?: number;
        samples?: number;
        timestamp?: string;
    }[];
}

interface Insight {
    tipo: 'success' | 'warning' | 'info';
    mensagem: string;
    recomendacao: string;
}

// Sub-component for managing Allowed Factors (REMOVED: logic moved to LearningAnalytics.tsx inline)

export default function HyperAIPage() {
    const [activeTab, setActiveTab] = useState<'dashboard' | 'logs' | 'analysis' | 'multipliers' | 'history'>('dashboard');
    const [status, setStatus] = useState<LearningStatus | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [logsTotal, setLogsTotal] = useState(0);
    const [calibrationStats, setCalibrationStats] = useState<{ calibrated: number; total: number; percentage: number }>({ calibrated: 0, total: 0, percentage: 0 });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [insights, setInsights] = useState<Insight[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null);
    const [isReconciling, setIsReconciling] = useState(false);
    const [isCalibrating, setIsCalibrating] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [actionResult, setActionResult] = useState<string | null>(null);
    const [multipliers, setMultipliers] = useState<Record<string, any>>({});
    const [selectedGenerateDate, setSelectedGenerateDate] = useState<Date | null>(new Date());
    const [confirmAction, setConfirmAction] = useState<{
        open: boolean;
        title: string;
        message: string;
        type: 'danger' | 'warning' | 'info';
        onConfirm: () => void;
    }>({
        open: false,
        title: '',
        message: '',
        type: 'warning',
        onConfirm: () => { }
    });
    const [isLoadingDetail, setIsLoadingDetail] = useState(false);

    // Handlers
    const handleForceRegeneration = async () => {
        if (!selectedGenerateDate) return;
        setIsGenerating(true);
        setActionResult('🔄 Forçando regeneração...');
        try {
            const dateStr = selectedGenerateDate.toISOString().split('T')[0];

            // 1. Generate (Force)
            setActionResult(`🔄 1/3 Regenerando previsões para ${dateStr}...`);
            const res = await api.post('/forecast/learning/generate-for-date', {
                date: dateStr,
                force: true
            });

            if (res.data.success) {
                const generated = res.data.data.predictions_made;

                // 2. Reconcile
                setActionResult(`✅ ${generated} previsões recriadas. 🔄 2/3 Buscando vendas reais para ${dateStr}...`);
                await api.post('/forecast/learning/reconcile', { date: dateStr });

                // 3. Calibrate (Force)
                setActionResult(`✅ Reconciliado. 🔄 3/3 Recalibrando (Forçado) para ${dateStr}...`);
                const resCal = await api.post('/forecast/learning/calibrate', { force: true, date: dateStr });

                if (resCal.data.status === 'success') {
                    const count = resCal.data.adjustments?.length || 0;
                    setActionResult(`✅ Pipeline completo! ⚡ Calibrado com ${count} ajustes.`);
                } else if (resCal.data.status === 'skipped') {
                    const reason = resCal.data.reason === 'insufficient_samples' ? 'Poucas amostras' : resCal.data.reason;
                    setActionResult(`⚠️ Pipeline concluído, mas calibração pulada: ${reason}`);
                } else {
                    setActionResult(`✅ Pipeline completo.`);
                }

                // Force refresh logs
                fetchLogs(1);
                fetchAll();
            } else {
                setActionResult(`❌ ${res.data.error}`);
            }
        } catch (e: any) {
            setActionResult(`❌ ${e.message}`);
        } finally {
            setIsGenerating(false);
            setConfirmAction(prev => ({ ...prev, open: false }));
        }
    };
    const [incompleteDays, setIncompleteDays] = useState<any[]>([]);
    const [isUpdatingIncomplete, setIsUpdatingIncomplete] = useState(false);
    const [isSavingMults, setIsSavingMults] = useState(false);
    const [history, setHistory] = useState<any[]>([]);
    const isMounted = useRef(false);

    // Sorting controls
    const [sortBy, setSortBy] = useState<'hora_alvo' | 'status' | 'erro_percentual' | 'valor_previsto' | 'valor_real'>('hora_alvo');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

    // Date Filters
    const [period, setPeriod] = useState('Hoje');
    const [customDate, setCustomDate] = useState({ start: '', end: '' });
    const [showCustomRange, setShowCustomRange] = useState(false);

    // Product Mix Expansion
    const [expandedProductIndex, setExpandedProductIndex] = useState<number | null>(null);

    // Refresh Control
    const [isRefreshing, setIsRefreshing] = useState(false);

    const getDateRange = () => {
        const today = new Date();
        const end = new Date(today);
        let start = new Date(today);

        if (period === 'Ontem') {
            start.setDate(today.getDate() - 1);
            end.setDate(today.getDate() - 1);
        } else if (period === '7D') {
            start.setDate(today.getDate() - 7);
        } else if (period === '30D') {
            start.setDate(today.getDate() - 30);
        } else if (period === 'Custom' && customDate.start && customDate.end) {
            return {
                start: customDate.start,
                end: customDate.end
            };
        }
        // 'Hoje' is default (start=today, end=today)

        return {
            start: `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-${String(start.getDate()).padStart(2, '0')}`,
            end: `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`
        };
    };

    const fetchStatus = async () => {
        try {
            const { start, end } = getDateRange();
            const res = await api.get(`/forecast/learning/status?start_date=${start}&end_date=${end}`);
            setStatus(res.data.data);
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    };

    const fetchLogs = async (page = 1) => {
        try {
            const { start, end } = getDateRange();
            // Convert to datetime format for proper filtering
            const dateFrom = `${start}T00:00:00`;
            const dateTo = `${end}T23:59:59`;
            const res = await api.get(`/forecast/learning/logs?page=${page}&per_page=15&date_from=${dateFrom}&date_to=${dateTo}&sort_by=${sortBy}&sort_order=${sortOrder}`);
            setLogs(res.data.data.logs || []);
            setLogsTotal(res.data.data.total || 0);
            setTotalPages(res.data.data.total_pages || 1);
            setCurrentPage(page);
            if (res.data.data.calibration_stats) {
                setCalibrationStats(res.data.data.calibration_stats);
            }
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    };

    const fetchLogDetail = async (logId: number) => {
        setIsLoadingDetail(true);
        try {
            const res = await api.get(`/forecast/learning/logs/${logId}`);
            if (res.data.success) {
                // Update selectedLog with full details
                setSelectedLog(prev => {
                    if (!prev) return res.data.data;
                    return {
                        ...res.data.data,
                        baseline: res.data.data.baseline_usado,
                        fatores_usados: res.data.data.fatores_usados || {},
                        // Preserve calibration if missing in detail response
                        calibration_impact: (res.data.data.calibration_impact && res.data.data.calibration_impact.length > 0)
                            ? res.data.data.calibration_impact
                            : (prev.calibration_impact && prev.calibration_impact.length > 0 ? prev.calibration_impact : []),
                        calibrated: (prev.calibrated === 'Y' || (prev.calibration_impact && prev.calibration_impact.length > 0)) ? 'Y' : res.data.data.calibrated
                    };
                });
            }
        } catch (error) {
            console.error('Error fetching log detail:', error);
        } finally {
            setIsLoadingDetail(false);
        }
    };

    // Handler to open log detail modal
    const handleOpenLogDetail = (log: LogEntry) => {
        setSelectedLog(log); // Show immediately with basic data
        fetchLogDetail(log.id); // Then fetch full details including calibration
    };

    const fetchAnalytics = async () => {
        try {
            const { start, end } = getDateRange();
            const res = await api.get(`/forecast/learning/analytics?start_date=${start}&end_date=${end}`);
            setInsights(res.data.data.insights || []);
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    const fetchMultipliers = async () => {
        try {
            const res = await api.get('/factors');
            setMultipliers(res.data.data || {});
        } catch (error) {
            console.error('Error fetching multipliers:', error);
        }
    };

    const fetchHistory = async () => {
        try {
            const { start, end } = getDateRange();
            const res = await api.get(`/history/hyper_ai?start_date=${start}&end_date=${end}`);
            setHistory(res.data.data || []);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    };

    const saveMultipliers = async () => {
        setIsSavingMults(true);
        try {
            // Save each multiplier weight individually
            const promises = Object.entries(multipliers).map(([key, config]) =>
                api.put(`/factors/${key}/weight`, { weight: config.weight })
            );
            await Promise.all(promises);
            setActionResult('Pesos salvos com sucesso!');
        } catch (error) {
            setActionResult('Erro ao salvar pesos');
        } finally {
            setIsSavingMults(false);
        }
    };

    const updateMultiplierWeight = (key: string, weight: number) => {
        setMultipliers((prev: Record<string, any>) => ({
            ...prev,
            [key]: { ...prev[key], weight }
        }));
    };

    const fetchAll = async (showLoader = false) => {
        if (showLoader) {
            setIsLoading(true);
        }

        const tasks: Promise<any>[] = [fetchStatus(), fetchLogs(), fetchAnalytics(), fetchMultipliers(), fetchHistory()];

        if (showLoader) {
            // Enforce minimum 4000ms loader only on initial load
            const minLoadTime = new Promise(resolve => setTimeout(resolve, 4000));
            tasks.push(minLoadTime);
        }

        await Promise.all(tasks);

        setIsLoading(false);
    };

    const handleRefresh = async () => {
        if (isRefreshing) return;
        setIsRefreshing(true);
        try {
            // Smart Refresh: Trigger quick sync and reconciliation ensuring fresh data
            // 1. Sync recent orders (Quick Sync - Last 2h)
            await api.post('/jobs/trigger');

            // 2. Reconcile logs with the newly fetched orders
            await api.post('/forecast/learning/reconcile');

            // 3. Update UI
            await fetchAll(false);
        } catch (e) {
            console.error("Smart refresh failed", e);
            // Fallback to just fetching just in case sync failed
            await fetchAll(false);
        } finally {
            // Small delay to ensure manual refresh feels responsive (optional, but good for UX)
            setTimeout(() => setIsRefreshing(false), 500);
        }
    };

    useEffect(() => {
        // Only auto-fetch for presets. Custom range requires manual "Apply".
        if (period !== 'Custom') {
            if (!isMounted.current) {
                isMounted.current = true;
                fetchAll(true); // Initial load with specific delay
            } else {
                fetchAll(false); // Silent update for filter changes
            }
        }
    }, [period]);

    // Refetch logs when sorting changes
    useEffect(() => {
        if (isMounted.current) {
            fetchLogs(1); // Reset to page 1 when sorting changes
        }
    }, [sortBy, sortOrder]);

    const handleHeaderSort = (key: 'hora_alvo' | 'status' | 'erro_percentual' | 'valor_previsto' | 'valor_real') => {
        if (sortBy === key) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(key);
            setSortOrder('desc');
        }
    };

    const handleReconcile = async () => {
        setIsReconciling(true);
        setActionResult(null);
        try {
            const payload: any = {};
            if (selectedGenerateDate) {
                payload.date = selectedGenerateDate.toISOString().split('T')[0];
            }
            const res = await api.post('/forecast/learning/reconcile', payload);
            setActionResult(`Reconciliação: ${res.data.data.reconciled} logs processados${payload.date ? ` para ${payload.date}` : ''}`);
            fetchAll();
            fetchIncompleteDays();
        } catch (error: any) {
            console.error(error);
            setActionResult(`Erro na reconciliação: ${error.response?.data?.error || error.message}`);
        } finally {
            setIsReconciling(false);
        }
    };

    const handleCalibrate = async () => {
        setIsCalibrating(true);
        setActionResult(null);
        try {
            const payload: any = {};
            if (selectedGenerateDate) {
                payload.date = selectedGenerateDate.toISOString().split('T')[0];
            }
            const res = await api.post('/forecast/learning/calibrate', payload);
            if (res.data.data.status === 'skipped') {
                setActionResult(`Calibração pulada: ${res.data.data.reason}`);
            } else {
                setActionResult(`Calibração: ${res.data.data.adjustments?.length || 0} ajustes${payload.date ? ` para ${payload.date}` : ''}`);
            }
            fetchAll();
        } catch (error: any) {
            console.error(error);
            setActionResult(`Erro na calibração: ${error.response?.data?.error || error.message}`);
        } finally {
            setIsCalibrating(false);
        }
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setActionResult(null);

        try {
            // Use selected date or default to yesterday
            const targetDate = selectedGenerateDate || new Date(Date.now() - 24 * 60 * 60 * 1000);
            const dateStr = targetDate.toISOString().split('T')[0];

            const res = await api.post('/forecast/learning/generate-for-date', { date: dateStr });

            if (res.data.success) {
                setActionResult(`✅ ${res.data.data.message}`);
            } else {
                setActionResult(`❌ Erro: ${res.data.error}`);
            }

            fetchAll();
        } catch (e: any) {
            console.error(e);
            setActionResult(`❌ Erro: ${e.response?.data?.error || e.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const fetchIncompleteDays = async () => {
        setIsUpdatingIncomplete(true);
        try {
            const res = await api.get('/forecast/learning/incomplete-days');
            if (res.data.success) {
                setIncompleteDays(res.data.data.incomplete_days);
            }
        } catch (e) {
            console.error('Error fetching incomplete days:', e);
        } finally {
            setIsUpdatingIncomplete(false);
        }
    };


    const generateForDay = async (date: string) => {
        setIsGenerating(true);
        setActionResult('🔄 Iniciando pipeline completo...');

        try {
            // Step 1: Generate predictions
            setActionResult('🔄 1/3 Gerando previsões...');
            const resGen = await api.post('/forecast/learning/generate-for-date', { date });

            if (!resGen.data.success) {
                setActionResult(`❌ Erro na geração: ${resGen.data.error}`);
                return;
            }

            const generated = resGen.data.data.predictions_made;

            // Step 2: Reconcile (fetch real sales)
            setActionResult(`✅ Geradas ${generated} previsões. 🔄 2/3 Reconciliando...`);
            const resRec = await api.post('/forecast/learning/reconcile');

            // Step 3: Calibrate (adjust multipliers)
            setActionResult(`✅ Reconciliado. 🔄 3/3 Calibrando multiplicadores...`);
            const resCal = await api.post('/forecast/learning/calibrate');

            setActionResult(`✅ Pipeline completo para ${date}! ${generated} previsões → reconciliadas → calibradas`);
            fetchIncompleteDays(); // Refresh the list
            fetchAll();
        } catch (e: any) {
            console.error(e);
            setActionResult(`❌ Erro no pipeline: ${e.response?.data?.error || e.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const generateAllIncomplete = async () => {
        if (incompleteDays.length === 0) return;

        setIsGenerating(true);
        setActionResult('🔄 Gerando previsões para múltiplos dias...');

        let successCount = 0;
        let errorCount = 0;

        for (const day of incompleteDays) {
            try {
                const res = await api.post('/forecast/learning/generate-for-date', { date: day.date });
                if (res.data.success) {
                    successCount++;
                } else {
                    errorCount++;
                }
            } catch (e) {
                errorCount++;
            }
        }

        setActionResult(`✅ Concluído! ${successCount} dias preenchidos${errorCount > 0 ? `, ${errorCount} erros` : ''}`);
        fetchIncompleteDays();
        fetchAll();
        setIsGenerating(false);
    };




    const getStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            pending: 'bg-yellow-500/20 text-yellow-400',
            awaiting: 'bg-blue-500/20 text-blue-400',
            reconciled: 'bg-emerald-500/20 text-emerald-400',
            high_error: 'bg-red-500/20 text-red-400'
        };
        const labels: Record<string, string> = {
            pending: '⏳ Pendente',
            awaiting: '🔄 Aguardando',
            reconciled: '✅ Reconciliado',
            high_error: '⚠️ Erro Alto'
        };
        return <span className={`px-2 py-1 rounded text-xs ${styles[status]}`}>{labels[status]}</span>;
    };

    const formatDate = (d: string | null) => {
        if (!d) return '-';
        return new Date(d).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    };

    const formatCurrency = (v: number | null | undefined) => {
        if (v === null || v === undefined) return '-';
        return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    const getInsightIcon = (tipo: string) => {
        if (tipo === 'success') return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
        if (tipo === 'warning') return <AlertCircle className="w-5 h-5 text-yellow-400" />;
        return <Lightbulb className="w-5 h-5 text-blue-400" />;
    };

    const renderHistoryDetails = (log: any) => {
        if (!log.details) return <span className="text-slate-500">-</span>;

        const details = log.details;
        const action = details.action;

        if (action === 'calibration') {
            return (
                <div className="flex flex-col gap-1 text-xs">
                    <span className="text-cyan-400 font-medium">{details.factor}</span>
                    <div className="flex items-center gap-2">
                        <span className="text-slate-400">{details.old_value?.toFixed(3)} ➜ {details.new_value?.toFixed(3)}</span>
                        <span className={`px-1.5 py-0.5 rounded ${details.change_percent > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {details.change_percent > 0 ? '+' : ''}{details.change_percent}%
                        </span>
                    </div>
                </div>
            );
        }

        if (action === 'reconciliation') {
            return (
                <div className="flex flex-col gap-1 text-xs">
                    <span className="text-white">{details.count} previsões</span>
                    <span className="text-slate-400">Erro médio: {details.avg_abs_error}%</span>
                </div>
            );
        }

        return (
            <pre className="text-[10px] text-slate-500 overflow-hidden text-ellipsis max-w-[200px]">
                {JSON.stringify(details).slice(0, 50)}
            </pre>
        );
    };

    if (isLoading) {
        return <PremiumLoader />;
    }

    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white p-6 pt-20 md:p-10 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300 ease-out fill-mode-both">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-purple-500/30">
                            <div className="w-8 h-8">
                                <BrainHub />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Hyper AI <span className="text-slate-500 font-medium">Status</span></h1>
                            <p className="text-slate-400 text-sm">Centro de Comando do Sistema de Aprendizado</p>
                        </div>
                    </div>
                    <div className="flex gap-2">

                        <button
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                            className={`p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 transition-all ${isRefreshing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-slate-600'}`}
                            title="Atualizar Dados"
                        >
                            <RefreshCw className={`w-5 h-5 text-slate-400 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
                        </button>
                    </div>
                </div>

                {/* Tabs */}
                {/* Tabs & Filters */}
                <div className="flex flex-col lg:flex-row items-end lg:items-center justify-between gap-4 mb-6 border-b border-slate-800/50 pb-2">
                    <div className="flex gap-2 overflow-x-auto w-full lg:w-auto">
                        {[
                            { key: 'dashboard', label: 'Dashboard', icon: BarChart3 },
                            { key: 'logs', label: 'Logs de Previsões', icon: Activity },
                            { key: 'analysis', label: 'Análise', icon: Lightbulb },
                            { key: 'multipliers', label: 'Multiplicadores de Fatores', icon: Sliders },
                            { key: 'history', label: 'Histórico', icon: Clock }
                        ].map(tab => (
                            <button
                                key={tab.key}
                                onClick={() => setActiveTab(tab.key as any)}
                                className={`px-4 py-2 rounded-t-lg flex items-center gap-2 transition-colors whitespace-nowrap cursor-pointer ${activeTab === tab.key
                                    ? 'bg-slate-800 text-white border-b-2 border-cyan-400'
                                    : 'text-slate-400 hover:text-white'
                                    }`}
                            >
                                <tab.icon className="w-4 h-4" />
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Date Filters */}
                    <div className="flex items-center gap-2">
                        {/* Quick Selectors */}
                        <div className="bg-[#1A1A2E] border border-slate-700/50 rounded-lg p-0.5 flex items-center gap-1">
                            {['Hoje', 'Ontem', '7D', '30D'].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => { setPeriod(p); setShowCustomRange(false); }}
                                    className={`px-3 py-1 text-[11px] font-bold rounded-md transition-all cursor-pointer whitespace-nowrap ${period === p
                                        ? 'text-white bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.4)]'
                                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                            <button
                                onClick={() => { setPeriod('Custom'); setShowCustomRange(!showCustomRange); }}
                                className={`px-3 py-1 text-[11px] font-bold rounded-md transition-all cursor-pointer whitespace-nowrap ${period === 'Custom'
                                    ? 'text-white bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.4)]'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                    }`}
                            >
                                Personalizado
                            </button>
                        </div>

                        {/* Custom Range Inputs */}
                        {period === 'Custom' && (
                            <div className="flex items-center gap-2 bg-[#1A1A2E] border border-slate-700/50 rounded-lg p-1 animate-in fade-in slide-in-from-right-4 duration-300">
                                <input
                                    type="date"
                                    className="bg-slate-800 text-white text-xs px-2 py-1 rounded border border-slate-700 outline-none focus:border-cyan-500 transition-colors"
                                    value={customDate.start}
                                    onChange={(e) => setCustomDate(prev => ({ ...prev, start: e.target.value }))}
                                />
                                <span className="text-slate-500 text-xs">até</span>
                                <input
                                    type="date"
                                    className="bg-slate-800 text-white text-xs px-2 py-1 rounded border border-slate-700 outline-none focus:border-cyan-500 transition-colors"
                                    value={customDate.end}
                                    onChange={(e) => setCustomDate(prev => ({ ...prev, end: e.target.value }))}
                                />
                                <button
                                    onClick={() => fetchAll(false)}
                                    className="p-1 rounded bg-cyan-500 hover:bg-cyan-600 text-white transition-colors cursor-pointer"
                                    title="Aplicar Filtro"
                                >
                                    <CheckCircle2 size={12} />
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Dashboard Tab */}
                {activeTab === 'dashboard' && (
                    <>
                        {/* Daily Forecast Summary (New Feature) */}
                        <div className="bg-gradient-to-br from-[#1A1A2E] to-[#12121a] rounded-xl border border-slate-800/60 p-6 mb-6 relative overflow-hidden group">
                            <div className="absolute -top-4 -right-4 w-32 h-32 opacity-30 group-hover:opacity-50 transition-opacity">
                                <BrainCircuit />
                            </div>

                            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2 relative z-10">
                                <Activity className="w-5 h-5 text-cyan-400" />
                                Resumo do Dia: Previsão vs Realizado
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
                                {/* Projected */}
                                <div className="flex flex-col">
                                    <div className="flex items-center gap-1 mb-1">
                                        <span className="text-slate-500 text-xs uppercase font-bold tracking-wider">Total Previsto</span>
                                        <div className="group/item relative flex items-center">
                                            <Info className="w-3 h-3 text-slate-600 cursor-help" />
                                            <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                Soma de todas as previsões geradas pela IA para as 24 horas do dia.
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-3xl font-bold text-cyan-400">
                                        {formatCurrency(status?.today_summary?.projected || 0)}
                                    </div>
                                </div>

                                {/* Realized */}
                                <div className="flex flex-col">
                                    <div className="flex items-center gap-1 mb-1">
                                        <span className="text-slate-500 text-xs uppercase font-bold tracking-wider">Total Realizado</span>
                                        <div className="group/item relative flex items-center">
                                            <Info className="w-3 h-3 text-slate-600 cursor-help" />
                                            <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                Valor total de vendas reais apuradas até o momento (apenas horas reconciliadas).
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-3xl font-bold text-emerald-400">
                                        {formatCurrency(status?.today_summary?.realized || 0)}
                                    </div>
                                </div>

                                {/* Accuracy / Gap */}
                                <div className="flex flex-col justify-center">
                                    <div className="flex justify-between items-end mb-2">
                                        <div className="flex items-center gap-1">
                                            <span className="text-slate-400 text-xs uppercase font-medium">Acuracidade Diária</span>
                                            <span className="group/item relative flex items-center">
                                                <Info className="w-3 h-3 text-slate-600 cursor-help" />
                                                <div className="absolute top-0 right-full mr-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                    Mede o quão próximo o modelo chegou do valor real.
                                                    <br /><span className="text-emerald-400">100% = Perfeito.</span>
                                                </div>
                                            </span>
                                        </div>
                                        <span className="text-xl font-bold text-white">{status?.today_summary?.accuracy || 0}%</span>
                                    </div>
                                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full ${(status?.today_summary?.accuracy || 0) >= 90 ? 'bg-emerald-500' :
                                                (status?.today_summary?.accuracy || 0) >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                                                }`}
                                            style={{ width: `${Math.min(status?.today_summary?.accuracy || 0, 100)}%` }}
                                        />
                                    </div>
                                    <div className="mt-2 text-right">
                                        <span className="text-xs text-slate-500">
                                            Diferença: <span className={(status?.today_summary?.realized || 0) - (status?.today_summary?.projected || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                                                {formatCurrency((status?.today_summary?.realized || 0) - (status?.today_summary?.projected || 0))}
                                            </span>
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Metric Cards (Existing) */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-8">
                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6 cursor-default hover:border-slate-700 transition-colors h-full flex flex-col justify-between">
                                <div className="flex items-center gap-2 mb-3">
                                    <Activity className="w-4 h-4 text-cyan-400" />
                                    <span className="text-slate-500 text-xs uppercase tracking-wider">Previsões Logadas</span>
                                    <div className="group/item relative ml-1">
                                        <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                        <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                            Total de horas com previsões geradas para o dia selecionado.
                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                Meta ideal: 24 horas preenchidas.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-3xl font-bold text-white">{status?.total_predictions_logged || 0}</div>
                            </div>

                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6 cursor-default hover:border-slate-700 transition-colors h-full flex flex-col justify-between">
                                <div className="flex items-center gap-2 mb-3">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                                    <span className="text-slate-500 text-xs uppercase tracking-wider">Reconciliadas</span>
                                    <div className="group/item relative ml-1">
                                        <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                        <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                            Horas que já possuem valor Real de vendas apurado (passado).
                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                Dados consolidados e finais.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-3xl font-bold text-white">{status?.predictions_reconciled || 0}</div>
                            </div>

                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6 cursor-default hover:border-slate-700 transition-colors h-full flex flex-col justify-between">
                                <div className="flex items-center gap-2 mb-3">
                                    <Clock className="w-4 h-4 text-yellow-400" />
                                    <span className="text-slate-500 text-xs uppercase tracking-wider">Pendentes</span>
                                    <div className="group/item relative ml-1">
                                        <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                        <div className="absolute top-0 left-full ml-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                            Horas aguardando fechamento ou valor Real ainda não disponível.
                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                Geralmente refere-se a horas futuras ou atuais.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-3xl font-bold text-white">{status?.pending_reconciliation || 0}</div>
                            </div>

                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6 cursor-default hover:border-slate-700 transition-colors h-full flex flex-col justify-between">
                                <div className="flex items-center gap-2 mb-3">
                                    <TrendingUp className="w-4 h-4 text-purple-400" />
                                    <span className="text-slate-500 text-xs uppercase tracking-wider">Erro Médio (7d)</span>
                                    <div className="group/item relative ml-1">
                                        <Info className="w-3.5 h-3.5 text-slate-500 cursor-help" />
                                        <div
                                            className="absolute top-0 mr-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50"
                                            style={{ right: '100%' }}
                                        >
                                            Média absoluta da diferença entre Previsão e Real nos últimos 7 dias.
                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                Indica a margem de erro média das previsões. Ideal que se mantenha abaixo de 20-30%.
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className={`text-3xl font-bold ${Math.abs(status?.avg_error_7d || 0) <= 10 ? 'text-emerald-400' : Math.abs(status?.avg_error_7d || 0) <= 20 ? 'text-yellow-400' : 'text-red-400'}`}>
                                    {status?.avg_error_7d || 0}%
                                </div>
                            </div>
                        </div>

                        {/* Manual Actions */}
                        <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-4 mb-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Ações Manuais</h2>


                            {/* Incomplete Days List */}
                            <div className="mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-sm font-medium text-slate-300">
                                            📊 Dias com Previsões Incompletas
                                        </h3>
                                        {incompleteDays.length > 0 && (
                                            <span className="px-2 py-0.5 bg-red-900/30 border border-red-700/50 rounded text-red-400 text-xs font-medium">
                                                {incompleteDays.length}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {incompleteDays.length > 0 && (
                                            <button
                                                onClick={generateAllIncomplete}
                                                disabled={isGenerating}
                                                className="px-3 py-1 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-600/50 rounded text-emerald-400 text-xs font-medium disabled:opacity-50 flex items-center gap-1 cursor-pointer"
                                            >
                                                <Activity className="w-3 h-3" />
                                                Preencher Todos
                                            </button>
                                        )}
                                        <div className="flex items-center gap-2">
                                            {isUpdatingIncomplete && <span className="text-xs text-slate-500 animate-pulse">Verificando...</span>}
                                            <Tooltip content="Atualizar lista de dias com horas faltantes.">
                                                <button
                                                    onClick={fetchIncompleteDays}
                                                    className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 cursor-pointer transition-colors"
                                                >
                                                    <RefreshCw className={`w-3 h-3 ${isUpdatingIncomplete ? 'animate-spin' : ''}`} />
                                                    Atualizar
                                                </button>
                                            </Tooltip>
                                        </div>
                                    </div>
                                </div>

                                {incompleteDays.length === 0 ? (
                                    <div className="flex flex-col gap-1">
                                        <p className="text-sm text-slate-400">✅ Todos os dias completos (24h cada)</p>
                                        <p className="text-[10px] text-slate-600 italic">* O dia de hoje não é contabilizado pois ainda está em andamento.</p>
                                    </div>
                                ) : (
                                    <>
                                        <p className="text-sm text-red-400 mb-3">⚠️ {incompleteDays.length} dias incompletos encontrados</p>
                                        <p className="text-[10px] text-slate-600 italic mb-2">* O dia de hoje não é contabilizado.</p>
                                        <div className="space-y-2 max-h-48 overflow-y-auto">
                                            {incompleteDays.slice(0, 10).map((day: any) => (
                                                <div key={day.date} className="flex items-center justify-between p-2 bg-slate-800/50 rounded border border-slate-700/30">
                                                    <div className="flex-1">
                                                        <span className="text-sm font-mono text-white">{day.date}</span>
                                                        <span className="ml-3 text-xs text-slate-400">
                                                            {day.count}/24 previsões
                                                            <span className="text-red-400 ml-1">
                                                                (faltam {day.missing})
                                                            </span>
                                                        </span>
                                                    </div>
                                                    <button
                                                        onClick={() => generateForDay(day.date)}
                                                        disabled={isGenerating}
                                                        className="px-3 py-1 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-600/50 rounded text-emerald-400 text-xs font-medium disabled:opacity-50 cursor-pointer"
                                                    >
                                                        Preencher
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </>
                                )}
                            </div>



                            {/* Force Regenerate Section */}
                            <div className="mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                                <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                                    <Zap className="w-4 h-4 text-yellow-400" />
                                    Regeneração Forçada
                                </h3>
                                <div className="flex flex-wrap items-center gap-4">
                                    <ModernDatePicker
                                        value={selectedGenerateDate}
                                        onChange={setSelectedGenerateDate}
                                    />

                                    <button
                                        onClick={() => {
                                            if (selectedGenerateDate) {
                                                setConfirmAction({
                                                    open: true,
                                                    title: "Regeneração Forçada",
                                                    message: `Deseja realmente regenerar todas as previsões para ${selectedGenerateDate?.toLocaleDateString()}?\n\nO sistema irá:\n• Apagar e recriar previsões deste dia\n• Reconciliar com vendas reais (Profundo)\n• Forçar calibração dos aprendizados\n\nIsso pode levar alguns segundos.`,
                                                    type: "warning",
                                                    onConfirm: handleForceRegeneration
                                                });
                                            }
                                        }}
                                        disabled={isGenerating || !selectedGenerateDate}
                                        className="px-4 py-2 bg-yellow-600/20 hover:bg-yellow-600/30 border border-yellow-600/50 rounded-lg text-yellow-400 text-xs font-bold disabled:opacity-50 flex items-center gap-2 cursor-pointer transition-all active:scale-95 shadow-lg shadow-yellow-900/20"
                                    >
                                        <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                                        Forçar Dia Completo
                                    </button>
                                </div>
                                <p className="text-[10px] text-slate-500 mt-3 ml-1 flex items-center gap-2 bg-slate-800/50 p-2 rounded border border-slate-700/50 w-fit">
                                    <AlertCircle className="w-3 h-3 text-yellow-500" />
                                    Esta ação regenera previsões, preserva vendas reais e recalibra com novos fatores.
                                </p>
                            </div>



                            <details className="w-full">
                                <summary className="text-[10px] text-slate-500 cursor-pointer hover:text-cyan-400 transition-colors mb-2 select-none flex items-center gap-1">
                                    <span className="bg-slate-800 px-2 py-1 rounded">Opções Avançadas</span>
                                </summary>
                                <div className="flex flex-wrap gap-4 p-4 border border-slate-800 rounded-lg bg-slate-900/30">
                                    <button onClick={handleReconcile} disabled={isReconciling} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 cursor-pointer text-xs">
                                        {isReconciling ? <RefreshCw className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />}
                                        Forçar Apenas Reconciliação
                                    </button>
                                    <button onClick={handleCalibrate} disabled={isCalibrating} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 cursor-pointer text-xs">
                                        {isCalibrating ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
                                        Forçar Apenas Calibração
                                    </button>
                                </div>
                            </details>
                            {actionResult && <div className="mt-4 p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-300">{actionResult}</div>}
                        </div>
                    </>
                )
                }

                {/* Logs Tab */}
                {
                    activeTab === 'logs' && (
                        <div className="space-y-4 h-fit">
                            <div className="p-4 flex flex-wrap justify-between items-center gap-4">
                                <div className="flex items-center gap-4">
                                    <h2 className="text-lg font-semibold text-white">📋 Logs de Previsões ({logsTotal} total)</h2>
                                    {calibrationStats.total > 0 && (
                                        <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs font-medium flex items-center gap-1.5">
                                            ⚡ {calibrationStats.calibrated}/{calibrationStats.total} calibrados ({calibrationStats.percentage}%)
                                        </span>
                                    )}
                                </div>

                                {/* Sorting Controls */}
                                <div className="flex items-center gap-3">
                                    <div className="flex items-center gap-2 text-xs bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-800">
                                        <span className="text-slate-500 font-medium mr-2">Precisão:</span>
                                        <span className="flex items-center gap-1.5 mr-3"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>&lt;10% (Excelente)</span>
                                        <span className="flex items-center gap-1.5 mr-3"><span className="w-2 h-2 rounded-full bg-yellow-500"></span>10-30% (Atenção)</span>
                                        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500"></span>&gt;30% (Alto)</span>
                                    </div>
                                </div>
                            </div>
                            <div className="overflow-x-auto h-fit [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
                                <table className="w-full">
                                    <thead className="sticky top-0 z-10 bg-[#0a0a0f] border-b border-slate-800">
                                        <tr className="text-left text-slate-500 text-[10px] uppercase tracking-widest font-bold">
                                            <th className="px-4 py-3 cursor-default">Data/Hora Previsão</th>
                                            <th
                                                className="px-4 py-3 cursor-pointer hover:bg-slate-800/50 transition-colors group"
                                                onClick={() => handleHeaderSort('hora_alvo')}
                                            >
                                                <div className="flex items-center gap-1">
                                                    Hora Alvo
                                                    {sortBy === 'hora_alvo' && (
                                                        sortOrder === 'asc' ? <ArrowUp size={14} className="text-cyan-500" /> : <ArrowDown size={14} className="text-cyan-500" />
                                                    )}
                                                </div>
                                            </th>
                                            <th
                                                className="px-4 py-3 cursor-pointer hover:bg-slate-800/50 transition-colors group"
                                                onClick={() => handleHeaderSort('valor_previsto')}
                                            >
                                                <div className="flex items-center gap-1">
                                                    Previsto
                                                    {sortBy === 'valor_previsto' && (
                                                        sortOrder === 'asc' ? <ArrowUp size={14} className="text-cyan-500" /> : <ArrowDown size={14} className="text-cyan-500" />
                                                    )}
                                                </div>
                                            </th>
                                            <th
                                                className="px-4 py-3 cursor-pointer hover:bg-slate-800/50 transition-colors group"
                                                onClick={() => handleHeaderSort('valor_real')}
                                            >
                                                <div className="flex items-center gap-1">
                                                    Real
                                                    {sortBy === 'valor_real' && (
                                                        sortOrder === 'asc' ? <ArrowUp size={14} className="text-cyan-500" /> : <ArrowDown size={14} className="text-cyan-500" />
                                                    )}
                                                </div>
                                            </th>
                                            <th
                                                className="px-4 py-3 cursor-pointer hover:bg-slate-800/50 transition-colors group"
                                                onClick={() => handleHeaderSort('erro_percentual')}
                                            >
                                                <div className="flex items-center gap-1">
                                                    Erro (%)
                                                    {sortBy === 'erro_percentual' && (
                                                        sortOrder === 'asc' ? <ArrowUp size={14} className="text-cyan-500" /> : <ArrowDown size={14} className="text-cyan-500" />
                                                    )}
                                                </div>
                                            </th>
                                            <th className="px-4 py-3">Calibrado</th>
                                            <th className="px-4 py-3 text-center">Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-800/50">
                                        {logs.length === 0 ? (
                                            <tr><td colSpan={8} className="px-4 py-8 text-center text-slate-500">Nenhum log encontrado.</td></tr>
                                        ) : (
                                            logs.map((log, index) => {
                                                // Check if we need a date separator
                                                const logDate = log.hora_alvo ? new Date(log.hora_alvo).toLocaleDateString('pt-BR') : '';
                                                const prevLogDate = index > 0 && logs[index - 1].hora_alvo
                                                    ? new Date(logs[index - 1].hora_alvo).toLocaleDateString('pt-BR')
                                                    : '';
                                                const showDateSeparator = index === 0 || logDate !== prevLogDate;

                                                return (
                                                    <React.Fragment key={log.id}>
                                                        {/* Date Separator Removed */}
                                                        <tr className="border-b border-slate-800/50 hover:bg-slate-800/60 even:bg-slate-900/30 transition-all duration-200 group">
                                                            <td className="px-4 py-1 text-slate-400 text-sm group-hover:text-slate-300 transition-colors">{formatDate(log.timestamp_previsao)}</td>
                                                            <td className="px-4 py-1 text-white font-medium group-hover:text-cyan-400 transition-colors">{formatDate(log.hora_alvo)}</td>
                                                            <td className="px-4 py-1 text-cyan-400">{formatCurrency(log.valor_previsto)}</td>
                                                            <td className="px-4 py-1 text-emerald-400">{formatCurrency(log.valor_real)}</td>
                                                            <td className="px-4 py-1">
                                                                {log.erro_percentual !== null ? (
                                                                    <span className={log.erro_percentual > 0 ? 'text-red-400' : 'text-emerald-400'}>
                                                                        {log.erro_percentual > 0 ? '+' : ''}{log.erro_percentual.toFixed(1)}%
                                                                    </span>
                                                                ) : '-'}
                                                            </td>
                                                            <td className="px-4 py-1">
                                                                {log.calibrated === 'Y' && log.calibration_impact && log.calibration_impact.length > 0 ? (
                                                                    <div className="group/calib relative inline-block">
                                                                        <div className="group/calib relative inline-block">
                                                                            {(() => {
                                                                                // 1. Find factors that actually applied to THIS specific hour
                                                                                const affectingFactors = log.calibration_impact.filter((impact: any) => {
                                                                                    const type = impact.factor_type || impact.tipo_fator;
                                                                                    const key = impact.factor_key || impact.fator_chave || impact.factor || impact.key;
                                                                                    const metaKey = `_meta_${type}`;
                                                                                    const usedValue = log.fatores_usados[metaKey] || log.fatores_usados[type];
                                                                                    if (!usedValue) return false;

                                                                                    // Match logic: normalize both to string and lowercase
                                                                                    return String(usedValue).toLowerCase() === String(key).toLowerCase();
                                                                                });

                                                                                // 2. Calculate Cumulative Multiplier Impact
                                                                                // e.g. (1.1 * 0.95) = 1.045 (+4.5%)
                                                                                let cumulativeMultiplier = 1.0;
                                                                                affectingFactors.forEach((f: any) => {
                                                                                    const m = f.new_value / f.old_value;
                                                                                    cumulativeMultiplier *= m;
                                                                                });
                                                                                const rowImpactPercent = (cumulativeMultiplier - 1.0) * 100;

                                                                                // If no specific match, we'll show a "Neutral" or "Global" indicator
                                                                                const hasSpecificMatch = affectingFactors.length > 0;
                                                                                const displayImpact = hasSpecificMatch ? rowImpactPercent : 0;

                                                                                return (
                                                                                    <>
                                                                                        <div className="inline-flex items-center gap-2 bg-slate-800/80 px-2 py-1 rounded-md border border-slate-700/50 hover:border-purple-500/50 transition-colors cursor-help">
                                                                                            <Activity size={12} className={hasSpecificMatch ? "text-purple-400" : "text-slate-500"} />
                                                                                            <span className={`text-xs font-mono font-medium ${displayImpact > 0.05 ? 'text-emerald-400' :
                                                                                                displayImpact < -0.05 ? 'text-red-400' :
                                                                                                    'text-slate-400'
                                                                                                }`}>
                                                                                                {displayImpact > 0 ? '+' : ''}{displayImpact.toFixed(1)}%
                                                                                            </span>
                                                                                        </div>

                                                                                        {/* Custom Tooltip */}
                                                                                        <div className="absolute right-full top-0 mr-2 w-72 bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl opacity-0 group-hover/calib:opacity-100 transition-opacity pointer-events-none z-[60]">
                                                                                            <div className="text-xs font-semibold text-white mb-2 pb-2 border-b border-slate-800 flex justify-between">
                                                                                                <span>{hasSpecificMatch ? 'Fatores nesta Previsão' : 'Calibração Ativa (Geral)'}</span>
                                                                                                {hasSpecificMatch && <span className="text-purple-400">{affectingFactors.length} itens</span>}
                                                                                            </div>

                                                                                            <div className="space-y-1 max-h-48 overflow-y-auto pr-1 custom-scrollbar">
                                                                                                {hasSpecificMatch ? (
                                                                                                    affectingFactors.map((impact: any, i: number) => {
                                                                                                        const change = ((impact.new_value - impact.old_value) / impact.old_value * 100);
                                                                                                        const rawKey = impact.factor_key || impact.fator_chave || impact.factor || impact.key || 'Fator';
                                                                                                        const type = impact.factor_type || impact.tipo_fator || '';

                                                                                                        const displayName = getFactorLabel(type, rawKey);

                                                                                                        return (
                                                                                                            <div key={i} className="flex justify-between items-center text-[10px] gap-4">
                                                                                                                <span className="text-slate-300 capitalize truncate" title={displayName}>{displayName}</span>
                                                                                                                <span className={`font-mono font-bold ${change > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                                                                                    {change > 0 ? '+' : ''}{change.toFixed(1)}%
                                                                                                                </span>
                                                                                                            </div>
                                                                                                        )
                                                                                                    })
                                                                                                ) : (
                                                                                                    <>
                                                                                                        <div className="text-[10px] text-slate-500 mb-2 italic">Nenhum fator específico impactou esta hora. Mostrando maiores ajustes do ciclo:</div>
                                                                                                        {log.calibration_impact.slice(0, 3).map((impact: any, i: number) => {
                                                                                                            const change = ((impact.new_value - impact.old_value) / impact.old_value * 100);
                                                                                                            const rawKey = impact.factor_key || impact.fator_chave || 'Fator';
                                                                                                            return (
                                                                                                                <div key={i} className="flex justify-between items-center text-[10px] gap-4 opacity-70">
                                                                                                                    <span className="text-slate-400 capitalize truncate">{String(rawKey).replace(/_/g, ' ')}</span>
                                                                                                                    <span className="font-mono">{change > 0 ? '+' : ''}{change.toFixed(1)}%</span>
                                                                                                                </div>
                                                                                                            )
                                                                                                        })}
                                                                                                    </>
                                                                                                )}
                                                                                            </div>

                                                                                            {hasSpecificMatch && (
                                                                                                <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center">
                                                                                                    <span className="text-[10px] text-slate-500 font-medium">Impacto Total</span>
                                                                                                    <span className={`text-[10px] font-bold ${displayImpact > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                                                                        {displayImpact > 0 ? '+' : ''}{displayImpact.toFixed(1)}%
                                                                                                    </span>
                                                                                                </div>
                                                                                            )}
                                                                                        </div>
                                                                                    </>
                                                                                );
                                                                            })()}
                                                                        </div>
                                                                    </div>
                                                                ) : (
                                                                    <span className="text-slate-600 text-xs">-</span>
                                                                )}
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <div className="flex items-center justify-center gap-2">
                                                                    <button
                                                                        onClick={() => handleOpenLogDetail(log)}
                                                                        className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-slate-600"
                                                                        title="Ver detalhes"
                                                                    >
                                                                        <Eye className="w-4 h-4 text-slate-400" />
                                                                    </button>
                                                                    <button
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            setConfirmAction({
                                                                                open: true,
                                                                                title: 'Regenerar Previsão',
                                                                                message: 'Tem certeza que deseja forçar a regeneração desta previsão? O valor antigo será perdido e um novo cálculo será feito com os fatores atuais.',
                                                                                type: 'warning',
                                                                                onConfirm: async () => {
                                                                                    try {
                                                                                        setActionResult(`🔄 Regenerando log #${log.id}...`);
                                                                                        const res = await api.post(`/forecast/learning/logs/${log.id}/regenerate`);
                                                                                        if (res.data.success) {
                                                                                            setActionResult(`✅ Log #${log.id} regenerado com sucesso!`);
                                                                                            fetchLogs(currentPage);
                                                                                        }
                                                                                    } catch (err: any) {
                                                                                        alert("Erro: " + err.message);
                                                                                    }
                                                                                }
                                                                            });
                                                                        }}
                                                                        className="p-2 hover:bg-cyan-500/10 rounded-lg group/btn transition-colors cursor-pointer border border-transparent hover:border-cyan-500/30"
                                                                        title="Regenerar Previsão"
                                                                    >
                                                                        <RefreshCw className="w-4 h-4 text-slate-500 group-hover/btn:text-cyan-400" />
                                                                    </button>
                                                                    <button
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            setConfirmAction({
                                                                                open: true,
                                                                                title: 'Excluir Log',
                                                                                message: 'Tem certeza que deseja EXCLUIR este log permanentemente? Esta ação não pode ser desfeita.',
                                                                                type: 'danger',
                                                                                onConfirm: async () => {
                                                                                    try {
                                                                                        await api.delete(`/forecast/learning/logs/${log.id}`);
                                                                                        fetchLogs(currentPage);
                                                                                    } catch (err: any) {
                                                                                        alert("Erro: " + err.message);
                                                                                    }
                                                                                }
                                                                            });
                                                                        }}
                                                                        className="p-2 hover:bg-red-500/10 rounded-lg group/btn transition-colors cursor-pointer border border-transparent hover:border-red-500/30"
                                                                        title="Excluir Log"
                                                                    >
                                                                        <Trash2 className="w-4 h-4 text-slate-500 group-hover/btn:text-red-400" />
                                                                    </button>
                                                                </div>
                                                            </td>
                                                        </tr>
                                                    </React.Fragment>
                                                );
                                            })
                                        )}
                                    </tbody>
                                </table>
                            </div>
                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="p-4 border-t border-slate-800/50 flex justify-between items-center">
                                    <span className="text-slate-400 text-sm">Página {currentPage} de {totalPages}</span>
                                    <div className="flex gap-2">
                                        <button onClick={() => fetchLogs(currentPage - 1)} disabled={currentPage === 1} className="p-2 bg-slate-800 rounded-lg disabled:opacity-50 cursor-pointer">
                                            <ChevronLeft className="w-4 h-4 text-slate-400" />
                                        </button>
                                        <button onClick={() => fetchLogs(currentPage + 1)} disabled={currentPage === totalPages} className="p-2 bg-slate-800 rounded-lg disabled:opacity-50 cursor-pointer">
                                            <ChevronRight className="w-4 h-4 text-slate-400" />
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )
                }

                {/* Analysis Tab */}
                {
                    activeTab === 'analysis' && (
                        <LearningAnalytics
                            period={period}
                            startDate={getDateRange().start}
                            endDate={getDateRange().end}
                        />
                    )
                }

                {/* Fatores/Multipliers Tab */}
                {
                    activeTab === 'multipliers' && (
                        <>
                            <div className="bg-[#12121a] rounded-xl border border-slate-800/50">
                                <div className="p-4 border-b border-slate-800/50 flex justify-between items-center">
                                    <div>
                                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                            <Sliders className="w-5 h-5 text-purple-400" />
                                            Ajuste de Pesos dos Fatores
                                        </h2>
                                        <p className="text-slate-500 text-sm mt-1">Ajuste os pesos de cada fator. Ative/desative em Configurações → Hyper AI</p>
                                    </div>
                                    <button
                                        onClick={saveMultipliers}
                                        disabled={isSavingMults}
                                        className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center gap-2 cursor-pointer"
                                    >
                                        {isSavingMults ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                        Salvar Pesos
                                    </button>
                                </div>

                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="text-left text-slate-500 text-[10px] uppercase tracking-widest font-bold">
                                                <th className="px-4 py-3 border-r border-slate-800/30">Status</th>
                                                <th className="px-4 py-3 border-r border-slate-800/30">Fator Multiplicador</th>
                                                <th className="px-4 py-3 border-r border-slate-800/30">Descrição</th>
                                                <th className="px-4 py-3 border-r border-slate-800/30">Peso</th>
                                                <th className="px-4 py-3 border-r border-slate-800/30">Min</th>
                                                <th className="px-4 py-3">Max</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-800/50">
                                            {Object.entries(multipliers).map(([key, config]: [string, any]) => (
                                                <tr key={key} className={`transition-colors ${config?.enabled ? 'hover:bg-slate-800/30' : 'opacity-40'}`}>
                                                    <td className="px-4 py-3">
                                                        <div className={`w-3 h-3 rounded-full ${config?.enabled ? 'bg-emerald-500' : 'bg-slate-600'}`} title={config?.enabled ? 'Ativo' : 'Desativado em Settings'} />
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <span className={`font-mono text-sm ${config?.enabled ? 'text-cyan-400' : 'text-slate-500'}`}>
                                                            {translateFactorKey(key.replace('mult_', ''))}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 text-slate-400 text-sm">{config?.desc || '-'}</td>
                                                    <td className="px-4 py-3">
                                                        <input
                                                            type="number"
                                                            step="0.1"
                                                            min="0"
                                                            max="2"
                                                            value={config?.weight || 1}
                                                            onChange={(e) => updateMultiplierWeight(key, parseFloat(e.target.value))}
                                                            disabled={!config?.enabled}
                                                            className="w-16 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white text-sm disabled:opacity-50"
                                                        />
                                                    </td>
                                                    <td className="px-4 py-3 text-slate-500 text-sm">{config?.min || 0}</td>
                                                    <td className="px-4 py-3 text-slate-500 text-sm">{config?.max || 2}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>

                                {Object.keys(multipliers).length === 0 && (
                                    <div className="p-8 text-center text-slate-500">
                                        Nenhum fator configurado. Verifique Configurações → Hyper AI.
                                    </div>
                                )}

                                {actionResult && (
                                    <div className="p-4 border-t border-slate-800/50">
                                        <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-300">
                                            {actionResult}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </>
                    )
                }

                {/* History Tab */}
                {
                    activeTab === 'history' && (
                        <div className="bg-[#12121a] rounded-xl border border-slate-800/50">
                            <div className="p-4 border-b border-slate-800/50 flex justify-between items-center">
                                <div>
                                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                        <Clock className="w-5 h-5 text-purple-400" />
                                        Histórico de Calibrações
                                    </h2>
                                    <p className="text-slate-400 text-sm mt-1">
                                        Registro completo de ajustes automáticos do sistema de aprendizado
                                    </p>
                                </div>
                                <button onClick={fetchHistory} className="p-2 hover:bg-slate-700/50 rounded-lg cursor-pointer" title="Atualizar">
                                    <RefreshCw className="w-4 h-4 text-slate-400" />
                                </button>
                            </div>

                            {history.length === 0 ? (
                                <div className="p-8 text-center">
                                    <div className="inline-block p-4 rounded-full bg-slate-800/50 mb-4">
                                        <Clock className="w-12 h-12 text-slate-600" />
                                    </div>
                                    <p className="text-slate-500">Nenhum histórico de calibração encontrado para o período selecionado.</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-slate-800/50">
                                    {history.map((entry: any, index: number) => {
                                        const details = typeof entry.details === 'string' ? JSON.parse(entry.details) : (entry.details || {});
                                        const isCalibration = details.action === 'calibration';
                                        const isReconciliation = details.action === 'reconciliation';

                                        if (!isCalibration && !isReconciliation) return null;

                                        return (
                                            <div key={index} className="p-4 hover:bg-slate-800/30 transition-colors">
                                                <div className="flex items-start justify-between gap-4">
                                                    <div className="flex items-start gap-3 flex-1">
                                                        {isCalibration ? (
                                                            <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
                                                                <Zap className="w-5 h-5 text-purple-400" />
                                                            </div>
                                                        ) : (
                                                            <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
                                                                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                                                            </div>
                                                        )}

                                                        <div className="flex-1">
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <h3 className="font-medium text-white">{entry.message}</h3>
                                                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${entry.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' :
                                                                    entry.status === 'error' ? 'bg-red-500/20 text-red-400' :
                                                                        'bg-slate-500/20 text-slate-400'
                                                                    }`}>
                                                                    {entry.status}
                                                                </span>
                                                            </div>

                                                            <div className="text-xs text-slate-500 mb-2">
                                                                {new Date(entry.timestamp).toLocaleString('pt-BR')}
                                                            </div>

                                                            {isCalibration && (
                                                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3">
                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Fator</div>
                                                                        <div className="text-sm font-mono text-slate-300">{details.factor}</div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Anterior</div>
                                                                        <div className="text-sm font-mono text-slate-400">{details.old_value?.toFixed(3) || '-'}</div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-purple-500/30">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Novo</div>
                                                                        <div className="text-sm font-mono text-purple-400 font-bold">{details.new_value?.toFixed(3) || '-'}</div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Ajuste</div>
                                                                        <div className={`text-sm font-mono font-bold ${(details.change_percent || 0) > 0 ? 'text-emerald-400' : 'text-red-400'
                                                                            }`}>
                                                                            {(details.change_percent || 0) > 0 ? '+' : ''}{details.change_percent?.toFixed(2) || '0.00'}%
                                                                        </div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Erro</div>
                                                                        <div className="text-sm font-mono text-amber-400">{details.avg_error?.toFixed(1) || '0.0'}%</div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Amostras</div>
                                                                        <div className="text-sm font-mono text-slate-300">{details.samples || 0}</div>
                                                                    </div>
                                                                </div>
                                                            )}

                                                            {isReconciliation && (
                                                                <div className="grid grid-cols-2 gap-3 mt-3">
                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Previsões</div>
                                                                        <div className="text-sm font-mono text-slate-300">{details.count || 0}</div>
                                                                    </div>

                                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Erro Abs.</div>
                                                                        <div className="text-sm font-mono text-amber-400">{details.avg_abs_error?.toFixed(2) || '0.00'}%</div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )
                }

                {/* Log Details Modal */}
                {
                    selectedLog && (
                        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
                            <div className="bg-[#151520] border border-slate-800 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
                                <div className="p-6 border-b border-slate-800 flex justify-between items-center sticky top-0 bg-[#151520] z-10">
                                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                        <Activity className={`w-5 h-5 ${isLoadingDetail ? 'text-amber-400 animate-pulse' : 'text-cyan-400'}`} />
                                        Detalhes da Previsão #{selectedLog.id}
                                        {isLoadingDetail && <span className="text-xs text-amber-400/70 font-normal animate-pulse ml-2">(Carregando mix real...)</span>}
                                    </h2>
                                    <button onClick={() => setSelectedLog(null)} className="p-2 hover:bg-slate-800 rounded-lg cursor-pointer" title="Fechar">
                                        <X className="w-5 h-5 text-slate-400" />
                                    </button>
                                </div>

                                <div className="p-6 space-y-6">
                                    {/* Basic Info Grid (Moved Top) */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/50">
                                            <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Criado em</div>
                                            <div className="text-white font-medium">{formatDate(selectedLog.timestamp_previsao)}</div>
                                        </div>
                                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/50">
                                            <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Hora Alvo</div>
                                            <div className="text-white font-medium">{formatDate(selectedLog.hora_alvo)}</div>
                                        </div>
                                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/50">
                                            <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Receita Ponderada</div>
                                            <div className="text-2xl font-bold text-cyan-400">{formatCurrency(selectedLog.valor_previsto)}</div>
                                            <div className="text-[10px] text-slate-500 mt-1">Soma das probabilidades</div>
                                        </div>
                                        <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/50">
                                            <div className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Valor Real</div>
                                            <div className="text-2xl font-bold text-emerald-400">{formatCurrency(selectedLog.valor_real)}</div>
                                        </div>
                                    </div>

                                    {/* Product Mix Section (Top Priority) */}
                                    {selectedLog.fatores_usados && selectedLog.fatores_usados._product_mix && (
                                        <div className="mb-0">
                                            <h3 className="text-lg font-semibold text-white mb-4 flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <ShoppingCart className={`w-5 h-5 ${isLoadingDetail ? 'text-slate-600 animate-spin' : 'text-emerald-400'}`} />
                                                    Mix de Produtos Previsto
                                                </div>
                                                <span className="text-xs text-slate-500 font-normal">
                                                    {isLoadingDetail ? '...' : (selectedLog.fatores_usados._product_mix as any[]).length} itens listados
                                                </span>
                                            </h3>
                                            <div className="bg-slate-900/50 rounded-xl border-x border-b border-slate-800/50 overflow-hidden relative min-h-[100px]">
                                                {isLoadingDetail && (
                                                    <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center gap-3">
                                                        <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
                                                        <span className="text-xs text-emerald-400 font-medium tracking-widest uppercase">Identificando Vendas Reais...</span>
                                                    </div>
                                                )}
                                                <div className={`max-h-[400px] overflow-y-auto ${isLoadingDetail ? 'opacity-20 grayscale scale-[0.99]' : 'opacity-100 grayscale-0 scale-100'} transition-all duration-700`}>
                                                    <table className="w-full text-sm">
                                                        <thead className="sticky top-0 z-10 bg-[#151520] shadow-[0_1px_0_0_rgba(30,41,59,0.5)]">
                                                            <tr className="text-left text-slate-500 text-[10px] uppercase tracking-widest font-bold border-b border-slate-800">
                                                                <th className="px-4 py-3 w-8 border-r border-slate-800/30 cursor-default"></th>
                                                                <th className="px-4 py-3 border-r border-slate-800/30 cursor-default">Produto</th>
                                                                <th className="px-4 py-3 text-right border-r border-slate-800/30 cursor-default">Preço Unit.</th>
                                                                <th className="px-4 py-3 text-right border-r border-slate-800/30 cursor-default">Qtd. Prevista</th>
                                                                <th className="px-4 py-3 text-right text-emerald-400 border-r border-slate-800/30 cursor-default">Qtd. Real</th>
                                                                <th className="px-4 py-3 text-right cursor-default">Receita Est.</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="divide-y divide-slate-800/30">
                                                            {(selectedLog.fatores_usados._product_mix as any[]).map((prod: any, idx: number) => {
                                                                // USER REQUEST: Hide out of stock items completely
                                                                if ((prod.stock || 0) <= 0) return null;

                                                                const mult = prod.combined_product_mult || 0;
                                                                const units = prod.units_expected || 0;
                                                                const revenue = prod.revenue_expected || 0;
                                                                const unitsReal = prod.realized_units || 0;
                                                                const unitPrice = units > 0 ? revenue / units : 0;
                                                                const isExpanded = expandedProductIndex === idx;

                                                                const isProb = units < 0.99;
                                                                // USER REQUEST: Always show decimal, no percentage, with comma
                                                                const displayQty = `${units.toFixed(2)}`.replace('.', ',');

                                                                return (
                                                                    <React.Fragment key={idx}>
                                                                        <tr
                                                                            className={`hover:bg-slate-800/40 cursor-pointer transition-all duration-200 border-b border-white/5 
                                                                            ${isExpanded ? 'bg-slate-800/40' : ''} 
                                                                            ${unitsReal > 0 ? 'bg-emerald-500/5 border-l-[3px] border-l-emerald-500' : 'border-l-[3px] border-l-transparent'}`}
                                                                            onClick={() => setExpandedProductIndex(isExpanded ? null : idx)}
                                                                        >
                                                                            <td className="px-4 py-3 text-center">
                                                                                {isExpanded ? (
                                                                                    <ChevronDown className="w-4 h-4 text-cyan-400" />
                                                                                ) : (
                                                                                    <ChevronRight className={`w-4 h-4 ${unitsReal > 0 ? 'text-emerald-500' : 'text-slate-600'}`} />
                                                                                )}
                                                                            </td>
                                                                            <td className="px-4 py-3">
                                                                                <div className="flex items-center gap-2">
                                                                                    <div className={`text-sm font-medium ${unitsReal > 0 ? 'text-emerald-400' : 'text-slate-200'}`} title={prod.title}>
                                                                                        {prod.title || 'Produto Desconhecido'}
                                                                                    </div>
                                                                                    {unitsReal > 0 && (
                                                                                        <span className="text-[9px] border border-emerald-500/50 text-emerald-400 px-1.5 py-0.5 rounded tracking-wider uppercase font-bold shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                                                                            Vendido
                                                                                        </span>
                                                                                    )}
                                                                                </div>
                                                                                <div className="text-[10px] text-slate-500 mt-1 flex items-center gap-2">
                                                                                    <span title="Multiplicador combinado aplicado" className="bg-slate-800/50 px-1.5 py-0.5 rounded text-slate-400 border border-white/5">
                                                                                        ⚡ {mult.toFixed(2)}x
                                                                                    </span>
                                                                                    {isExpanded && <span className="text-cyan-400 text-[10px] ml-2 animate-pulse">Detalhes abertos</span>}
                                                                                </div>
                                                                            </td>
                                                                            <td className="px-4 py-3 text-right text-slate-400 font-mono whitespace-nowrap">
                                                                                {formatCurrency(unitPrice)}
                                                                            </td>
                                                                            <td className={`px-4 py-3 text-right font-mono ${isProb ? 'text-cyan-400' : 'text-white'}`}>
                                                                                {displayQty}
                                                                            </td>
                                                                            <td className="px-4 py-3 text-right font-mono font-medium">
                                                                                {unitsReal > 0 ? (
                                                                                    <span className="text-emerald-400 font-bold">
                                                                                        {unitsReal}
                                                                                    </span>
                                                                                ) : (
                                                                                    <span className="text-slate-700">-</span>
                                                                                )}
                                                                            </td>
                                                                            <td className="px-4 py-3 text-right text-emerald-400 font-mono font-medium whitespace-nowrap text-xs">
                                                                                {formatCurrency(revenue)}
                                                                            </td>
                                                                        </tr>
                                                                        {isExpanded && prod.product_multipliers && (
                                                                            <tr className="bg-[#0f0f18] border-b border-slate-800/50">
                                                                                <td colSpan={6} className="p-4 pl-12">
                                                                                    <div className="space-y-2">
                                                                                        <div className="flex items-center gap-2 mb-2">
                                                                                            <Sliders className="w-3 h-3 text-slate-400" />
                                                                                            <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Fatores Específicos do Produto</span>
                                                                                        </div>
                                                                                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                                                                                            {Object.entries(prod.product_multipliers).map(([key, rawVal]: [string, any]) => {
                                                                                                const val = Number(rawVal);

                                                                                                // Check if this specific factor was calibrated
                                                                                                // Works for both global calibrations affecting products AND product-specific calibrations
                                                                                                const calibrationInfo = selectedLog.calibration_impact && selectedLog.calibration_impact.find(
                                                                                                    (i: any) => {
                                                                                                        // Match by factor_type (product calibration: is_product_factor=true)
                                                                                                        if (i.is_product_factor && i.factor_type === key) return true;
                                                                                                        // Legacy: match by factor_key
                                                                                                        if (i.factor_key === key || i.factor_key === `product_${key}`) return true;
                                                                                                        return false;
                                                                                                    }
                                                                                                );

                                                                                                let colorClass = "text-slate-300";
                                                                                                if (val > 1.05) colorClass = "text-emerald-400 font-bold";
                                                                                                if (val < 0.95) colorClass = "text-rose-400 font-bold";
                                                                                                if (val === 0) colorClass = "text-slate-500";

                                                                                                return (
                                                                                                    <div key={key} className={`bg-slate-900 border ${calibrationInfo ? 'border-purple-500/30' : 'border-slate-800'} rounded p-2 flex flex-col items-start gap-1 relative overflow-hidden`}>
                                                                                                        {calibrationInfo && (
                                                                                                            <div className="absolute top-0 right-0 w-2 h-2 bg-purple-500 rounded-bl-full" title="Fator Calibrado" />
                                                                                                        )}
                                                                                                        <span className="text-[10px] text-slate-500 uppercase font-medium truncate w-full" title={translateFactorKey(key)}>
                                                                                                            {translateFactorKey(key)}
                                                                                                        </span>

                                                                                                        {calibrationInfo ? (
                                                                                                            <div className="flex flex-col w-full">
                                                                                                                <div className="flex items-center gap-1 opacity-60">
                                                                                                                    <span className="text-[10px] text-slate-400 line-through">{calibrationInfo.old_value.toFixed(2)}x</span>
                                                                                                                    <ArrowRight className="w-2 h-2 text-slate-600" />
                                                                                                                </div>
                                                                                                                <div className="flex items-center gap-2">
                                                                                                                    <span className="text-sm font-mono text-purple-400 font-bold">
                                                                                                                        {calibrationInfo.new_value.toFixed(2)}x
                                                                                                                    </span>
                                                                                                                    {(() => {
                                                                                                                        const delta = ((calibrationInfo.new_value / calibrationInfo.old_value) - 1) * 100;
                                                                                                                        return (
                                                                                                                            <span className={`text-[10px] font-bold ${delta > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                                                                                                {delta > 0 ? '+' : ''}{delta.toFixed(1)}%
                                                                                                                            </span>
                                                                                                                        );
                                                                                                                    })()}
                                                                                                                </div>
                                                                                                            </div>
                                                                                                        ) : (
                                                                                                            <span className={`text-sm font-mono ${colorClass}`}>
                                                                                                                {val.toFixed(2)}x
                                                                                                            </span>
                                                                                                        )}
                                                                                                    </div>
                                                                                                );
                                                                                            })}
                                                                                        </div>
                                                                                        <div className="mt-2 text-[10px] text-slate-500 italic">
                                                                                            * Probabilidade = Base × Global ({selectedLog.fatores_usados.global_multiplier || '1.0'}x) × {prod.combined_product_mult?.toFixed(3)}x (Produto)
                                                                                        </div>
                                                                                    </div>
                                                                                </td>
                                                                            </tr>
                                                                        )}
                                                                    </React.Fragment>
                                                                );
                                                            })}
                                                            {/* Reconciliation Row for Long Tail */}
                                                            {(() => {
                                                                const listSum = (selectedLog.fatores_usados._product_mix as any[]).reduce((acc, p) => acc + (p.revenue_expected || 0), 0);
                                                                const diff = (selectedLog.valor_previsto || 0) - listSum;
                                                                if (diff > 0.05) {
                                                                    return (
                                                                        <tr className="bg-slate-800/20 italic">
                                                                            <td className="px-4 py-3 text-center">-</td>
                                                                            <td className="px-4 py-3 text-slate-400">
                                                                                Outros Produtos (Cauda Longa)
                                                                                <div className="text-[10px] text-slate-500">Itens com probabilidade muito baixa</div>
                                                                            </td>
                                                                            <td className="px-4 py-3 text-right text-slate-500 font-mono">-</td>
                                                                            <td className="px-4 py-3 text-right text-slate-500 font-mono">-</td>
                                                                            <td className="px-4 py-3 text-right text-slate-500 font-mono">-</td>
                                                                            <td className="px-4 py-3 text-right text-emerald-400/70 font-mono">
                                                                                {formatCurrency(diff)}
                                                                            </td>
                                                                        </tr>
                                                                    );
                                                                }
                                                                return null;
                                                            })()}
                                                            <tr className="bg-[#0f0f18] font-bold border-t border-slate-700/50">
                                                                <td colSpan={2} className="px-4 py-3 text-right text-slate-400 uppercase text-xs tracking-wider">
                                                                    Totais do Período
                                                                </td>
                                                                <td className="px-4 py-3 text-right font-mono text-slate-300">
                                                                    {/* Price Avg irrelvant */}
                                                                </td>
                                                                <td className="px-4 py-3 text-right text-white font-mono">
                                                                    {(selectedLog.fatores_usados._product_mix as any[]).reduce((acc, p) => acc + (p.units_expected || 0), 0).toFixed(2)} UN
                                                                </td>
                                                                <td className="px-4 py-3 text-right text-emerald-400 font-mono text-xs">
                                                                    {/* TOTAL REAL REVENUE - Put in Real Qty col? No, put in next column, merge logic? */}
                                                                    {/* To align with 'Qtd Real' column, we should show UNITS sum? */}
                                                                    {/* User wants Revenue Real next to Revenue Expected. */}
                                                                    {/* Let's put Total Real Revenue in the LAST column, and Predicted Revenue in diff col? */}
                                                                    {/* Current Header: Product | Price | QtyExp | QtyReal | RevExp */}
                                                                    {/* Footer Col 5 (QtyReal) -> Show Real Revenue? Confusing. */}
                                                                    {/* Let's show Real Revenue in Col 5 (QtyReal) designated as 'Realized $' and RevExp in Col 6. */}
                                                                    <span className="text-[10px] text-slate-500 block">REAL</span>
                                                                    {formatCurrency(
                                                                        (selectedLog.fatores_usados._product_mix as any[]).reduce((acc, p) => acc + ((p.realized_units || 0) * (p.revenue_expected / p.units_expected || 0)), 0)
                                                                    )}
                                                                </td>
                                                                <td className="px-4 py-3 text-right text-emerald-400 font-mono">
                                                                    <span className="text-[10px] text-slate-500 block">PREVISTO</span>
                                                                    {formatCurrency(selectedLog.valor_previsto || 0)}
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </div>
                                    )}



                                    {/* Status Box */}
                                    <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800/50">
                                        <div className="flex justify-between items-start mb-4">
                                            <span className="text-sm font-medium text-slate-400">Status de Calibração</span>
                                            {getStatusBadge(selectedLog.status)}
                                        </div>

                                        {selectedLog.calibration_impact && selectedLog.calibration_impact.length > 0 ? (
                                            <div>
                                                <div className="flex flex-col gap-2 mb-4">
                                                    <h4 className="text-purple-400 font-bold text-sm flex items-center gap-2">
                                                        <Zap className="w-4 h-4" />
                                                        Insights de Recalibragem
                                                    </h4>
                                                </div>

                                                {/* DATA GRID */}
                                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-2">
                                                    {/* Metric 1: Previous Bias */}
                                                    {(() => {
                                                        const impact = selectedLog.calibration_impact!;
                                                        const avgError = impact.reduce((acc: number, i: any) => acc + (i.avg_error || 0), 0) / impact.length;
                                                        const isOver = avgError > 0;
                                                        return (
                                                            <div className="bg-slate-900/50 rounded-lg p-3 border border-purple-500/20 relative">
                                                                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-1 flex items-center justify-between">
                                                                    <span>Viés Anterior</span>
                                                                    <div className="relative group/item ml-1">
                                                                        <Info size={12} className="text-slate-600 hover:text-cyan-400 cursor-help" />
                                                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 normal-case tracking-normal shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                                            Diferença média entre o previsto e o real detectada antes deste ciclo de recalibragem.
                                                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                                                Abaixo de 0% = Corrigindo subestimativa. Acima de 0% = Corrigindo superestimativa.
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div className={`text-lg font-mono font-bold ${isOver ? 'text-amber-400' : 'text-blue-400'}`}>
                                                                    {Math.abs(avgError).toFixed(1)}% {isOver ? 'Acima' : 'Abaixo'}
                                                                </div>
                                                                <div className="text-[10px] text-slate-600 leading-tight mt-1">
                                                                    Média de erro detectada antes do ajuste.
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}

                                                    {/* Metric 2: Confidence (Samples) */}
                                                    {(() => {
                                                        const impact = selectedLog.calibration_impact!;
                                                        const totalSamples = impact.reduce((acc: number, i: any) => acc + (i.samples || 0), 0);
                                                        return (
                                                            <div className="bg-slate-900/50 rounded-lg p-3 border border-purple-500/20 relative">
                                                                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-1 flex items-center justify-between">
                                                                    <span>Amostragem</span>
                                                                    <div className="relative group/item ml-1">
                                                                        <Info size={12} className="text-slate-600 hover:text-cyan-400 cursor-help" />
                                                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 normal-case tracking-normal shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                                            Quantidade total de previsões históricas que o sistema analisou para calibrar os pesos.
                                                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                                                Amostragens maiores (ex: {'>'}100) garantem calibrações mais estáveis.
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div className="text-lg font-mono font-bold text-slate-200">
                                                                    {totalSamples}
                                                                </div>
                                                                <div className="text-[10px] text-slate-600 leading-tight mt-1">
                                                                    Total de previsões analisadas para decidir.
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}

                                                    {/* Metric 3: Intensity */}
                                                    {(() => {
                                                        const impact = selectedLog.calibration_impact!;
                                                        const avgChange = impact.reduce((acc: number, i: any) => {
                                                            const change = Math.abs((i.new_value - i.old_value) / i.old_value);
                                                            return acc + change;
                                                        }, 0) / impact.length;

                                                        return (
                                                            <div className="bg-slate-900/50 rounded-lg p-3 border border-purple-500/20 relative">
                                                                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-1 flex items-center justify-between">
                                                                    <span>Intensidade</span>
                                                                    <div className="relative group/item ml-1">
                                                                        <Info size={12} className="text-slate-600 hover:text-cyan-400 cursor-help" />
                                                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 normal-case tracking-normal shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                                            Magnitude média dos ajustes aplicados nos multiplicadores de fatores.
                                                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                                                Indica se o ciclo foi de "ajuste fino" ({'<'}1%) ou "correção forte" ({'>'}5%).
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div className="text-lg font-mono font-bold text-purple-400">
                                                                    ~{(avgChange * 100).toFixed(1)}%
                                                                </div>
                                                                <div className="text-[10px] text-slate-600 leading-tight mt-1">
                                                                    Magnitude média das correções aplicadas.
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}

                                                    {/* Metric 4: Top Factor */}
                                                    {(() => {
                                                        const impact = selectedLog.calibration_impact!;
                                                        const topFactor = impact.reduce((max: any, i: any) => {
                                                            const change = Math.abs((i.new_value - i.old_value) / i.old_value);
                                                            return change > (max.change || 0) ? { ...i, change } : max;
                                                        }, {} as any);

                                                        return (
                                                            <div className="bg-slate-900/50 rounded-lg p-3 border border-purple-500/20 relative">
                                                                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-1 flex items-center justify-between">
                                                                    <span>Maior Correção</span>
                                                                    <div className="relative group/item ml-1">
                                                                        <Info size={12} className="text-slate-600 hover:text-cyan-400 cursor-help" />
                                                                        <div className="absolute bottom-full right-0 mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-300 normal-case tracking-normal shadow-xl opacity-0 group-hover/item:opacity-100 transition-opacity pointer-events-none z-50">
                                                                            O fator que recebeu o maior ajuste percentual neste ciclo de calibração.
                                                                            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-800 pt-1">
                                                                                Identifica qual variável estava mais "descalibrada" no período.
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <div className="text-sm font-bold text-white truncate" title={translateFactorKey(topFactor.factor_key || '', topFactor.factor_type)}>
                                                                    {translateFactorKey(topFactor.factor_key || '', topFactor.factor_type)}
                                                                </div>
                                                                <div className="text-[10px] text-slate-600 leading-tight mt-1">
                                                                    Fator que sofreu maior alteração ({(topFactor.change * 100).toFixed(1)}%).
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </div>
                                            </div>
                                        ) : (
                                            <p className="text-sm text-slate-500">
                                                {selectedLog.calibrated === 'Y'
                                                    ? 'Este log foi processado, mas nenhum ajuste significativo foi necessário nos fatores atuais.'
                                                    : 'Este log ainda não foi processado pela calibração automática.'}
                                            </p>
                                        )}
                                    </div>

                                    {/* Factors List */}
                                    <div>
                                        <h3 className="text-lg font-semibold text-white mb-4">Fatores Globais (Macro)</h3>
                                        <div className="bg-slate-900/50 rounded-xl border border-slate-800/50 overflow-hidden">
                                            <table className="w-full text-sm">
                                                <thead>
                                                    <tr className="bg-slate-800/50 text-left text-slate-500 text-xs uppercase">
                                                        <th className="px-4 py-3">Fator</th>
                                                        <th className="px-4 py-3 text-right">Antes</th>
                                                        <th className="px-4 py-3 text-right">Depois</th>
                                                        <th className="px-4 py-3 text-center">Ajuste</th>
                                                        <th className="px-4 py-3 text-right">Valor Final</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-slate-800/30">
                                                    {/* Baseline */}
                                                    <tr>
                                                        <td className="px-4 py-3 flex items-center gap-2">
                                                            <BarChart3 className="w-4 h-4 text-slate-500" />
                                                            <span className="text-slate-300">Baseline Histórico</span>
                                                        </td>
                                                        <td className="px-4 py-3 text-right text-slate-500">-</td>
                                                        <td className="px-4 py-3 text-right text-slate-500">-</td>
                                                        <td className="px-4 py-3 text-center text-slate-500">-</td>
                                                        <td className="px-4 py-3 text-right font-mono text-white">
                                                            {formatCurrency(selectedLog.baseline)}
                                                        </td>
                                                    </tr>
                                                    {/* Multipliers */}
                                                    {selectedLog.fatores_usados && Object.entries(selectedLog.fatores_usados).map(([key, value]: [string, any]) => {
                                                        // Skip internal metadata keys like _product_mix
                                                        if (key.startsWith('_')) return null;

                                                        // Normalize keys for matching (e.g. Day Of Week -> day_of_week)
                                                        const normalizedKey = key.toLowerCase().replace(/ /g, '_');

                                                        // Check if this factor was calibrated
                                                        // WE MUST MATCH AGAINST factor_type ("day_of_week"), NOT factor_key ("Monday")
                                                        const calibrationInfo = selectedLog.calibration_impact && selectedLog.calibration_impact.find(
                                                            (i: any) => i.factor_type === key || i.factor_type === normalizedKey || i.factor_type.includes(normalizedKey)
                                                        );

                                                        let adjustment = 0;
                                                        if (calibrationInfo) {
                                                            adjustment = ((calibrationInfo.new_value - calibrationInfo.old_value) / calibrationInfo.old_value) * 100;
                                                        }

                                                        return (
                                                            <tr key={key} className={calibrationInfo ? 'bg-purple-500/5' : ''}>
                                                                <td className="px-4 py-3 text-slate-300 capitalize flex items-center gap-2">
                                                                    {translateFactorType(key)}
                                                                </td>
                                                                <td className="px-4 py-3 text-right font-mono text-slate-500">
                                                                    {calibrationInfo ? `${calibrationInfo.old_value.toFixed(4)}x` : '-'}
                                                                </td>
                                                                <td className="px-4 py-3 text-right font-mono text-cyan-400">
                                                                    {calibrationInfo ? `${calibrationInfo.new_value.toFixed(4)}x` : '-'}
                                                                </td>
                                                                <td className="px-4 py-3 text-center">
                                                                    {calibrationInfo ? (
                                                                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${adjustment > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                                                                            {adjustment > 0 ? '+' : ''}{adjustment.toFixed(2)}%
                                                                        </span>
                                                                    ) : '-'}
                                                                </td>
                                                                <td className="px-4 py-3 text-right font-mono text-white">
                                                                    {typeof value === 'number' ? `${value.toFixed(2)}x` : value}
                                                                </td>
                                                            </tr>
                                                        );
                                                    })}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
                }
                <ConfirmModal
                    isOpen={confirmAction.open}
                    onClose={() => setConfirmAction(prev => ({ ...prev, open: false }))}
                    onConfirm={confirmAction.onConfirm}
                    title={confirmAction.title}
                    message={confirmAction.message}
                    type={confirmAction.type}
                />
            </div >
        </div >
    );
}
