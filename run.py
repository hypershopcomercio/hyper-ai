import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Inicia o servidor
from app.web import app

if __name__ == "__main__":
    print("Iniciando servidor Hyper Sync...")
    app.run(host="0.0.0.0", port=5000, debug=True)
