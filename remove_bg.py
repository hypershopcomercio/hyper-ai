from PIL import Image
import sys

def remove_bg(input_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()
        width, height = img.size
        
        # Sample corner colors to identify background
        # Top-left, Top-right, Bottom-left, Bottom-right
        corners = [
            img.getpixel((0, 0)),
            img.getpixel((width-1, 0)),
            img.getpixel((0, height-1)),
            img.getpixel((width-1, height-1))
        ]
        
        # Use top-left as primary reference
        bg_ref = corners[0]
        
        # Function to check similarity
        def is_similar(c1, c2, threshold=30):
            return (abs(c1[0] - c2[0]) < threshold and
                    abs(c1[1] - c2[1]) < threshold and
                    abs(c1[2] - c2[2]) < threshold)

        newData = []
        for item in datas:
            # Check against the reference background color
            if is_similar(item, bg_ref):
                newData.append((255, 255, 255, 0)) # Transparent
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(input_path, "PNG")
        print(f"Processed {input_path} using corner detection (Ref: {bg_ref})")
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    remove_bg(r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-full.png")
    remove_bg(r"c:\Users\Usuário\OneDrive\Documentos\01 - Projetos\projeto-hyper-ai\hyper-data\frontend\public\logo-icon.png")
