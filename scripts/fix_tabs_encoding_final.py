
import os

file_path = r'c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data/frontend/src/components/AdDetailsModal.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix remaining known corruptions
content = content.replace('REVERSíƒO', 'REVERSÃO')
content = content.replace('Fí“RMULA', 'FÓRMULA')
content = content.replace('EXPLICAí‡íƒO', 'EXPLICAÇÃO')
content = content.replace('Iní­cio', 'Início')
content = content.replace('Lí­q', 'Líq')
content = content.replace('Lí­quida', 'Líquida')
content = content.replace('Mí­n', 'Mín')
content = content.replace('Mí­nima', 'Mínima')
content = content.replace('comissíµes', 'comissões')
content = content.replace('í·', '÷')
content = content.replace('í—', '×')
content = content.replace('â€¢', '•')
content = content.replace('â†’', '→')
content = content.replace('âš¡', '⚡')
content = content.replace('âš ï¸', '⚠️')
content = content.replace('âœ“', '✓')
content = content.replace('irreversí­vel', 'irreversível')
content = content.replace('Prí³prio', 'Próprio')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Final encoding cleanups applied.")
