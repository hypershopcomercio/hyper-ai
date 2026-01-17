import os

file_path = "c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data/frontend/src/components/AdDetailsModal.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix common Mojibake patterns
# These look like UTF-8 bytes interpreted as Windows-1252 or Latin-1
# e.g. Ã§ -> ç
# We can try to encode as latin-1 and decode as utf-8, but sometimes it's mixed.
# Let's try the standard verify.

try:
    fixed_content = content.encode("cp1252").decode("utf-8")
    print("Successfully decoded using cp1252 -> utf-8")
except:
    try:
        fixed_content = content.encode("latin1").decode("utf-8")
        print("Successfully decoded using latin1 -> utf-8")
    except Exception as e:
        print(f"Failed to decode: {e}")
        # Manual replacements if bulk decode fails
        replacements = {
            "Ã§Ã£": "çã",
            "Ã§": "ç",
            "Ã£": "ã",
            "Ã©": "é",
            "Ã¡": "á",
            "Ã": "í", # Risks matching others, be careful
            "Ã³": "ó",
            "Ãª": "ê",
            "Ãº": "ú",
            "Ã¢": "â",
            "Ãµ": "õ",
            "Ã€": "À",
            "Ãš": "Ú",
            # 'PrÃ³prio' -> 'Próprio'
        }
        fixed_content = content
        for k, v in replacements.items():
            fixed_content = fixed_content.replace(k, v)

# Safety check: if the file becomes empty or significantly smaller, abort
if len(fixed_content) < len(content) * 0.9:
    print("Error: Fixed content is too small, aborting.")
    exit(1)

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print("File encoding fixed.")
