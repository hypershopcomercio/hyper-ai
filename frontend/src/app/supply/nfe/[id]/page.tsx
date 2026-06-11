"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import {
    ArrowLeft, FileText, Building2, Calendar, DollarSign,
    Box, CheckCircle, AlertTriangle, Search, Link2, Truck
} from 'lucide-react';

export default function NFeDetailPage() {
    const params = useParams();
    const router = useRouter();
    const [nfe, setNfe] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (params.id) {
            loadNfe(params.id as string);
        }
    }, [params.id]);

    const loadNfe = async (id: string) => {
        setLoading(true);
        try {
            const res = await api.get(`/nfe/${id}`);
            if (res.data.success) {
                setNfe(res.data.data);
            }
        } catch (error) {
            console.error("Error loading NFe detail", error);
        } finally {
            setLoading(false);
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

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 space-y-6">
            <button onClick={() => router.push('/supply/nfe')} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm w-fit">
                <ArrowLeft size={16} /> Voltar para lista de NFs
            </button>

            {/* Header NFe */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-32 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 relative z-10">
                    <div className="space-y-4 flex-1">
                        <div>
                            <div className="flex items-center gap-3 mb-1">
                                <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                                    <FileText className="text-blue-500" />
                                    NF-e {nfe.nfe_number || '-'} 
                                    <span className="text-slate-500 text-lg font-normal">Série {nfe.series || '-'}</span>
                                </h1>
                                {nfe.status === 'linked' ? (
                                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-xs rounded border border-emerald-500/20">Vinculada</span>
                                ) : (
                                    <span className="px-2 py-0.5 bg-amber-500/10 text-amber-400 text-xs rounded border border-amber-500/20">Análise Pendente</span>
                                )}
                            </div>
                            <p className="text-slate-400 text-xs font-mono break-all max-w-2xl">{nfe.access_key}</p>
                        </div>

                        <div className="flex flex-wrap gap-x-8 gap-y-4">
                            <div className="flex items-start gap-3">
                                <Building2 className="text-slate-500 mt-0.5" size={16} />
                                <div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Fornecedor / Emitente</p>
                                    <p className="text-sm text-slate-200 font-medium">{nfe.issuer_name}</p>
                                    <p className="text-xs text-slate-400 font-mono">{nfe.issuer_cnpj}</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Calendar className="text-slate-500 mt-0.5" size={16} />
                                <div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Emissão</p>
                                    <p className="text-sm text-slate-200">{new Date(nfe.issue_date).toLocaleString('pt-BR')}</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <Truck className="text-slate-500 mt-0.5" size={16} />
                                <div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Frete Total</p>
                                    <p className="text-sm text-slate-200">{nfe.total_freight.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[#1A1A24] border border-white/5 p-5 rounded-xl min-w-[200px] shrink-0">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1 flex items-center gap-1">
                            <DollarSign size={12} /> Valor Total da NF
                        </p>
                        <p className="text-3xl font-black text-white font-mono tracking-tight">
                            {nfe.total_invoice_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                        </p>
                    </div>
                </div>
            </div>

            {/* Items Table */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl overflow-hidden">
                <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
                    <h3 className="font-bold text-white flex items-center gap-2">
                        <Box size={18} className="text-slate-400" />
                        Itens da Nota ({nfe.items.length})
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-[#1A1A24] border-b border-white/5 text-slate-400 text-xs">
                            <tr>
                                <th className="px-4 py-3 font-medium w-12 text-center">#</th>
                                <th className="px-4 py-3 font-medium min-w-[250px]">Produto (XML) / Identificadores</th>
                                <th className="px-4 py-3 font-medium text-right">Qtd</th>
                                <th className="px-4 py-3 font-medium text-right">Val. Unit</th>
                                <th className="px-4 py-3 font-medium text-right">Impostos & Rateio</th>
                                <th className="px-4 py-3 font-medium text-right">Custo Unit NF</th>
                                <th className="px-4 py-3 font-medium min-w-[200px]">Vínculo de Catálogo</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {nfe.items.map((item: any) => (
                                <tr key={item.id} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-4 py-4 text-center text-slate-500 font-mono text-xs">{item.n_item}</td>
                                    
                                    {/* Identificadores e Descrição */}
                                    <td className="px-4 py-4">
                                        <div className="font-medium text-slate-200 mb-2 truncate max-w-[300px]" title={item.description}>
                                            {item.description}
                                        </div>
                                        <div className="flex flex-wrap gap-2 text-xs">
                                            {item.ean && item.ean !== "SEM GTIN" ? (
                                                <span className="px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded font-mono border border-blue-500/20" title="EAN">
                                                    EAN: {item.ean}
                                                </span>
                                            ) : (
                                                <span className="px-1.5 py-0.5 bg-slate-800 text-slate-500 rounded font-mono" title="EAN">
                                                    Sem GTIN
                                                </span>
                                            )}
                                            {item.sku_supplier && (
                                                <span className="px-1.5 py-0.5 bg-purple-500/10 text-purple-400 rounded font-mono border border-purple-500/20" title="Código do Fornecedor (cProd)">
                                                    Forn: {item.sku_supplier}
                                                </span>
                                            )}
                                            <span className="px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded font-mono" title="NCM">
                                                NCM: {item.ncm}
                                            </span>
                                        </div>
                                    </td>
                                    
                                    {/* Quantidade */}
                                    <td className="px-4 py-4 text-right font-mono text-slate-300">
                                        {item.quantity}
                                    </td>
                                    
                                    {/* Valor Unitario Bruto */}
                                    <td className="px-4 py-4 text-right font-mono text-slate-300">
                                        {item.unit_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        <div className="text-[10px] text-slate-500 mt-1">
                                            Total: {item.product_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </div>
                                    </td>
                                    
                                    {/* Impostos e Rateio */}
                                    <td className="px-4 py-4 text-right">
                                        <div className="flex flex-col items-end gap-1 text-[10px] font-mono text-slate-400">
                                            {item.freight_allocated > 0 && <div>+ Frete: {item.freight_allocated.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</div>}
                                            {item.ipi_value > 0 && <div>+ IPI: {item.ipi_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</div>}
                                            {item.st_value > 0 && <div>+ ST: {item.st_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</div>}
                                            {item.icms_value > 0 && <div className="text-slate-500">ICMS: {item.icms_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} (embutido)</div>}
                                        </div>
                                    </td>
                                    
                                    {/* Custo Real Resolvido da NF */}
                                    <td className="px-4 py-4 text-right">
                                        <div className="font-mono text-emerald-400 font-bold">
                                            {item.unit_cost_nf.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </div>
                                        <div className="text-[10px] text-slate-500 mt-1 uppercase tracking-wider">
                                            Custo Contábil
                                        </div>
                                    </td>
                                    
                                    {/* Status do Vinculo */}
                                    <td className="px-4 py-4 bg-black/20">
                                        {item.link_status === 'confirmed' ? (
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-bold">
                                                    <CheckCircle size={14} /> SKU: {item.linked_sku}
                                                </div>
                                                <div className="text-[10px] text-slate-500">MLB: {item.linked_mlb_id}</div>
                                            </div>
                                        ) : (
                                            <div className="flex flex-col items-start gap-2">
                                                <div className="flex items-center gap-1.5 text-amber-500/80 text-xs font-medium">
                                                    <AlertTriangle size={14} /> Vínculo Pendente
                                                </div>
                                                <button className="flex items-center gap-2 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/20 px-3 py-1.5 rounded text-xs font-medium transition-colors w-full justify-center">
                                                    <Link2 size={14} /> Buscar Produto
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
