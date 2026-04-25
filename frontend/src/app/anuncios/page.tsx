'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { AdTable } from '@/components/AdTable';
import { Megaphone, Package, Power, PauseCircle, TrendingDown, DollarSign, Filter, RefreshCw } from 'lucide-react';
import { Tooltip } from '@/components/ui/Tooltip';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { PremiumLoader } from '@/components/ui/PremiumLoader';
import { AdDetailsModal } from '@/components/AdDetailsModal';
import { AnimatePresence } from 'framer-motion';

export default function AnunciosPage() {
  const [activeTab, setActiveTab] = useState('todos');
  const [ads, setAds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAdId, setSelectedAdId] = useState<string | null>(null);

  // Sort State
  const [sort, setSort] = useState('sales_30d');
  const [sortOrder, setSortOrder] = useState('desc');

  const tabs = [
    { id: 'todos', label: 'Todos', icon: Package },
    { id: 'active', label: 'Ativos', icon: Power },
    { id: 'paused', label: 'Pausados', icon: PauseCircle },
    { id: 'baixa-margem', label: 'Baixa Margem', icon: DollarSign },
    { id: 'sem-vendas', label: 'Sem Vendas', icon: TrendingDown }
  ];



  useEffect(() => {
    loadAds();
  }, [activeTab, sort, sortOrder]);

  const loadAds = async () => {
    setLoading(true);
    try {
      const params: any = {
        sort_by: sort,
        sort_order: sortOrder
      };

      // Map tabs to filter_type or status
      if (activeTab === 'active') params.status = 'active';
      if (activeTab === 'paused') params.status = 'paused';
      if (activeTab === 'baixa-margem') params.filter_type = 'low_margin';
      if (activeTab === 'sem-vendas') params.filter_type = 'no_sales';

      const res = await axios.get('http://localhost:5000/api/ads', { params });

      let data = [];
      if (res.data.data && Array.isArray(res.data.data)) {
        data = res.data.data;
      } else if (res.data.ads && Array.isArray(res.data.ads)) {
        data = res.data.ads;
      } else if (Array.isArray(res.data)) {
        data = res.data;
      }

      setAds(data);
    } catch (error) {
      console.error('Erro ao carregar anúncios:', error);
      toast.error('Erro ao carregar lista de anúncios');
      setAds([]);
    } finally {
      if (loading) setTimeout(() => setLoading(false), 4000);
      else setLoading(false);
    }
  };

  const handleSync = async () => {
    const toastId = toast.loading('Sincronizando dados...');
    try {
      await api.post('/sync/listings');
      toast.success('Sincronização concluída!', { id: toastId });
      loadAds();
    } catch (error) {
      console.error('Erro ao sincronizar:', error);
      toast.error('Erro ao sincronizar dados', { id: toastId });
    }
  };

  const handleSort = (field: string) => {
    if (sort === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSort(field);
      setSortOrder('desc');
    }
  };

  // Filter ads by search term
  const filteredAds = ads.filter(ad =>
    ad.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ad.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <PremiumLoader />;
  }

  return (
    <div className="p-8 max-w-[1800px] mx-auto min-h-screen animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-300 ease-out fill-mode-both">

      {/* Header */}
      <div className="flex flex-col gap-6 mb-8">
        <div className="flex justify-between items-center bg-[#0F1016] border border-[#1F2128] p-6 rounded-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />

          <div className="relative z-10">
            <h1 className="text-3xl font-bold text-white flex items-center gap-4 mb-2">
              <div className="relative flex items-center justify-center w-12 h-12 bg-blue-500/10 rounded-xl border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.2)] group-hover:shadow-[0_0_25px_rgba(59,130,246,0.3)] transition-all duration-500">
                <div className="absolute inset-0 bg-blue-400/10 blur-lg rounded-full animate-pulse" />
                <div className="absolute inset-0 border-t border-white/10 rounded-xl" />
                <Megaphone className="relative z-10 text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]" size={24} />
              </div>
              Anúncios
            </h1>
            <p className="text-slate-400 text-sm">
              Gerencie seu catálogo no Mercado Livre
            </p>
          </div>

          <Tooltip title="Sincronizar" content="Atualizar lista de anúncios" position="bottom">
            <button
              onClick={handleSync}
              className="flex items-center justify-center p-3 bg-[#1A1A22] hover:bg-[#252530] text-slate-200 rounded-lg transition-all border border-[#2D2D3A] hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/5 group/btn cursor-pointer"
            >
              <RefreshCw size={18} className="group-hover/btn:rotate-180 transition-transform duration-700" />
            </button>
          </Tooltip>
        </div>

        {/* Controls - Transparent & Clean */}
        <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 border-b border-white/5 pb-6">

          {/* Tabs */}
          <div className="flex flex-wrap gap-2">
            {tabs.map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-all cursor-pointer ${isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                    : 'text-slate-400 bg-white/5 hover:bg-white/10 hover:text-slate-200'
                    }`}
                >
                  <Icon size={14} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <div className="flex gap-4 w-full xl:w-auto">
            {/* Search */}
            <div className="relative flex-1 xl:w-72 group">
              <Filter className="absolute left-3 top-2.5 w-4 h-4 text-slate-500 group-focus-within:text-blue-500 transition-colors" />
              <input
                type="text"
                placeholder="Buscar por título, SKU ou ID..."
                className="w-full pl-10 pr-4 py-2 bg-[#0F1016] border border-[#2D2D3A] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500/50 focus:bg-[#151520] transition-all placeholder:text-slate-600"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

          </div>
        </div>

        {/* Stats Summary (simplified for now) */}

      </div>

      {/* Table Component */}
      <AdTable
        ads={filteredAds}
        loading={loading}
        sort={sort}
        sortOrder={sortOrder}
        onSort={handleSort}
        onAdSelect={setSelectedAdId}
      />

      <AnimatePresence>
        {selectedAdId && (
          <AdDetailsModal
            adId={selectedAdId}
            onClose={() => {
              setSelectedAdId(null);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
