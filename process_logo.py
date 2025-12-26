from PIL import Image, ImageFilter
import math

def remove_background_ssaa_ultra(input_path, output_path):
    print("Starting Ultra Quality (4x SSAA) processing...")
    # 1. Open original
    img = Image.open(input_path).convert("RGBA")
    
    # 2. Upscale (Supersampling 4x for extreme precision)
    factor = 4
    target_w, target_h = img.width * factor, img.height * factor
    img_hd = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    datas = img_hd.getdata()
    new_data = []
    
    bg_r, bg_g, bg_b = 255, 255, 255
    
    # Thresholds adjusted for 4x scale
    full_transparent_dist = 45  
    full_opaque_dist = 130      
    
    for item in datas:
        r, g, b, a = item
        
        dist = math.sqrt((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2)
        
        if dist < full_transparent_dist:
            # Transparent
            new_data.append((r, g, b, 0))
        elif dist >= full_opaque_dist:
            # Opaque
            new_data.append((r, g, b, 255))
        else:
            # Semi-transparent AA edge
            alpha_norm = (dist - full_transparent_dist) / (full_opaque_dist - full_transparent_dist)
            alpha = int(alpha_norm * 255)
            
            # Uncomposite / Color Recovery
            if alpha > 0:
                alpha_f = alpha / 255.0
                
                # Formula: True = (Obs - BG * (1 - alpha)) / alpha
                rec_r = (r - 255.0) / alpha_f + 255.0
                rec_g = (g - 255.0) / alpha_f + 255.0
                rec_b = (b - 255.0) / alpha_f + 255.0
                
                new_r = int(min(max(rec_r, 0), 255))
                new_g = int(min(max(rec_g, 0), 255))
                new_b = int(min(max(rec_b, 0), 255))
                
                new_data.append((new_r, new_g, new_b, alpha))
            else:
                new_data.append((r, g, b, 0))

    img_hd.putdata(new_data)
    
    # 3. Downscale back to original
    # 4x downscaling with Lanczos provides the smoothest possible edges
    img_final = img_hd.resize((img.width, img.height), Image.Resampling.LANCZOS)
    
    # 4. Auto Crop
    bbox = img_final.getbbox()
    if bbox:
        img_final = img_final.crop(bbox)
        
    img_final.save(output_path, "PNG")
    print(f"Saved Ultra Supersampled (4x) logo to {output_path}")

if __name__ == "__main__":
    input_file = "C:/Users/Usuário/.gemini/antigravity/brain/283f5017-6e88-4efa-929f-849be2018a52/uploaded_image_1766612518431.png"
    output_file = "c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data/frontend/public/logo-ai.png"
    try:
        remove_background_ssaa_ultra(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
