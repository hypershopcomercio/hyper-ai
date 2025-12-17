
from PIL import Image, ImageChops
import numpy as np
import os

# Source is the LATEST ICON upload (uploaded_image_1765754302900.png)
source_path = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_1765754302900.png"
dest_path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-icon-final.png"

def fix_logo():
    try:
        print(f"Opening {source_path}...")
        img = Image.open(source_path).convert("RGBA")
        
        # --- Step 1: Background Removal ---
        data = np.array(img)
        # Use int16 for safe math on channels
        r = data[..., 0].astype(np.int16)
        g = data[..., 1].astype(np.int16)
        b = data[..., 2].astype(np.int16)

        # Condition A: White/Very Light (All > 180)
        is_light = (r > 180) & (g > 180) & (b > 180)
        
        # Condition B: Neutral Gray (Checkerboards)
        # R, G, B are close to each other (variance < 20) AND they are not dark (> 100)
        is_neutral = (np.abs(r - g) < 20) & (np.abs(g - b) < 20) & (np.abs(r - b) < 20)
        is_gray_bg = is_neutral & (r > 100)

        # Apply Transparency
        data[..., 3][is_light | is_gray_bg] = 0
        
        # Update Image object from Modified Data
        img = Image.fromarray(data)
        
        # --- Step 2: Trim ---
        bg = Image.new(img.mode, img.size, (0,0,0,0))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
        if bbox:
            img = img.crop(bbox)
            print(f"Trimmed to {img.size}")
            
        # --- Step 3: Text Color Swap ---
        # NOW we reload data from the cropped image so shapes match
        data = np.array(img)
        red, green, blue, alpha = data.T
        
        # Define Accents (Green/Orange) to Preserve
        # Green: G > R+10 AND G > B+10
        # NOTE: np.array(img) is (H,W,C). unpacking .T gives (W, H). 
        # WAIT. logic below relies on .T unpacking? 
        # red, green, blue, alpha = data.T  <-- This makes r,g,b,a shape (W, H) because data is (H,W,C) -> T is (C, W, H).
        # So r,g,b,a ARE transposed relative to data[..., 0].
        
        # If I strictly use H,W logic without T?
        r = data[..., 0].astype(np.int16)
        g = data[..., 1].astype(np.int16)
        b = data[..., 2].astype(np.int16)
        a = data[..., 3]
        
        is_green = (g > r + 10) & (g > b + 10)
        is_orange = (r > g + 10) & (r > b + 10)
        
        is_visible = (a > 0)
        target_mask = is_visible & (~is_green) & (~is_orange)

        data[..., 0][target_mask] = 255
        data[..., 1][target_mask] = 255
        data[..., 2][target_mask] = 255

        
        # Save
        new_img = Image.fromarray(data)
        new_img.save(dest_path)
        print(f"Saved cleaned icon to {dest_path}")
        
    except Exception as e:
        print(f"Error fixing icon: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_logo()
