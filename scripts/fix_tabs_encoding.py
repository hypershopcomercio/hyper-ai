
import os

file_path = r'c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data/frontend/src/components/AdDetailsModal.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix specific known corruptions
content = content.replace('Saíºde', 'Saúde')
content = content.replace('Concorríªncia', 'Concorrência')
content = content.replace('PrecificaÃ§Ã£o', 'Precificação') 

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Encoding fixes applied.")
