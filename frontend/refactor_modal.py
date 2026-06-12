import re
import sys

file_path = 'frontend/src/components/AdDetailsModal.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
if 'import { AdMediaTab }' not in content:
    content = content.replace(
        "import { FiscalParametersTab } from './FiscalParametersTab';",
        "import { FiscalParametersTab } from './FiscalParametersTab';\nimport { AdMediaTab } from './AdMediaTab';"
    )

# 2. activeTab state
content = content.replace(
    "useState<'overview' | 'performance' | 'health' | 'competition' | 'margin' | 'fiscal'>('overview')",
    "useState<'overview' | 'performance' | 'health' | 'competition' | 'margin' | 'fiscal' | 'media'>('overview')"
)

# 3. Modal width
content = content.replace(
    "className=\"relative w-full max-w-7xl max-h-[95vh] h-[90vh]",
    "className=\"relative w-[92vw] max-w-[1600px] h-[90vh] max-h-none"
)

# 4. FULL badge in Header
header_id_target = "<span className=\"text-slate-300 font-bold select-all\">{adId}</span>"
header_id_replacement = "<span className=\"text-slate-300 font-bold select-all\">{adId}</span>\n                                    <span className={`ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-widest border ${ad.is_full ? 'bg-[#00A650]/20 text-[#00A650] border-[#00A650]/30' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>{ad.is_full ? 'FULL' : (ad.shipping_mode === 'me2' ? 'Envios' : 'Próprio')}</span>"
if "{ad.is_full ? 'FULL' : (ad.shipping_mode === 'me2' ? 'Envios' : 'Próprio')}" not in content[:content.find(header_id_target)+300]:
    content = content.replace(header_id_target, header_id_replacement)

# 5. Main Grid
content = content.replace(
    "<div className=\"p-6 pt-0 grid grid-cols-1 lg:grid-cols-5 gap-6\">",
    "<div className=\"p-6 pt-0 flex-1 flex flex-col min-h-0\">"
)

# 6. Remove left panel (lg:col-span-2)
lines = content.split('\n')
start_idx = -1
for i, line in enumerate(lines):
    if '<div className="lg:col-span-2 space-y-0">' in line:
        start_idx = i
        break

if start_idx != -1:
    open_divs = 0
    end_idx = -1
    for i in range(start_idx, len(lines)):
        line = lines[i]
        open_divs += line.count('<div')
        open_divs -= line.count('</div')
        if open_divs == 0:
            end_idx = i
            break
    
    if end_idx != -1:
        del lines[start_idx:end_idx+1]
        content = '\n'.join(lines)
    else:
        print('Could not find matching closing div for lg:col-span-2')
        sys.exit(1)

# 7. lg:col-span-3 -> full width
content = content.replace(
    "<div className=\"lg:col-span-3 flex flex-col h-full bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden\">",
    "<div className=\"flex flex-col h-full bg-[#13141b] rounded-2xl border border-white/5 overflow-hidden\">"
)

# 8. Tab Button
if "onClick={() => setActiveTab('media')}" not in content:
    tab_replacement = """                                            <div
                                                onClick={() => setActiveTab('media')}
                                                className={`px-4 py-2 rounded-lg text-xs font-bold uppercase transition-colors flex items-center gap-2 cursor-pointer ${activeTab === 'media' ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                            >
                                                <ExternalLink size={14} /> Mídia
                                            </div>
"""
    old_fiscal_block = "Ficha Fiscal\n                                            </div>"
    new_fiscal_block = "Ficha Fiscal\n                                            </div>\n" + tab_replacement
    content = content.replace(old_fiscal_block, new_fiscal_block)

# 9. Render AdMediaTab
render_target = "{activeTab === 'fiscal' && ("
if "{activeTab === 'media' && (" not in content:
    render_replacement = """                                            {activeTab === 'media' && (
                                                <AdMediaTab ad={ad} setIsLightboxOpen={setIsLightboxOpen} />
                                            )}

                                            {activeTab === 'fiscal' && ("""
    content = content.replace(render_target, render_replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Refactor successful')
