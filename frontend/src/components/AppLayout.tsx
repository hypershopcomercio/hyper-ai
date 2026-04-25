"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { StatusBar } from "@/components/StatusBar";

export function AppLayout({ children }: { children: React.ReactNode }) {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const pathname = usePathname();

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    // Routes that should NOT have the sidebar/header layout
    const isAuthRoute = pathname === '/login' || pathname?.startsWith('/auth');

    // For auth routes, render children without layout
    if (isAuthRoute) {
        return <>{children}</>;
    }

    return (
        <>
            <Sidebar isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
            <Header isCollapsed={isCollapsed} />
            <main
                className={`
                    transition-all duration-300 ease-in-out
                    mt-[64px] mb-[40px] min-h-[calc(100vh-104px)] 
                    bg-[#0D0D14] text-slate-200
                    ${isCollapsed ? 'ml-[80px]' : 'ml-[260px]'}
                `}
            >
                {children}
            </main>
            <StatusBar isCollapsed={isCollapsed} />
        </>
    );
}

