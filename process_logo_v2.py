
from PIL import Image
import numpy as np
import os

# Source is the LATEST upload (uploaded_image_1765752514715.png)
source_path = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_1765752514715.png"
dest_path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-final.png"

def process_logo():
    try:
        print(f"Opening {source_path}...")
        img = Image.open(source_path).convert("RGBA")
        data = np.array(img)

        # Extract channels
        red, green, blue, alpha = data.T

        # 1. Background Removal:
        # Aggressive threshold for white/light gray
        light_areas = (red > 200) & (green > 200) & (blue > 200)
        data[..., 3][light_areas.T] = 0  # Set alpha to 0

        # 2. Text Color Swap: Dark Blue to White
        # Target Dark Pixels: R<100, G<100, B<150
        # Exclude accents (Green/Orange)
        dark_areas = (red < 80) & (green < 100) & (blue < 130) & (data[..., 3].T > 0)
        
        # Set these pixels to White (255, 255, 255)
        data[..., 0][dark_areas.T] = 255 # R
        data[..., 1][dark_areas.T] = 255 # G
        data[..., 2][dark_areas.T] = 255 # B

        # Reconstruct image
        new_img = Image.fromarray(data)
        new_img.save(dest_path)
        print(f"Saved processed logo to {dest_path}")
        
    except Exception as e:
        print(f"Error processing logo: {e}")

if __name__ == "__main__":
    process_logo()
