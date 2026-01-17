

import re
import logging

# Configure basic logging if not already configured
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdQualityService:
    def __init__(self):
        pass

    def minimize_issues(self, issues):
        return issues[:3] # Limit to top 3 issues to avoid UI clutter



    def analyze(self, ad_data: dict):
        """
        Analyzes Ad data using Strict SOP Rules (Training Mode).
        """
        try:
            title_data = self._analyze_title(ad_data.get('title', ''))
            media_data = self._analyze_media(
                ad_data.get('pictures', []), 
                ad_data.get('video_id'), 
                ad_data.get('short_description'),
                ad_data.get('manual_video_verified', False)
            )
            attr_data = self._analyze_attributes(ad_data.get('attributes', []))

            final_score = title_data['score'] + media_data['score'] + attr_data['score']
            
            health_label = 'Crítico'
            if final_score >= 80:
                health_label = 'Excelente'
            elif final_score >= 50:
                health_label = 'Regular'

            return {
                "score": int(final_score),
                "label": health_label,
                "sections": {
                    "title": title_data,
                    "media": media_data,
                    "attributes": attr_data
                }
            }
        except Exception as e:
            logger.error(f"Error in AdQualityService.analyze: {e}", exc_info=True)
            raise e

    def _analyze_title(self, title: str):
        criteria = []
        max_points = 30 # Balanced with others
        
        if not title:
            title = ""
            
        length = len(title)
        
        # SOP Rule 1: Stop Words (10 pts)
        stop_words = ['de', 'para', 'com', 'e', 'do', 'da', 'em', 'no', 'na', 'por']
        found_stops = [word for word in stop_words if f" {word} " in f" {title.lower()} "]
        
        c1_met = len(found_stops) == 0
        criteria.append({
            "label": f"Sem palavras de parada ({', '.join(found_stops) if found_stops else 'Nenhuma'})",
            "met": c1_met,
            "score": 10 if c1_met else 0,
            "max_score": 10
        })

        # SOP Rule 2: Keyword Density / Length (10 pts)
        # Target: 50-60 chars (High usage of space without spam)
        c2_met = 50 <= length <= 60
        criteria.append({
            "label": "Uso eficiente do espaço (50-60 caracteres)",
            "met": c2_met,
            "score": 10 if c2_met else (5 if 40 <= length < 50 else 0),
            "max_score": 10
        })

        # SOP Rule 3: No All Caps (10 pts)
        is_all_caps = title.isupper() and length > 10
        criteria.append({
            "label": "Caixa Alta controlada",
            "met": not is_all_caps,
            "score": 10 if not is_all_caps else 0,
            "max_score": 10
        })

        total_score = sum(c['score'] for c in criteria)
        return {"score": total_score, "max_score": max_points, "criteria": criteria, "issues": [c['label'] for c in criteria if not c['met']]}

    def _analyze_media(self, pictures: list, video_id: str, short_description: str = None, manual_video_verified: bool = False):
        criteria = []
        max_points = 45 # 30 for photos + 15 for video
        
        qty = len(pictures or [])
        
        # SOP Definitions for each slot (Training Mode)
        sop_slots = [
            ("Foto 1: Capa (Fundo Branco + Produto Centralizado)", 6),
            ("Foto 2: Ambientada (Produto em uso/contexto)", 3),
            ("Foto 3: Quebra de Objeção (Detalhe/Zoom)", 3),
            ("Foto 4: Detalhe Técnico (Foco em acabamento/conexões)", 3),
            ("Foto 5: Benefício Principal (Lifestyle)", 3),
            ("Foto 6: Dimensões/Escala (Com referência de tamanho)", 3),
            ("Foto 7: Embalagem/Unboxing (O que vai na caixa)", 3),
            ("Foto 8: Prova Social ou Variante (Aplicação real)", 3),
            ("Foto 9: Diferencial Competitivo ou Garantia", 3)
        ]

        # Iterate 1-9 to create checklist
        for idx, (label, points) in enumerate(sop_slots):
            slot_num = idx + 1
            is_filled = qty >= slot_num
            
            criteria.append({
                "label": label,
                "met": is_filled,
                "score": points if is_filled else 0,
                "max_score": points,
                "hint": "Adicione foto neste slot para completar o SOP." if not is_filled else None
            })

        # SOP Rule: Video/Clips (15 pts)
        has_video = bool(video_id) or bool(short_description) or manual_video_verified
        criteria.append({
            "label": "Vídeo ou Clips Vinculado (Manual aceito)",
            "met": has_video,
            "score": 15 if has_video else 0,
            "max_score": 15,
            "hint": "Adicione um vídeo no YouTube ou confirme manualmente se houver Clips." if not has_video else None
        })
        
        total_score = sum(c['score'] for c in criteria)
        return {"score": total_score, "max_score": max_points, "criteria": criteria, "issues": []}

    def _analyze_attributes(self, attributes: list):
        criteria = []
        max_points = 25
        
        if not attributes:
            attributes = []

        filled = [a for a in attributes if a.get('value_name')]
        total_count = len(attributes)
        completeness = len(filled) / total_count if total_count > 0 else 0
        
        # SOP Rule 1: Technical Completeness (15 pts)
        criteria.append({
            "label": "Ficha Técnica Completa (>80%)",
            "met": completeness >= 0.8,
            "score": 15 if completeness >= 0.8 else (5 if completeness >= 0.5 else 0),
            "max_score": 15
        })

        # SOP Rule 2: Brand/Model (10 pts)
        attr_ids = [a.get('id') for a in attributes]
        has_brand = 'BRAND' in attr_ids or 'MARCA' in attr_ids
        criteria.append({
            "label": "Marca Identificada",
            "met": has_brand,
            "score": 10 if has_brand else 0,
            "max_score": 10
        })

        total_score = sum(c['score'] for c in criteria)
        return {"score": total_score, "max_score": max_points, "criteria": criteria, "issues": []}
