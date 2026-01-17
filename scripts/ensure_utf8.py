import sys
import os

path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\src\components\AdDetailsModal.tsx"

# Try reading with varying encodings
content = None
encodings = ['utf-8', 'cp1252', 'latin1']

for enc in encodings:
    try:
        with open(path, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Read successfully with {enc}")
        break
    except UnicodeDecodeError:
        continue
    except Exception as e:
        print(f"Error reading with {enc}: {e}")

if content is not None:
    # Write back as utf-8
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved as UTF-8")
else:
    print("Failed to read file")
