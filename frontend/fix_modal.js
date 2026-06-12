const fs = require('fs');
const path = require('path');

const modalPath = path.join(__dirname, 'src', 'components', 'AdDetailsModal.tsx');
let modalContent = fs.readFileSync(modalPath, 'utf-8');

// Fix 1: Remove height constraints from Main Grid
modalContent = modalContent.replace(
    '<div className="p-6 pt-0 flex-1 flex flex-col min-h-0">',
    '<div className="p-6 pt-0 flex flex-col">'
);

// Fix 2: Remove height/overflow constraints from Tabs Container
modalContent = modalContent.replace(
    '<div className="flex flex-col h-full bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden">',
    '<div className="flex flex-col bg-[#13141b] rounded-2xl border border-white/5">'
);

// Fix 3: Remove height/overflow constraints from Tabs Content Box
modalContent = modalContent.replace(
    '<div className="flex-1 p-6 overflow-y-auto custom-scrollbar">',
    '<div className="p-6">'
);

fs.writeFileSync(modalPath, modalContent, 'utf-8');

const fiscalPath = path.join(__dirname, 'src', 'components', 'FiscalParametersTab.tsx');
let fiscalContent = fs.readFileSync(fiscalPath, 'utf-8');

// Fix Fiscal Loading State
const loadingBlock = `    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-12">
                <PremiumLoader />
                <p className="text-slate-400 mt-4 text-sm animate-pulse">Sincronizando base fiscal...</p>
            </div>
        );
    }`;
fiscalContent = fiscalContent.replace(loadingBlock, '');

// Update the header of Fiscal Tab to show "Carregando..."
const headerTarget = '<h3 className="text-lg font-bold text-white flex items-center gap-2">';
const headerReplacement = `<h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-indigo-400" />
                        Parâmetros Fiscais (V1)
                        {loading && <span className="ml-4 text-xs font-normal text-slate-400 flex items-center gap-2"><PremiumLoader /> Carregando...</span>}
                    </h3>`;
fiscalContent = fiscalContent.replace(
    `<h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-indigo-400" />
                        Parâmetros Fiscais (V1)
                    </h3>`,
    headerReplacement
);

fs.writeFileSync(fiscalPath, fiscalContent, 'utf-8');

console.log('Fixes applied successfully');
