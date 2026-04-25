import React from 'react';
import { AlertTriangle, CheckCircle2, X } from 'lucide-react';
import { createPortal } from 'react-dom';

interface ConfirmModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    type?: 'danger' | 'warning' | 'info';
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'Confirmar',
    cancelText = 'Cancelar',
    type = 'warning'
}) => {
    if (!isOpen) return null;

    // Use portal if possible, or just render (nextjs sometimes tricky with document)
    // For simplicity in this context, direct render fixed overlay

    const colors = {
        danger: {
            icon: 'text-rose-500',
            bg: 'bg-rose-500/10',
            border: 'border-rose-500/20',
            button: 'bg-rose-600 hover:bg-rose-700'
        },
        warning: {
            icon: 'text-yellow-500',
            bg: 'bg-yellow-500/10',
            border: 'border-yellow-500/20',
            button: 'bg-yellow-600 hover:bg-yellow-700'
        },
        info: {
            icon: 'text-cyan-500',
            bg: 'bg-cyan-500/10',
            border: 'border-cyan-500/20',
            button: 'bg-cyan-600 hover:bg-cyan-700'
        }
    };

    const activeColor = colors[type];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-[#1A1A2E] border border-slate-700 w-full max-w-md rounded-xl shadow-2xl scale-100 animate-in zoom-in-95 duration-200 overflow-hidden">
                {/* Header */}
                <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-[#151525]">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <AlertTriangle className={`w-5 h-5 ${activeColor.icon}`} />
                        {title}
                    </h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6">
                    <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
                        {message}
                    </p>

                    {type === 'warning' && (
                        <div className={`mt-4 p-3 rounded-lg ${activeColor.bg} border ${activeColor.border} flex gap-3`}>
                            <AlertTriangle className={`w-5 h-5 ${activeColor.icon} shrink-0`} />
                            <span className="text-xs text-slate-300">
                                Esta ação não pode ser desfeita. Certifique-se de que escolheu a data correta.
                            </span>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-[#151525] border-t border-slate-800 flex items-center justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                    >
                        {cancelText}
                    </button>
                    <button
                        onClick={() => { onConfirm(); onClose(); }}
                        className={`px-4 py-2 rounded-lg text-sm font-medium text-white shadow-lg transition-all transform active:scale-95 flex items-center gap-2 cursor-pointer ${activeColor.button}`}
                    >
                        {type === 'info' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
};
