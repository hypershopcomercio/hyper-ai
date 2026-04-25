
'use client';

import { useState } from 'react';
import { X, CheckCircle, Package } from 'lucide-react';
import axios from 'axios';

// Ad type for PurchaseModal
interface Ad {
    id: string;
    title: string;
    cost?: number;
}

interface PurchaseModalProps {
    isOpen: boolean;
    onClose: () => void;
    product: Ad | null;
    onSuccess?: (purchase: any) => void;
}

export default function PurchaseModal({ isOpen, onClose, product, onSuccess }: PurchaseModalProps) {
    const [quantity, setQuantity] = useState<string>('');
    const [supplier, setSupplier] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen || !product) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const qty = parseInt(quantity);
            if (isNaN(qty) || qty <= 0) {
                alert("Quantidade inválida");
                return;
            }

            const payload = {
                item_id: product.id,
                title: product.title,
                quantity: qty,
                cost: product.cost,
                supplier_id: null,
                status: 'ordered',
                expected_arrival: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // Default 7 days
            };

            const res = await axios.post('http://localhost:5000/api/purchases', payload);

            if (onSuccess) onSuccess(res.data);
            onClose();
        } catch (error) {
            console.error(error);
            alert("Erro ao registrar compra");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-md p-6 relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-slate-400 hover:text-white"
                >
                    <X size={20} />
                </button>

                <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                    <Package className="text-cyan-400" />
                    Registrar Compra
                </h2>
                <p className="text-sm text-slate-400 mb-6 truncate">{product.title}</p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Quantidade</label>
                        <input
                            type="number"
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-cyan-500 outline-none"
                            placeholder="Ex: 50"
                            value={quantity}
                            onChange={e => setQuantity(e.target.value)}
                            autoFocus
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Fornecedor (Opcional)</label>
                        <input
                            type="text"
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white outline-none"
                            placeholder="Nome do fornecedor"
                            value={supplier}
                            onChange={e => setSupplier(e.target.value)}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 rounded-lg transition-colors flex justify-center items-center gap-2 mt-4"
                    >
                        {loading ? 'Registrando...' : 'Confirmar Compra'}
                        {!loading && <CheckCircle size={18} />}
                    </button>
                </form>
            </div>
        </div>
    );
}
