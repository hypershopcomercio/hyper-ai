import React, { useState } from 'react';
import { Ad } from '@/types';
import { ExternalLink, Download, Maximize2, ChevronLeft, ChevronRight } from 'lucide-react';

interface Props {
    ad: Ad;
    setIsLightboxOpen: (open: boolean) => void;
}

export function AdMediaTab({ ad, setIsLightboxOpen }: Props) {
    const [activeImageIndex, setActiveImageIndex] = useState(0);

    const handlePrevImage = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (ad.pictures && ad.pictures.length > 0) {
            setActiveImageIndex((prev) => (prev === 0 ? ad.pictures!.length - 1 : prev - 1));
        }
    };

    const handleNextImage = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (ad.pictures && ad.pictures.length > 0) {
            setActiveImageIndex((prev) => (prev === ad.pictures!.length - 1 ? 0 : prev + 1));
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-full bg-[#13141b] rounded-2xl p-6">
            <div className="w-full max-w-2xl aspect-square bg-white rounded-xl mb-6 p-4 flex items-center justify-center relative group overflow-hidden shadow-lg border border-white/10">
                <div className="absolute top-4 right-4 z-10 flex gap-2">
                    <a
                        href={ad.pictures?.[activeImageIndex]?.url || ad.thumbnail.replace('I.jpg', 'O.jpg')}
                        target="_blank"
                        rel="noreferrer"
                        className="p-3 bg-white/90 backdrop-blur rounded-full text-slate-700 hover:text-blue-600 shadow-md transition-all hover:scale-110 flex items-center justify-center"
                        title="Abrir Original"
                    >
                        <ExternalLink size={20} />
                    </a>
                    <a
                        href={ad.pictures?.[activeImageIndex]?.url || ad.thumbnail.replace('I.jpg', 'O.jpg')}
                        download={`foto_${ad.id}_${activeImageIndex + 1}`}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="p-3 bg-white/90 backdrop-blur rounded-full text-slate-700 hover:text-emerald-600 shadow-md transition-all hover:scale-110 flex items-center justify-center"
                        title="Baixar Foto"
                    >
                        <Download size={20} />
                    </a>
                </div>

                {ad.pictures && ad.pictures.length > 1 && (
                    <>
                        <button
                            onClick={handlePrevImage}
                            className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-black/40 hover:bg-black/60 backdrop-blur text-white rounded-full transition-all z-10 cursor-pointer hover:scale-110"
                        >
                            <ChevronLeft size={24} />
                        </button>
                        <button
                            onClick={handleNextImage}
                            className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-black/40 hover:bg-black/60 backdrop-blur text-white rounded-full transition-all z-10 cursor-pointer hover:scale-110"
                        >
                            <ChevronRight size={24} />
                        </button>
                    </>
                )}

                <div className="absolute bottom-4 right-4 p-2 bg-black/20 text-slate-300 rounded-lg pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur">
                    <Maximize2 size={20} />
                </div>

                <img
                    src={ad.pictures?.[activeImageIndex]?.url || ad.thumbnail.replace('I.jpg', 'O.jpg')}
                    alt={ad.title}
                    onClick={() => setIsLightboxOpen(true)}
                    className="max-w-full max-h-full object-contain mix-blend-multiply group-hover:scale-105 transition-transform duration-500 cursor-zoom-in"
                />
            </div>

            {/* Thumbnails */}
            {ad.pictures && ad.pictures.length > 1 && (
                <div className="w-full max-w-4xl overflow-x-auto flex gap-3 pb-4 custom-scrollbar justify-center">
                    {ad.pictures.map((pic, idx) => (
                        <button
                            key={pic.id}
                            onClick={() => setActiveImageIndex(idx)}
                            className={`flex-shrink-0 w-20 h-20 rounded-xl bg-white border-2 overflow-hidden transition-all cursor-pointer ${
                                activeImageIndex === idx 
                                    ? 'border-indigo-500 ring-4 ring-indigo-500/20 scale-105' 
                                    : 'border-transparent opacity-50 hover:opacity-100 hover:scale-105'
                            }`}
                        >
                            <img src={pic.url} alt={`Thumb ${idx + 1}`} className="w-full h-full object-cover mix-blend-multiply" />
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
