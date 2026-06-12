import re
import unicodedata
import difflib
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import SessionLocal
from app.models.nfe import NfeItem, NfeImport
from app.models.ad import Ad
from app.models.tiny_product import TinyProduct

class NfeLinkerService:
    
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        # Uppercase
        text = text.upper()
        # Keep letters, numbers, spaces, and specific punctuation
        text = re.sub(r'[^A-Z0-9\sVWL]', ' ', text)
        # Compact spaces
        text = ' '.join(text.split())
        return text

    @staticmethod
    def run_linker(nfe_id: int):
        """
        Runs the heuristic linker for all pending items in a specific NFe.
        Returns a summary of the operations.
        """
        db = SessionLocal()
        try:
            nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
            if not nfe:
                return {"error": "NFe not found"}
                
            items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id, NfeItem.link_status == 'pending').all()
            
            summary = {
                "total_items": len(items),
                "suggested_count": 0,
                "ambiguous_count": 0,
                "pending_count": 0,
                "suggestions": []
            }
            
            for item in items:
                candidates = NfeLinkerService._generate_candidates(db, nfe, item)
                
                if not candidates:
                    summary["pending_count"] += 1
                    summary["suggestions"].append({
                        "n_item": item.n_item,
                        "description": item.description,
                        "status": "pending",
                        "reason": "No candidates found"
                    })
                    continue
                
                # Sort candidates by score descending
                candidates.sort(key=lambda x: x['score'], reverse=True)
                
                top_candidate = candidates[0]
                is_ambiguous = False
                
                # Check for ambiguity
                if len(candidates) > 1:
                    second_candidate = candidates[1]
                    if (top_candidate['score'] - second_candidate['score']) < 8:
                        is_ambiguous = True
                
                if is_ambiguous:
                    summary["ambiguous_count"] += 1
                    summary["suggestions"].append({
                        "n_item": item.n_item,
                        "description": item.description,
                        "status": "ambiguous",
                        "candidates": candidates[:3] # Return top 3 for UI
                    })
                else:
                    summary["suggested_count"] += 1
                    
                    # Update Item
                    item.linked_sku = top_candidate['sku']
                    item.linked_mlb_id = top_candidate.get('mlb_id')
                    item.link_status = 'suggested'
                    item.link_confidence = top_candidate['confidence']
                    item.link_method = top_candidate['method']
                    
                    summary["suggestions"].append({
                        "n_item": item.n_item,
                        "description": item.description,
                        "status": "suggested",
                        "suggested_match": top_candidate
                    })
            
            db.commit()
            return summary
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def _generate_candidates(db: Session, nfe: NfeImport, item: NfeItem):
        candidates = []
        candidate_keys = set() # (sku, mlb_id) to avoid duplicates
        
        def add_candidate(sku, mlb_id, method, score, confidence, explanation):
            key = (sku, mlb_id)
            if key in candidate_keys:
                return
            
            # Additional validation: check if candidate already exists in the candidates list
            # and only keep the higher score
            existing_idx = next((i for i, c in enumerate(candidates) if c['sku'] == sku and c.get('mlb_id') == mlb_id), -1)
            
            cand = {
                "sku": sku,
                "mlb_id": mlb_id,
                "method": method,
                "score": score,
                "confidence": confidence,
                "explanation": explanation
            }
            
            if existing_idx >= 0:
                if score > candidates[existing_idx]['score']:
                    candidates[existing_idx] = cand
            else:
                candidates.append(cand)
                candidate_keys.add(key)
        
        # 1. Historical Supplier Match (Score: 100)
        if item.sku_supplier:
            history = db.query(NfeItem).join(NfeImport).filter(
                NfeImport.issuer_cnpj == nfe.issuer_cnpj,
                NfeItem.sku_supplier == item.sku_supplier,
                NfeItem.link_status == 'confirmed',
                NfeItem.linked_sku.isnot(None)
            ).first()
            if history:
                add_candidate(
                    sku=history.linked_sku,
                    mlb_id=history.linked_mlb_id,
                    method="historical_supplier_code",
                    score=100,
                    confidence="high",
                    explanation=f"Histórico: Fornecedor {nfe.issuer_cnpj} cProd {item.sku_supplier} já vinculado ao SKU {history.linked_sku}."
                )

        # 2. EAN/GTIN Match (Score: 95)
        if item.ean and item.ean.strip().upper() not in ["", "SEM GTIN"]:
            # Check Ad
            ads_by_ean = db.query(Ad).filter(Ad.gtin == item.ean).all()
            for ad in ads_by_ean:
                add_candidate(
                    sku=ad.sku,
                    mlb_id=ad.id,
                    method="ean_match",
                    score=95,
                    confidence="high",
                    explanation=f"EAN {item.ean} bate exatamente com o anúncio {ad.id}."
                )
            
            # Check TinyProduct
            tiny_by_ean = db.query(TinyProduct).filter(
                or_(TinyProduct.sku == item.ean, TinyProduct.sku.like(f"%{item.ean}%"))
            ).all()
            # Careful with like, better strict:
            tiny_strict = [t for t in tiny_by_ean if t.sku == item.ean]
            for t in tiny_strict:
                add_candidate(
                    sku=t.sku,
                    mlb_id=None,
                    method="ean_match_tiny",
                    score=95,
                    confidence="high",
                    explanation=f"EAN {item.ean} bate exatamente com Produto Tiny {t.sku}."
                )

        # 3. Regex MLB (Score: 92)
        mlb_match = re.search(r'(MLB\s?\d+)', item.description, re.IGNORECASE)
        if mlb_match:
            mlb_code = mlb_match.group(1).replace(" ", "").upper()
            ad = db.query(Ad).filter(Ad.id == mlb_code).first()
            if ad:
                add_candidate(
                    sku=ad.sku,
                    mlb_id=ad.id,
                    method="regex_mlb",
                    score=92,
                    confidence="high",
                    explanation=f"Código {mlb_code} extraído da descrição e encontrado na base."
                )

        # 4. SKU Supplier Exact Match (Score: 85)
        if item.sku_supplier:
            ads_by_sku = db.query(Ad).filter(Ad.sku == item.sku_supplier).all()
            for ad in ads_by_sku:
                add_candidate(
                    sku=ad.sku,
                    mlb_id=ad.id,
                    method="sku_supplier_match",
                    score=85,
                    confidence="high" if len(ads_by_sku) == 1 else "medium",
                    explanation=f"Código do fornecedor {item.sku_supplier} bate com nosso SKU."
                )
            
            tiny_by_sku = db.query(TinyProduct).filter(TinyProduct.sku == item.sku_supplier).all()
            for t in tiny_by_sku:
                add_candidate(
                    sku=t.sku,
                    mlb_id=None,
                    method="sku_supplier_match_tiny",
                    score=85,
                    confidence="high" if len(tiny_by_sku) == 1 else "medium",
                    explanation=f"Código do fornecedor {item.sku_supplier} bate com SKU Tiny."
                )

        # 5. Fuzzy Description Match (Score variable <= 85)
        norm_desc = NfeLinkerService.normalize_text(item.description)
        if norm_desc:
            # We don't want to load ALL products if we already have a 95+ score?
            # But the user asked to generate all candidates and check ambiguity.
            # Loading all strings from DB to do difflib can be slow. We'll do a basic fetch.
            # We fetch distinct Titles and Tiny Names.
            # To optimize, we can limit the fuzzy search if we already have a 100 score.
            # Wait, the rule says "generate candidates". Let's fetch all Ads titles.
            all_ads = db.query(Ad.id, Ad.sku, Ad.title).all()
            for ad_id, ad_sku, ad_title in all_ads:
                if ad_title:
                    norm_title = NfeLinkerService.normalize_text(ad_title)
                    ratio = difflib.SequenceMatcher(None, norm_desc, norm_title).ratio()
                    score = int(ratio * 100)
                    
                    if score >= 75:
                        conf = "medium" if score >= 85 else "low"
                        add_candidate(
                            sku=ad_sku,
                            mlb_id=ad_id,
                            method="fuzzy_description",
                            score=score,
                            confidence=conf,
                            explanation=f"Similaridade de descrição ({score}%): '{ad_title}'"
                        )
                        
            all_tiny = db.query(TinyProduct.id, TinyProduct.sku, TinyProduct.name).all()
            for t_id, t_sku, t_name in all_tiny:
                if t_name:
                    norm_name = NfeLinkerService.normalize_text(t_name)
                    ratio = difflib.SequenceMatcher(None, norm_desc, norm_name).ratio()
                    score = int(ratio * 100)
                    
                    if score >= 75:
                        conf = "medium" if score >= 85 else "low"
                        add_candidate(
                            sku=t_sku,
                            mlb_id=None,
                            method="fuzzy_description_tiny",
                            score=score,
                            confidence=conf,
                            explanation=f"Similaridade de descrição Tiny ({score}%): '{t_name}'"
                        )

        return candidates
