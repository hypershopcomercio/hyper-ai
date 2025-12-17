
from PIL import Image
import numpy as np

# Source is the LATEST upload (uploaded_image_1765752514715.png)
source_path = r"C:\Users\Usuário\.gemini\antigravity\brain\d3a0a145-d5b3-4b45-9471-b28bfbaef24c\uploaded_image_1765752514715.png"
dest_path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-final.png"

def restore_logo():
    try:
        print(f"Opening {source_path}...")
        img = Image.open(source_path).convert("RGBA")
        data = np.array(img)

        red, green, blue, alpha = data.T

        # 1. Background Removal (Keep aggressive removal of white/light)
        # Anything very light is transparency.
        light_areas = (red > 210) & (green > 210) & (blue > 210)
        data[..., 3][light_areas.T] = 0

        # 2. Text Color Swap
        # Strategy: Identify Green and Orange. Everything else that is VISIBLE is Text (Navy).
        # Green: G > R and G > B. (Safety margin of 10)
        is_green = (green > red + 10) & (green > blue + 10)
        
        # Orange: R > G and R > B.
        is_orange = (red > green + 10) & (red > blue + 10)
        
        # Text Candidates: Visible pixels that are NOT Green and NOT Orange.
        # This includes Dark Navy and Lighter Navy (AA artifacts).
        # We assume there are no other colors in the logo.
        is_visible = (data[..., 3].T > 0)
        
        # Refine: Ensure we don't pick up white background pixels that missed the threshold?
        # The light_areas set alpha to 0, so is_visible handles that.
        
        # Target:
        target_mask = is_visible & (~is_green) & (~is_orange)

        # Apply White to Target
        data[..., 0][target_mask.T] = 255
        data[..., 1][target_mask.T] = 255
        data[..., 2][target_mask.T] = 255

        # Reconstruct
        new_img = Image.fromarray(data)
        new_img.save(dest_path)
        print(f"Saved restored logo to {dest_path}")
        
    except Exception as e:
        print(f"Error restoring logo: {e}")

if __name__ == "__main__":
    restore_logo()
