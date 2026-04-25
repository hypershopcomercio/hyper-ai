import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Plus, Trash2, DollarSign, Calendar, Tag, Pencil, Check, X } from 'lucide-react';
import { toast } from 'sonner';

interface FixedCost {
    id: number;
    name: string;
    amount: number;
    category: string;
    day_of_month: number;
    active: boolean;
}

export function FixedCostsManager() {
    const [costs, setCosts] = useState<FixedCost[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAdding, setIsAdding] = useState(false);

    // Form State
    const [newName, setNewName] = useState('');
    const [newAmount, setNewAmount] = useState('');
    const [newCategory, setNewCategory] = useState('operational');
    const [newDay, setNewDay] = useState('5');

    // Edit State
    const [editId, setEditId] = useState<number | null>(null);
    const [editName, setEditName] = useState('');
    const [editAmount, setEditAmount] = useState('');
    const [editCategory, setEditCategory] = useState('operational');
    const [editDay, setEditDay] = useState('');

    useEffect(() => {
        loadCosts();
    }, []);

    const loadCosts = async () => {
        setLoading(true);
        try {
            const res = await api.get('/financial/costs');
            setCosts(res.data);
        } catch (error) {
            console.error(error);
            toast.error("Erro ao carregar custos");
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const triggerRecalculation = async () => {
        try {
            await api.post('/financial/calculate-metrics');
            toast.success("Métricas financeiras recalculadas!");
        } catch (error) {
            console.error(error);
        }
    };

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const payload = {
                name: newName,
                amount: parseFloat(newAmount),
                category: newCategory,
                day_of_month: parseInt(newDay)
            };

            await api.post('/financial/costs', payload);
            toast.success("Custo adicionado com sucesso!");
            setIsAdding(false);
            setNewName('');
            setNewAmount('');
            loadCosts();
            triggerRecalculation();
        } catch (error) {
            toast.error("Erro ao adicionar custo");
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Tem certeza que deseja remover este custo?")) return;
        try {
            await api.delete(`/financial/costs/${id}`);
            toast.success("Custo removido.");
            loadCosts();
            triggerRecalculation();
        } catch (error) {
            toast.error("Erro ao remover custo");
        }
    };

    const startEdit = (cost: FixedCost) => {
        setEditId(cost.id);
        setEditName(cost.name);
        setEditAmount(cost.amount.toString());
        setEditCategory(cost.category);
        setEditDay(cost.day_of_month.toString());
    };

    const cancelEdit = () => {
        setEditId(null);
        setEditName('');
        setEditAmount('');
        setEditCategory('operational');
        setEditDay('');
    };

    const handleSaveEdit = async () => {
        if (!editId) return;
        try {
            const payload = {
                name: editName,
                amount: parseFloat(editAmount),
                category: editCategory,
                day_of_month: parseInt(editDay)
            };

            await api.put(`/financial/costs/${editId}`, payload);
            toast.success("Custo atualizado com sucesso!");
            setEditId(null);
            loadCosts();
            triggerRecalculation();
        } catch (error) {
            toast.error("Erro ao atualizar custo");
        }
    };

    const totalMonthly = costs.reduce((sum, c) => sum + c.amount, 0);

    return (
        <div className="space-y-6">
            {/* KPI Card */}
            <div className="bg-[#13141b] rounded-xl p-6 border border-white/5 bg-gradient-to-br from-[#13141b] to-emerald-900/10">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-slate-400 font-medium">Custo Fixo Mensal Total</p>
                        <h2 className="text-3xl font-bold text-white mt-1">
                            {formatCurrency(totalMonthly)}
                        </h2>
                        <p className="text-xs text-slate-500 mt-2">
                            Base para cálculo de ponto de equilíbrio
                        </p>
                    </div>
                    <div className="bg-emerald-500/10 p-4 rounded-full border border-emerald-500/20">
                        <DollarSign size={32} className="text-emerald-400" />
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white">Custos Recorrentes</h3>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                >
                    <Plus size={16} />
                    Adicionar Custo
                </button>
            </div>

            {/* Add Form */}
            {isAdding && (
                <form onSubmit={handleAdd} className="bg-[#1A1A2E] p-4 rounded-lg border border-blue-500/30 animate-in fade-in slide-in-from-top-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Descrição</label>
                            <input
                                type="text"
                                value={newName}
                                onChange={e => setNewName(e.target.value)}
                                placeholder="Ex: Aluguel"
                                className="w-full bg-[#0D0D14] border border-white/10 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Valor (R$)</label>
                            <input
                                type="number"
                                step="0.01"
                                value={newAmount}
                                onChange={e => setNewAmount(e.target.value)}
                                placeholder="0.00"
                                className="w-full bg-[#0D0D14] border border-white/10 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Categoria</label>
                            <select
                                value={newCategory}
                                onChange={e => setNewCategory(e.target.value)}
                                className="w-full bg-[#0D0D14] border border-white/10 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                            >
                                <option value="operational">Operacional</option>
                                <option value="administrative">Administrativo</option>
                                <option value="personnel">Pessoal/Sócios</option>
                                <option value="software">Software/Serviços</option>
                                <option value="marketing">Marketing/Ads</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs text-slate-400 mb-1">Dia Vencimento</label>
                            <input
                                type="number"
                                min="1" max="31"
                                value={newDay}
                                onChange={e => setNewDay(e.target.value)}
                                className="w-full bg-[#0D0D14] border border-white/10 rounded px-3 py-2 text-white text-sm focus:border-blue-500 focus:outline-none"
                                required
                            />
                        </div>
                    </div>
                    <div className="flex justify-end mt-4 gap-2">
                        <button
                            type="button"
                            onClick={() => setIsAdding(false)}
                            className="bg-transparent hover:bg-white/5 text-slate-400 px-3 py-1.5 rounded text-xs"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded text-xs font-medium"
                        >
                            Salvar Custo
                        </button>
                    </div>
                </form>
            )}

            {/* Table */}
            <div className="bg-[#13141b] rounded-xl border border-white/5 overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/5 bg-white/[0.02]">
                            <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Descrição</th>
                            <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Categoria</th>
                            <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Dia Venc.</th>
                            <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Valor Mensal</th>
                            <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {loading ? (
                            <tr>
                                <td colSpan={5} className="py-8 text-center text-slate-500">
                                    Carregando custos...
                                </td>
                            </tr>
                        ) : costs.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="py-8 text-center text-slate-500">
                                    Nenhum custo cadastrado.
                                </td>
                            </tr>
                        ) : (
                            costs.map((cost) => (
                                <tr key={cost.id} className="hover:bg-white/[0.02] transition-colors group">
                                    {editId === cost.id ? (
                                        <>
                                            <td className="py-3 px-4">
                                                <input
                                                    type="text"
                                                    value={editName}
                                                    onChange={(e) => setEditName(e.target.value)}
                                                    className="w-full bg-[#0D0D14] border border-white/10 rounded px-2 py-1 text-xs text-white"
                                                />
                                            </td>
                                            <td className="py-3 px-4">
                                                <select
                                                    value={editCategory}
                                                    onChange={(e) => setEditCategory(e.target.value)}
                                                    className="w-full bg-[#0D0D14] border border-white/10 rounded px-2 py-1 text-xs text-white"
                                                >
                                                    <option value="operational">Operacional</option>
                                                    <option value="administrative">Administrativo</option>
                                                    <option value="personnel">Pessoal</option>
                                                    <option value="software">Software</option>
                                                    <option value="marketing">Marketing</option>
                                                </select>
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <input
                                                    type="number"
                                                    value={editDay}
                                                    onChange={(e) => setEditDay(e.target.value)}
                                                    className="w-20 bg-[#0D0D14] border border-white/10 rounded px-2 py-1 text-xs text-white text-right"
                                                />
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    value={editAmount}
                                                    onChange={(e) => setEditAmount(e.target.value)}
                                                    className="w-24 bg-[#0D0D14] border border-white/10 rounded px-2 py-1 text-xs text-white text-right"
                                                />
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <div className="flex justify-end gap-2">
                                                    <button onClick={handleSaveEdit} className="text-emerald-400 hover:text-emerald-300"><Check size={14} /></button>
                                                    <button onClick={cancelEdit} className="text-slate-500 hover:text-white"><X size={14} /></button>
                                                </div>
                                            </td>
                                        </>
                                    ) : (
                                        <>
                                            <td className="py-3 px-4 text-sm text-slate-300 font-medium">
                                                {cost.name}
                                            </td>
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-1.5">
                                                    <Tag size={12} className="text-slate-500" />
                                                    <span className="text-xs text-slate-400 capitalize">
                                                        {cost.category === 'personnel' ? 'Pessoal' :
                                                            cost.category === 'software' ? 'Software' : cost.category}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <div className="inline-flex items-center gap-1 text-xs text-slate-400 bg-white/5 px-2 py-0.5 rounded">
                                                    <Calendar size={10} />
                                                    Dia {cost.day_of_month}
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-right text-sm font-bold text-emerald-400">
                                                {formatCurrency(cost.amount)}
                                            </td>
                                            <td className="py-3 px-4 text-right">
                                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button
                                                        onClick={() => startEdit(cost)}
                                                        className="text-slate-500 hover:text-blue-400 p-1"
                                                        title="Editar"
                                                    >
                                                        <Pencil size={14} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(cost.id)}
                                                        className="text-slate-500 hover:text-red-400 p-1"
                                                        title="Remover"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                </div>
                                            </td>
                                        </>
                                    )}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
