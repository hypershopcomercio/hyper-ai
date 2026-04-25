
path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\src\components\AdDetailsModal.tsx"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 1148 (1-based) is index 1147. We keep it.
# Line 1149 (1-based) is index 1148. We cut from here.
# Line 1496 (1-based) is index 1495. We cut up to here.
# Line 1497 (1-based) is index 1496. We resume here.

# Slicing:
# lines[:1148] includes indices 0 to 1147. Correct.
# lines[1496:] includes indices 1496 to end. Correct.

new_content = lines[:1148] + lines[1496:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print(f"Successfully processed {path}. Lines before: {len(lines)}, Lines after: {len(new_content)}")
