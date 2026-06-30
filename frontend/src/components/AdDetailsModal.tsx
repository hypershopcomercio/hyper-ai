import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { CompetitorManager } from "./hyper-ai/CompetitorManager";
import { AdPerformanceCharts } from "./hyper-ai/AdPerformanceCharts";
import { X, ExternalLink, Package, Activity, AlertTriangle, TrendingUp, TrendingDown, Clock, Truck, BarChart3, Info, DollarSign, ArrowRight, Edit3, PauseCircle, PlayCircle, Sparkles, LayoutDashboard, Wallet, Boxes, TestTube2, Award, Search, CheckCircle, ArrowUpCircle, Megaphone, ShieldCheck, FileText, Warehouse, Box, CheckCircle2, Trophy, Download, ChevronLeft, ChevronRight, Maximize2, Minimize2, Users, History, Calculator, Tag, Check, Target, ArrowUp, ArrowDown, Percent, Building2, Archive, RotateCcw, Trash2, RefreshCw, Zap, Calendar } from "lucide-react";
import { Ad } from "@/types";
import { api } from "@/lib/api";
import { PremiumLoader } from "@/components/ui/PremiumLoader";
import { AnimatePresence, motion } from "framer-motion";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { Tooltip } from "@/components/ui/Tooltip";
import { PromoSelector } from './PromoSelector';
import { MarginSimulator } from './MarginSimulator';
import { FiscalParametersTab } from './FiscalParametersTab';
import { RepricerStrategyPanel } from './RepricerStrategyPanel';
import { AdMediaTab } from './AdMediaTab';



interface Props {
    adId: string;
    onClose: () => void;
}



export function AdDetailsModal({ adId, onClose }: Props) {
    const [ad, setAd] = useState<Ad | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'health' | 'competition' | 'margin' | 'fiscal' | 'media'>('overview');
    const [activeImageIndex, setActiveImageIndex] = useState(0);
    const [isLightboxOpen, setIsLightboxOpen] = useState(false);
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

    // Protection Modal State
    const [isProtectionModalOpen, setIsProtectionModalOpen] = useState(false);
    const [protectionState, setProtectionState] = useState<'intro' | 'scanning' | 'results' | 'success'>('intro');
    const [scannedCompetitors, setScannedCompetitors] = useState<any[]>([]);

    const [competitorCount, setCompetitorCount] = useState<number>(0);
    const [isMarginModalOpen, setIsMarginModalOpen] = useState(false);
    const [marginState, setMarginState] = useState<'analysis' | 'actions'>('analysis');
    const [targetMargin, setTargetMargin] = useState<number>(0);
    const [simulatedPrice, setSimulatedPrice] = useState<number>(0);
    const [showStrategy, setShowStrategy] = useState(false); // Added missing state
    
    // Pricing Resolution State
    const [pricingResolution, setPricingResolution] = useState<any>(null);
    const [isResolvingPricing, setIsResolvingPricing] = useState(false);


    // Price Execution Modal State
    const [priceExecutionModal, setPriceExecutionModal] = useState<{
        open: boolean;
        targetPrice: number;
        status: 'confirm' | 'loading' | 'success' | 'error';
        oldPrice?: number;
        errorMessage?: string;
    }>({
        open: false,
        targetPrice: 0,
        status: 'confirm'
    });
    const [originalVals, setOriginalVals] = useState<{ price: number, margin: number }>({ price: 0, margin: 0 });


    // Reset Strategy Panel when Target Margin changes (user moves slider)
    useEffect(() => {
        setShowStrategy(false);
    }, [targetMargin]);

    // FIX: Reset ALL pricing state when switching to a different product
    // This prevents state bleeding between products (old values showing for new product)
    useEffect(() => {
        setTargetMargin(0);
        setSimulatedPrice(0);
        setOriginalVals({ price: 0, margin: 0 });
        setShowStrategy(false);
    }, [adId]);

    // Fetch ad and competitors on mount
    useEffect(() => {
        if (adId) {
            setLoading(true);
            Promise.all([
                api.get(`/ads/${adId}`),
                api.get(`/ads/${adId}/competitors`)
            ]).then(([adRes, compRes]) => {
                setAd(adRes.data);
                setCompetitorCount(compRes.data.length);
                if (compRes.data.length > 0) {
                    setScannedCompetitors(compRes.data);
                }
            }).catch(err => {
                console.error(err);
            }).finally(() => {
                setLoading(false);
            });
        }
    }, [adId]);

    // Initialize Simulation when entering the tab - ALWAYS recalculate
    useEffect(() => {
        if (activeTab === 'margin' && ad) {
            // Calculate effective price (promo price if active)
            const effectivePrice = (ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price)
                ? ad.promotion_price
                : ad.price;

            // ONLY initialize if targetMargin is 0 (first time entering tab)
            if (targetMargin === 0) {
                const currentMargin = (ad.financials as any)?.net_margin_percent || ad.margin_percent || 0;

                // User Request Fix: Only load stored target if strategy is ACTIVE.
                // If strategy is NOT active, we force a reset to current margin (0% breakeven relative to current).
                // This prevents "auto-saved drafts" from confusing the user on refresh.
                const isActive = ad.strategy_start_price && ad.strategy_start_price > 0;
                const savedTarget = (isActive && ad.target_margin) ? ad.target_margin * 100 : null;

                // If saved target exists (and strategy is active), use it; otherwise use CURRENT margin
                const initialMargin = savedTarget !== null && savedTarget > 0 ? savedTarget : currentMargin;

                // Set original values first - USE EFFECTIVE PRICE
                setOriginalVals({ price: effectivePrice, margin: currentMargin });

                // Set margin to stored value or current value
                setTargetMargin(initialMargin);

                // Set simulated price: Recalculate based on target margin to ensure sync (Fix "Random Value" issue)
                if (Math.abs(initialMargin - currentMargin) < 0.1) {
                    setSimulatedPrice(effectivePrice);
                } else {
                    const currentMarginDec = currentMargin / 100;
                    const targetMarginDec = initialMargin / 100;
                    // Derived costs from current price/margin
                    const cmValue = (currentMarginDec * effectivePrice);
                    const derivedCost = effectivePrice - cmValue;
                    
                    const newSimPrice = derivedCost / (1 - targetMarginDec);
                    setSimulatedPrice(newSimPrice > 0 ? newSimPrice : effectivePrice);
                }
            }
        }
    }, [activeTab, ad, targetMargin]);

    // Fetch Pricing Resolution Effect (Fase 2.6)
    useEffect(() => {
        if ((activeTab === 'margin' || activeTab === 'fiscal') && ad) {
            const fetchResolution = async () => {
                setIsResolvingPricing(true);
                try {
                    const res = await api.get(`/pricing/resolve/${ad.id}`);
                    setPricingResolution(res.data);
                } catch (err: any) {
                    console.error("Erro no resolver:", err);
                    setPricingResolution(null);
                } finally {
                    setIsResolvingPricing(false);
                }
            };
            fetchResolution();
        }
    }, [activeTab, ad]);


    const handleProtectClick = () => {
        setIsProtectionModalOpen(true);
        if (competitorCount > 0) {
            setProtectionState('success'); // Already protected
        } else {
            setProtectionState('intro');
        }
    }


    const handleMarginClick = () => {
        setActiveTab('margin');
        // Initialization is handled by the useEffect above when activeTab changes
    };



    const updateSimulation = (newMargin: number, skipClamping = false) => {
        setTargetMargin(newMargin);
        if (!ad) return;

        // Use effective price (promo price if active)
        const effectivePrice = (ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price)
            ? ad.promotion_price
            : ad.price;
        const price = originalVals.price || effectivePrice || 0;
        if (price <= 0) return;

        const currentMarginPct = (ad.financials as any)?.net_margin_percent || ad.margin_percent || 0;
        const currentMarginDec = currentMarginPct / 100;
        const currentCosts = price * (1 - currentMarginDec);

        // If skipping clamping (Discrete Slider), just set values directly
        if (skipClamping) {
            const targetMarginDec = newMargin / 100;
            if (targetMarginDec >= 0.99) {
                setSimulatedPrice(price); // Safety
                return;
            }
            const newPrice = currentCosts / (1 - targetMarginDec);
            setSimulatedPrice(newPrice);
            return;
        }

        // --- OLD CLAMPING LOGIC (Kept for fallback) ---
        // ... (rest of old logic hidden/replaced by this block return)
        // SIMPLE CORRECT FORMULA:
        // Margin = (Price - Costs) / Price
        // Therefore: Costs = Price * (1 - Margin)
        // And: NewPrice = Costs / (1 - NewMargin)

        // FIX: Use larger of 5% or R$5.00 as minimum step (was 1% which is too restrictive for low-priced items)
        // For R$ 86.53: minStep = R$ 5.00 → range R$ 81.53 to R$ 91.53
        // For R$ 1000: minStep = R$ 50.00 → range R$ 950 to R$ 1050
        const minStep = Math.max(price * 0.05, 5.00);
        const maxAllowedPrice = price + minStep;
        const minAllowedPrice = Math.max(price - minStep, 1); // Never go below R$ 1

        let maxAllowedMarginPct = 99;
        let minAllowedMarginPct = -99; // Allow negative margins if needed (loss leader)

        if (maxAllowedPrice > 0) {
            const maxAllowedMarginDec = 1 - (currentCosts / maxAllowedPrice);
            maxAllowedMarginPct = maxAllowedMarginDec * 100;
        }

        if (minAllowedPrice > 0) {
            const minAllowedMarginDec = 1 - (currentCosts / minAllowedPrice);
            minAllowedMarginPct = minAllowedMarginDec * 100;
        }

        // Clamp the new margin strictly within the +/- 1% window
        // But allow it if the user is dragging; simply clamping the setter is enough.

        let effectiveMargin = newMargin;
        if (newMargin > maxAllowedMarginPct) effectiveMargin = maxAllowedMarginPct;
        if (newMargin < minAllowedMarginPct) effectiveMargin = minAllowedMarginPct;

        setTargetMargin(effectiveMargin);

        // Update Simulated Price based on Effective Margin
        const targetMarginDec = effectiveMargin / 100;

        // If close to original, revert to original price (Center "Deadzone")
        if (Math.abs(effectiveMargin - currentMarginPct) < 0.05) {
            setSimulatedPrice(price);
            return;
        }

        // Calculate new price
        // Safety cap for calc
        if (targetMarginDec >= 0.95) {
            const safeMax = price * 1.01;
            setSimulatedPrice(safeMax);
            return;
        }

        const newPrice = currentCosts / (1 - targetMarginDec);
        setSimulatedPrice(newPrice);
    };

    // Helper to calculate pricing steps
    const calculateSteps = (start: number, target: number) => {
        const steps = [];
        const totalSteps = 4;
        const diff = target - start;
        const stepSize = diff / totalSteps;

        for (let i = 0; i <= totalSteps; i++) {
            steps.push({
                step: i,
                price: start + (stepSize * i),
                date: new Date(Date.now() + (i * 24 * 60 * 60 * 1000)).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) // Exemplary date
            });
        }
        return steps;
    };

    const confirmProtection = async () => {
        setProtectionState('scanning');
        try {
            // 1. Fetch current competitors to see if we have data
            const res = await api.get(`/ads/${adId}/competitors`);
            setScannedCompetitors(res.data);

            // Artificial delay for "Scanning" effect to let user read the progress
            setTimeout(async () => {
                // 2. If we have competitors, we sync them. 
                // If not, we still move to results but prompting for addition.
                if (res.data.length > 0) {
                    await api.post(`/ads/${adId}/competitors/sync`);
                }
                setProtectionState(res.data.length > 0 ? 'success' : 'results');
            }, 2000);

        } catch (error) {
            console.error("Protection error", error);
            setProtectionState('results'); // Fallback to results (likely empty)
        }
    };

    const handleNextImage = (e?: React.MouseEvent) => {
        e?.stopPropagation();
        if (ad && ad.pictures) {
            setActiveImageIndex((prev) => (prev + 1) % ad.pictures!.length);
        }
    };

    const handlePrevImage = (e?: React.MouseEvent) => {
        e?.stopPropagation();
        if (ad && ad.pictures) {
            setActiveImageIndex((prev) => (prev - 1 + ad.pictures!.length) % ad.pictures!.length);
        }
    };

    // Reset image index when ad changes
    useEffect(() => {
        setActiveImageIndex(0);
    }, [adId]);

    const [performancePeriod, setPerformancePeriod] = useState('30d');
    const [showDetails, setShowDetails] = useState(false);

    useEffect(() => {
        const fetchAd = async () => {
            try {
                const res = await api.get(`/ads/${adId}`);
                setAd(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchAd();
    }, [adId]);

    // Click outside to close
    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) onClose();
    };

    // Lifecycle Calculation
    const getLifecycleStage = () => {
        if (!ad) return null;
        const ageDays = (new Date().getTime() - new Date(ad.created_at || new Date()).getTime()) / (1000 * 3600 * 24);
        const sales = ad.sales_30d || 0;

        if (sales < 10 && ageDays < 60) return { name: 'Validação', step: 1, color: 'blue', icon: TestTube2 };
        if (sales >= 10 && (ad.sales_7d_change || 0) > 0) return { name: 'Crescimento', step: 2, color: 'purple', icon: TrendingUp };
        if (sales > 30) return { name: 'Consolidação', step: 3, color: 'emerald', icon: Award };
        return { name: 'Recuperação', step: 4, color: 'amber', icon: AlertTriangle };
    };

    const lifecycle = getLifecycleStage();

    if (!activeTab) setActiveTab('overview');
    if (!adId) return null;

    return (
        <>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 text-slate-200">
                <div
                    className="absolute inset-0 bg-black/90 backdrop-blur-md transition-opacity"
                    onClick={onClose}
                />

                <div className="relative w-[92vw] max-w-[1600px] h-[90vh] max-h-none bg-[#0c0d12] rounded-[24px] border border-white/10 shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">
                    {/* 1. HEADER: Compact & Actionable */}
                    <div className="w-full bg-[#13141b] border-b border-white/5 px-6 py-4 flex items-center justify-between shrink-0">
                        <div className="flex items-center gap-4 min-w-0 flex-1 mr-4">
                            {loading ? (
                                <div className="w-12 h-12 rounded-lg bg-white/5 animate-pulse shrink-0" />
                            ) : ad ? (
                                <div className="w-12 h-12 rounded-lg bg-white/5 border border-white/5 p-1 shrink-0">
                                    <img src={ad.thumbnail} alt="Thumb" className="w-full h-full object-contain" />
                                </div>
                            ) : null}

                            <div className="flex flex-col min-w-0 py-1">
                                {loading ? (
                                    <div className="h-6 w-48 bg-white/5 rounded animate-pulse mb-1" />
                                ) : (
                                    <h2 className="text-sm sm:text-base font-bold text-white leading-tight line-clamp-2" title={ad?.title}>
                                        {ad?.title || 'Carregando...'}
                                    </h2>
                                )}
                                <div className="flex items-center gap-2 text-[10px] sm:text-[11px] text-slate-500 font-mono mt-1 whitespace-nowrap">
                                    <span className="text-slate-400">SKU:</span>
                                    <span className="select-all text-slate-300">{ad?.sku || '---'}</span>
                                    <span className="w-1 h-1 rounded-full bg-slate-700 mx-1" />
                                    <span className="text-slate-400">ID:</span>
                                    <span className="text-slate-300 font-bold select-all">{adId}</span>
                                    {ad && <span className={`ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border ${ad.is_full ? 'bg-[#00A650]/20 text-[#00A650] border-[#00A650]/30' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>{ad.is_full ? 'FULL' : (ad.shipping_mode === 'me2' ? 'Envios' : 'Próprio')}</span>}
                                </div>
                            </div>
                        </div>

                        {/* Lifecycle Stepper (Compact & Actionable) */}
                        {!loading && ad && lifecycle && (
                            <div className="hidden xl:flex items-center gap-2 px-4 py-2 rounded-full bg-black/40 border border-white/5 mx-4">
                                {['Validação', 'Crescimento', 'Consolidação'].map((step, idx) => {
                                    const isCurrent = lifecycle.step === idx + 1;
                                    const isPast = (lifecycle.step || 0) > idx + 1;
                                    const color = lifecycle.color || 'blue';

                                    return (
                                        <div key={step} className="flex items-center group cursor-pointer">
                                            <div className={`flex items-center gap-2 px-2 py-1 rounded-lg transition-all ${isCurrent
                                                ? `bg-${color}-500/10 text-${color}-400 ring-1 ring-${color}-500/20`
                                                : isPast
                                                    ? 'text-slate-500 hover:text-slate-300'
                                                    : 'text-slate-700'
                                                }`}>
                                                <div className={`w-1.5 h-1.5 rounded-full ${isCurrent ? `bg-${color}-500 animate-pulse` : isPast ? 'bg-slate-500' : 'bg-slate-800'
                                                    }`} />
                                                <span className="text-[10px] uppercase font-bold tracking-wider">{step}</span>
                                            </div>
                                            {idx < 2 && <div className={`w-4 h-px mx-1 ${isPast ? 'bg-slate-600' : 'bg-white/5'}`} />}
                                        </div>
                                    )
                                })}
                            </div>
                        )}

                        {/* RANKING HEADER (New) */}
                        <div className="hidden lg:flex flex-col mx-8 px-6 border-l border-r border-white/5 h-10 justify-center">
                            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest mb-0.5">
                                <Trophy size={12} className="text-yellow-500" /> Ranking
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="text-sm font-bold text-white"># --</span>
                                <span className="text-[10px] bg-white/5 px-2 rounded-full text-slate-400">Pá¡g. --</span>
                                <span className="text-[10px] text-slate-500 truncate max-w-[120px]">---</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-3 shrink-0">
                            {/* MOVED STATUS HERE */}
                            {ad && (
                                <div className={`px-3 py-1.5 rounded-full border text-xs font-bold uppercase flex items-center gap-2 ${ad.status === 'active'
                                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                                    : 'bg-slate-800/50 border-slate-700 text-slate-400'
                                    }`}>
                                    <Activity size={14} />
                                    {ad.status === 'active' ? 'Ativo' : 'Pausado'}
                                </div>
                            )}
                            <div className="w-px h-8 bg-white/10 mx-1" />
                            <button onClick={onClose} className="p-2 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
                                <X size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Main Content - No Loader, immediate display with skeleton fallback if needed later */}
                    <AnimatePresence mode="wait">
                        {ad ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 20 }}
                                className="flex-1 flex flex-col overflow-y-auto custom-scrollbar bg-[#09090b] pb-20"
                            >

                                {/* 2. KPI RIBBON: High-Level Metrics */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 pt-6 pb-2">
                                    {/* Price Card (1st) */}
                                    <div className="bg-[#13141b] p-5 rounded-2xl border border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400"><DollarSign size={18} /></div>
                                            {/* Discount badge */}
                                            {ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price && (
                                                <span className="px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 text-[10px] font-bold border border-rose-500/30">
                                                    -{Math.round(((ad.price - ad.promotion_price) / ad.price) * 100)}% OFF
                                                </span>
                                            )}
                                        </div>
                                        <div className="text-2xl font-bold text-white mb-1">
                                            {ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price ? (
                                                <div className="flex flex-col">
                                                    <span className="text-sm line-through text-slate-500 font-medium">
                                                        {ad.price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                    </span>
                                                    <span className="text-emerald-400">
                                                        {ad.promotion_price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                    </span>
                                                </div>
                                            ) : (
                                                ad.price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                                            )}
                                        </div>
                                        <p className="text-xs text-slate-500 font-medium">
                                            {ad.promotion_price && ad.promotion_price > 0 && ad.promotion_price < ad.price ? 'Preço Promocional' : 'Preço Atual'}
                                        </p>
                                    </div>

                                    {/* Visits Card (2nd) */}
                                    <div className="bg-[#13141b] p-5 rounded-2xl border border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400"><TrendingUp size={18} /></div>
                                        </div>
                                        <div className="text-2xl font-bold text-white mb-1">{ad.total_visits ? ad.total_visits.toLocaleString('pt-BR') : '0'}</div>
                                        <p className="text-xs text-slate-500 font-medium">Visitas</p>
                                    </div>

                                    {/* Sales Card (3rd) */}
                                    <div className="bg-[#13141b] p-5 rounded-2xl border border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400"><Package size={18} /></div>
                                        </div>
                                        <div className="text-2xl font-bold text-white mb-1">{ad.sold_quantity || 0}</div>
                                        <p className="text-xs text-slate-500 font-medium">Vendas Totais</p>
                                    </div>

                                    {/* Conversion Card (4th) */}
                                    <div className="bg-[#13141b] p-5 rounded-2xl border border-white/5 relative overflow-hidden group hover:border-white/10 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400"><BarChart3 size={18} /></div>
                                        </div>
                                        <div className="text-2xl font-bold text-emerald-400 mb-1">
                                            {ad.total_visits ? ((ad.sold_quantity || 0) / ad.total_visits * 100).toFixed(2) : '0.00'}%
                                        </div>
                                        <p className="text-xs text-slate-500 font-medium">Conversão</p>
                                    </div>
                                </div>

                                {/* Slim Strategy Divider with Premium Line Shimmer */}
                                <div className="mx-16 my-6 flex items-center gap-3">
                                    {/* Left line with inline shimmer */}
                                    <div className={`flex-1 h-px relative overflow-hidden ${lifecycle?.name === 'Validação' ? 'bg-blue-500/20' :
                                        lifecycle?.name === 'Crescimento' ? 'bg-purple-500/20' :
                                            lifecycle?.name === 'Consolidação' ? 'bg-emerald-500/20' :
                                                lifecycle?.name === 'Recuperação' ? 'bg-amber-500/20' :
                                                    'bg-slate-500/20'
                                        }`}>
                                        <div className={`absolute inset-0 w-1/4 h-full bg-gradient-to-r from-transparent ${lifecycle?.name === 'Validação' ? 'via-blue-400' :
                                            lifecycle?.name === 'Crescimento' ? 'via-purple-400' :
                                                lifecycle?.name === 'Consolidação' ? 'via-emerald-400' :
                                                    lifecycle?.name === 'Recuperação' ? 'via-amber-400' :
                                                        'via-slate-400'
                                            } to-transparent animate-[slideRight_3s_ease-in-out_infinite]`}></div>
                                    </div>

                                    {/* Center icon */}
                                    <div className={`${lifecycle?.name === 'Validação' ? 'text-blue-400' :
                                        lifecycle?.name === 'Crescimento' ? 'text-purple-400' :
                                            lifecycle?.name === 'Consolidação' ? 'text-emerald-400' :
                                                lifecycle?.name === 'Recuperação' ? 'text-amber-400' :
                                                    'text-slate-400'
                                        }`}>
                                        {lifecycle?.name === 'Validação' && <TestTube2 size={14} />}
                                        {lifecycle?.name === 'Crescimento' && <TrendingUp size={14} />}
                                        {lifecycle?.name === 'Consolidação' && <Award size={14} />}
                                        {lifecycle?.name === 'Recuperação' && <AlertTriangle size={14} />}
                                        {!lifecycle && <Activity size={14} />}
                                    </div>

                                    {/* Right line with inline shimmer (delayed) */}
                                    <div className={`flex-1 h-px relative overflow-hidden ${lifecycle?.name === 'Validação' ? 'bg-blue-500/20' :
                                        lifecycle?.name === 'Crescimento' ? 'bg-purple-500/20' :
                                            lifecycle?.name === 'Consolidação' ? 'bg-emerald-500/20' :
                                                lifecycle?.name === 'Recuperação' ? 'bg-amber-500/20' :
                                                    'bg-slate-500/20'
                                        }`}>
                                        <div className={`absolute inset-0 w-1/4 h-full bg-gradient-to-r from-transparent ${lifecycle?.name === 'Validação' ? 'via-blue-400' :
                                            lifecycle?.name === 'Crescimento' ? 'via-purple-400' :
                                                lifecycle?.name === 'Consolidação' ? 'via-emerald-400' :
                                                    lifecycle?.name === 'Recuperação' ? 'via-amber-400' :
                                                        'via-slate-400'
                                            } to-transparent animate-[slideRight_3s_ease-in-out_infinite]`} style={{ animationDelay: '1.5s' }}></div>
                                    </div>
                                </div>

                                {/* 3. MAIN DASHBOARD GRID */}
                                <div className="p-6 pt-0 flex flex-col">

                                    {/* LEFT: Product Identity & Logistics (1 Col) */}

                                    {/* RIGHT: Detailed Analysis Tabs (2 Cols) */}
                                    <div className="flex flex-col bg-[#13141b] rounded-2xl border border-white/5">
                                        <div className="flex items-center gap-1 p-2 border-b border-white/5 overflow-x-auto">
                                            <button
                                                onClick={() => setActiveTab('overview')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'overview' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <LayoutDashboard size={14} /> Financeiro
                                            </button>
                                            <button
                                                onClick={() => setActiveTab('performance')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'performance' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <BarChart3 size={14} /> Desempenho
                                            </button>
                                            <button
                                                onClick={() => setActiveTab('health')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'health' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <Activity size={14} /> Saúde
                                            </button>
                                            <button
                                                onClick={() => setActiveTab('competition')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'competition' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <Search size={14} /> Concorrência
                                            </button>
                                            <div
                                                onClick={() => setActiveTab('margin')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'margin' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <Calculator className="w-4 h-4" />
                                                Precificação
                                            </div>
                                            <div
                                                onClick={() => setActiveTab('fiscal')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'fiscal' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-500 hover:text-indigo-400'}`}
                                            >
                                                <Building2 className="w-4 h-4" />
                                                Ficha Fiscal
                                            </div>
                                        </div>

                                        <div className="p-6">
                                            {activeTab === 'overview' && (
                                                <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">

                                                    {/* 1. HERO METRICS ROW - 3 Wide Cards, Compact Height */}
                                                    <div className="grid grid-cols-3 gap-2">
                                                        {/* Revenue */}
                                                        <Tooltip title="Receita" content="Faturamento total do anúncio (preço × quantidade vendida)" position="bottom">
                                                            <div className="bg-[#0e0f14] p-3 rounded-lg border border-emerald-500/20 hover:border-emerald-500/40 transition-all cursor-help h-[72px] flex flex-col justify-between">
                                                                <div className="flex justify-between items-center">
                                                                    <p className="text-[10px] font-semibold text-emerald-400/80 uppercase tracking-wide">Receita</p>
                                                                    <DollarSign size={12} className="text-emerald-500" />
                                                                </div>
                                                                <div className="text-lg font-bold text-white tabular-nums">
                                                                    {((ad.sold_quantity || 0) * ad.price).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })}
                                                                </div>
                                                                <div className="h-0.5 w-full bg-slate-800/50 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-emerald-500/60 w-full rounded-full"></div>
                                                                </div>
                                                            </div>
                                                        </Tooltip>

                                                        {/* Ads Spend (Total) */}
                                                        <Tooltip title="Ads (Total)" content="Total investido em campanhas de anúncios pagos no Mercado Ads" position="bottom">
                                                            <div className="bg-[#0e0f14] p-3 rounded-lg border border-blue-500/20 hover:border-blue-500/40 transition-all cursor-help h-[72px] flex flex-col justify-between">
                                                                <div className="flex justify-between items-center">
                                                                    <p className="text-[10px] font-semibold text-blue-400/80 uppercase tracking-wide">Ads Total</p>
                                                                    <Megaphone size={12} className="text-blue-500" />
                                                                </div>
                                                                <div className="text-lg font-bold text-slate-400 tabular-nums">
                                                                    R$ 0,00
                                                                </div>
                                                                <div className="h-0.5 w-full bg-slate-800/50 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-blue-500/30 w-0 rounded-full"></div>
                                                                </div>
                                                            </div>
                                                        </Tooltip>

                                                        {/* Ads Sales */}
                                                        <Tooltip title="Ads Sales" content="Vendas geradas diretamente por campanhas de anúncios pagos" position="bottom">
                                                            <div className="bg-[#0e0f14] p-3 rounded-lg border border-purple-500/20 hover:border-purple-500/40 transition-all cursor-help h-[72px] flex flex-col justify-between">
                                                                <div className="flex justify-between items-center">
                                                                    <p className="text-[10px] font-semibold text-purple-400/80 uppercase tracking-wide">Ads Sales</p>
                                                                    <Target size={12} className="text-purple-500" />
                                                                </div>
                                                                <div className="text-lg font-bold text-slate-400 tabular-nums">
                                                                    R$ 0,00
                                                                </div>
                                                                <div className="h-0.5 w-full bg-slate-800/50 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-purple-500/30 w-0 rounded-full"></div>
                                                                </div>
                                                            </div>
                                                        </Tooltip>
                                                    </div>

                                                    {/* 2. COMPACT BREAKDOWN GRID */}
                                                    <div>
                                                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">

                                                            {/* Creation Date */}
                                                            <Tooltip title="Criação" content="Data em que o anúncio foi criado no Mercado Livre" position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Criação</span>
                                                                        <Calendar size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-sm font-semibold text-white group-hover:text-white transition-colors">
                                                                            {ad.start_time ? new Date(ad.start_time).toLocaleDateString('pt-BR') : '-'}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500">
                                                                            {ad.start_time ? `${Math.floor((new Date().getTime() - new Date(ad.start_time).getTime()) / (1000 * 3600 * 24))} dias` : '-'}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* ACOS */}
                                                            <Tooltip title="ACOS" content={<><strong>Advertising Cost of Sales</strong><br />Custo de publicidade / Vendas de anúncios</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-amber-500/20 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">ACOS</span>
                                                                        <Activity size={12} className="text-amber-500 group-hover:text-amber-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-sm font-semibold text-slate-400 group-hover:text-slate-300 transition-colors">
                                                                            0.00%
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500">
                                                                            Custo/Vendas
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* ROAS */}
                                                            <Tooltip title="ROAS" content={<><strong>Return on Advertising Spend</strong><br />Retorno sobre investimento em anúncios</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-cyan-500/20 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">ROAS</span>
                                                                        <TrendingUp size={12} className="text-cyan-500 group-hover:text-cyan-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-sm font-semibold text-slate-400 group-hover:text-slate-300 transition-colors">
                                                                            0.00x
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500">
                                                                            Retorno
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* TACOS */}
                                                            <Tooltip title="TACOS" content={<><strong>Total Advertising Cost of Sales</strong><br />Custo de ads total / Vendas totais</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-orange-500/20 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">TACOS</span>
                                                                        <Activity size={12} className="text-orange-500 group-hover:text-orange-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-sm font-semibold text-slate-400 group-hover:text-slate-300 transition-colors">
                                                                            0.00%
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500">
                                                                            Total
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Product Cost */}
                                                            <Tooltip title="Custo Produto" content="Valor de aquisição do produto junto ao fornecedor, incluindo custos de fabricação" position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Custo Produto</span>
                                                                        <Package size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{ad.cost?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) || 'R$ 0,00'}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            {((ad.cost || 0) / ad.price * 100).toFixed(1)}% do preço
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* DIFAL */}
                                                            <Tooltip title="DIFAL" content={<><span className="text-rose-400 font-bold">Diferencial de Alíquota do ICMS</span><br />Imposto interestadual cobrado quando comprador e vendedor estão em estados diferentes</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400 border-b border-dotted border-slate-700">DIFAL</span>
                                                                        <FileText size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-sm font-mono font-medium text-slate-500 group-hover:text-slate-400 transition-colors">
                                                                            R$ 0,00
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            ICMS Interestadual
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Tax */}
                                                            <Tooltip title="Impostos (DAS)" content={<><span className="text-rose-400 font-bold">Documento de Arrecadação do Simples Nacional</span><br />Imposto unificado para empresas do Simples Nacional que inclui IRPJ, CSLL, PIS, COFINS, etc.</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Impostos (DAS)</span>
                                                                        <FileText size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{ad.financials?.tax_cost?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) || 'R$ 0,00'}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            {((ad.financials?.tax_cost || 0) / ad.price * 100).toFixed(1)}%
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* ML Fee */}
                                                            <Tooltip title="Comissão ML" content={<><span className="text-rose-400 font-bold">Comissão Mercado Livre</span><br />Taxa percentual cobrada pelo Mercado Livre sobre cada venda realizada na plataforma</>} position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Comissão ML</span>
                                                                        <Percent size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{ad.financials?.commission_cost?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) || 'R$ 0,00'}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            {((ad.financials?.commission_cost || 0) / ad.price * 100).toFixed(1)}%
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Shipping (Frete) */}
                                                            <Tooltip title="Frete" content="Custo de envio do produto até o cliente final, pago ao Mercado Envios" position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Frete</span>
                                                                        <Truck size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{((ad.financials?.shipping_cost || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            Envio ao cliente
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Fixed Costs */}
                                                            <Tooltip title="Custos Fixos" content={
                                                                <div className="space-y-2 w-64">
                                                                    <div className="flex justify-between text-[10px]">
                                                                        <span className="text-slate-400">Rateio Mensal:</span>
                                                                        <span className="text-rose-400 font-bold">-{((ad.financials?.fixed_cost_share || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                                                                    </div>
                                                                    <div className="border-t border-slate-700/50 pt-2 text-[9px] text-slate-500 space-y-1">
                                                                        <p>• Água • Luz • Internet • Aluguel</p>
                                                                        <p>• Pessoal • Contador • Manutenção</p>
                                                                        <p>• Softwares • Equipamentos</p>
                                                                    </div>
                                                                    <div className="flex justify-between text-[10px] pt-1 border-t border-slate-700/50">
                                                                        <span className="text-slate-400">% do Preço:</span>
                                                                        <span className="text-slate-300 font-medium">{((ad.financials?.fixed_cost_share || 0) / ad.price * 100).toFixed(1)}%</span>
                                                                    </div>
                                                                </div>
                                                            } position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400 border-b border-dotted border-slate-700">Custos Fixos</span>
                                                                        <Building2 size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{((ad.financials?.fixed_cost_share || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            {((ad.financials?.fixed_cost_share || 0) / ad.price * 100).toFixed(1)}% do preço
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Variable Costs */}
                                                            <Tooltip title="Custos Variáveis" content={
                                                                <div className="space-y-2 w-64">
                                                                    <div className="flex justify-between text-[10px]">
                                                                        <span className="text-slate-400">Custo por Unidade:</span>
                                                                        <span className="text-rose-400 font-bold">-{((((ad.financials as Record<string, unknown>)?.variable_cost as number) || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                                                                    </div>
                                                                    <div className="border-t border-slate-700/50 pt-2 text-[9px] text-slate-500 space-y-1">
                                                                        <p>• Fita adesiva • Plástico bolha</p>
                                                                        <p>• Caixa / Embalagem • Etiquetas</p>
                                                                        <p>• Lacre • Papel de seda</p>
                                                                    </div>
                                                                    <div className="flex justify-between text-[10px] pt-1 border-t border-slate-700/50">
                                                                        <span className="text-slate-400">% do Preço:</span>
                                                                        <span className="text-slate-300 font-medium">{((((ad.financials as Record<string, unknown>)?.variable_cost as number) || 0) / ad.price * 100).toFixed(1)}%</span>
                                                                    </div>
                                                                </div>
                                                            } position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400 border-b border-dotted border-slate-700">C. Variáveis</span>
                                                                        <Package size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{((((ad.financials as Record<string, unknown>)?.variable_cost as number) || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            Embalagem/Un.
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Inbound Freight */}
                                                            <Tooltip title="Envio Full" content="Custo de envio do produto até o centro de distribuição Full do Mercado Livre" position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Envio Full</span>
                                                                        <Truck size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{((ad.financials?.inbound_freight_cost || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            {((ad.financials?.inbound_freight_cost || 0) / ad.price * 100).toFixed(1)}% do preço
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Daily Storage */}
                                                            <Tooltip title="Armazenagem" content="Custo diário de armazenamento do produto no centro de distribuição Full" position="bottom">
                                                                <div className="bg-[#0e0f14] p-3 rounded-lg border border-white/5 hover:border-white/10 hover:bg-[#13141b] transition-all group flex flex-col justify-between h-20 cursor-help">
                                                                    <div className="flex items-center justify-between">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Armazenagem</span>
                                                                        <Archive size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                                                    </div>
                                                                    <div>
                                                                        <p className="text-base font-mono font-semibold text-rose-400 group-hover:text-rose-300 transition-colors">
                                                                            -{((ad.financials?.storage_cost || 0)).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>
                                                                        <p className="text-[10px] text-slate-500 font-mono">
                                                                            Custo Diário
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                            {/* Net Margin (Highlighted Hero - Compact) */}
                                                            <Tooltip title="Margem Líquida" content={<><span className="text-emerald-400 font-bold">Lucro líquido por unidade vendida</span><br />Valor que sobra após descontar todos os custos, impostos e comissões</>} position="bottom">
                                                                <div className="bg-gradient-to-br from-emerald-950/20 to-[#0e0f14] p-3 rounded-lg border border-emerald-500/30 group hover:border-emerald-500/50 transition-all flex flex-col justify-between h-20 relative overflow-hidden cursor-help">
                                                                    <div className="absolute top-0 right-0 p-2 opacity-10">
                                                                        <Wallet size={32} className="text-emerald-400" />
                                                                    </div>

                                                                    <div className="flex items-center justify-between relative z-10">
                                                                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-500">Margem Líq.</span>
                                                                        <Wallet size={12} className="text-emerald-500" />
                                                                    </div>
                                                                    <div className="relative z-10">
                                                                        <p className="text-base font-mono font-bold text-emerald-400">
                                                                            {(ad.financials?.net_margin_value || ad.margin_value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                                        </p>

                                                                        <div className="flex items-center justify-between mt-1">
                                                                            <div className="w-12 bg-slate-800/50 rounded-full h-1 overflow-hidden">
                                                                                <div
                                                                                    className="h-full bg-emerald-500 rounded-full"
                                                                                    style={{ width: `${Math.min(Math.max((ad.financials?.net_margin_percent || 0), 0), 100)}%` }}
                                                                                />
                                                                            </div>
                                                                            <span className="text-[9px] text-emerald-500 font-mono font-bold">
                                                                                {((ad.financials?.net_margin_percent || ad.margin_percent || 0)).toFixed(2)}%
                                                                            </span>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </Tooltip>

                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {activeTab === 'performance' && (
                                                <div className="space-y-6">
                                                    <AdPerformanceCharts ad={ad} />
                                                </div>
                                            )}

                                            {activeTab === 'health' && (
                                                <div className="space-y-6 h-full overflow-hidden flex flex-col">
                                                    {ad.intelligence?.health ? (
                                                        <div className="grid grid-cols-12 gap-6 h-full">
                                                            {/* Overall Score - Left Column */}
                                                            <div className="col-span-12 md:col-span-4 bg-[#09090b] rounded-xl p-6 border border-white/5 flex flex-col items-center justify-center relative overflow-hidden group">
                                                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                                                <div className="relative w-40 h-40 flex items-center justify-center mb-6">
                                                                    <svg className="w-full h-full transform -rotate-90 drop-shadow-2xl">
                                                                        <circle cx="80" cy="80" r="70" stroke="#1e293b" strokeWidth="12" fill="transparent" />
                                                                        <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent"
                                                                            strokeDasharray={440}
                                                                            strokeDashoffset={440 - (440 * ad.intelligence.health.score) / 100}
                                                                            strokeLinecap="round"
                                                                            className={`${ad.intelligence.health.score > 70 ? 'text-emerald-500' : ad.intelligence.health.score > 40 ? 'text-amber-500' : 'text-rose-500'} transition-all duration-1000 filter drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]`}
                                                                        />
                                                                    </svg>
                                                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                                                                        <span className="text-5xl font-black text-white tracking-tighter">{Math.round(ad.intelligence.health.score)}</span>
                                                                        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Pontos</span>
                                                                    </div>
                                                                </div>
                                                                <h3 className="text-xl font-bold text-white text-center mb-2">{ad.intelligence.health.label}</h3>
                                                                <p className="text-xs text-slate-400 text-center max-w-[200px] leading-relaxed">
                                                                    {ad.intelligence.health.score > 70
                                                                        ? "Seu anúncio está otimizado para máxima Conversão."
                                                                        : "Existem oportunidades claras de melhoria para este anúncio."}
                                                                </p>
                                                            </div>

                                                            {/* Sections Breakdown - Right Column */}
                                                            <div className="col-span-12 md:col-span-8 bg-[#09090b] rounded-xl border border-white/5 overflow-y-auto custom-scrollbar p-1">
                                                                <div className="grid grid-cols-1 gap-1 p-2">
                                                                    {Object.entries(ad.intelligence.health.sections).map(([key, section]: [string, any]) => (
                                                                        <div key={key} className="bg-[#13141b] p-4 rounded-lg border border-white/5 hover:border-white/10 transition-colors">
                                                                            <div className="flex items-center gap-4 mb-3">
                                                                                <div className={`p-2 rounded-lg ${key === 'title' ? 'bg-blue-500/10 text-blue-400' : key === 'media' ? 'bg-purple-500/10 text-purple-400' : 'bg-amber-500/10 text-amber-400'}`}>
                                                                                    {key === 'title' ? <FileText size={18} /> : key === 'media' ? <Sparkles size={18} /> : <Tag size={18} />}
                                                                                </div>
                                                                                <div className="flex-1">
                                                                                    <div className="flex justify-between items-center mb-1">
                                                                                        <h4 className="text-sm font-bold text-white capitalize">
                                                                                            {key === 'title' ? 'Qualidade do Título' : key === 'media' ? 'Mídia & Imagens' : 'Atributos & Ficha'}
                                                                                        </h4>
                                                                                        <span className={`text-xs font-bold ${section.score === section.max_score ? 'text-emerald-400' : 'text-slate-400'}`}>
                                                                                            {section.score}/{section.max_score} pts
                                                                                        </span>
                                                                                    </div>
                                                                                    <div className="w-full bg-slate-800/50 rounded-full h-1.5 overflow-hidden">
                                                                                        <div
                                                                                            className={`h-full rounded-full transition-all duration-1000 ${key === 'title' ? 'bg-blue-500' : key === 'media' ? 'bg-purple-500' : 'bg-amber-500'}`}
                                                                                            style={{ width: `${(section.score / section.max_score) * 100}%` }}
                                                                                        ></div>
                                                                                    </div>
                                                                                </div>
                                                                            </div>

                                                                            {/* Detailed Criteria */}
                                                                            <div className="space-y-2 mt-2">
                                                                                {section.criteria && section.criteria.map((criterion: any, idx: number) => (
                                                                                    <div key={idx} className="flex items-start gap-2 text-xs p-2 rounded bg-white/5 hover:bg-white/10 transition-colors group">
                                                                                        {criterion.met ? (
                                                                                            <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                                                                                        ) : (
                                                                                            <AlertTriangle size={14} className="text-amber-400 shrink-0 mt-0.5" />
                                                                                        )}
                                                                                        <div className="flex-1">
                                                                                            <p className={criterion.met ? "text-slate-300" : "text-amber-100/80"}>
                                                                                                {criterion.label}
                                                                                            </p>
                                                                                            {criterion.hint && !criterion.met && (
                                                                                                <p className="text-[10px] text-slate-500 mt-1">{criterion.hint}</p>
                                                                                            )}
                                                                                        </div>
                                                                                        {criterion.score > 0 && (
                                                                                            <span className="text-[10px] font-mono text-slate-500">
                                                                                                +{criterion.score}
                                                                                            </span>
                                                                                        )}

                                                                                        {/* Action Buttons for Video/Clips */}
                                                                                        {(criterion.label.toLowerCase().includes('vídeo') || criterion.label.toLowerCase().includes('clips')) && (
                                                                                            <div className="ml-2 flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                                                                {!criterion.met && (
                                                                                                    <button
                                                                                                        onClick={(e) => { e.stopPropagation(); toast.success("Vídeo confirmado manualmente!"); }}
                                                                                                        className="p-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg transition-colors cursor-pointer"
                                                                                                        title="Confirmar Manualmente"
                                                                                                    >
                                                                                                        <CheckCircle2 size={12} />
                                                                                                    </button>
                                                                                                )}
                                                                                                {criterion.met && (
                                                                                                    <button
                                                                                                        onClick={(e) => { e.stopPropagation(); toast.success("Confirmação de vídeo removida!"); }}
                                                                                                        className="p-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 rounded-lg transition-colors cursor-pointer"
                                                                                                        title="Remover Confirmação"
                                                                                                    >
                                                                                                        <Trash2 size={12} />
                                                                                                    </button>
                                                                                                )}
                                                                                            </div>
                                                                                        )}
                                                                                    </div>
                                                                                ))}
                                                                            </div>

                                                                            {/* Issues List */}
                                                                            {section.issues && section.issues.length > 0 && (
                                                                                <div className="pt-2 border-t border-white/5 mt-2 space-y-1">
                                                                                    {section.issues.map((issue: string, i: number) => (
                                                                                        <li key={i} className="text-xs text-rose-400 flex items-start gap-1">
                                                                                            <AlertTriangle size={10} className="mt-0.5 shrink-0" /> {issue}
                                                                                        </li>
                                                                                    ))}
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <div className="p-8 text-center text-slate-500">
                                                            Análise de Saúde não disponível para este anúncio.
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                            {activeTab === 'competition' && (
                                                <div className="space-y-6">
                                                    {/* Protection Dashboard */}
                                                    <div className="grid grid-cols-3 gap-3">
                                                        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col justify-between">
                                                            <div className="flex items-center gap-2 text-emerald-400 mb-2">
                                                                <ShieldCheck size={18} />
                                                                <span className="text-xs font-bold uppercase tracking-wider">Status da Blindagem</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-xl font-bold text-white block">Ativo</span>
                                                                <span className="text-[10px] text-emerald-400/80">Monitorando 24/7</span>
                                                            </div>
                                                        </div>
                                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5 flex flex-col justify-between">
                                                            <div className="flex items-center gap-2 text-slate-400 mb-2">
                                                                <Users size={18} />
                                                                <span className="text-xs font-bold uppercase tracking-wider">Ameaças</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-xl font-bold text-white block">{competitorCount}</span>
                                                                <span className="text-[10px] text-slate-500">Concorrentes diretos</span>
                                                            </div>
                                                        </div>
                                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5 flex flex-col justify-between group relative cursor-help transition-colors hover:bg-white/10">
                                                            <div className="flex items-center gap-2 text-slate-400 mb-2">
                                                                <History size={18} />
                                                                <span className="text-xs font-bold uppercase tracking-wider">Última Varredura</span>
                                                            </div>
                                                            <div>
                                                                <span className="text-xl font-bold text-white block">
                                                                    {ad?.last_updated
                                                                        ? (new Date(ad.last_updated).toLocaleDateString('pt-BR') === new Date().toLocaleDateString('pt-BR')
                                                                            ? 'Hoje'
                                                                            : new Date(ad.last_updated).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }))
                                                                        : '-'}
                                                                </span>
                                                                <span className="text-[10px] text-slate-500">
                                                                    {ad?.last_updated
                                                                        ? new Date(ad.last_updated).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
                                                                        : '--:--'}
                                                                </span>
                                                            </div>

                                                            {/* Tooltip Explanation */}
                                                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-80 bg-[#0c0d12] border border-white/10 rounded-lg p-3 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                                                <p className="text-xs text-slate-300 leading-relaxed">
                                                                    Indica o momento exato da Última sincronização de dados (Preço, estoque, status) deste anúncio diretamente da API do Mercado Livre.
                                                                </p>
                                                                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-[#0c0d12] border-l-transparent border-r-transparent"></div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <CompetitorManager adId={adId} />
                                                </div>
                                            )}
                                            {activeTab === 'media' && (
                                                <AdMediaTab ad={ad} setIsLightboxOpen={setIsLightboxOpen} />
                                            )}

                                            {activeTab === 'fiscal' && (
                                                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                                                    <FiscalParametersTab 
                                                        adId={ad.id} 
                                                        pricingResolution={pricingResolution} 
                                                        isResolvingPricing={isResolvingPricing} 
                                                        onSaved={() => {
                                                            const fetchResolution = async () => {
                                                                setIsResolvingPricing(true);
                                                                try {
                                                                    const res = await api.get(`/pricing/resolve/${ad.id}`);
                                                                    setPricingResolution(res.data);
                                                                } catch (err: any) {
                                                                    console.error("Erro no resolver:", err);
                                                                } finally {
                                                                    setIsResolvingPricing(false);
                                                                }
                                                            };
                                                            fetchResolution();
                                                        }}
                                                    />
                                                </div>
                                            )}

                                            {activeTab === 'margin' && (
                                                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                                                    <RepricerStrategyPanel
                                                        ad={ad}
                                                        requestConfirm={(cfg) => setConfirmAction({ ...cfg, open: true })}
                                                        onAdUpdate={(patch) => setAd(prev => prev ? { ...prev, ...patch } : null)}
                                                    />
                                                    <MarginSimulator
                                                        ad={ad}
                                                        simulatedPrice={simulatedPrice > 0 ? simulatedPrice : (ad.promotion_price || ad.price || 0)}
                                                        pricingResolution={pricingResolution}
                                                    />
                                                </div>
                                            )}


                                        </div>
                                    </div>
                                </div>








                            </motion.div >
                        ) : null
                        }
                    </AnimatePresence >
                </div >
            </div >

            {/* Lightbox Overlay */}
            <AnimatePresence>
                {
                    isLightboxOpen && ad && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-[60] bg-black/95 flex items-center justify-center p-4 backdrop-blur-sm"
                            onClick={() => setIsLightboxOpen(false)}
                        >
                            <button
                                className="absolute top-4 right-4 p-2 text-white/50 hover:text-white transition-colors cursor-pointer"
                                onClick={() => setIsLightboxOpen(false)}
                            >
                                <Minimize2 size={32} />
                            </button>

                            <div
                                className="relative w-full max-w-6xl h-full max-h-[90vh] flex items-center justify-center"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {ad.pictures && ad.pictures.length > 1 && (
                                    <>
                                        <button
                                            onClick={handlePrevImage}
                                            className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors backdrop-blur-md cursor-pointer"
                                        >
                                            <ChevronLeft size={32} />
                                        </button>
                                        <button
                                            onClick={handleNextImage}
                                            className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-white/10 hover:bg-white/20 text-white rounded-full transition-colors backdrop-blur-md cursor-pointer"
                                        >
                                            <ChevronRight size={32} />
                                        </button>
                                    </>
                                )}
                                <img
                                    src={ad.pictures?.[activeImageIndex]?.url || ad.thumbnail.replace('I.jpg', 'O.jpg')}
                                    alt={ad.title}

                                    className="max-w-full max-h-full object-contain drop-shadow-2xl"
                                />
                                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/50 text-sm font-mono bg-black/50 px-3 py-1 rounded-full">
                                    {activeImageIndex + 1} / {ad.pictures?.length || 1}
                                </div>
                            </div>
                        </motion.div>
                    )
                }
            </AnimatePresence >

            {/* Smart Protection Modal */}
            <AnimatePresence>
                {
                    isProtectionModalOpen && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-[70] bg-black/90 flex items-center justify-center p-4 backdrop-blur-sm"
                        >
                            <div className="w-full max-w-lg bg-[#0c0d12] rounded-2xl border border-white/10 overflow-hidden shadow-2xl flex flex-col">
                                {/* Header */}
                                <div className="bg-[#13141b] px-6 py-4 border-b border-white/5 flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
                                            <ShieldCheck size={20} />
                                        </div>
                                        <h3 className="text-lg font-bold text-white">Blindagem de Anúncio</h3>
                                    </div>
                                    <button onClick={() => setIsProtectionModalOpen(false)} className="text-slate-500 hover:text-white cursor-pointer transition-colors"><X size={20} /></button>
                                </div>

                                {/* Content */}
                                <div className="p-6">
                                    {protectionState === 'intro' && (
                                        <div className="space-y-4">
                                            <p className="text-slate-300 text-sm leading-relaxed">
                                                Para proteger sua posição de <strong>Consolidação</strong>, vamos ativar o protocolo de defesa de mercado.
                                            </p>
                                            <div className="space-y-3 bg-white/5 rounded-xl p-4 border border-white/5">
                                                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Ações do Protocolo:</h4>
                                                <div className="flex items-start gap-3">
                                                    <div className="bg-blue-500/20 p-1 rounded text-blue-400 mt-0.5"><Search size={14} /></div>
                                                    <div>
                                                        <strong className="text-white text-sm block">Monitoramento 24/7</strong>
                                                        <p className="text-xs text-slate-400">Rastreio contínuo de Preços e estoque da concorrência.</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-start gap-3">
                                                    <div className="bg-amber-500/20 p-1 rounded text-amber-400 mt-0.5"><AlertTriangle size={14} /></div>
                                                    <div>
                                                        <strong className="text-white text-sm block">Alertas de Perda de BuyBox</strong>
                                                        <p className="text-xs text-slate-400">Notificação imediata se você perder a posição de destaque.</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-start gap-3">
                                                    <div className="bg-emerald-500/20 p-1 rounded text-emerald-400 mt-0.5"><TrendingDown size={14} /></div>
                                                    <div>
                                                        <strong className="text-white text-sm block">Defesa de Margem</strong>
                                                        <p className="text-xs text-slate-400">Sugerimos ajustes para manter competitividade sem sacrificar lucro.</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {protectionState === 'scanning' && (
                                        <div className="flex flex-col items-center justify-center py-8 space-y-4">
                                            <div className="relative w-16 h-16">
                                                <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
                                                <div className="absolute inset-0 rounded-full border-t-4 border-emerald-500 animate-spin"></div>
                                            </div>
                                            <div className="text-center">
                                                <h4 className="text-white font-bold animate-pulse">Analisando Concorrência...</h4>
                                                <p className="text-xs text-slate-400 mt-1">Varrendo Mercado Livre por anúncios similares</p>
                                            </div>
                                        </div>
                                    )}

                                    {protectionState === 'success' && (
                                        <div className="text-center py-4 space-y-4">
                                            <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto text-emerald-500">
                                                <CheckCircle2 size={32} />
                                            </div>
                                            <div>
                                                <h4 className="text-xl font-bold text-white mb-2">Proteção Ativa</h4>
                                                <p className="text-slate-400 text-sm">
                                                    Este anúncio já¡ está sendo monitorado contra <strong>{competitorCount} concorrentes</strong>.
                                                </p>
                                            </div>
                                            <div className="bg-white/5 rounded-xl p-4 border border-white/5 text-left space-y-2">
                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-slate-400">Status</span>
                                                    <span className="text-emerald-400 font-bold flex items-center gap-1"><Activity size={12} /> Monitorando</span>
                                                </div>
                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-slate-400">Última Varredura</span>
                                                    <span className="text-white font-mono">Agora</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {protectionState === 'results' && (
                                        <div className="text-center py-4 space-y-4">
                                            <div className="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto text-amber-500">
                                                <Info size={32} />
                                            </div>
                                            <div>
                                                <h4 className="text-xl font-bold text-white mb-2">Nenhum Concorrente Monitorado</h4>
                                                <p className="text-slate-400 text-sm mb-4">
                                                    Para ativar a blindagem, precisamos saber quem são seus rivais. Adicione links de concorrentes na aba de Concorrência.
                                                </p>
                                                <button
                                                    onClick={() => { setIsProtectionModalOpen(false); setActiveTab('competition'); }}
                                                    className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold text-sm cursor-pointer"
                                                >
                                                    Ir para Concorrência
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Footer */}
                                {(protectionState === 'intro' || protectionState === 'success' || protectionState === 'results') && (
                                    <div className="bg-[#13141b] px-6 py-4 border-t border-white/5 flex justify-end gap-3 cursor-pointer">
                                        {protectionState === 'intro' ? (
                                            <>
                                                <button
                                                    onClick={() => setIsProtectionModalOpen(false)}
                                                    className="px-4 py-2 hover:bg-white/5 rounded-lg text-sm font-medium text-slate-400 hover:text-white transition-colors cursor-pointer"
                                                >
                                                    Cancelar
                                                </button>
                                                <button
                                                    onClick={confirmProtection}
                                                    className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-sm shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 flex items-center gap-2 cursor-pointer"
                                                >
                                                    <ShieldCheck size={16} /> Ativar Proteção
                                                </button>
                                            </>
                                        ) : (
                                            <div className="flex gap-2 w-full">
                                                {protectionState === 'success' && (
                                                    <button
                                                        onClick={() => { setIsProtectionModalOpen(false); setActiveTab('competition'); }}
                                                        className="flex-1 px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white rounded-lg font-bold text-sm transition-colors border border-white/10 hover:border-white/20 cursor-pointer"
                                                    >
                                                        Gerenciar Concorrentes
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => { setIsProtectionModalOpen(false); }}
                                                    className="flex-1 px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-bold text-sm transition-colors cursor-pointer"
                                                >
                                                    Fechar
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )
                }
            </AnimatePresence >



            <ConfirmModal
                isOpen={confirmAction.open}
                onClose={() => setConfirmAction(prev => ({ ...prev, open: false }))}
                onConfirm={confirmAction.onConfirm}
                title={confirmAction.title}
                message={confirmAction.message}
                type={confirmAction.type}
            />

            {/* Price Execution Modal */}
            {
                priceExecutionModal.open && ad && (
                    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
                        <div className="relative bg-gradient-to-br from-[#1a1c2e] to-[#12141e] border border-slate-700/50 w-full max-w-md rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4 duration-300">
                            {/* Header */}
                            <div className="px-6 py-4 border-b border-slate-800/50 bg-gradient-to-r from-indigo-500/10 to-purple-500/10">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                                            <DollarSign className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-white">Ajuste de Preço</h3>
                                            <p className="text-xs text-slate-400">Execução Manual</p>
                                        </div>
                                    </div>
                                    {priceExecutionModal.status !== 'loading' && (
                                        <button
                                            onClick={() => setPriceExecutionModal(prev => ({ ...prev, open: false }))}
                                            className="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-slate-800/50"
                                        >
                                            <X className="w-5 h-5" />
                                        </button>
                                    )}
                                </div>
                            </div>

                            {/* Body */}
                            <div className="p-6">
                                {priceExecutionModal.status === 'confirm' && (
                                    <div className="space-y-4">
                                        <p className="text-slate-300 text-sm">
                                            Você está prestes a alterar o Preço deste anúncio no Mercado Livre.
                                        </p>

                                        {/* Price Comparison */}
                                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/50">
                                            <div className="flex items-center justify-between gap-3">
                                                <div className="text-center flex-1">
                                                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Preço Atual</p>
                                                    <p className="text-lg font-mono font-bold text-slate-400">
                                                        {(priceExecutionModal.oldPrice || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                    </p>
                                                </div>
                                                <ArrowRight className="text-indigo-400 w-6 h-6 animate-pulse" />
                                                <div className="text-center flex-1">
                                                    <p className="text-[10px] text-indigo-400 uppercase font-bold mb-1">Novo Preço</p>
                                                    <p className="text-xl font-mono font-bold text-white">
                                                        {priceExecutionModal.targetPrice.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="mt-3 pt-3 border-t border-slate-800/50 text-center">
                                                <span className={`text-sm font-semibold ${priceExecutionModal.targetPrice > (priceExecutionModal.oldPrice || 0) ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {priceExecutionModal.targetPrice > (priceExecutionModal.oldPrice || 0) ? <ArrowUp className="inline w-3 h-3 mr-1" /> : <ArrowDown className="inline w-3 h-3 mr-1" />}
                                                    {Math.abs(((priceExecutionModal.targetPrice / (priceExecutionModal.oldPrice || 1)) - 1) * 100).toFixed(2)}%
                                                </span>
                                            </div>
                                        </div>

                                        {/* Warning */}
                                        <div className="flex items-start gap-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                                            <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                                            <div className="text-xs text-amber-200/80">
                                                <p className="font-medium">Esta ação é irreversível.</p>
                                                <p className="text-amber-200/60 mt-0.5">O Preço será¡ atualizado imediatamente no Mercado Livre.</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {priceExecutionModal.status === 'loading' && (
                                    <div className="py-8 flex flex-col items-center gap-4">
                                        <div className="w-16 h-16 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin" />
                                        <div className="text-center">
                                            <p className="text-white font-medium">Atualizando Preço...</p>
                                            <p className="text-sm text-slate-400 mt-1">Conectando ao Mercado Livre</p>
                                        </div>
                                    </div>
                                )}

                                {priceExecutionModal.status === 'success' && (
                                    <div className="py-6 flex flex-col items-center gap-4">
                                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/40 animate-in zoom-in-75 duration-300">
                                            <CheckCircle2 className="w-8 h-8 text-white drop-shadow" />
                                        </div>
                                        <div className="text-center">
                                            <p className="text-xl font-bold text-white">Preço Atualizado!</p>
                                            <p className="text-sm text-slate-400 mt-2">
                                                Novo Preço: <span className="text-emerald-400 font-mono font-bold">{priceExecutionModal.targetPrice.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                                            </p>
                                        </div>
                                    </div>
                                )}

                                {priceExecutionModal.status === 'error' && (
                                    <div className="py-6 flex flex-col items-center gap-4">
                                        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-rose-500/20 to-rose-600/20 flex items-center justify-center border-2 border-rose-500/30 animate-in zoom-in-75 duration-300">
                                            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-rose-400 to-rose-600 flex items-center justify-center shadow-lg shadow-rose-500/40">
                                                <AlertTriangle className="w-7 h-7 text-white drop-shadow" />
                                            </div>
                                        </div>
                                        <div className="text-center space-y-3 max-w-sm">
                                            <p className="text-xl font-bold text-white">Ops! Algo deu errado</p>
                                            <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-3">
                                                <p className="text-xs text-rose-300/90 font-mono leading-relaxed break-words">
                                                    {(priceExecutionModal.errorMessage || 'não foi possível atualizar o Preço.').slice(0, 200)}
                                                    {(priceExecutionModal.errorMessage?.length || 0) > 200 ? '...' : ''}
                                                </p>
                                            </div>
                                            <p className="text-xs text-slate-500">
                                                Verifique a conexá£o ou tente novamente em alguns instantes.
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="px-6 py-4 bg-slate-900/30 border-t border-slate-800/50 flex items-center justify-end gap-3">
                                {priceExecutionModal.status === 'confirm' && (
                                    <>
                                        <button
                                            onClick={() => setPriceExecutionModal(prev => ({ ...prev, open: false }))}
                                            className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                                        >
                                            Cancelar
                                        </button>
                                        <button
                                            onClick={async () => {
                                                setPriceExecutionModal(prev => ({ ...prev, status: 'loading' }));
                                                try {
                                                    const response = await api.post(`/ads/${ad.id}/execute-price-step`, { target_price: priceExecutionModal.targetPrice });
                                                    if (response.data?.success) {
                                                        setPriceExecutionModal(prev => ({ ...prev, status: 'success' }));
                                                        setTimeout(() => window.location.reload(), 1500);
                                                    } else {
                                                        setPriceExecutionModal(prev => ({
                                                            ...prev,
                                                            status: 'error',
                                                            errorMessage: response.data?.error || 'Falha ao atualizar'
                                                        }));
                                                    }
                                                } catch (err: any) {
                                                    setPriceExecutionModal(prev => ({
                                                        ...prev,
                                                        status: 'error',
                                                        errorMessage: err.response?.data?.error || err.message
                                                    }));
                                                }
                                            }}
                                            className="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all transform active:scale-95 flex items-center gap-2 cursor-pointer"
                                        >
                                            <DollarSign className="w-4 h-4" />
                                            Confirmar Alteração
                                        </button>
                                    </>
                                )}
                                {priceExecutionModal.status === 'success' && (
                                    <button
                                        onClick={() => window.location.reload()}
                                        className="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg transition-all cursor-pointer flex items-center gap-2"
                                    >
                                        <CheckCircle2 className="w-4 h-4" />
                                        Concluído
                                    </button>
                                )}
                                {priceExecutionModal.status === 'error' && (
                                    <>
                                        <button
                                            onClick={() => setPriceExecutionModal(prev => ({ ...prev, open: false }))}
                                            className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                                        >
                                            Fechar
                                        </button>
                                        <button
                                            onClick={() => setPriceExecutionModal(prev => ({ ...prev, status: 'confirm' }))}
                                            className="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-rose-600 hover:bg-rose-500 shadow-lg transition-all cursor-pointer flex items-center gap-2"
                                        >
                                            Tentar Novamente
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                )
            }


        </>
    );
}





