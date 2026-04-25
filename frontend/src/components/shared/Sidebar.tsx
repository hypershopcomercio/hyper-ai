
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Package,
  Link as LinkIcon,
  Bell,
  FileText,
  Settings,
  LogOut
} from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    {
      icon: LayoutDashboard,
      label: 'Dashboard',
      path: '/dashboard'
    },
    {
      icon: Package,
      label: 'Anúncios',
      path: '/anuncios'
    },
    {
      icon: LinkIcon,
      label: 'Integrações',
      path: '/integracoes'
    },
    {
      icon: Bell,
      label: 'Alertas',
      path: '/alertas'
    },
    {
      icon: FileText,
      label: 'Logs',
      path: '/logs'
    },
    {
      icon: Settings,
      label: 'Configurações',
      path: '/configuracoes'
    }
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 min-h-screen flex flex-col fixed left-0 top-0 z-50">

      {/* Header / Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
          <span className="text-cyan-400">hyper</span>
          <span className="text-white">shop</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 px-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path || pathname?.startsWith(`${item.path}/`);

          return (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 group ${isActive
                  ? 'bg-cyan-500/10 text-cyan-400 shadow-sm border border-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
                }`}
            >
              <Icon size={20} className={`transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer / User */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/50 rounded-lg p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-cyan-900/50 flex items-center justify-center text-cyan-400 font-bold text-xs">
            HS
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate">Hyper Shop</p>
            <p className="text-xs text-slate-500 truncate">v1.0.0</p>
          </div>
          <button className="text-slate-500 hover:text-slate-300 transition-colors">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
