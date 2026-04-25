"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { User, Mail, Shield, Lock, Eye, EyeOff, Save, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';

export default function ProfilePage() {
    const router = useRouter();
    const [user, setUser] = useState<{ id?: number; name?: string; email?: string; role?: string } | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    // Form state
    const [name, setName] = useState('');
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (userData) {
            try {
                const parsed = JSON.parse(userData);
                setUser(parsed);
                setName(parsed.name || '');
            } catch (e) {
                console.error("Error parsing user data:", e);
            }
        }
    }, []);

    const handleSaveProfile = async () => {
        if (!name.trim()) {
            toast.error("O nome não pode estar vazio");
            return;
        }

        setIsSaving(true);
        try {
            const res = await api.put('/auth/profile', { name: name.trim() });

            if (res.data.success) {
                // Update localStorage
                const updatedUser = { ...user, name: name.trim() };
                localStorage.setItem('user', JSON.stringify(updatedUser));
                setUser(updatedUser);
                setIsEditing(false);
                toast.success("Perfil atualizado com sucesso!");
            } else {
                toast.error(res.data.error || "Erro ao atualizar perfil");
            }
        } catch (err: any) {
            toast.error(err.response?.data?.error || "Erro ao atualizar perfil");
        } finally {
            setIsSaving(false);
        }
    };

    const handleChangePassword = async () => {
        if (!currentPassword || !newPassword || !confirmPassword) {
            toast.error("Preencha todos os campos de senha");
            return;
        }

        if (newPassword !== confirmPassword) {
            toast.error("As senhas não coincidem");
            return;
        }

        if (newPassword.length < 6) {
            toast.error("A nova senha deve ter pelo menos 6 caracteres");
            return;
        }

        setIsSaving(true);
        try {
            const res = await api.put('/auth/password', {
                current_password: currentPassword,
                new_password: newPassword
            });

            if (res.data.success) {
                setCurrentPassword('');
                setNewPassword('');
                setConfirmPassword('');
                toast.success("Senha alterada com sucesso!");
            } else {
                toast.error(res.data.error || "Erro ao alterar senha");
            }
        } catch (err: any) {
            toast.error(err.response?.data?.error || "Erro ao alterar senha");
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <button
                    onClick={() => router.back()}
                    className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-4 cursor-pointer"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Voltar
                </button>
                <h1 className="text-2xl font-bold text-white">Meu Perfil</h1>
                <p className="text-slate-400 mt-1">Gerencie suas informações pessoais e segurança</p>
            </div>

            <div className="grid gap-6">
                {/* Profile Card */}
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-800/50 bg-gradient-to-r from-indigo-500/10 to-purple-500/10">
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <User className="w-5 h-5 text-indigo-400" />
                            Informações Pessoais
                        </h2>
                    </div>

                    <div className="p-6 space-y-6">
                        {/* Avatar */}
                        <div className="flex items-center gap-4">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-2xl font-bold text-white shadow-xl">
                                {user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'}
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-white">{user?.name || 'Usuário'}</p>
                                <span className="inline-block mt-1 px-3 py-1 text-xs font-bold rounded-full bg-indigo-500/20 text-indigo-400 uppercase">
                                    {user?.role || 'admin'}
                                </span>
                            </div>
                        </div>

                        {/* Name Field */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Nome</label>
                            {isEditing ? (
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all"
                                />
                            ) : (
                                <div className="flex items-center justify-between bg-slate-900/30 rounded-lg px-4 py-3 border border-slate-800/50">
                                    <span className="text-white">{user?.name || '-'}</span>
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="text-indigo-400 hover:text-indigo-300 text-sm font-medium cursor-pointer"
                                    >
                                        Editar
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Email Field (readonly) */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Email</label>
                            <div className="flex items-center gap-3 bg-slate-900/30 rounded-lg px-4 py-3 border border-slate-800/50">
                                <Mail className="w-4 h-4 text-slate-500" />
                                <span className="text-slate-300">{user?.email}</span>
                            </div>
                        </div>

                        {/* Role Field (readonly) */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Função</label>
                            <div className="flex items-center gap-3 bg-slate-900/30 rounded-lg px-4 py-3 border border-slate-800/50">
                                <Shield className="w-4 h-4 text-slate-500" />
                                <span className="text-slate-300 capitalize">{user?.role || 'admin'}</span>
                            </div>
                        </div>

                        {/* Save Button */}
                        {isEditing && (
                            <div className="flex items-center gap-3 pt-2">
                                <button
                                    onClick={handleSaveProfile}
                                    disabled={isSaving}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 cursor-pointer"
                                >
                                    {isSaving ? (
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <Save className="w-4 h-4" />
                                    )}
                                    Salvar Alterações
                                </button>
                                <button
                                    onClick={() => { setIsEditing(false); setName(user?.name || ''); }}
                                    className="px-4 py-2.5 text-slate-400 hover:text-white transition-colors cursor-pointer"
                                >
                                    Cancelar
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Security Card */}
                <div className="bg-[#12121a] rounded-xl border border-slate-800/50 overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-800/50 bg-gradient-to-r from-rose-500/10 to-orange-500/10">
                        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                            <Lock className="w-5 h-5 text-rose-400" />
                            Segurança
                        </h2>
                    </div>

                    <div className="p-6 space-y-4">
                        <p className="text-sm text-slate-400">Altere sua senha para manter sua conta segura.</p>

                        {/* Current Password */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Senha Atual</label>
                            <div className="relative">
                                <input
                                    type={showCurrentPassword ? 'text' : 'password'}
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        {/* New Password */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Nova Senha</label>
                            <div className="relative">
                                <input
                                    type={showNewPassword ? 'text' : 'password'}
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 pr-12 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowNewPassword(!showNewPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                >
                                    {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Confirmar Nova Senha</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••"
                                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 transition-all"
                            />
                        </div>

                        {/* Change Password Button */}
                        <div className="pt-2">
                            <button
                                onClick={handleChangePassword}
                                disabled={isSaving || !currentPassword || !newPassword || !confirmPassword}
                                className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                            >
                                {isSaving ? (
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <CheckCircle2 className="w-4 h-4" />
                                )}
                                Alterar Senha
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
