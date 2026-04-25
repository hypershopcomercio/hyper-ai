import React, { useRef } from 'react';
import { Calendar as CalendarIcon, ChevronDown } from 'lucide-react';

interface ModernDatePickerProps {
    value: Date | null;
    onChange: (date: Date | null) => void;
    placeholder?: string;
    className?: string;
}

export const ModernDatePicker: React.FC<ModernDatePickerProps> = ({
    value,
    onChange,
    placeholder = "Selecione uma data",
    className = ""
}) => {
    const inputRef = useRef<HTMLInputElement>(null);

    const handleContainerClick = () => {
        // Trigger the native date picker
        if (inputRef.current) {
            inputRef.current.showPicker();
        }
    };

    const formatDate = (date: Date) => {
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
    };

    return (
        <div
            className={`relative group cursor-pointer ${className}`}
            onClick={handleContainerClick}
        >
            <div className="flex items-center gap-3 px-4 py-2.5 bg-[#1A1A2E] border border-slate-700/50 rounded-lg group-hover:border-cyan-500/50 group-hover:bg-slate-800/80 transition-all duration-300 shadow-sm">
                <div className="p-1.5 bg-cyan-500/10 rounded-md group-hover:bg-cyan-500/20 transition-colors">
                    <CalendarIcon className="w-4 h-4 text-cyan-400" />
                </div>

                <div className="flex-1">
                    <span className={`text-sm font-medium ${value ? 'text-white' : 'text-slate-500'}`}>
                        {value ? formatDate(value) : placeholder}
                    </span>
                </div>

                <ChevronDown className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            </div>

            {/* Hidden native input for accessibility and functionality */}
            <input
                ref={inputRef}
                type="date"
                className="absolute inset-0 opacity-0 cursor-pointer pointer-events-none" // pointer-events-none because we trigger via container click
                value={value ? value.toISOString().split('T')[0] : ''}
                onChange={(e) => {
                    const d = e.target.value ? new Date(e.target.value) : null;
                    // Reset time to noon to avoid timezone shift issues on pure dates
                    if (d) {
                        const userTimezoneOffset = d.getTimezoneOffset() * 60000;
                        const adjustedDate = new Date(d.getTime() + userTimezoneOffset + (12 * 60 * 60 * 1000));
                        onChange(adjustedDate);
                    } else {
                        onChange(null);
                    }
                }}
            />
        </div>
    );
};
