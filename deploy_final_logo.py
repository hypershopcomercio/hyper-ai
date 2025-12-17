
import shutil
import os

# Source is the NEWEST upload
source_path = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_1765752514715.png"
dest_path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-final.png"

try:
    print(f"Copying {source_path} to {dest_path}...")
    shutil.copy2(source_path, dest_path)
    print("Success: logo-final.png saved.")
except Exception as e:
    print(f"Error copying files: {e}")
