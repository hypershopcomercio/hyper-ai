
import shutil
import os

# New uploads from the user
source_full = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_0_1765751500167.png"
dest_full = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-full.png"

source_icon = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_1_1765751500167.png"
dest_icon = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-icon.png"

try:
    print(f"Copying new full logo from {source_full}...")
    shutil.copy2(source_full, dest_full)
    print("Success: logo-full.png updated.")
    
    print(f"Copying new icon from {source_icon}...")
    shutil.copy2(source_icon, dest_icon)
    print("Success: logo-icon.png updated.")
except Exception as e:
    print(f"Error copying files: {e}")
