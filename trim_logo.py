
from PIL import Image, ImageChops
import sys

path = r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-final.png"

def trim():
    try:
        print(f"Opening {path}...")
        im = Image.open(path)
        
        # Get bounding box of non-transparent pixels
        # getbbox() returns (left, upper, right, lower) or None if fully transparent
        # By default it operates on the alpha channel if available or black borders
        # Let's ensure we look at alpha
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
            
        bg = Image.new(im.mode, im.size, (0,0,0,0))
        diff = ImageChops.difference(im, bg)
        # diff = ImageChops.add(diff, diff, 2.0, -100) # Optional boost
        bbox = im.getbbox()
        
        if bbox:
            print(f"Original size: {im.size}")
            print(f"Content bbox: {bbox}")
            # Crop
            cropped = im.crop(bbox)
            print(f"New size: {cropped.size}")
            cropped.save(path)
            print(f"Saved trimmed logo to {path}")
        else:
            print("No content found (image is fully transparent?)")
            
    except Exception as e:
        print(f"Error trimming logo: {e}")

if __name__ == "__main__":
    trim()
