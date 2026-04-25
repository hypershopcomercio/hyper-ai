/**
 * PromoSelector - Component to select and apply promotions when item has active promo
 * Shown instead of simulation when ad.hasPromo is true
 */

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Tag, Percent, Calendar, AlertCircle, Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface PromoDeal {
    type: string;
    name: string;
    description: string;
    max_discount: number;
    max_days: number;
}

interface CurrentPromo {
    type: string;
    deal_price: number;
    original_price: number;
    discount_percent: number;
    start_date: string;
    finish_date: string;
    status: string;
}

interface Props {
    adId: string;
    currentPrice: number;
    originalPrice: number;
    promoPrice: number;
    suggestedPrice: number;
    onApplyPromo?: (dealPrice: number) => void;
}

export function PromoSelector({ adId, currentPrice, originalPrice, promoPrice, suggestedPrice, onApplyPromo }: Props) {
    const [loading, setLoading] = useState(true);
    const [applying, setApplying] = useState(false);
    const [promoData, setPromoData] = useState<{
        hasPromotions: boolean;
        currentPromotions: CurrentPromo[];
        availableDeals: PromoDeal[];
        error: string | null;
    }>({
        hasPromotions: false,
        currentPromotions: [],
        availableDeals: [],
        error: null
    });

    const [selectedDeal, setSelectedDeal] = useState<string>('PRICE_DISCOUNT');
    const [dealPrice, setDealPrice] = useState(suggestedPrice || promoPrice);
    const [duration, setDuration] = useState(14);

    useEffect(() => {
        fetchPromotions();
    }, [adId]);

    useEffect(() => {
        setDealPrice(suggestedPrice || promoPrice);
    }, [suggestedPrice, promoPrice]);

    const fetchPromotions = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/ads/${adId}/promotions`);
            setPromoData({
                hasPromotions: res.data.has_promotions,
                currentPromotions: res.data.current_promotions || [],
                availableDeals: res.data.available_deals || [],
                error: res.data.error
            });
        } catch (err: any) {
            console.error('Error fetching promotions:', err);
            setPromoData(prev => ({ ...prev, error: err.message }));
        } finally {
            setLoading(false);
        }
    };

    const handleApplyPromo = async () => {
        if (!dealPrice || dealPrice <= 0) {
            toast.error('Informe um preço de promoção válido');
            return;
        }

        setApplying(true);
        try {
            const res = await api.post(`/ads/${adId}/promotions`, {
                deal_price: dealPrice,
                days: duration
            });

            if (res.data.success) {
                toast.success('Promoção aplicada com sucesso!');
                onApplyPromo?.(dealPrice);
                fetchPromotions();
            } else {
                toast.error(res.data.error || 'Erro ao aplicar promoção');
            }
        } catch (err: any) {
            toast.error(err.response?.data?.error || 'Erro ao aplicar promoção');
        } finally {
            setApplying(false);
        }
    };

    const discountPercent = originalPrice > 0
        ? ((originalPrice - dealPrice) / originalPrice * 100).toFixed(1)
        : '0';

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <Loader2 className="animate-spin text-amber-400" size={24} />
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Tag className="text-rose-400" size={18} />
                <h3 className="text-sm font-semibold text-white">Gestão de Promoção</h3>
            </div>

            {/* Current Promo Status */}
            {promoData.currentPromotions.length > 0 && (
                <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
                    <p className="text-xs text-rose-300 font-medium mb-2">📉 Promoção Ativa</p>
                    {promoData.currentPromotions.map((promo, i) => (
                        <div key={i} className="flex justify-between text-xs text-slate-300">
                            <span>R$ {promo.deal_price?.toFixed(2)}</span>
                            <span className="text-rose-400">-{promo.discount_percent?.toFixed(1)}%</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Apply New Promotion */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-4">
                <div className="flex items-center gap-2 text-sm text-slate-300">
                    <Percent size={14} className="text-emerald-400" />
                    <span>Aplicar Nova Promoção</span>
                </div>

                {/* Price Input */}
                <div className="space-y-2">
                    <label className="text-xs text-slate-500">Preço Promocional (R$)</label>
                    <div className="relative">
                        <input
                            type="number"
                            value={dealPrice}
                            onChange={(e) => setDealPrice(parseFloat(e.target.value) || 0)}
                            className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-white font-mono focus:border-amber-500 focus:outline-none"
                            step="0.01"
                            min="0"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500">
                            -{discountPercent}% off
                        </span>
                    </div>
                </div>

                {/* Duration */}
                <div className="space-y-2">
                    <label className="text-xs text-slate-500 flex items-center gap-1">
                        <Calendar size={12} />
                        Duração (dias)
                    </label>
                    <div className="flex gap-2">
                        {[7, 10, 14].map(d => (
                            <button
                                key={d}
                                onClick={() => setDuration(d)}
                                className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-all ${duration === d
                                        ? 'bg-amber-500 text-black'
                                        : 'bg-white/5 text-slate-400 hover:bg-white/10'
                                    }`}
                            >
                                {d} dias
                            </button>
                        ))}
                    </div>
                </div>

                {/* Price Preview */}
                <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                    <div className="flex justify-between items-center">
                        <span className="text-xs text-slate-400">Preço Original</span>
                        <span className="text-sm text-slate-200 font-mono">R$ {originalPrice?.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center mt-1">
                        <span className="text-xs text-emerald-400">Preço Promo</span>
                        <span className="text-lg text-emerald-400 font-bold font-mono">R$ {dealPrice?.toFixed(2)}</span>
                    </div>
                </div>

                {/* Warning */}
                <div className="flex items-start gap-2 p-2 rounded-lg bg-amber-500/5 text-xs text-amber-300/80">
                    <AlertCircle size={14} className="flex-shrink-0 mt-0.5" />
                    <span>A promoção será aplicada via API do Mercado Livre e ficará ativa por {duration} dias.</span>
                </div>

                {/* Apply Button */}
                <button
                    onClick={handleApplyPromo}
                    disabled={applying || dealPrice <= 0}
                    className="w-full py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-black font-semibold rounded-lg flex items-center justify-center gap-2 hover:brightness-110 disabled:opacity-50 transition-all"
                >
                    {applying ? (
                        <Loader2 className="animate-spin" size={16} />
                    ) : (
                        <>
                            <Check size={16} />
                            Aplicar Promoção
                        </>
                    )}
                </button>
            </div>

            {/* Error Display */}
            {promoData.error && (
                <div className="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
                    {promoData.error}
                </div>
            )}
        </div>
    );
}
