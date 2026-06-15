import re
import unicodedata
import difflib
import logging
import traceback
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
    def extract_critical_tokens(text: str):
        if not text: return set(), set(), set(), set()
        text = text.upper()
        volts = set(f"{v}V" for v in re.findall(r'\b(110|127|220)\s*[Vv]\b', text))
        watts = set(f"{w}W" for w in re.findall(r'\b(\d+)\s*[Ww]\b', text))
        liters = set(f"{l}L" for l in re.findall(r'\b(\d+)\s*[Ll]\b', text))
        colors = set()
        for c in ['PRETO', 'BRANCO', 'VERMELHO', 'AZUL', 'AMARELO', 'VERDE', 'CINZA', 'PRATA', 'INOX']:
            if re.search(rf'\b{c}\b', text): colors.add(c)
        return volts, watts, liters, colors

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
                
            items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id, NfeItem.link_status.in_(['pending', 'suggested'])).all()
            
            summary = {
                "total_items": len(items),
                "suggested_count": 0,
                "ambiguous_count": 0,
                "pending_count": 0,
                "suggestions": []
            }
            
            # Pre-load ads and tiny products to avoid N+1 and slow loops
            all_ads = db.query(Ad.id, Ad.sku, Ad.title).all()
            all_tiny = db.query(TinyProduct.id, TinyProduct.sku, TinyProduct.name).all()
            
            from app.models.ad_variation import AdVariation
            all_variations = db.query(
                AdVariation.id, 
                AdVariation.ad_id, 
                AdVariation.sku, 
                AdVariation.attribute_combination
            ).all()
            
            ads_with_variations = {v.ad_id for v in all_variations if v.ad_id}
            
            variations_by_ad = {}
            for v in all_variations:
                if v.ad_id not in variations_by_ad:
                    variations_by_ad[v.ad_id] = []
                variations_by_ad[v.ad_id].append(v)
            
            for item in items:
                candidates = NfeLinkerService._generate_candidates(db, nfe, item, all_ads, all_tiny, variations_by_ad, ads_with_variations)
                
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
                
                # Check for ambiguity (only if SKUs are different)
                if len(candidates) > 1:
                    second_candidate = candidates[1]
                    if (top_candidate['score'] - second_candidate['score']) < 8:
                        if top_candidate.get('sku') != second_candidate.get('sku'):
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
                    if top_candidate['confidence'] == 'high':
                        summary["suggested_count"] += 1
                        
                        # Update Item
                        item.linked_sku = top_candidate['sku']
                        item.linked_mlb_id = top_candidate.get('mlb_id')
                        item.linked_variation_id = top_candidate.get('variation_id')
                        item.linked_catalog_product_id = top_candidate.get('catalog_product_id')
                        item.link_status = 'suggested'
                        item.link_confidence = top_candidate['confidence']
                        item.link_method = top_candidate['method']
                        
                        summary["suggestions"].append({
                            "n_item": item.n_item,
                            "description": item.description,
                            "status": "suggested",
                            "suggested_match": top_candidate
                        })
                    else:
                        summary["pending_count"] += 1
                        summary["suggestions"].append({
                            "n_item": item.n_item,
                            "description": item.description,
                            "status": "pending",
                            "reason": "Single candidate but not high confidence",
                            "candidates": candidates[:3]
                        })
            
            db.commit()
            return summary
            
        except Exception as e:
            db.rollback()
            logging.error(f"Error in run_linker: {traceback.format_exc()}")
            raise e
        finally:
            db.close()

    @staticmethod
    def run_backfill(nfe_id: int):
        """
        Reprocessa itens já confirmados para preencher variation_id quando faltante.
        """
        db = SessionLocal()
        try:
            nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
            if not nfe:
                return {"error": "NFe not found"}
                
            items = db.query(NfeItem).filter(
                NfeItem.nfe_id == nfe_id, 
                NfeItem.link_status == 'confirmed',
                NfeItem.linked_mlb_id.isnot(None),
                NfeItem.linked_variation_id.is_(None)
            ).all()
            
            from app.models.ad_variation import AdVariation
            
            summary = {
                "updated_count": 0,
                "conflict_count": 0,
                "skipped_count": 0,
                "logs": []
            }
            
            for item in items:
                vars = db.query(AdVariation).filter(AdVariation.ad_id == item.linked_mlb_id).all()
                if not vars:
                    summary["skipped_count"] += 1
                    continue
                    
                # 1. Tentar match exato por SKU
                exact_sku_matches = [v for v in vars if v.sku and v.sku.strip().upper() == str(item.linked_sku).strip().upper()]
                
                if len(exact_sku_matches) == 1:
                    item.linked_variation_id = exact_sku_matches[0].id
                    summary["updated_count"] += 1
                    summary["logs"].append(f"Item {item.n_item}: Vinculado à variação {item.linked_variation_id} por SKU exato.")
                    continue
                    
                # 2. Heurística de tokens críticos
                i_volts, i_watts, i_liters, i_colors = NfeLinkerService.extract_critical_tokens(item.description)
                i_cprod = item.sku_supplier.upper() if item.sku_supplier else None
                
                candidates = []
                for v in vars:
                    score = 0
                    v_text = ((v.attribute_combination or "") + " " + (v.sku or "")).upper()
                    c_volts, c_watts, c_liters, c_colors = NfeLinkerService.extract_critical_tokens(v_text)
                    
                    matched_any = False
                    if i_volts and i_volts & c_volts: score += 10; matched_any = True
                    elif c_volts: score -= 20
                    
                    if i_watts and i_watts & c_watts: score += 10; matched_any = True
                    elif c_watts: score -= 20
                    
                    if i_liters and i_liters & c_liters: score += 10; matched_any = True
                    elif c_liters: score -= 20
                    
                    if i_colors and i_colors & c_colors: score += 10; matched_any = True
                    elif c_colors: score -= 20
                    
                    if i_cprod and i_cprod in v_text: score += 15; matched_any = True
                    
                    if matched_any and score > 0:
                        candidates.append((score, v))
                
                if candidates:
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    top_score = candidates[0][0]
                    top_matches = [c for c in candidates if c[0] == top_score]
                    
                    if len(top_matches) == 1:
                        item.linked_variation_id = top_matches[0][1].id
                        summary["updated_count"] += 1
                        summary["logs"].append(f"Item {item.n_item}: Vinculado à variação {item.linked_variation_id} por heurística.")
                        continue
                
                # Conflito ou sem match claro
                item.link_status = 'suggested'
                item.link_method = 'backfill_conflict'
                item.link_confidence = 'low'
                summary["conflict_count"] += 1
                summary["logs"].append(f"Item {item.n_item}: Múltiplas variações ou nenhuma clara. Marcado como 'suggested' para revisão.")
            
            db.commit()
            return summary
        except Exception as e:
            db.rollback()
            logging.error(f"Error in run_backfill: {traceback.format_exc()}")
            raise e
        finally:
            db.close()

    @staticmethod
    def _generate_candidates(db: Session, nfe: NfeImport, item: NfeItem, all_ads: list, all_tiny: list, variations_by_ad: dict, ads_with_variations: set):
        candidates = []
        candidate_keys = set() # (sku, mlb_id, variation_id) to avoid duplicates
        
        def add_candidate(sku, mlb_id, variation_id, catalog_product_id, title, variation_name, method, score, confidence, explanation):
            if not sku:
                return # We cannot link without an SKU
                
            key = (sku, mlb_id, variation_id)
            if key in candidate_keys:
                return
            
            existing_idx = next((i for i, c in enumerate(candidates) if c['sku'] == sku and c.get('mlb_id') == mlb_id and c.get('variation_id') == variation_id), -1)
            
            cand = {
                "sku": sku,
                "mlb_id": mlb_id,
                "variation_id": variation_id,
                "catalog_product_id": catalog_product_id,
                "title": title,
                "variation_name": variation_name,
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

        def expand_ad_candidates(ad_obj, method, score, confidence, explanation_prefix):
            if ad_obj.id in ads_with_variations:
                # Add each variation
                for v in variations_by_ad.get(ad_obj.id, []):
                    add_candidate(
                        sku=v.sku,
                        mlb_id=ad_obj.id,
                        variation_id=v.id,
                        catalog_product_id=None,
                        title=ad_obj.title,
                        variation_name=v.attribute_combination,
                        method=method,
                        score=score,
                        confidence=confidence,
                        explanation=f"{explanation_prefix} (Variação: {v.attribute_combination})"
                    )
            else:
                # Add just the parent ad
                add_candidate(
                    sku=ad_obj.sku,
                    mlb_id=ad_obj.id,
                    variation_id=None,
                    catalog_product_id=None,
                    title=ad_obj.title,
                    variation_name=None,
                    method=method,
                    score=score,
                    confidence=confidence,
                    explanation=explanation_prefix
                )
        
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
                    variation_id=history.linked_variation_id,
                    catalog_product_id=history.linked_catalog_product_id,
                    title=None,
                    variation_name=None,
                    method="historical_supplier_code",
                    score=100,
                    confidence="high",
                    explanation=f"Histórico: Fornecedor {nfe.issuer_cnpj} cProd {item.sku_supplier} já vinculado ao SKU {history.linked_sku}."
                )

        # Pre-calculate Critical Tokens for NFE item
        i_volts, i_watts, i_liters, i_colors = NfeLinkerService.extract_critical_tokens(item.description or "")

        # 2. EAN/GTIN Match (Score: 95)
        if item.ean and str(item.ean).strip().upper() not in ["", "SEM GTIN", "NONE"]:
            ads_by_ean = db.query(Ad).filter(Ad.gtin == item.ean).all()
            for ad in ads_by_ean:
                c_volts, c_watts, c_liters, c_colors = NfeLinkerService.extract_critical_tokens((ad.title or "") + " " + (ad.sku or ""))
                
                conflict = False
                if i_volts and c_volts and not (i_volts & c_volts): conflict = True
                if i_liters and c_liters and not (i_liters & c_liters): conflict = True
                if i_colors and c_colors and not (i_colors & c_colors): conflict = True
                
                if conflict:
                    expand_ad_candidates(ad, "ean_match_with_conflict", 50, "low", f"EAN bate, mas voltagem/litragem diverge.")
                else:
                    expand_ad_candidates(ad, "ean_match", 95, "high", f"EAN {item.ean} bate com anúncio {ad.id}")
            
            # Check TinyProduct
            tiny_by_ean = db.query(TinyProduct).filter(
                or_(TinyProduct.sku == item.ean, TinyProduct.sku.like(f"%{item.ean}%"))
            ).all()
            tiny_strict = [t for t in tiny_by_ean if t.sku == item.ean]
            for t in tiny_strict:
                add_candidate(
                    sku=t.sku,
                    mlb_id=None,
                    variation_id=None,
                    catalog_product_id=None,
                    title=t.name,
                    variation_name=None,
                    method="ean_match_tiny",
                    score=95,
                    confidence="high",
                    explanation=f"EAN {item.ean} bate exatamente com Produto Tiny {t.sku}."
                )

        # 3. Regex MLB (Score: 92)
        if item.description:
            mlb_match = re.search(r'(MLB\s?\d+)', item.description, re.IGNORECASE)
            if mlb_match:
                mlb_code = mlb_match.group(1).replace(" ", "").upper()
                ad = db.query(Ad).filter(Ad.id == mlb_code).first()
                if ad:
                    expand_ad_candidates(ad, "regex_mlb", 92, "high", f"Código {mlb_code} extraído da descrição")

        # 4. SKU Supplier Exact Match (Score: 85)
        if item.sku_supplier:
            ads_by_sku = db.query(Ad).filter(Ad.sku == item.sku_supplier).all()
            for ad in ads_by_sku:
                conf = "high" if len(ads_by_sku) == 1 else "medium"
                expand_ad_candidates(ad, "sku_supplier_match", 85, conf, f"Código do fornecedor {item.sku_supplier} bate com nosso SKU")
            
            tiny_by_sku = db.query(TinyProduct).filter(TinyProduct.sku == item.sku_supplier).all()
            for t in tiny_by_sku:
                add_candidate(
                    sku=t.sku,
                    mlb_id=None,
                    variation_id=None,
                    catalog_product_id=None,
                    title=t.name,
                    variation_name=None,
                    method="sku_supplier_match_tiny",
                    score=85,
                    confidence="high" if len(tiny_by_sku) == 1 else "medium",
                    explanation=f"Código do fornecedor {item.sku_supplier} bate com SKU Tiny."
                )

        # 5. Fuzzy Description Match (Score variable <= 85)
        if item.description:
            norm_desc = NfeLinkerService.normalize_text(item.description)
            if norm_desc:
                for ad_id, ad_sku, ad_title in all_ads:
                    if ad_title:
                        norm_title = NfeLinkerService.normalize_text(ad_title)
                        if not norm_title: continue
                        ratio = difflib.SequenceMatcher(None, norm_desc, norm_title).ratio()
                        score = int(ratio * 100)
                        
                        if score >= 75:
                            conf = "medium" if score >= 85 else "low"
                            if ad_id in ads_with_variations:
                                for v in variations_by_ad.get(ad_id, []):
                                    add_candidate(
                                        sku=v.sku,
                                        mlb_id=ad_id,
                                        variation_id=v.id,
                                        catalog_product_id=None,
                                        title=ad_title,
                                        variation_name=v.attribute_combination,
                                        method="fuzzy_description",
                                        score=score,
                                        confidence=conf,
                                        explanation=f"Similaridade de descrição ({score}%): '{ad_title}' (Variação: {v.attribute_combination})"
                                    )
                            else:
                                if ad_sku:
                                    add_candidate(
                                        sku=ad_sku,
                                        mlb_id=ad_id,
                                        variation_id=None,
                                        catalog_product_id=None,
                                        title=ad_title,
                                        variation_name=None,
                                        method="fuzzy_description",
                                        score=score,
                                        confidence=conf,
                                        explanation=f"Similaridade de descrição ({score}%): '{ad_title}'"
                                    )
                            
                for t_id, t_sku, t_name in all_tiny:
                    if t_name and t_sku:
                        norm_name = NfeLinkerService.normalize_text(t_name)
                        if not norm_name: continue
                        ratio = difflib.SequenceMatcher(None, norm_desc, norm_name).ratio()
                        score = int(ratio * 100)
                        
                        if score >= 75:
                            conf = "medium" if score >= 85 else "low"
                            add_candidate(
                                sku=t_sku,
                                mlb_id=None,
                                variation_id=None,
                                catalog_product_id=None,
                                title=t_name,
                                variation_name=None,
                                method="fuzzy_description_tiny",
                                score=score,
                                confidence=conf,
                                explanation=f"Similaridade de descrição Tiny ({score}%): '{t_name}'"
                            )

        # Tie-breaker heuristic
        if len(candidates) > 1 and item.description:
            # (Removido extração duplicada pois agora é feito no topo da função)
            i_cprod = item.sku_supplier.upper() if item.sku_supplier else None
            
            for cand in candidates:
                cand_text = ((cand.get('title') or "") + " " + (cand.get('variation_name') or "") + " " + (cand.get('sku') or "")).upper()
                c_volts, c_watts, c_liters, c_colors = NfeLinkerService.extract_critical_tokens(cand_text)
                
                # Compare Volts
                if i_volts:
                    if i_volts & c_volts: cand['score'] += 10
                    elif c_volts: cand['score'] -= 20
                
                # Compare Watts
                if i_watts:
                    if i_watts & c_watts: cand['score'] += 10
                    elif c_watts: cand['score'] -= 20
                    
                # Compare Liters
                if i_liters:
                    if i_liters & c_liters: cand['score'] += 10
                    elif c_liters: cand['score'] -= 20
                    
                # Compare Colors
                if i_colors:
                    if i_colors & c_colors: cand['score'] += 10
                    elif c_colors: cand['score'] -= 20
                    
                # Compare cProd
                if i_cprod and i_cprod in cand_text:
                    cand['score'] += 15

        return candidates
