const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'src', 'components', 'AdDetailsModal.tsx');
let content = fs.readFileSync(filePath, 'utf-8');

// 1. Imports
if (!content.includes('import { AdMediaTab }')) {
    content = content.replace(
        "import { FiscalParametersTab } from './FiscalParametersTab';",
        "import { FiscalParametersTab } from './FiscalParametersTab';\nimport { AdMediaTab } from './AdMediaTab';"
    );
}

// 2. activeTab state
content = content.replace(
    "useState<'overview' | 'performance' | 'health' | 'competition' | 'margin' | 'fiscal'>('overview')",
    "useState<'overview' | 'performance' | 'health' | 'competition' | 'margin' | 'fiscal' | 'media'>('overview')"
);

// 3. Modal width
content = content.replace(
    'className="relative w-full max-w-7xl max-h-[95vh] h-[90vh]',
    'className="relative w-[92vw] max-w-[1600px] h-[90vh] max-h-none'
);

// 4. FULL badge in Header
const headerIdTarget = '<span className="text-slate-300 font-bold select-all">{adId}</span>';
const headerIdReplacement = `<span className="text-slate-300 font-bold select-all">{adId}</span>
                                    <span className={\`ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border \${ad.is_full ? 'bg-[#00A650]/20 text-[#00A650] border-[#00A650]/30' : 'bg-slate-800 text-slate-400 border-slate-700'}\`}>{ad.is_full ? 'FULL' : (ad.shipping_mode === 'me2' ? 'Envios' : 'Próprio')}</span>`;
if (!content.substring(0, content.indexOf(headerIdTarget) + 300).includes('ad.is_full ? \'FULL\'')) {
    content = content.replace(headerIdTarget, headerIdReplacement);
}

// 5. Main Grid
content = content.replace(
    '<div className="p-6 pt-0 grid grid-cols-1 lg:grid-cols-5 gap-6">',
    '<div className="p-6 pt-0 flex-1 flex flex-col min-h-0">'
);

// 6. Remove left panel (lg:col-span-2)
const lines = content.split('\n');
let startIdx = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('<div className="lg:col-span-2 space-y-0">')) {
        startIdx = i;
        break;
    }
}

if (startIdx !== -1) {
    let openDivs = 0;
    let endIdx = -1;
    for (let i = startIdx; i < lines.length; i++) {
        const line = lines[i];
        openDivs += (line.match(/<div/g) || []).length;
        openDivs -= (line.match(/<\/div/g) || []).length;
        if (openDivs === 0) {
            endIdx = i;
            break;
        }
    }
    
    if (endIdx !== -1) {
        lines.splice(startIdx, endIdx - startIdx + 1);
        content = lines.join('\n');
    } else {
        console.error('Could not find matching closing div for lg:col-span-2');
        process.exit(1);
    }
}

// 7. lg:col-span-3 -> full width
content = content.replace(
    '<div className="lg:col-span-3 flex flex-col h-full bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden">',
    '<div className="flex flex-col h-full bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden">'
);

// 8. Tab Button
if (!content.includes("onClick={() => setActiveTab('media')}")) {
    const tabReplacement = `                                            <div
                                                onClick={() => setActiveTab('media')}
                                                className={\`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer \${activeTab === 'media' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}\`}
                                            >
                                                <ExternalLink size={14} /> Mídia
                                            </div>
`;
    const oldFiscalBlock = "Ficha Fiscal\n                                            </div>";
    const newFiscalBlock = "Ficha Fiscal\n                                            </div>\n" + tabReplacement;
    content = content.replace(oldFiscalBlock, newFiscalBlock);
}

// 9. Render AdMediaTab
const renderTarget = "{activeTab === 'fiscal' && (";
if (!content.includes("{activeTab === 'media' && (")) {
    const renderReplacement = `                                            {activeTab === 'media' && (
                                                <AdMediaTab ad={ad} setIsLightboxOpen={setIsLightboxOpen} />
                                            )}

                                            {activeTab === 'fiscal' && (` ;
    content = content.replace(renderTarget, renderReplacement);
}

fs.writeFileSync(filePath, content, 'utf-8');
console.log('Refactor successful');
