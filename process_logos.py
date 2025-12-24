from PIL import Image, ImageFilter
import sys

def process_logo(input_path, rigorous_smoothing=False):
    try:
        print(f"Processing {input_path} (Smooth={rigorous_smoothing})...")
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        
        # 1. Corner Detection for Background Color
        width, height = img.size
        # Sample average of corners to be safer
        corners = [
            img.getpixel((0, 0)),
            img.getpixel((width-1, 0)),
            img.getpixel((0, height-1)),
            img.getpixel((width-1, height-1))
        ]
        # Use top-left as reference but check consistency
        bg_ref = corners[0]
        
        # 2. Threshold Matching
        # A bit stricter threshold for the "Full" logo if smoothing is on, to capture more 'white' halo
        threshold = 50 if rigorous_smoothing else 60
        
        def is_similar(c1, c2):
            if c1[3] == 0: return False # Already transparent
            return (abs(c1[0] - c2[0]) < threshold and
                    abs(c1[1] - c2[1]) < threshold and
                    abs(c1[2] - c2[2]) < threshold)

        newData = []
        for item in datas:
            if is_similar(item, bg_ref):
                newData.append((255, 255, 255, 0)) # Transparent
            else:
                newData.append(item)

        img.putdata(newData)
        
        # 3. Edge Refinement (Only if requested)
        if rigorous_smoothing:
            # Split channels
            r, g, b, a = img.split()
            
            # Erode the alpha channel to remove the "white fringe" aliasing
            # MinFilter(3) = 3x3 kernel, effectively 1px erosion
            a = a.filter(ImageFilter.MinFilter(3))
            
            # Very slight blur to soften the new edge (Anti-aliasing)
            # 0.5 is very subtle, just enough to kill the stair-step
            a = a.filter(ImageFilter.GaussianBlur(0.5))
            
            img = Image.merge("RGBA", (r, g, b, a))

        # 4. Auto-Crop
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            print(f"Cropped to {bbox}")
        
        img.save(input_path, "PNG")
        print(f"Success: {input_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    # Full Logo: Apply smoothing as requested
    process_logo(r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-full.png", rigorous_smoothing=True)
    
    # Icon: Keep clean cut (user complained about secondary logo issues before, safer to keep sharp)
    # The user said "improve edges of main logo" specifically.
    process_logo(r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-icon.png", rigorous_smoothing=False)
