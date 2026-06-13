"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import {
    ArrowLeft, FileText, Building2, Calendar, DollarSign,
    Box, CheckCircle, AlertTriangle, Search, Link2, Truck, Info, CheckCircle2, ChevronRight
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
    const [linkerSummary, setLinkerSummary] = useState<any>(null); // Results from last run
    
    // Manual Search Modal
    const [showSearchModal, setShowSearchModal] = useState(false);
    const [searchItem, setSearchItem] = useState<any>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    
    // Ambiguous Modal
    const [showAmbiguousModal, setShowAmbiguousModal] = useState(false);
    const [ambiguousItemData, setAmbiguousItemData] = useState<any>(null); // from linkerSummary

    useEffect(() => {
        if (params.id) {
            loadNfe(params.id as string);
        }
    }, [params.id]);

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
    
    const handleRunLinker = async () => {
        setLinkingItems(true);
        try {
            const res = await api.post(`/nfe/${params.id}/linker/run`);
            if (res.data.success) {
                setLinkerSummary(res.data.data);
            }
            loadNfe(params.id as string);
        } catch (error: any) {
            console.error("Error running linker", error);
            alert("Erro ao rodar Linker: " + (error.response?.data?.error || error.message));
        } finally {
            setLinkingItems(false);
        }
    };
    
    const confirmBatch = async () => {
        try {
            await api.post(`/nfe/${params.id}/linker/confirm_batch`);
            loadNfe(params.id as string);
            // Optionally clear linker summary or update it
            if (linkerSummary) {
                const newSummary = {...linkerSummary};
                newSummary.suggested_count = 0;
                setLinkerSummary(newSummary);
            }
        } catch (error) {
            console.error("Error confirming batch", error);
        }
    };
    
    const confirmLink = async (itemId: number, sku: string, mlbId: string) => {
        try {
            await api.post(`/nfe/${params.id}/items/${itemId}/confirm`, {
                linked_sku: sku,
                linked_mlb_id: mlbId
            });
            setShowAmbiguousModal(false);
            setShowSearchModal(false);
            loadNfe(params.id as string);
        } catch (error) {
            console.error("Error confirming link", error);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery) return;
        setIsSearching(true);
        try {
            const res = await api.get(`/ads?search=${encodeURIComponent(searchQuery)}&limit=10`);
            setSearchResults(res.data.data || []);
        } catch (error) {
            console.error(error);
        } finally {
            setIsSearching(false);
        }
    };

    if (loading) {
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

    // Calculando métricas da tabela combinando DB state e Linker state local
    const totalItems = nfe.items.length;
    let confirmedCount = 0;
    let suggestedHighCount = 0;
    let reviewNeededCount = 0;
    let pendingCount = 0;

    nfe.items.forEach((item: any) => {
        // Find if we have an ambiguous state for this item from recent run
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
                    <div className="flex items-center justify-center p-6 bg-[#1A1A24] rounded-lg border border-white/5 border-dashed">
                        <div className="text-center flex flex-col items-center">
                            <p className="text-amber-500 text-sm font-medium mb-1">Conciliação Pendente</p>
                            <p className="text-slate-400 text-[11px]">Nenhum valor financeiro real foi vinculado a esta nota ainda.</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Banner de Resumo do Linker */}
            <div className="grid grid-cols-5 gap-3">
                <div className="bg-[#1A1A24] border border-white/5 p-3 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">Total de Itens</p>
                    <p className="text-xl font-bold text-white">{totalItems}</p>
                </div>
                <div className="bg-emerald-500/5 border border-emerald-500/20 p-3 rounded-lg">
                    <p className="text-[10px] text-emerald-500/80 uppercase font-bold mb-1">Alta Confiança</p>
                    <p className="text-xl font-bold text-emerald-400">{suggestedHighCount}</p>
                </div>
                <div className="bg-amber-500/5 border border-amber-500/20 p-3 rounded-lg">
                    <p className="text-[10px] text-amber-500/80 uppercase font-bold mb-1">Revisão Necessária</p>
                    <p className="text-xl font-bold text-amber-400">{reviewNeededCount}</p>
                </div>
                <div className="bg-blue-500/5 border border-blue-500/20 p-3 rounded-lg">
                    <p className="text-[10px] text-blue-500/80 uppercase font-bold mb-1">Pendentes</p>
                    <p className="text-xl font-bold text-blue-400">{pendingCount}</p>
                </div>
                <div className="bg-slate-800 border border-white/10 p-3 rounded-lg">
                    <p className="text-[10px] text-slate-400 uppercase font-bold mb-1">Confirmados</p>
                    <p className="text-xl font-bold text-white">{confirmedCount}</p>
                </div>
            </div>

            {/* Items Table */}
            <div className="bg-[#121217] border border-white/5 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#1A1A24]">
                    <h3 className="font-bold text-white flex items-center gap-2 text-sm">
                        <Box size={16} className="text-slate-400" />
                        Itens da Nota
                    </h3>
                    <div className="flex gap-2">
                        <button 
                            onClick={handleRunLinker}
                            disabled={linkingItems || confirmedCount === totalItems}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-xs font-bold transition-colors disabled:opacity-50 flex items-center gap-2"
                        >
                            <Search size={14} />
                            {linkingItems ? 'Analisando vínculos...' : 'Sugerir Vínculos Automaticamente'}
                        </button>
                        {suggestedHighCount > 0 && (
                            <button 
                                onClick={confirmBatch}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md text-xs font-bold transition-colors flex items-center gap-2"
                            >
                                <CheckCircle2 size={14} />
                                Confirmar todos ({suggestedHighCount})
                            </button>
                        )}
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                        <thead className="bg-[#1A1A24] border-b border-white/5 text-slate-400">
                            <tr>
                                <th className="px-3 py-2 font-medium w-10 text-center">#</th>
                                <th className="px-3 py-2 font-medium min-w-[200px]">Produto (XML) / Identificadores</th>
                                <th className="px-3 py-2 font-medium text-right">Qtd</th>
                                <th className="px-3 py-2 font-medium text-right">Val. Unit</th>
                                <th className="px-3 py-2 font-medium text-right">Custo Contábil</th>
                                <th className="px-3 py-2 font-medium min-w-[250px]">Vínculo de Catálogo</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {nfe.items.map((item: any) => {
                                const linkerItem = linkerSummary?.suggestions?.find((s:any) => s.n_item === item.n_item);
                                const isAmbiguous = linkerItem && linkerItem.status === 'ambiguous';
                                const isPendingWithoutSuggestion = item.link_status === 'pending' && (!linkerItem || linkerItem.status === 'pending');
                                
                                return (
                                <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-3 py-4 text-center text-slate-500 font-mono text-[10px] align-top">{item.n_item}</td>
                                    
                                    {/* Identificadores e Descrição */}
                                    <td className="px-3 py-4 align-top">
                                        <div className="font-medium text-slate-200 mb-2 max-w-[300px]" title={item.description}>
                                            {item.description}
                                        </div>
                                        <div className="flex flex-wrap gap-1.5 text-[9px]">
                                            {item.ean && item.ean !== "SEM GTIN" ? (
                                                <span className="px-1 py-0.5 bg-blue-500/10 text-blue-400 rounded font-mono border border-blue-500/20">
                                                    EAN: {item.ean}
                                                </span>
                                            ) : (
                                                <span className="px-1 py-0.5 bg-slate-800 text-slate-500 rounded font-mono">
                                                    Sem GTIN
                                                </span>
                                            )}
                                            {item.sku_supplier && (
                                                <span className="px-1 py-0.5 bg-purple-500/10 text-purple-400 rounded font-mono border border-purple-500/20">
                                                    cProd: {item.sku_supplier}
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    
                                    {/* Quantidade */}
                                    <td className="px-3 py-4 text-right font-mono text-slate-300 align-top">
                                        {item.quantity}
                                    </td>
                                    
                                    {/* Valor Unitario Bruto */}
                                    <td className="px-3 py-4 text-right font-mono text-slate-300 align-top">
                                        {item.unit_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        <div className="text-[9px] text-slate-500 mt-1">
                                            Total: {item.product_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </div>
                                    </td>
                                    
                                    {/* Custo Real Resolvido da NF */}
                                    <td className="px-3 py-4 text-right align-top">
                                        <div className="font-mono text-emerald-400 font-bold text-sm">
                                            {item.unit_cost_nf.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </div>
                                    </td>
                                    
                                    {/* Status do Vinculo */}
                                    <td className="px-3 py-4 align-top bg-black/20 border-l border-white/5">
                                        {item.link_status === 'confirmed' ? (
                                            <div className="bg-emerald-500/10 border border-emerald-500/20 p-2 rounded-lg">
                                                <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-bold mb-1">
                                                    <CheckCircle size={14} /> Confirmado
                                                </div>
                                                <div className="font-mono text-[11px] text-white">SKU: {item.linked_sku}</div>
                                                {item.linked_mlb_id && <div className="text-[10px] text-slate-400 mt-0.5">MLB: {item.linked_mlb_id}</div>}
                                            </div>
                                        ) : isAmbiguous ? (
                                            <div className="bg-amber-500/10 border border-amber-500/20 p-2 rounded-lg flex flex-col gap-2">
                                                <div className="flex items-center gap-1.5 text-amber-500 text-xs font-bold">
                                                    <AlertTriangle size={14} /> Revisão Necessária
                                                </div>
                                                <p className="text-[9px] text-amber-400/80">Múltiplos candidatos encontrados</p>
                                                <button 
                                                    onClick={() => {
                                                        setAmbiguousItemData({ item, candidates: linkerItem.candidates });
                                                        setShowAmbiguousModal(true);
                                                    }}
                                                    className="w-full bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 py-1.5 rounded text-[10px] font-bold transition-colors"
                                                >
                                                    Ver Opções ({linkerItem.candidates.length})
                                                </button>
                                            </div>
                                        ) : item.link_status === 'suggested' ? (
                                            <div className="bg-blue-500/10 border border-blue-500/20 p-2 rounded-lg flex flex-col gap-2">
                                                <div className="flex items-center gap-1.5 text-blue-400 text-xs font-bold">
                                                    <Info size={14} /> 
                                                    {item.link_confidence === 'high' ? 'Sugestão: Alta Confiança' : 'Revisão Necessária'}
                                                </div>
                                                <div>
                                                    <div className="font-mono text-[11px] text-white">SKU: {item.linked_sku}</div>
                                                    {item.linked_mlb_id && <div className="text-[10px] text-slate-400 mt-0.5">MLB: {item.linked_mlb_id}</div>}
                                                </div>
                                                <div className="flex gap-1.5 w-full mt-1">
                                                    <button 
                                                        onClick={() => confirmLink(item.id, item.linked_sku, item.linked_mlb_id)}
                                                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-1.5 rounded text-[10px] font-bold transition-colors text-center"
                                                    >
                                                        Confirmar
                                                    </button>
                                                    <button 
                                                        onClick={() => {
                                                            setSearchItem(item);
                                                            setShowSearchModal(true);
                                                        }}
                                                        className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-white/10 py-1.5 rounded text-[10px] font-medium transition-colors text-center"
                                                    >
                                                        Trocar
                                                    </button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="bg-slate-800/50 border border-white/5 p-2 rounded-lg flex flex-col items-center gap-2">
                                                <div className="text-slate-500 text-[10px] font-medium uppercase tracking-wider mb-1">
                                                    Sem sugestão
                                                </div>
                                                <button 
                                                    onClick={() => {
                                                        setSearchItem(item);
                                                        setShowSearchModal(true);
                                                    }}
                                                    className="w-full flex items-center justify-center gap-1.5 bg-white/5 hover:bg-white/10 text-slate-300 py-1.5 rounded text-[10px] font-medium transition-colors border border-white/10"
                                                >
                                                    <Search size={12} /> Buscar Manualmente
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
                                    Vincular Produto Manualmente
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
                                {searchResults.map((ad: any) => (
                                    <div key={ad.id} className="bg-[#1A1A24] border border-white/5 p-3 rounded-lg flex items-center justify-between hover:border-blue-500/50 transition-colors">
                                        <div className="flex items-start gap-3">
                                            {ad.thumbnail && <img src={ad.thumbnail} alt="" className="w-10 h-10 rounded object-cover" />}
                                            <div>
                                                <p className="text-sm text-slate-200 font-medium line-clamp-1">{ad.title}</p>
                                                <div className="flex items-center gap-3 mt-1 text-[11px] font-mono text-slate-400">
                                                    <span>SKU: {ad.sku || 'N/A'}</span>
                                                    <span>MLB: {ad.id}</span>
                                                    <span className="text-emerald-400">{Number(ad.price).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <button 
                                            onClick={() => confirmLink(searchItem.id, ad.sku, ad.id)}
                                            className="bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 px-3 py-1.5 rounded text-xs font-bold"
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
                                    Revisão Necessária: Múltiplos Candidatos
                                </h3>
                                <p className="text-[11px] text-slate-400 mt-1 max-w-xl truncate">
                                    Item XML: <span className="text-slate-300 font-medium">{ambiguousItemData.item.description}</span>
                                </p>
                            </div>
                            <button onClick={() => setShowAmbiguousModal(false)} className="text-slate-400 hover:text-white px-3 py-1">Fechar</button>
                        </div>
                        
                        <div className="flex-1 overflow-y-auto p-5 bg-[#09090b]">
                            <p className="text-sm text-slate-300 mb-4">O Linker encontrou candidatos muito similares. Escolha o correto:</p>
                            <div className="space-y-3">
                                {ambiguousItemData.candidates.map((cand: any, idx: number) => (
                                    <div key={idx} className="bg-[#1A1A24] border border-white/5 p-4 rounded-xl flex items-center justify-between hover:border-blue-500/50 transition-colors">
                                        <div className="space-y-1.5">
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono text-sm text-white font-bold">{cand.sku}</span>
                                                <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">MLB: {cand.mlb_id || 'N/A'}</span>
                                            </div>
                                            <p className="text-xs text-slate-400">{cand.explanation}</p>
                                            <div className="flex gap-3 text-[10px] font-bold uppercase tracking-wider mt-2">
                                                <span className="text-blue-400">Score: {cand.score}</span>
                                                <span className="text-emerald-500">Heurística: {cand.method}</span>
                                            </div>
                                        </div>
                                        <button 
                                            onClick={() => confirmLink(ambiguousItemData.item.id, cand.sku, cand.mlb_id)}
                                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-bold shadow-lg shadow-emerald-500/20"
                                        >
                                            Confirmar Este
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Modal de Conciliação (existente) */}
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
                                {financialValue && parseFloat(financialValue) > 0 && (
                                    <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-center justify-between">
                                        <div>
                                            <p className="text-[10px] text-emerald-500/80 font-bold uppercase tracking-wider">Multiplicador de Custo</p>
                                            <p className="text-sm text-emerald-400 font-mono font-bold mt-0.5">{(parseFloat(financialValue) / nfe.total_invoice_value).toFixed(4)}x</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-[10px] text-emerald-500/80 font-bold uppercase tracking-wider">Cobertura Calculada</p>
                                            <p className="text-sm text-emerald-400 font-mono font-bold mt-0.5">{((nfe.total_invoice_value / parseFloat(financialValue)) * 100).toFixed(2)}%</p>
                                        </div>
                                    </div>
                                )}
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
                                {submittingRecon ? 'Salvando...' : 'Confirmar Conciliação'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
