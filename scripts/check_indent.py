with open(r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\src\components\AdDetailsModal.tsx", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "currentPrice" in line:
            print(f"Line {i+1}: {repr(line)}")
