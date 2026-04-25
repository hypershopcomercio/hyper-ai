"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Package,
    RefreshCw,
    BarChart2,
    ShoppingCart,
    AlertTriangle,
    CreditCard,
    Truck,
    ChevronDown,
    ChevronRight,
    Settings,
    LogOut,
    Brain,
    Wallet
} from "lucide-react";
import { useState, useEffect } from "react";

interface SidebarProps {
    isCollapsed: boolean;
    toggleSidebar: () => void;
}

export function Sidebar({ isCollapsed, toggleSidebar }: SidebarProps) {
    const pathname = usePathname();

    const menuGroups = [
        {
            name: "Catalog",
            icon: Package,
            items: []
        },
        {
            name: "Sync",
            icon: RefreshCw,
            items: [
                { name: "Anúncios", href: "/anuncios", icon: Package }
            ]
        },
        {
            name: "Perform",
            icon: BarChart2,
            items: [
                { name: "Analytics", href: "/perform/analytics", icon: BarChart2 },
                { name: "Métricas", href: "/perform/metrics", icon: BarChart2, disabled: true },
                { name: "Regras", href: "/perform/rules", icon: BarChart2, disabled: true }
            ]
        },
        {
            name: "Supply",
            icon: ShoppingCart,
            items: [
                { name: "Forecast", href: "/supply/estoque", icon: Package },
                { name: "Compras", href: "/supply/compras", icon: CreditCard },
                { name: "Envio Full", href: "/supply/full", icon: Truck, disabled: true }
            ]
        },
        {
            name: "Intelligence",
            icon: Brain,
            items: [
                { name: "Machine Learning", href: "/settings/hyper-ai", icon: Brain },
                { name: "Padrões (IA)", href: "/intelligence/patterns", icon: RefreshCw, disabled: true }
            ]
        },
        {
            name: "Financeiro",
            icon: Wallet,
            items: [
                { name: "Dashboard", href: "/finance", icon: BarChart2 },
                { name: "Configurações", href: "/financial/settings", icon: Settings, disabled: true }
            ]
        },
        {
            name: "Settings",
            icon: Settings,
            items: [
                { name: "Configurações", href: "/configuracoes", icon: Settings },
                { name: "Integrações", href: "/integracoes", icon: RefreshCw }
            ]
        }
    ];


    // Initialize with the group that contains the current path
    const [expandedGroup, setExpandedGroup] = useState<string | null>(() => {
        const activeGroup = menuGroups.find(group =>
            group.items.some(item => pathname.startsWith(item.href))
        );
        return activeGroup ? activeGroup.name : "Perform";
    });

    // Internal state for isCollapsed removed, now passed via props.
    // const [isCollapsed, setIsCollapsed] = useState(false);
    // const toggleCollapse = () => {
    //     setIsCollapsed(!isCollapsed);
    // };

    // Auto-expand group when navigating
    // Only expand if the new path belongs to a different group
    useEffect(() => {
        const activeGroup = menuGroups.find(group =>
            group.items.some(item => pathname.startsWith(item.href))
        );
        if (activeGroup) {
            setExpandedGroup(activeGroup.name);
        }
    }, [pathname]);

    const toggleGroup = (name: string) => {
        if (isCollapsed) return; // Disable group toggle when collapsed
        setExpandedGroup(prev => (prev === name ? null : name));
    };

    return (
        <aside
            className={`fixed left-0 top-0 h-screen bg-[#1A1A2E] border-r border-[#2D2D3A] text-white flex flex-col transition-all duration-300 z-50 ${isCollapsed ? 'w-[80px]' : 'w-[260px]'}`}
        >
            {/* Logo Section */}
            <div className="h-[64px] flex items-center justify-center border-b border-[#2D2D3A] relative">
                <Link href="/perform/analytics" className={`h-full transition-all duration-300 flex items-center justify-center overflow-hidden cursor-pointer ${isCollapsed ? 'w-full' : 'w-full'}`}>
                    {isCollapsed ? (
                        <img
                            src="/logo-icon.png"
                            alt="HyPerform"
                            className="h-[32px] w-auto object-contain animate-in fade-in zoom-in duration-300"
                        />
                    ) : (
                        <img
                            src="/logo-full.png"
                            alt="HyPerform"
                            className="h-[44px] w-auto object-contain animate-in fade-in zoom-in duration-300"
                        />
                    )}
                </Link>

                {/* Toggle Button */}
                <button
                    onClick={toggleSidebar}
                    className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 bg-[#2D2D3A] rounded-full flex items-center justify-center border border-[#1A1A2E] text-slate-400 hover:text-white hover:bg-[#3D3D4A] transition-colors z-50 cursor-pointer shadow-md"
                >
                    {isCollapsed ? <ChevronRight size={14} /> : <div className="rotate-180"><ChevronRight size={14} /></div>}
                </button>
            </div>

            <nav className={`flex-1 py-4 custom-scrollbar ${isCollapsed ? 'overflow-visible' : 'overflow-y-auto'}`}>
                {menuGroups.map((group) => {
                    const isExpanded = expandedGroup === group.name;
                    const GroupIcon = group.icon;

                    return (
                        <div key={group.name} className="mb-2 relative group">
                            {/* Group Header */}
                            <button
                                onClick={() => toggleGroup(group.name)}
                                className={`flex items-center w-full text-slate-400 hover:text-white transition-all duration-200 cursor-pointer px-4 py-2
                                    ${isCollapsed ? 'justify-center' : 'justify-between'}
                                `}
                            // Remove title to avoid double tooltip
                            // title={isCollapsed ? group.name : undefined}
                            >
                                <div className="flex items-center gap-3">
                                    <GroupIcon size={20} className="shrink-0" />
                                    {!isCollapsed && <span className="font-semibold">{group.name}</span>}
                                </div>
                                {!isCollapsed && group.items.length > 0 && (
                                    isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />
                                )}
                            </button>

                            {/* Flyout Menu (Collapsed Mode) */}
                            {isCollapsed && group.items.length > 0 && (
                                <div className="absolute left-full top-0 ml-1 bg-[#1A1A2E] border border-[#2D2D3A] rounded-lg shadow-xl p-2 w-[200px] z-[60] invisible opacity-0 group-hover:visible group-hover:opacity-100 transition-all duration-200 pointer-events-none group-hover:pointer-events-auto before:content-[''] before:absolute before:-left-4 before:top-0 before:h-full before:w-6 before:bg-transparent">
                                    <div className="font-semibold text-white mb-2 px-3 py-1 border-b border-[#2D2D3A]">{group.name}</div>
                                    <div className="flex flex-col space-y-1">
                                        {group.items.map((item: any) => {
                                            const isActive = pathname === item.href;
                                            return (
                                                <Link
                                                    key={item.name}
                                                    href={item.disabled ? '#' : item.href}
                                                    className={`
                                                        flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all whitespace-nowrap
                                                        ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-800/80'}
                                                        ${isActive && !item.disabled ? "bg-blue-600/10 text-blue-400" : "text-slate-400"}
                                                    `}
                                                >
                                                    <item.icon size={16} className={`shrink-0 ${isActive ? "text-blue-400" : "text-slate-500"}`} />
                                                    {item.name}
                                                    {item.disabled && (
                                                        <span className="ml-auto text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-500">Breve</span>
                                                    )}
                                                </Link>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Group Items (Only when not collapsed) */}
                            <div
                                className={`grid transition-all duration-300 ease-in-out bg-black/10 
                                    ${(isExpanded && !isCollapsed) ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}
                                `}
                            >
                                <div className="overflow-hidden">
                                    <div className="space-y-1 ml-4 border-l border-slate-800 pl-3 py-1 mr-4">
                                        {group.items.map((item: any) => {
                                            const isActive = pathname === item.href;
                                            return (
                                                <div key={item.name} className="relative">
                                                    <Link
                                                        href={item.disabled ? '#' : item.href}
                                                        className={`
                                                            flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-all whitespace-nowrap
                                                            ${item.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-800/80'}
                                                            ${isActive && !item.disabled ? "bg-blue-600/10 text-blue-400" : "text-slate-400"}
                                                        `}
                                                    >
                                                        <item.icon size={16} className={`shrink-0 ${isActive ? "text-blue-400" : "text-slate-500"}`} />
                                                        {item.name}
                                                        {item.disabled && (
                                                            <span className="ml-auto text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-500">Breve</span>
                                                        )}
                                                    </Link>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-[#2D2D3A]">
                <div className={`flex items-center gap-3 px-3 py-2 text-sm text-slate-400 hover:text-white cursor-pointer hover:bg-slate-800 active:scale-95 rounded-lg transition-all duration-200 ${isCollapsed ? 'justify-center' : ''}`}>
                    <LogOut size={16} />
                    {!isCollapsed && <span>Sair</span>}
                </div>
            </div>
        </aside>
    );
}
