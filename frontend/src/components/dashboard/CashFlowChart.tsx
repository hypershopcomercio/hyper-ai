'use client';

import { useState } from 'react';
import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
    ReferenceDot,
    Legend
} from 'recharts';

interface CashFlowData {
    name: string;
    receita: number | null;
    custo: number | null;
    lucro: number | null;
    receita_anterior?: number | null;
    receita_projetada?: number | null;
}

interface CashFlowChartProps {
    data: CashFlowData[];
    isLive?: boolean; // If true, shows pulsing dot at current point
}

// Custom animated dot component for live indicator (Slow Pulse)
const LiveDot = (props: any) => {
    const { cx, cy } = props;
    if (!cx || !cy) return <g />;

    return (
        <g>
            {/* Pulsing outer ring - slower animation (3s) and centered origin */}
            <circle
                cx={cx}
                cy={cy}
                r={8}
                fill="none"
                stroke="#10b981"
                strokeWidth={2}
                opacity={0.4}
                className="animate-ping origin-center"
                style={{ transformBox: 'fill-box', transformOrigin: 'center', animationDuration: '3s' }}
            />
            {/* Inner solid dot */}
            <circle
                cx={cx}
                cy={cy}
                r={4}
                fill="#10b981"
                stroke="#fff"
                strokeWidth={1}
            />
        </g>
    );
};

export function CashFlowChart({ data, isLive = false }: CashFlowChartProps) {
    // Default hidden: custo, lucro, receita_anterior. Visible: receita, receita_projetada.
    const [hiddenKeys, setHiddenKeys] = useState<string[]>(['custo', 'lucro', 'receita_anterior']);

    if (!data || data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-zinc-500">
                <p>Sem dados de fluxo de caixa para o período.</p>
            </div>
        );
    }

    // Format currency
    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
        }).format(value);
    };

    // Find current hour data point for live indicator
    const getCurrentHourPoint = () => {
        if (!isLive) return null;
        const currentHour = new Date().getHours();
        const bucketHour = Math.floor(currentHour); // 1h resolution
        const bucketKey = `${String(bucketHour).padStart(2, '0')}h`;
        return data.find(d => d.name === bucketKey);
    };
    const currentPoint = getCurrentHourPoint();

    // For live (today) chart: map future hours to null to cut the line but keep x-axis
    const chartData = isLive && currentPoint
        ? data.map(d => {
            const hourNum = parseInt(d.name.replace('h', ''));
            const currentHourNum = parseInt(currentPoint.name.replace('h', ''));

            // Future: Hide Real, Keep Projection & Comparison
            if (hourNum > currentHourNum) {
                return { ...d, receita: null, custo: null, lucro: null };
            }
            // Past & Current: Keep Real AND Projection (projection stays as reference line)
            return d;
        })
        : data;

    const handleLegendClick = (e: any) => {
        const { dataKey } = e;
        setHiddenKeys(prev =>
            prev.includes(dataKey)
                ? prev.filter(k => k !== dataKey)
                : [...prev, dataKey]
        );
    };

    return (
        <div className="w-full h-full min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 10,
                        left: 0,
                        bottom: 0,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />

                    <XAxis
                        dataKey="name"
                        stroke="#71717a"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={30} // Prevent overlap
                    />

                    <YAxis
                        stroke="#71717a"
                        fontSize={12}
                        width={80}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `R$ ${value}`}
                    />

                    <Tooltip
                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                        itemStyle={{ fontSize: '12px' }}
                        labelStyle={{ color: '#e4e4e7', marginBottom: '4px', fontWeight: 'bold' }}
                        formatter={(value: any, name: any) => {
                            if (hiddenKeys.includes(name as string)) return [null, null]; // Don't show in tooltip if hidden? Or show? Standard behavior is show unless filtered data. Let's keep showing or hide. Recharts hides automatically if data is not rendered? No.
                            // If hide prop is true, it won't show in chart, but tooltip might still receive data payload.
                            // Better let Recharts handle it. If Area is hidden, it usually doesn't show in tooltip.

                            const colorMap: Record<string, string> = {
                                'receita': '#10b981',       // emerald
                                'receita_anterior': '#71717a', // zinc
                                'receita_projetada': '#e879f9', // fuchsia
                                'custo': '#f59e0b',         // amber
                                'lucro': '#3b82f6'          // blue
                            };
                            const labelMap: Record<string, string> = {
                                'receita': 'Receita',
                                'receita_anterior': 'Período Anterior',
                                'receita_projetada': 'Previsão',
                                'custo': 'Custos',
                                'lucro': 'Lucro'
                            };
                            return [
                                <span style={{ color: colorMap[name] || '#e4e4e7' }}>
                                    {formatCurrency(Number(value))}
                                </span>,
                                <span style={{ color: colorMap[name] || '#e4e4e7' }}>
                                    {labelMap[name] || name}
                                </span>
                            ];
                        }}
                    />

                    <Legend
                        wrapperStyle={{ paddingTop: '10px', cursor: 'pointer' }}
                        onClick={handleLegendClick}
                        formatter={(value: string) => {
                            const names: Record<string, string> = {
                                'receita': 'Receita',
                                'receita_anterior': 'Período Anterior',
                                'receita_projetada': 'Previsão',
                                'custo': 'Custos',
                                'lucro': 'Lucro'
                            };
                            const isHidden = hiddenKeys.includes(value);
                            return (
                                <span style={{
                                    color: isHidden ? '#52525b' : '#a1a1aa',
                                    textDecoration: isHidden ? 'line-through' : 'none',
                                    fontSize: '11px'
                                }}>
                                    {names[value] || value}
                                </span>
                            );
                        }}
                    />

                    <defs>
                        <linearGradient id="colorReceita" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorCusto" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorLucro" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>

                    {/* Revenue Area */}
                    <Area
                        type="monotone"
                        dataKey="receita"
                        stroke="#10b981" /* emerald-500 */
                        fillOpacity={1}
                        fill="url(#colorReceita)"
                        name="receita"
                        stackId="1"
                        dot={false}
                        activeDot={isLive && !hiddenKeys.includes('receita') ? { r: 6, fill: '#10b981', stroke: '#fff', strokeWidth: 2 } : undefined}
                        animationDuration={2500}
                        hide={hiddenKeys.includes('receita')}
                    />

                    {/* Comparison Line (Previous Period) */}
                    <Area
                        type="monotone"
                        dataKey="receita_anterior"
                        stroke="#71717a" /* zinc-500 */
                        strokeDasharray="5 5"
                        fill="none"
                        name="receita_anterior"
                        dot={false}
                        activeDot={false}
                        animationDuration={2500}
                        hide={hiddenKeys.includes('receita_anterior')}
                    />

                    {/* Projection Line (Ghost) - Magenta for clear distinction */}
                    {isLive && (
                        <Area
                            type="monotone"
                            dataKey="receita_projetada"
                            stroke="#e879f9" /* fuchsia-400 */
                            strokeDasharray="4 4"
                            fill="none"
                            name="receita_projetada"
                            dot={false}
                            activeDot={false}
                            strokeOpacity={0.8}
                            strokeWidth={2}
                            animationDuration={2500}
                            hide={hiddenKeys.includes('receita_projetada')}
                        />
                    )}

                    {/* Cost Area */}
                    <Area
                        type="monotone"
                        dataKey="custo"
                        stroke="#f59e0b" /* amber-500 */
                        fillOpacity={1}
                        fill="url(#colorCusto)"
                        name="custo"
                        stackId="2"
                        dot={false}
                        activeDot={false}
                        animationDuration={2500}
                        hide={hiddenKeys.includes('custo')}
                    />

                    {/* Profit Line */}
                    <Area
                        type="monotone"
                        dataKey="lucro"
                        stroke="#3b82f6" /* blue-500 */
                        fillOpacity={1}
                        fill="url(#colorLucro)"
                        name="lucro"
                        stackId="3"
                        dot={false}
                        activeDot={false}
                        animationDuration={2500}
                        hide={hiddenKeys.includes('lucro')}
                    />

                    {isLive && currentPoint && !hiddenKeys.includes('receita') && (
                        <ReferenceDot
                            x={currentPoint.name}
                            y={currentPoint.receita as number}
                            r={6}
                            fill="#10b981"
                            stroke="none"
                            shape={LiveDot}
                        />
                    )}
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
