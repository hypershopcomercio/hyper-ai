"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import {
    ArrowLeft, FileText, Building2, Calendar, DollarSign,
    Box, CheckCircle, AlertTriangle, Search, Link2, Truck, Info, CheckCircle2, ChevronRight, XCircle, RefreshCw
} from 'lucide-react';

export default function NFeDetailPage() {
    const params = useParams();
    const router = useRouter();
    const [nfe, setNfe] = useState<any>(null);
    const [reconciliation, setReconciliation] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    
    // Modal states
    const [showReconModal, setShowReconModal] = useState(false);
    const [financialValue, setFinancialValue] = useState("");
    const [submittingRecon, setSubmittingRecon] = useState(false);
    const [reconError, setReconError] = useState("");
    
    // Linker state
    const [linkingItems, setLinkingItems] = useState(false);
    const [linkerSummary, setLinkerSummary] = useState<any>(null);
    const [hasAutoRun, setHasAutoRun] = useState(false);
    
    // Manual Search Modal
    const [showSearchModal, setShowSearchModal] = useState(false);
    const [searchItem, setSearchItem] = useState<any>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    
    // Ambiguous Modal
    const [showAmbiguousModal, setShowAmbiguousModal] = useState(false);
    const [ambiguousItemData, setAmbiguousItemData] = useState<any>(null);

    useEffect(() => {
        if (params.id) {
            loadNfe(params.id as string);
        }
    }, [params.id]);

    useEffect(() => {
        // Auto-run linker on load if there are pending items and we haven't auto-run yet
        if (nfe && !hasAutoRun && !linkerSummary) {
            const hasPending = nfe.items.some((i: any) => i.link_status === 'pending');
            if (hasPending) {
                setHasAutoRun(true);
                handleRunLinker(false); // pass false to avoid loading state block
            }
        }
    }, [nfe, hasAutoRun, linkerSummary]);

    const loadNfe = async (id: string) => {
        setLoading(true);
        try {
            const [nfeRes, reconRes] = await Promise.all([
                api.get(`/nfe/${id}`),
                api.get(`/nfe/${id}/reconciliation`)
            ]);
            
            if (nfeRes.data.success) {
                setNfe(nfeRes.data.data);
            }
            if (reconRes.data.success) {
                setReconciliation(reconRes.data.data);
            }
        } catch (error) {
            console.error("Error loading NFe detail", error);
        } finally {
            setLoading(false);
        }
    };
    
    const handleReconciliationSubmit = async () => {
        setReconError("");
        if (!financialValue) return setReconError("Informe o valor financeiro");
        
        setSubmittingRecon(true);
        try {
            const res = await api.post(`/nfe/${params.id}/reconciliation`, {
                financial_value_real: parseFloat(financialValue),
                source_type: 'user_input'
            });
            if (res.data.success) {
                setShowReconModal(false);
                setFinancialValue("");
                loadNfe(params.id as string);
            }
        } catch (error: any) {
            setReconError(error.response?.data?.error || "Erro ao conciliar");
        } finally {
            setSubmittingRecon(false);
        }
    };
    
    const handleRunLinker = async (showLoadingState = true) => {
        if (showLoadingState) setLinkingItems(true);
        try {
            const res = await api.post(`/nfe/${params.id}/linker/run`);
            if (res.data.success) {
                setLinkerSummary(res.data.data);
            }
            loadNfe(params.id as string);
        } catch (error: any) {
            console.error("Error running linker", error);
            if (showLoadingState) alert("Erro ao rodar Linker: " + (error.response?.data?.error || error.message));
        } finally {
            if (showLoadingState) setLinkingItems(false);
        }
    };
    
    const confirmBatch = async () => {
        try {
            await api.post(`/nfe/${params.id}/linker/confirm_batch`);
            loadNfe(params.id as string);
            if (linkerSummary) {
                const newSummary = {...linkerSummary, suggested_count: 0};
                setLinkerSummary(newSummary);
            }
        } catch (error: any) {
            console.error("Error confirming batch", error);
            alert("Erro ao confirmar lote: " + (error.response?.data?.error || error.message));
        }
    };
    
    const confirmLink = async (itemId: number, sku: string, mlbId: string, variationId: string | null = null, catalogId: string | null = null) => {
        try {
            await api.post(`/nfe/${params.id}/items/${itemId}/confirm`, {
                linked_sku: sku,
                linked_mlb_id: mlbId,
                linked_variation_id: variationId,
                linked_catalog_product_id: catalogId
            });
            setShowAmbiguousModal(false);
            setShowSearchModal(false);
            loadNfe(params.id as string);
        } catch (error: any) {
            console.error("Error confirming link", error);
            alert("Erro ao confirmar vínculo: " + (error.response?.data?.error || error.message));
        }
    };

    const unlinkItem = async (itemId: number) => {
        try {
            await api.post(`/nfe/${params.id}/items/${itemId}/unlink`);
            loadNfe(params.id as string);
        } catch (error: any) {
            console.error("Error unlinking item", error);
            alert("Erro ao desvincular item: " + (error.response?.data?.error || error.message));
        }
    };

    const handleSearch = async () => {
        if (!searchQuery) return;
        setIsSearching(true);
        try {
            const res = await api.get(`/nfe/linker/search?q=${encodeURIComponent(searchQuery)}`);
            setSearchResults(res.data.data || []);
        } catch (error) {
            console.error(error);
        } finally {
            setIsSearching(false);
        }
    };

    if (loading && !nfe) {
        return <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 flex items-center justify-center">Carregando dados da nota fiscal...</div>;
    }

    if (!nfe) {
        return (
            <div className="min-h-screen bg-[#09090b] text-slate-100 p-8">
                <button onClick={() => router.back()} className="flex items-center gap-2 text-slate-400 hover:text-white mb-6">
                    <ArrowLeft size={16} /> Voltar
                </button>
                <div className="bg-[#121217] border border-rose-500/30 rounded-2xl p-8 text-center">
                    <AlertTriangle size={48} className="mx-auto text-rose-500 mb-4 opacity-50" />
                    <h2 className="text-xl font-bold text-white mb-2">Nota Fiscal não encontrada</h2>
                    <p className="text-slate-400">A NF que você tentou acessar não existe ou foi removida.</p>
                </div>
            </div>
        );
    }

    const totalItems = nfe.items.length;
    let confirmedCount = 0;
    let suggestedHighCount = 0;
    let reviewNeededCount = 0;
    let pendingCount = 0;

    nfe.items.forEach((item: any) => {
        const linkerItem = linkerSummary?.suggestions?.find((s:any) => s.n_item === item.n_item);
        
        if (item.link_status === 'confirmed') {
            confirmedCount++;
        } else if (linkerItem && linkerItem.status === 'ambiguous') {
            reviewNeededCount++;
        } else if (item.link_status === 'suggested') {
            if (item.link_confidence === 'high') {
                suggestedHighCount++;
            } else {
                reviewNeededCount++;
            }
        } else {
            pendingCount++;
        }
    });

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-6 space-y-4">
            <button onClick={() => router.push('/supply/nfe')} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-xs w-fit">
                <ArrowLeft size={14} /> Voltar para lista de NFs
            </button>

            {/* Header NFe */}
            <div className="bg-[#121217] border border-white/5 rounded-xl p-4 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-32 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                    <div className="space-y-3 flex-1">
                        <div>
                            <div className="flex items-center gap-3 mb-1">
                                <h1 className="text-lg font-bold text-white flex items-center gap-2">
                                    <FileText className="text-blue-500" size={18} />
                                    NF-e {nfe.nfe_number || '-'} 
                                    <span className="text-slate-500 text-sm font-normal">Série {nfe.series || '-'}</span>
                                </h1>
                                {nfe.status === 'linked' ? (
                                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] rounded border border-emerald-500/20 uppercase font-bold tracking-wide">Vinculada</span>
                                ) : (
                                    <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 text-[10px] rounded border border-amber-500/20 uppercase font-bold tracking-wide">Análise Pendente</span>
                                )}
                            </div>
                            <p className="text-slate-500 text-[10px] font-mono break-all">{nfe.access_key}</p>
                        </div>

                        <div className="flex flex-wrap gap-x-6 gap-y-2">
                            <div className="flex items-start gap-2">
                                <Building2 className="text-slate-500 mt-0.5" size={14} />
                                <div>
                                    <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Fornecedor / Emitente</p>
                                    <p className="text-xs text-slate-200 font-medium">{nfe.issuer_name}</p>
                                    <p className="text-[10px] text-slate-400 font-mono">{nfe.issuer_cnpj}</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <Calendar className="text-slate-500 mt-0.5" size={14} />
                                <div>
                                    <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Emissão</p>
                                    <p className="text-xs text-slate-200">{new Date(nfe.issue_date).toLocaleDateString('pt-BR')}</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-2">
                                <Truck className="text-slate-500 mt-0.5" size={14} />
                                <div>
                                    <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Frete Total</p>
                                    <p className="text-xs text-slate-200">{nfe.total_freight.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[#1A1A24] border border-white/5 p-4 rounded-lg min-w-[160px] shrink-0 text-right">
                        <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider mb-1 flex items-center justify-end gap-1">
                            <DollarSign size={10} /> Valor Fiscal XML
                        </p>
                        <p className="text-xl font-black text-white font-mono tracking-tight">
                            {nfe.total_invoice_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                    </div>
                </div>
            </div>
            
            {/* Bloco Conciliação Fiscal x Financeira */}
            <div className="bg-[#121217] border border-white/5 rounded-xl overflow-hidden p-5 relative">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
                            <DollarSign size={16} className="text-emerald-500" />
                            Conciliação Fiscal x Financeira
                        </h3>
                        <p className="text-[11px] text-slate-400 mt-1">
                            Esta conciliação é interna para controle financeiro e precificação. O XML fiscal permanece inalterado.
                        </p>
                    </div>
                    {!reconciliation && (
                        <button 
                            onClick={() => setShowReconModal(true)}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md font-medium transition-colors text-xs h-8"
                        >
                            Conciliar operação
                        </button>
                    )}
                </div>
                
                {reconciliation ? (
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 bg-[#1A1A24] rounded-lg p-4 border border-white/5">
                        <div>
                            <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Valor Fiscal XML</p>
                            <p className="text-sm font-mono text-white mt-1">
                                {reconciliation.fiscal_value_xml.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </p>
                        </div>
                        <div>
                            <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Cobertura da NF</p>
                            <p className="text-sm font-mono text-white mt-1">
                                {reconciliation.coverage_percent.toFixed(2)}%
                            </p>
                        </div>
                        <div>
                            <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Valor Financeiro Real</p>
                            <p className="text-sm font-mono text-emerald-400 font-bold mt-1">
                                {reconciliation.financial_value_real.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                            </p>
                        </div>
                        <div>
                            <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Multiplicador Financeiro</p>
                            <div className="flex items-center gap-2 mt-1">
                                <p className="text-sm font-mono text-white">
                                    {reconciliation.financial_multiplier.toFixed(4)}x
                                </p>
                            </div>
                        </div>
                        <div>
                            <p className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Custo p/ Precificação</p>
                            <p className="text-[10px] text-slate-400 mt-1 italic">
                                Aplicado aos itens
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center justify-center p-4 bg-[#1A1A24] rounded-lg border border-white/5 border-dashed">
                        <div className="text-center flex flex-col items-center">
                            <p className="text-amber-500 text-sm font-medium mb-1">Conciliação Pendente</p>
                            <p className="text-slate-400 text-[11px]">Nenhum valor financeiro real foi vinculado a esta nota ainda.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Items Table */}
            <div className="bg-[#121217] border border-white/5 rounded-xl overflow-hidden">
                <div className="px-5 py-4 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#1A1A24]">
                    <div>
                        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
                            <Box size={16} className="text-slate-400" />
                            Itens da Nota ({totalItems})
                            <span className="text-slate-500 font-normal ml-2">
                                — {confirmedCount} vinculados
                                {reviewNeededCount > 0 ? ` · ${reviewNeededCount} revisão necessária` : ''}
                                {suggestedHighCount > 0 ? ` · ${suggestedHighCount} sugestões` : ''}
                                {pendingCount > 0 ? ` · ${pendingCount} pendentes` : ''}
                            </span>
                        </h3>
                    </div>
                    <div className="flex gap-2">
                        <button 
                            onClick={() => handleRunLinker(true)}
                            disabled={linkingItems || confirmedCount === totalItems}
                            className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/5 px-3 py-1.5 rounded-md text-[11px] font-medium transition-colors disabled:opacity-50 flex items-center gap-1.5"
                            title="Reprocessar sugestões"
                        >
                            <RefreshCw size={12} className={linkingItems ? 'animate-spin' : ''} />
                            Reprocessar
                        </button>
                        {suggestedHighCount > 0 && (
                            <button 
                                onClick={confirmBatch}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-[11px] font-bold transition-colors flex items-center gap-1.5 shadow-md shadow-blue-500/10"
                            >
                                <CheckCircle2 size={12} />
                                Confirmar alta confiança
                            </button>
                        )}
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                        <thead className="bg-[#1A1A24] border-b border-white/5 text-slate-400">
                            <tr>
                                <th className="px-4 py-2 font-medium min-w-[250px]">Produto</th>
                                <th className="px-4 py-2 font-medium text-right w-20">Qtd</th>
                                <th className="px-4 py-2 font-medium text-right w-24">Valor</th>
                                <th className="px-4 py-2 font-medium text-right w-28">Custo NF</th>
                                <th className="px-4 py-2 font-medium min-w-[250px]">Vínculo</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {nfe.items.map((item: any) => {
                                const linkerItem = linkerSummary?.suggestions?.find((s:any) => s.n_item === item.n_item);
                                const isAmbiguous = linkerItem && linkerItem.status === 'ambiguous';
                                
                                return (
                                <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                                    {/* Produto */}
                                    <td className="px-4 py-3 align-middle">
                                        <div className="font-medium text-slate-200 line-clamp-2 leading-tight mb-1" title={item.description}>
                                            <span className="text-slate-500 mr-2 text-[10px] font-mono">{item.n_item}</span>
                                            {item.description}
                                        </div>
                                        <div className="flex gap-2 text-[10px] font-mono">
                                            {item.ean && item.ean !== "SEM GTIN" && (
                                                <span className="text-slate-400">EAN: {item.ean}</span>
                                            )}
                                            {item.sku_supplier && (
                                                <span className="text-slate-400">cProd: {item.sku_supplier}</span>
                                            )}
                                        </div>
                                    </td>
                                    
                                    {/* Qtd */}
                                    <td className="px-4 py-3 text-right font-mono text-slate-300 align-middle">
                                        {item.quantity}
                                    </td>
                                    
                                    {/* Valor Bruto */}
                                    <td className="px-4 py-3 text-right font-mono text-slate-300 align-middle">
                                        {item.unit_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                    </td>
                                    
                                    {/* Custo Resolvido */}
                                    <td className="px-4 py-3 text-right align-middle">
                                        <span className="font-mono text-emerald-400 font-bold">
                                            {item.unit_cost_nf.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </span>
                                    </td>
                                    
                                    {/* Vinculo */}
                                    <td className="px-4 py-3 align-middle">
                                        {item.link_status === 'confirmed' ? (
                                            <div className="flex items-center justify-between gap-3">
                                                <div>
                                                    <div className="flex items-center gap-1.5 text-emerald-400 text-[11px] font-bold mb-0.5">
                                                        <CheckCircle size={12} /> Confirmado: {item.linked_sku}
                                                    </div>
                                                    <div className="text-[10px] font-mono text-slate-500">
                                                        MLB: {item.linked_mlb_id}
                                                        {item.linked_variation_id && ` | Var: ${item.linked_variation_id}`}
                                                        {item.linked_catalog_product_id && ` | Cat: ${item.linked_catalog_product_id}`}
                                                    </div>
                                                </div>
                                                <div className="flex gap-1.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button 
                                                        onClick={() => { setSearchItem(item); setShowSearchModal(true); }}
                                                        className="px-2 py-1 text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-white/5"
                                                    >
                                                        Trocar
                                                    </button>
                                                    <button 
                                                        onClick={() => unlinkItem(item.id)}
                                                        className="px-2 py-1 text-[10px] bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded border border-rose-500/10"
                                                    >
                                                        Desvincular
                                                    </button>
                                                </div>
                                            </div>
                                        ) : isAmbiguous ? (
                                            <div className="flex items-center justify-between gap-3">
                                                <div className="flex items-center gap-1.5 text-amber-500 text-[11px] font-bold">
                                                    <AlertTriangle size={12} /> Revisão necessária
                                                </div>
                                                <button 
                                                    onClick={() => {
                                                        setAmbiguousItemData({ item, candidates: linkerItem.candidates });
                                                        setShowAmbiguousModal(true);
                                                    }}
                                                    className="px-2 py-1 text-[10px] bg-amber-500/10 hover:bg-amber-500/20 text-amber-500 rounded font-medium border border-amber-500/20 shrink-0"
                                                >
                                                    Ver opções
                                                </button>
                                            </div>
                                        ) : item.link_status === 'suggested' ? (
                                            <div className="flex items-center justify-between gap-3">
                                                <div>
                                                    <div className="flex items-center gap-1.5 text-blue-400 text-[11px] font-bold mb-0.5">
                                                        <Info size={12} /> Sugestão: {item.linked_sku}
                                                    </div>
                                                    <div className="text-[10px] font-mono text-slate-500">
                                                        MLB: {item.linked_mlb_id}
                                                        {item.linked_variation_id && ` | Var: ${item.linked_variation_id}`}
                                                        {item.linked_catalog_product_id && ` | Cat: ${item.linked_catalog_product_id}`}
                                                    </div>
                                                </div>
                                                <div className="flex gap-1.5 shrink-0">
                                                    <button 
                                                        onClick={() => confirmLink(item.id, item.linked_sku, item.linked_mlb_id, item.linked_variation_id, item.linked_catalog_product_id)}
                                                        className="px-2 py-1 text-[10px] bg-blue-600 hover:bg-blue-700 text-white rounded font-medium"
                                                    >
                                                        Confirmar
                                                    </button>
                                                    <button 
                                                        onClick={() => { setSearchItem(item); setShowSearchModal(true); }}
                                                        className="px-2 py-1 text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-white/5 opacity-0 group-hover:opacity-100 transition-opacity"
                                                    >
                                                        Trocar
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex items-center justify-between gap-3">
                                                <div className="text-slate-500 text-[11px] font-medium">Sem vínculo</div>
                                                <button 
                                                    onClick={() => { setSearchItem(item); setShowSearchModal(true); }}
                                                    className="px-2 py-1 text-[10px] bg-white/5 hover:bg-white/10 text-slate-300 rounded border border-white/10 shrink-0 flex items-center gap-1"
                                                >
                                                    <Search size={10} /> Buscar
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            )})}
                        </tbody>
                    </table>
                </div>
            </div>
            
            {/* Modal de Busca Manual */}
            {showSearchModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-[#121217] border border-white/10 rounded-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[85vh]">
                        <div className="p-5 border-b border-white/5 flex justify-between items-center bg-[#1A1A24]">
                            <div>
                                <h3 className="text-base font-bold text-white flex items-center gap-2">
                                    <Search className="text-blue-500" size={18} />
                                    Buscar Produto
                                </h3>
                                <p className="text-[11px] text-slate-400 mt-1 max-w-xl truncate">
                                    Item XML: <span className="text-slate-300 font-medium">{searchItem?.description}</span>
                                </p>
                            </div>
                            <button onClick={() => setShowSearchModal(false)} className="text-slate-400 hover:text-white px-3 py-1">Fechar</button>
                        </div>
                        
                        <div className="p-5 border-b border-white/5 flex gap-2">
                            <input 
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder="Busque por Título, SKU ou MLB..."
                                className="flex-1 bg-[#1A1A24] border border-white/10 rounded-lg py-2 px-3 text-white focus:outline-none focus:border-blue-500 text-sm"
                            />
                            <button 
                                onClick={handleSearch}
                                disabled={isSearching || !searchQuery}
                                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2"
                            >
                                {isSearching ? 'Buscando...' : 'Buscar'}
                            </button>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto p-5 bg-[#09090b]">
                            {searchResults.length === 0 && !isSearching && (
                                <div className="text-center py-10 text-slate-500 text-sm">
                                    Nenhum produto encontrado ou busque acima.
                                </div>
                            )}
                            <div className="space-y-2">
                                {searchResults.map((cand: any, idx: number) => (
                                    <div key={`${cand.mlb_id}-${cand.variation_id || idx}`} className="bg-[#1A1A24] border border-white/5 p-3 rounded-lg flex items-center justify-between hover:border-blue-500/50 transition-colors">
                                        <div className="flex items-start gap-3">
                                            {cand.thumbnail && <img src={cand.thumbnail} alt="" className="w-10 h-10 rounded object-cover" />}
                                            <div>
                                                <p className="text-sm text-slate-200 font-medium line-clamp-1">{cand.title}</p>
                                                {cand.variation_name && <p className="text-xs text-blue-400 font-medium">Variação: {cand.variation_name}</p>}
                                                {cand.match_reason && !cand.variation_available && <p className="text-[10px] text-amber-500 font-medium mt-0.5">{cand.match_reason}</p>}
                                                {cand.match_reason && cand.variation_available && <p className="text-[10px] text-emerald-500 font-medium mt-0.5">{cand.match_reason}</p>}
                                                <div className="flex items-center gap-3 mt-1 text-[11px] font-mono text-slate-400">
                                                    <span>SKU: {cand.sku || 'N/A'}</span>
                                                    <span>MLB: {cand.mlb_id}</span>
                                                    {cand.variation_id && <span>VAR: {cand.variation_id}</span>}
                                                    {cand.catalog_product_id && <span>CAT: {cand.catalog_product_id}</span>}
                                                    <span className="text-emerald-400">{Number(cand.price).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <button 
                                            onClick={() => confirmLink(searchItem.id, cand.sku, cand.mlb_id, cand.variation_id, cand.catalog_product_id)}
                                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded text-xs font-bold shrink-0"
                                        >
                                            Selecionar
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de Ambiguidade */}
            {showAmbiguousModal && ambiguousItemData && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-[#121217] border border-white/10 rounded-2xl w-full max-w-4xl overflow-hidden flex flex-col max-h-[85vh]">
                        <div className="p-5 border-b border-white/5 flex justify-between items-center bg-[#1A1A24]">
                            <div>
                                <h3 className="text-base font-bold text-amber-500 flex items-center gap-2">
                                    <AlertTriangle size={18} />
                                    Revisão Necessária
                                </h3>
                                <p className="text-[11px] text-slate-400 mt-1 max-w-xl truncate">
                                    Item XML: <span className="text-slate-300 font-medium">{ambiguousItemData.item.description}</span>
                                </p>
                            </div>
                            <button onClick={() => setShowAmbiguousModal(false)} className="text-slate-400 hover:text-white px-3 py-1">Fechar</button>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto p-5 bg-[#09090b]">
                            <p className="text-sm text-slate-300 mb-4">Escolha a opção correta para vínculo:</p>
                            <div className="space-y-3">
                                {ambiguousItemData.candidates.map((cand: any, idx: number) => (
                                    <div key={idx} className="bg-[#1A1A24] border border-white/5 p-4 rounded-xl flex items-center justify-between hover:border-blue-500/50 transition-colors">
                                        <div className="space-y-1.5">
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono text-sm text-white font-bold">{cand.sku}</span>
                                                <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">MLB: {cand.mlb_id || 'N/A'}</span>
                                                {cand.variation_id && <span className="text-[10px] bg-blue-900/40 text-blue-400 px-1.5 py-0.5 rounded font-mono border border-blue-500/20">VAR: {cand.variation_id}</span>}
                                            </div>
                                            <p className="text-xs text-slate-300 font-medium">{cand.title}</p>
                                            {cand.variation_name && <p className="text-xs text-blue-400 font-medium">↳ {cand.variation_name}</p>}
                                            <p className="text-xs text-slate-500 mt-1">{cand.explanation}</p>
                                            <div className="flex gap-3 text-[10px] font-bold uppercase tracking-wider mt-2">
                                                <span className="text-blue-400">Score: {cand.score}</span>
                                                <span className="text-emerald-500">Heurística: {cand.method}</span>
                                            </div>
                                        </div>
                                        <button 
                                            onClick={() => confirmLink(ambiguousItemData.item.id, cand.sku, cand.mlb_id, cand.variation_id, cand.catalog_product_id)}
                                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-bold shadow-lg shadow-emerald-500/20 shrink-0"
                                        >
                                            Confirmar
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Modal de Conciliação */}
            {showReconModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[60] p-4">
                    <div className="bg-[#121217] border border-white/10 rounded-2xl w-full max-w-lg overflow-hidden">
                        <div className="p-5 border-b border-white/5">
                            <h3 className="text-base font-bold text-white flex items-center gap-2">
                                <DollarSign className="text-emerald-500" size={18} />
                                Conciliar Operação
                            </h3>
                            <p className="text-[11px] text-slate-400 mt-1">
                                Qual é a cobertura fiscal desta NF em relação ao pagamento real?
                            </p>
                        </div>
                        
                        <div className="p-5 space-y-5">
                            <div className="flex items-center justify-between bg-[#1A1A24] p-3 rounded-lg border border-white/5">
                                <span className="text-xs text-slate-400">Valor Fiscal Oficial (NF-e):</span>
                                <span className="text-sm font-bold text-white font-mono">
                                    {nfe.total_invoice_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                </span>
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-300 mb-2">Cobertura rápida (calcula o valor real automaticamente):</label>
                                <div className="grid grid-cols-5 gap-2">
                                    {[100, 50, 25, 10, 5].map((pct) => (
                                        <button 
                                            key={pct}
                                            type="button"
                                            onClick={() => setFinancialValue((nfe.total_invoice_value / (pct / 100)).toFixed(2))}
                                            className="bg-slate-800 hover:bg-blue-600/20 border border-white/10 hover:border-blue-500/50 text-slate-300 hover:text-blue-400 text-xs py-2 rounded transition-colors text-center"
                                        >
                                            {pct}%
                                        </button>
                                    ))}
                                </div>
                            </div>
                            
                            <div>
                                <label className="block text-xs font-medium text-emerald-400 mb-1">Informar valor financeiro (R$)</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                        <span className="text-slate-500 font-mono text-sm">R$</span>
                                    </div>
                                    <input 
                                        type="number"
                                        step="0.01"
                                        min="0.01"
                                        value={financialValue}
                                        onChange={(e) => setFinancialValue(e.target.value)}
                                        placeholder="Ex: 16438.74"
                                        className="w-full bg-[#1A1A24] border border-emerald-500/30 rounded-lg py-2 pl-10 pr-3 text-white font-mono focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm"
                                    />
                                </div>
                            </div>
                            
                            {reconError && (
                                <div className="p-3 bg-rose-500/10 text-rose-400 text-xs rounded border border-rose-500/20">
                                    {reconError}
                                </div>
                            )}
                        </div>
                        
                        <div className="p-4 border-t border-white/5 flex gap-2 justify-end bg-[#1A1A24]">
                            <button 
                                onClick={() => setShowReconModal(false)}
                                disabled={submittingRecon}
                                className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
                            >
                                Cancelar
                            </button>
                            <button 
                                onClick={handleReconciliationSubmit}
                                disabled={submittingRecon || !financialValue}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-xs font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {submittingRecon ? 'Salvando...' : 'Confirmar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
