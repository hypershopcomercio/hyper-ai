// History Tab Component to be inserted at line 1342 in page.tsx

{/* History Tab */ }
{
    activeTab === 'history' && (
        <div className="bg-[#12121a] rounded-xl border border-slate-800/50">
            <div className="p-4 border-b border-slate-800/50">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Clock className="w-5 h-5 text-purple-400" />
                    Histórico de Calibrações
                </h2>
                <p className="text-slate-400 text-sm mt-1">
                    Registro completo de ajustes automáticos do sistema de aprendizado
                </p>
            </div>

            {history.length === 0 ? (
                <div className="p-8 text-center">
                    <div className="inline-block p-4 rounded-full bg-slate-800/50 mb-4">
                        <Clock className="w-12 h-12 text-slate-600" />
                    </div>
                    <p className="text-slate-500">Nenhum histórico de calibração encontrado para o período selecionado.</p>
                </div>
            ) : (
                <div className="divide-y divide-slate-800/50">
                    {history.map((entry: any, index: number) => {
                        const details = entry.details ? JSON.parse(entry.details) : {};
                        const isCalibration = details.action === 'calibration';
                        const isReconciliation = details.action === 'reconciliation';

                        if (!isCalibration && !isReconciliation) return null;

                        return (
                            <div key={index} className="p-4 hover:bg-slate-800/30 transition-colors cursor-pointer">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex items-start gap-3 flex-1">
                                        {isCalibration ? (
                                            <div className="p-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
                                                <Zap className="w-5 h-5 text-purple-400" />
                                            </div>
                                        ) : (
                                            <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
                                                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                                            </div>
                                        )}

                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h3 className="font-medium text-white">{entry.message}</h3>
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${entry.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' :
                                                        entry.status === 'error' ? 'bg-red-500/20 text-red-400' :
                                                            'bg-slate-500/20 text-slate-400'
                                                    }`}>
                                                    {entry.status}
                                                </span>
                                            </div>

                                            <div className="text-xs text-slate-500 mb-2">
                                                {new Date(entry.timestamp).toLocaleString('pt-BR')}
                                            </div>

                                            {isCalibration && (
                                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3">
                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Fator</div>
                                                        <div className="text-sm font-mono text-slate-300">{details.factor}</div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Anterior</div>
                                                        <div className="text-sm font-mono text-slate-400">{details.old_value?.toFixed(3) || '-'}</div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-purple-500/30">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Novo</div>
                                                        <div className="text-sm font-mono text-purple-400 font-bold">{details.new_value?.toFixed(3) || '-'}</div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Ajuste</div>
                                                        <div className={`text-sm font-mono font-bold ${(details.change_percent || 0) > 0 ? 'text-emerald-400' : 'text-red-400'
                                                            }`}>
                                                            {(details.change_percent || 0) > 0 ? '+' : ''}{details.change_percent?.toFixed(2) || '0.00'}%
                                                        </div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Erro</div>
                                                        <div className="text-sm font-mono text-amber-400">{details.avg_error?.toFixed(1) || '0.0'}%</div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Amostras</div>
                                                        <div className="text-sm font-mono text-slate-300">{details.samples || 0}</div>
                                                    </div>
                                                </div>
                                            )}

                                            {isReconciliation && (
                                                <div className="grid grid-cols-2 gap-3 mt-3">
                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Previsões</div>
                                                        <div className="text-sm font-mono text-slate-300">{details.count || 0}</div>
                                                    </div>

                                                    <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Erro Abs.</div>
                                                        <div className="text-sm font-mono text-amber-400">{details.avg_abs_error?.toFixed(2) || '0.00'}%</div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}\r
                </div>
            )}
        </div>
    )
}
