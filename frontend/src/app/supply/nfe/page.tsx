"use client";

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import {
    FileText, Upload, CheckCircle, AlertTriangle, XCircle, Search, 
    ArrowRight, Loader2, FileUp, Box
} from 'lucide-react';

interface NfeImportSummary {
    id: number;
    access_key: string;
    nfe_number: string;
    series: string;
    issue_date: string;
    issuer_name: string;
    issuer_cnpj: string;
    total_invoice_value: number;
    status: string;
    parse_status: string;
    items_count: number;
    linked_items: number;
    created_at: string;
}

export default function NFeListPage() {
    const [nfes, setNfes] = useState<NfeImportSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const router = useRouter();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await api.get('/nfe');
            if (res.data.success) {
                setNfes(res.data.data);
            }
        } catch (error) {
            console.error("Error loading NFe data", error);
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0) return;
        const file = e.target.files[0];
        
        setUploading(true);
        setUploadError(null);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await api.post('/nfe/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            
            if (res.data.success || res.status === 201) {
                router.push(`/supply/nfe/${res.data.id}`);
            }
        } catch (error: any) {
            if (error.response && error.response.status === 409) {
                setUploadError("Esta Nota Fiscal já foi importada anteriormente.");
            } else if (error.response && error.response.data && error.response.data.error) {
                setUploadError(error.response.data.error);
            } else {
                setUploadError("Erro desconhecido ao processar o XML.");
            }
            console.error(error);
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const getStatusBadge = (status: string, parse_status: string) => {
        if (parse_status === 'error') {
            return <span className="px-2 py-1 bg-rose-500/10 text-rose-400 text-xs rounded-md border border-rose-500/20 flex items-center gap-1"><XCircle size={12}/> Erro</span>;
        }
        
        switch (status) {
            case 'imported':
                return <span className="px-2 py-1 bg-slate-500/10 text-slate-400 text-xs rounded-md border border-slate-500/20">Importada</span>;
            case 'pending_link':
                return <span className="px-2 py-1 bg-amber-500/10 text-amber-400 text-xs rounded-md border border-amber-500/20 flex items-center gap-1"><AlertTriangle size={12}/> Pendente</span>;
            case 'linked':
                return <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-md border border-emerald-500/20 flex items-center gap-1"><CheckCircle size={12}/> Vinculada</span>;
            case 'conflict':
                return <span className="px-2 py-1 bg-rose-500/10 text-rose-400 text-xs rounded-md border border-rose-500/20">Conflito</span>;
            default:
                return <span className="px-2 py-1 bg-slate-500/10 text-slate-400 text-xs rounded-md border border-slate-500/20">{status}</span>;
        }
    };

    return (
        <div className="min-h-screen bg-[#09090b] text-slate-100 p-8 space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <FileText className="text-blue-500" />
                        Notas Fiscais (XML)
                    </h1>
                    <p className="text-slate-400 mt-1">Repositório fiscal para cruzamento e automação de custos reais.</p>
                </div>
                <div>
                    <input 
                        type="file" 
                        accept=".xml" 
                        className="hidden" 
                        ref={fileInputRef} 
                        onChange={handleFileChange}
                        disabled={uploading}
                    />
                    <button 
                        onClick={() => fileInputRef.current?.click()}
                        disabled={uploading}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                        {uploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                        {uploading ? "Processando..." : "Importar XML"}
                    </button>
                </div>
            </div>

            {/* Error Message */}
            {uploadError && (
                <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-4 flex items-start gap-3">
                    <AlertTriangle className="text-rose-500 shrink-0 mt-0.5" size={18} />
                    <div>
                        <h4 className="font-bold text-rose-400 text-sm">Falha na Importação</h4>
                        <p className="text-sm text-rose-300/80">{uploadError}</p>
                    </div>
                </div>
            )}

            {/* Feature Plugs for Future */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#121217] border border-blue-500/30 rounded-xl p-4 flex items-center gap-3 opacity-100">
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center shrink-0">
                        <FileUp className="text-blue-500" size={18} />
                    </div>
                    <div>
                        <p className="text-sm font-bold text-white">Upload Manual</p>
                        <p className="text-xs text-slate-500">Ativo na V1</p>
                    </div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-xl p-4 flex items-center gap-3 opacity-50 grayscale">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
                        <Search className="text-slate-400" size={18} />
                    </div>
                    <div>
                        <p className="text-sm font-bold text-white">Chave de Acesso</p>
                        <p className="text-xs text-slate-500">Em Breve</p>
                    </div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-xl p-4 flex items-center gap-3 opacity-50 grayscale">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
                        <Box className="text-slate-400" size={18} />
                    </div>
                    <div>
                        <p className="text-sm font-bold text-white">Integração Tiny</p>
                        <p className="text-xs text-slate-500">Em Breve</p>
                    </div>
                </div>
                <div className="bg-[#121217] border border-white/5 rounded-xl p-4 flex items-center gap-3 opacity-50 grayscale">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
                        <AlertTriangle className="text-slate-400" size={18} />
                    </div>
                    <div>
                        <p className="text-sm font-bold text-white">SEFAZ Auto</p>
                        <p className="text-xs text-slate-500">Em Breve</p>
                    </div>
                </div>
            </div>

            {/* List */}
            <div className="bg-[#121217] border border-white/5 rounded-2xl overflow-hidden">
                {loading ? (
                    <div className="p-12 flex justify-center"><Loader2 size={32} className="animate-spin text-slate-500" /></div>
                ) : nfes.length === 0 ? (
                    <div className="p-12 text-center text-slate-500">
                        <FileText size={48} className="mx-auto mb-4 opacity-20" />
                        <p>Nenhuma nota fiscal importada ainda.</p>
                        <p className="text-sm mt-1">Faça o upload do seu primeiro XML de compra.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left whitespace-nowrap">
                            <thead className="bg-[#1A1A24] border-b border-white/5 text-slate-400">
                                <tr>
                                    <th className="px-6 py-4 font-medium">Nota / Série</th>
                                    <th className="px-6 py-4 font-medium">Emissão</th>
                                    <th className="px-6 py-4 font-medium">Fornecedor</th>
                                    <th className="px-6 py-4 font-medium">Valor Total</th>
                                    <th className="px-6 py-4 font-medium text-center">Vínculos</th>
                                    <th className="px-6 py-4 font-medium">Status</th>
                                    <th className="px-6 py-4 font-medium"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {nfes.map((nfe) => (
                                    <tr key={nfe.id} className="hover:bg-white/[0.02] transition-colors cursor-pointer" onClick={() => router.push(`/supply/nfe/${nfe.id}`)}>
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-white">{nfe.nfe_number || '-'} <span className="text-slate-500 font-normal">/ {nfe.series || '-'}</span></div>
                                            <div className="text-[10px] text-slate-500 truncate max-w-[200px]" title={nfe.access_key}>{nfe.access_key}</div>
                                        </td>
                                        <td className="px-6 py-4 text-slate-300">
                                            {new Date(nfe.issue_date).toLocaleDateString('pt-BR')}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="text-slate-200 truncate max-w-[250px]" title={nfe.issuer_name}>{nfe.issuer_name}</div>
                                            <div className="text-[10px] text-slate-500 font-mono">{nfe.issuer_cnpj}</div>
                                        </td>
                                        <td className="px-6 py-4 font-mono text-white">
                                            {nfe.total_invoice_value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-slate-800 text-xs">
                                                <span className={nfe.linked_items === nfe.items_count ? "text-emerald-400 font-bold" : "text-amber-400 font-bold"}>
                                                    {nfe.linked_items}
                                                </span>
                                                <span className="text-slate-500">/ {nfe.items_count}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            {getStatusBadge(nfe.status, nfe.parse_status)}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button className="text-slate-400 hover:text-white p-2" title="Abrir Detalhes">
                                                <ArrowRight size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
