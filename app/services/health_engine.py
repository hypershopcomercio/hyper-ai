
from app.models.ad import Ad
import re

class HealthEngine:
    """
    Analyzes Ad quality (SEO, completeness, media) and generates specific improvement suggestions.
    Targeting 'Platinum' standard for Mercado Livre.
    """

    def analyze(self, ad: Ad) -> dict:
        issues = []
        score = 100
        
        # 1. Title Analysis
        title_score = 100
        title_issues = []
        
        if not ad.title:
            title_score = 0
            title_issues.append("Título ausente.")
        else:
            title_len = len(ad.title)
            if title_len < 40:
                deduct = 20
                title_score -= deduct
                title_issues.append(f"Título muito curto ({title_len}/60 caracteres). Use mais palavras-chave relevantes.")
            elif title_len > 60:
                # ML limit is 60 usually
                deduct = 10
                title_score -= deduct
                title_issues.append("Título excede 60 caracteres (pode ser cortado em algumas views).")
            
            # Check for generic words
            if re.search(r'\b(promoção|oferta|barato|envio)\b', ad.title, re.IGNORECASE):
                deduct = 15
                title_score -= deduct
                title_issues.append("Evite palavras como 'promoção', 'oferta' ou 'barato' no título. Use isso em imagens ou descrições.")
        
        score -= (100 - title_score) * 0.4 # 40% weight

        # 2. Media/Photos Analysis
        media_score = 100
        media_issues = []
        
        pics = ad.pictures if ad.pictures else []
        pic_count = len(pics)
        
        if pic_count == 0:
            media_score = 0
            media_issues.append("Nenhuma foto disponível. Adicione fotos imediatamente.")
        elif pic_count < 3:
            deduct = 30
            media_score -= deduct
            media_issues.append(f"Poucas fotos ({pic_count}). Recomenda-se pelo menos 5 fotos.")
        elif pic_count < 5:
            deduct = 10
            media_score -= deduct
            media_issues.append("Adicione mais fotos mostrando detalhes e uso do produto.")
            
        # Check resolution (simulation as we might not have actual meta without scraping)
        # We assume first photo is white background
        
        score -= (100 - media_score) * 0.3 # 30% weight

        # 3. Attributes/Specs Analysis
        attr_score = 100
        attr_issues = []
        
        attrs = ad.attributes if ad.attributes else []
        filled_attrs = [a for a in attrs if a.get('value_name')]
        
        # Simple heuristic: meaningful attributes count
        if len(filled_attrs) < 5:
            deduct = 40
            attr_score -= deduct
            attr_issues.append("Ficha técnica incompleta. Preencha mais atributos para melhorar o SEO.")
        elif len(filled_attrs) < 8:
            deduct = 15
            attr_score -= deduct
            attr_issues.append("Complete mais características técnicas do produto.")
        
        # Check for specific critical attributes if possible (Brand, Model, etc)
        has_brand = any(a.get('id') == 'BRAND' for a in filled_attrs)
        if not has_brand:
            attr_score -= 10
            attr_issues.append("Marca (BRAND) não preenchida.")

        score -= (100 - attr_score) * 0.3 # 30% weight

        # Final Rounding
        final_score = max(0, min(100, round(score)))
        
        # Determine Status Label
        status = "excellent"
        if final_score < 50:
            status = "critical"
        elif final_score < 80:
            status = "warning"
        
        return {
            "score": final_score,
            "status": status,
            "label": "Excelente" if final_score >= 80 else "Regular" if final_score >= 50 else "Crítico",
            "sections": {
                "title": {
                    "score": title_score,
                    "issues": title_issues
                },
                "media": {
                    "score": media_score,
                    "issues": media_issues
                },
                "attributes": {
                    "score": attr_score,
                    "issues": attr_issues
                }
            },
            "all_issues": title_issues + media_issues + attr_issues
        }
