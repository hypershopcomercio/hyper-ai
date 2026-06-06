import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Save, AlertCircle, Calculator, Info } from "lucide-react";
import { PremiumLoader } from "@/components/ui/PremiumLoader";

interface Props {
    adId: string;
    onSaved?: () => void;
}

export function FiscalParametersTab({ adId, onSaved }: Props) {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Tax Profile State
    const [sku, setSku] = useState("");
    const [productOrigin, setProductOrigin] = useState("nacional");
    const [originUf, setOriginUf] = useState("");
    const [destinationUfDefault, setDestinationUfDefault] = useState("");
    const [ncm, setNcm] = useState("");
    const [cest, setCest] = useState("");
    const [hasSt, setHasSt] = useState(false);
    const [hasIpi, setHasIpi] = useState(false);
    const [hasDifal, setHasDifal] = useState(false);
    const [mvaRate, setMvaRate] = useState<number | "">("");
    const [ipiRate, setIpiRate] = useState<number | "">("");
    const [originIcmsRate, setOriginIcmsRate] = useState<number | "">("");
    const [destinationIcmsRate, setDestinationIcmsRate] = useState<number | "">("");
    const [taxNotes, setTaxNotes] = useState("");

    // Purchase Cost State
    const [realCost, setRealCost] = useState<number | "">("");
    const [nfValue, setNfValue] = useState<number | "">("");
    const [freightCost, setFreightCost] = useState<number | "">("");
    const [packagingCost, setPackagingCost] = useState<number | "">("");
    const [otherCosts, setOtherCosts] = useState<number | "">("");
    const [supplierName, setSupplierName] = useState("");
    const [nfNumber, setNfNumber] = useState("");

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/ads/${adId}/fiscal-profile`);
            const data = res.data?.data;
            if (data) {
                if (data.tax_profile) {
                    const tp = data.tax_profile;
                    setSku(tp.sku || "");
                    setProductOrigin(tp.product_origin || "nacional");
                    setOriginUf(tp.origin_uf || "");
                    setDestinationUfDefault(tp.destination_uf_default || "");
                    setNcm(tp.ncm || "");
                    setCest(tp.cest || "");
                    setHasSt(tp.has_st || false);
                    setHasIpi(tp.has_ipi || false);
                    setHasDifal(tp.has_difal || false);
                    setMvaRate(tp.mva_rate ?? "");
                    setIpiRate(tp.ipi_rate ?? "");
                    setOriginIcmsRate(tp.origin_icms_rate ?? "");
                    setDestinationIcmsRate(tp.destination_icms_rate ?? "");
                    setTaxNotes(tp.notes || "");
                }
                if (data.purchase_cost) {
                    const pc = data.purchase_cost;
                    if (!data.tax_profile?.sku) setSku(pc.sku || "");
                    setRealCost(pc.real_cost ?? "");
                    setNfValue(pc.nf_value ?? "");
                    setFreightCost(pc.freight_cost ?? "");
                    setPackagingCost(pc.packaging_cost ?? "");
                    setOtherCosts(pc.other_costs ?? "");
                    setSupplierName(pc.supplier_name || "");
                    setNfNumber(pc.nf_number || "");
                }
            }
        } catch (err: any) {
            if (err.response?.status === 404) {
                toast.error("Anúncio não encontrado (404).");
            } else if (err.response?.status === 401) {
                toast.error("Acesso Negado (401). Faça login novamente.");
            } else {
                toast.error("Erro ao carregar dados fiscais.");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [adId]);

    const handleSave = async () => {
        setSaving(true);
        try {
            const payload = {
                tax_profile: {
                    sku,
                    product_origin: productOrigin,
                    origin_uf: originUf,
                    destination_uf_default: destinationUfDefault,
                    ncm,
                    cest,
                    has_st: hasSt,
                    has_ipi: hasIpi,
                    has_difal: hasDifal,
                    mva_rate: mvaRate === "" ? null : Number(mvaRate),
                    ipi_rate: ipiRate === "" ? null : Number(ipiRate),
                    origin_icms_rate: originIcmsRate === "" ? null : Number(originIcmsRate),
                    destination_icms_rate: destinationIcmsRate === "" ? null : Number(destinationIcmsRate),
                    notes: taxNotes,
                    is_active: true
                },
                purchase_cost: {
                    sku,
                    real_cost: realCost === "" ? 0 : Number(realCost),
                    nf_value: nfValue === "" ? null : Number(nfValue),
                    freight_cost: freightCost === "" ? 0 : Number(freightCost),
                    packaging_cost: packagingCost === "" ? 0 : Number(packagingCost),
                    other_costs: otherCosts === "" ? 0 : Number(otherCosts),
                    supplier_name: supplierName,
                    nf_number: nfNumber,
                    data_source: "manual",
                    is_active: true
                }
            };

            await api.put(`/ads/${adId}/fiscal-profile`, payload);
            toast.success("Perfil fiscal atualizado com sucesso!");
            if (onSaved) onSaved();
            loadData();
        } catch (err: any) {
            console.error(err);
            toast.error("Erro ao salvar perfil fiscal.");
        } finally {
            setSaving(false);
        }
    };

    // Auto-calculate NF%
    const nfPercentage = (typeof nfValue === 'number' && typeof realCost === 'number' && realCost > 0)
        ? ((nfValue / realCost) * 100).toFixed(1)
        : null;



    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-indigo-400" />
                        Parâmetros Fiscais (V1)
                        {loading && <span className="ml-4 text-xs font-normal text-slate-400 flex items-center gap-2"><PremiumLoader /> Carregando...</span>}
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                        Configure as alíquotas reais de compra e NCM deste produto para precisão na DRE.
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 shadow-sm"
                >
                    {saving ? <PremiumLoader /> : <Save className="w-4 h-4" />}
                    Salvar
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* PERFIL FISCAL */}
                <div className="bg-[#131B2C] border border-[#1E293B] rounded-xl p-5 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-emerald-400" />
                        <h4 className="font-semibold text-slate-200">Perfil de Tributação</h4>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">SKU Pai</label>
                            <input
                                type="text"
                                value={sku}
                                onChange={e => setSku(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
                                placeholder="EX: 001"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Origem do Produto</label>
                            <select
                                value={productOrigin}
                                onChange={e => setProductOrigin(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white focus:border-indigo-500 outline-none"
                            >
                                <option value="nacional">0 - Nacional</option>
                                <option value="importado">1,2,3 - Importado</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">NCM</label>
                            <input
                                type="text"
                                value={ncm}
                                onChange={e => setNcm(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                placeholder="0000.00.00"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">CEST</label>
                            <input
                                type="text"
                                value={cest}
                                onChange={e => setCest(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                placeholder="00.000.00"
                            />
                        </div>

                        <div>
                            <label className="block text-xs text-slate-400 mb-1">UF Origem (Sua)</label>
                            <input
                                type="text"
                                maxLength={2}
                                value={originUf}
                                onChange={e => setOriginUf(e.target.value.toUpperCase())}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white uppercase"
                                placeholder="SP"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">UF Destino Padrão</label>
                            <input
                                type="text"
                                maxLength={2}
                                value={destinationUfDefault}
                                onChange={e => setDestinationUfDefault(e.target.value.toUpperCase())}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white uppercase"
                                placeholder="SP"
                            />
                        </div>
                    </div>

                    <div className="pt-2 border-t border-[#1E293B]">
                        <div className="flex gap-4 mb-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" checked={hasSt} onChange={e => setHasSt(e.target.checked)} className="rounded bg-slate-800 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
                                <span className="text-sm text-slate-300">Tem ST</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" checked={hasIpi} onChange={e => setHasIpi(e.target.checked)} className="rounded bg-slate-800 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
                                <span className="text-sm text-slate-300">Tem IPI</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" checked={hasDifal} onChange={e => setHasDifal(e.target.checked)} className="rounded bg-slate-800 border-slate-700 text-indigo-500 focus:ring-indigo-500" />
                                <span className="text-sm text-slate-300">Difal</span>
                            </label>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            {hasSt && (
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">MVA Original (%)</label>
                                    <input
                                        type="number"
                                        value={mvaRate}
                                        onChange={e => setMvaRate(e.target.value === "" ? "" : Number(e.target.value))}
                                        className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                        step="0.01"
                                    />
                                </div>
                            )}
                            {hasIpi && (
                                <div>
                                    <label className="block text-xs text-slate-400 mb-1">IPI (%)</label>
                                    <input
                                        type="number"
                                        value={ipiRate}
                                        onChange={e => setIpiRate(e.target.value === "" ? "" : Number(e.target.value))}
                                        className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                        step="0.01"
                                    />
                                </div>
                            )}
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">ICMS Origem (%)</label>
                                <input
                                    type="number"
                                    value={originIcmsRate}
                                    onChange={e => setOriginIcmsRate(e.target.value === "" ? "" : Number(e.target.value))}
                                    className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                    step="0.01"
                                    placeholder="Ex: 12.0"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">ICMS Destino Padrão (%)</label>
                                <input
                                    type="number"
                                    value={destinationIcmsRate}
                                    onChange={e => setDestinationIcmsRate(e.target.value === "" ? "" : Number(e.target.value))}
                                    className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                    step="0.01"
                                    placeholder="Ex: 18.0"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* CUSTO DE COMPRA */}
                <div className="bg-[#131B2C] border border-[#1E293B] rounded-xl p-5 space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-rose-400" />
                        <h4 className="font-semibold text-slate-200">Custo Histórico de Compra</h4>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[11px] font-medium text-slate-400 mb-1">Custo Real R$</label>
                            <input
                                type="number"
                                value={realCost}
                                onChange={e => setRealCost(e.target.value === "" ? "" : Number(e.target.value))}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-white font-semibold text-emerald-400 focus:border-indigo-500 outline-none"
                                step="0.01"
                            />
                        </div>
                        <div>
                            <label className="block text-[11px] font-medium text-slate-400 mb-1">Valor na NF R$</label>
                            <input
                                type="number"
                                value={nfValue}
                                onChange={e => setNfValue(e.target.value === "" ? "" : Number(e.target.value))}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-md px-3 py-1.5 text-sm text-white focus:border-indigo-500 outline-none"
                                step="0.01"
                            />
                            {nfPercentage && (
                                <div className="mt-1.5 inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                                    <Info className="w-3 h-3 text-indigo-400" />
                                    <span className="text-[10px] text-indigo-300 font-medium">NF: {nfPercentage}% do custo</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 pt-4 border-t border-[#1E293B]">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Frete Compra R$</label>
                            <input
                                type="number"
                                value={freightCost}
                                onChange={e => setFreightCost(e.target.value === "" ? "" : Number(e.target.value))}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                step="0.01"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Embalagem R$</label>
                            <input
                                type="number"
                                value={packagingCost}
                                onChange={e => setPackagingCost(e.target.value === "" ? "" : Number(e.target.value))}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                step="0.01"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Outros Custos R$</label>
                            <input
                                type="number"
                                value={otherCosts}
                                onChange={e => setOtherCosts(e.target.value === "" ? "" : Number(e.target.value))}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                step="0.01"
                            />
                        </div>
                    </div>

                    <div className="pt-4 border-t border-[#1E293B] grid grid-cols-2 gap-4">
                         <div>
                            <label className="block text-xs text-slate-400 mb-1">Fornecedor</label>
                            <input
                                type="text"
                                value={supplierName}
                                onChange={e => setSupplierName(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                placeholder="Nome da Fábrica/Distribuidora"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Nº NF de Entrada</label>
                            <input
                                type="text"
                                value={nfNumber}
                                onChange={e => setNfNumber(e.target.value)}
                                className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white"
                                placeholder="00000001"
                            />
                        </div>
                    </div>
                    
                    <div className="mt-4">
                        <label className="block text-xs text-slate-400 mb-1">Observações Internas</label>
                        <textarea
                            value={taxNotes}
                            onChange={e => setTaxNotes(e.target.value)}
                            rows={2}
                            className="w-full bg-[#0B1120] border border-[#1E293B] rounded-lg px-3 py-2 text-sm text-white focus:border-indigo-500 outline-none"
                            placeholder="Anotações sobre a configuração fiscal"
                        />
                    </div>
                </div>
            </div>

            {/* RESUMO FISCAL */}
            <div className="bg-[#131B2C] border border-[#1E293B] rounded-xl p-5 mt-6">
                <div className="flex items-center gap-2 mb-4">
                    <Calculator className="w-4 h-4 text-indigo-400" />
                    <h4 className="font-semibold text-slate-200">Resumo da Configuração</h4>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="bg-[#0B1120] p-3 rounded-lg border border-[#1E293B]">
                        <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Custo Total de Compra</div>
                        <div className="text-lg font-semibold text-white">
                            R$ {((Number(realCost) || 0) + (Number(freightCost) || 0) + (Number(packagingCost) || 0) + (Number(otherCosts) || 0)).toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-[#0B1120] p-3 rounded-lg border border-[#1E293B]">
                        <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">NCM / CEST</div>
                        <div className="text-sm font-medium text-slate-300 mt-1">
                            {ncm || '---'} / {cest || '---'}
                        </div>
                    </div>
                    <div className="bg-[#0B1120] p-3 rounded-lg border border-[#1E293B]">
                        <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Complexidade Tributária</div>
                        <div className="flex gap-2 mt-1.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${hasSt ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'}`}>ST</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${hasIpi ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'}`}>IPI</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${hasDifal ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'}`}>DIFAL</span>
                        </div>
                    </div>
                    <div className="bg-[#0B1120] p-3 rounded-lg border border-[#1E293B]">
                        <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Origem</div>
                        <div className="text-sm font-medium text-slate-300 mt-1 capitalize">
                            {productOrigin}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
