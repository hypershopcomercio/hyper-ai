"use client";

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import {
    Calendar,
    Plus,
    Edit2,
    Trash2,
    X,
    Check,
    RefreshCw
} from 'lucide-react';

interface Event {
    id: number;
    nome: string;
    descricao: string;
    data_inicio: string;
    data_fim: string;
    multiplicador: number;
    tipo: string;
    recorrente: boolean;
    ativo: boolean;
}

export default function EventsManager() {
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [editingEvent, setEditingEvent] = useState<Event | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        nome: '',
        descricao: '',
        data_inicio: '',
        data_fim: '',
        multiplicador: '1.0',
        tipo: 'manual',
        recorrente: false
    });

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const res = await api.get('/forecast/events?active=false');
            if (res.data.success) {
                setEvents(res.data.data.events);
            }
        } catch (e) {
            console.error('Error fetching events:', e);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingEvent) {
                await api.put(`/forecast/events/${editingEvent.id}`, {
                    ...formData,
                    multiplicador: parseFloat(formData.multiplicador)
                });
            } else {
                await api.post('/forecast/events', {
                    ...formData,
                    multiplicador: parseFloat(formData.multiplicador)
                });
            }
            fetchEvents();
            resetForm();
        } catch (e) {
            console.error('Error saving event:', e);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Excluir este evento?')) return;
        try {
            await api.delete(`/forecast/events/${id}`);
            fetchEvents();
        } catch (e) {
            console.error('Error deleting event:', e);
        }
    };

    const toggleActive = async (event: Event) => {
        try {
            await api.put(`/forecast/events/${event.id}`, { ativo: !event.ativo });
            fetchEvents();
        } catch (e) {
            console.error('Error toggling event:', e);
        }
    };

    const resetForm = () => {
        setFormData({
            nome: '',
            descricao: '',
            data_inicio: '',
            data_fim: '',
            multiplicador: '1.0',
            tipo: 'manual',
            recorrente: false
        });
        setEditingEvent(null);
        setShowForm(false);
    };

    const startEdit = (event: Event) => {
        setEditingEvent(event);
        setFormData({
            nome: event.nome,
            descricao: event.descricao || '',
            data_inicio: event.data_inicio,
            data_fim: event.data_fim,
            multiplicador: event.multiplicador.toString(),
            tipo: event.tipo,
            recorrente: event.recorrente
        });
        setShowForm(true);
    };

    const getMultiplierColor = (mult: number) => {
        if (mult > 1.2) return 'text-emerald-400';
        if (mult > 1) return 'text-emerald-300';
        if (mult < 0.8) return 'text-red-400';
        if (mult < 1) return 'text-red-300';
        return 'text-slate-300';
    };

    return (
        <div className="bg-[#12121a] rounded-xl border border-slate-800/50 p-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-purple-400" />
                    Eventos Especiais
                </h3>
                <div className="flex gap-2">
                    <button
                        onClick={fetchEvents}
                        disabled={loading}
                        className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                    <button
                        onClick={() => setShowForm(true)}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Novo Evento
                    </button>
                </div>
            </div>

            <p className="text-slate-500 text-sm mb-4">
                Eventos como Black Friday, Natal, promoções, etc. Afetam as previsões no período definido.
            </p>

            {/* Event Form Modal */}
            {showForm && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-[#1a1a24] rounded-xl p-6 max-w-md w-full mx-4 border border-slate-700">
                        <div className="flex justify-between items-center mb-4">
                            <h4 className="text-lg font-semibold text-white">
                                {editingEvent ? 'Editar Evento' : 'Novo Evento'}
                            </h4>
                            <button onClick={resetForm} className="text-slate-400 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm text-slate-400 mb-1">Nome</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.nome}
                                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    placeholder="Ex: Black Friday 2025"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-slate-400 mb-1">Descrição</label>
                                <input
                                    type="text"
                                    value={formData.descricao}
                                    onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    placeholder="Ex: Vendas esperadas 50% maiores"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-slate-400 mb-1">Data Início</label>
                                    <input
                                        type="date"
                                        required
                                        value={formData.data_inicio}
                                        onChange={(e) => setFormData({ ...formData, data_inicio: e.target.value })}
                                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-slate-400 mb-1">Data Fim</label>
                                    <input
                                        type="date"
                                        required
                                        value={formData.data_fim}
                                        onChange={(e) => setFormData({ ...formData, data_fim: e.target.value })}
                                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-slate-400 mb-1">Multiplicador</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        min="0.1"
                                        max="5"
                                        required
                                        value={formData.multiplicador}
                                        onChange={(e) => setFormData({ ...formData, multiplicador: e.target.value })}
                                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    />
                                    <p className="text-xs text-slate-500 mt-1">1.0 = normal, 1.5 = +50%, 0.8 = -20%</p>
                                </div>
                                <div>
                                    <label className="block text-sm text-slate-400 mb-1">Tipo</label>
                                    <select
                                        value={formData.tipo}
                                        onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                                    >
                                        <option value="manual">Manual</option>
                                        <option value="feriado">Feriado</option>
                                        <option value="promocao">Promoção</option>
                                        <option value="sazonal">Sazonal</option>
                                    </select>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="recorrente"
                                    checked={formData.recorrente}
                                    onChange={(e) => setFormData({ ...formData, recorrente: e.target.checked })}
                                    className="w-4 h-4"
                                />
                                <label htmlFor="recorrente" className="text-sm text-slate-300">
                                    Repetir anualmente (mesma data)
                                </label>
                            </div>

                            <div className="flex justify-end gap-2 pt-4">
                                <button
                                    type="button"
                                    onClick={resetForm}
                                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg flex items-center gap-2"
                                >
                                    <Check className="w-4 h-4" />
                                    Salvar
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Events List */}
            {events.length === 0 ? (
                <p className="text-slate-500 text-center py-8">Nenhum evento cadastrado.</p>
            ) : (
                <div className="space-y-2">
                    {events.map((event) => (
                        <div
                            key={event.id}
                            className={`flex items-center justify-between p-4 rounded-lg border ${event.ativo ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-900/20 border-slate-800/50 opacity-60'
                                }`}
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-2">
                                    <span className="text-white font-medium">{event.nome}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded ${event.tipo === 'feriado' ? 'bg-blue-500/20 text-blue-400' :
                                            event.tipo === 'promocao' ? 'bg-green-500/20 text-green-400' :
                                                event.tipo === 'sazonal' ? 'bg-orange-500/20 text-orange-400' :
                                                    'bg-slate-500/20 text-slate-400'
                                        }`}>
                                        {event.tipo}
                                    </span>
                                    {event.recorrente && (
                                        <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                                            recorrente
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                                    <span>{new Date(event.data_inicio).toLocaleDateString('pt-BR')} - {new Date(event.data_fim).toLocaleDateString('pt-BR')}</span>
                                    {event.descricao && <span>• {event.descricao}</span>}
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <span className={`text-xl font-mono font-bold ${getMultiplierColor(event.multiplicador)}`}>
                                    {event.multiplicador.toFixed(2)}×
                                </span>

                                <div className="flex items-center gap-1">
                                    <button
                                        onClick={() => toggleActive(event)}
                                        className={`p-1.5 rounded ${event.ativo ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}
                                        title={event.ativo ? 'Desativar' : 'Ativar'}
                                    >
                                        <Check className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => startEdit(event)}
                                        className="p-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handleDelete(event.id)}
                                        className="p-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
