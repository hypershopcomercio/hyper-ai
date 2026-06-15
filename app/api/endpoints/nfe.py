from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.nfe import NfeImport, NfeItem, NfeReconciliation
from app.services.nfe_parser_service import NfeParserService
from app.schemas.nfe import ParseStatusEnum
from app.api.endpoints.auth import require_auth
import hashlib
from datetime import datetime

@api_bp.route("/nfe/upload", methods=["POST"])
@require_auth
def upload_nfe():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if not file.filename.lower().endswith('.xml'):
        return jsonify({"success": False, "error": "Invalid file type. Only XML is allowed."}), 400

    try:
        xml_bytes = file.read()
        xml_content = xml_bytes.decode('utf-8', errors='ignore')
        xml_sha256 = hashlib.sha256(xml_bytes).hexdigest()
    except Exception as e:
        return jsonify({"success": False, "error": f"Error reading file: {str(e)}"}), 400

    db = SessionLocal()
    try:
        # Duplicity Check by SHA256
        existing_sha = db.query(NfeImport).filter(NfeImport.xml_sha256 == xml_sha256).first()
        if existing_sha:
            return jsonify({
                "success": False, 
                "error": "XML/NF already imported (SHA256 Match)",
                "id": existing_sha.id
            }), 409

        # Parse XML
        parsed = NfeParserService.parse_xml(xml_content)
        
        # If parsing completely failed without access key, abort saving or save as error?
        if parsed.parse_status == ParseStatusEnum.error and not parsed.access_key:
            return jsonify({"success": False, "error": f"Invalid XML or missing access key: {parsed.parse_error}"}), 400

        # Duplicity Check by Access Key (in case of different XML formatting but same NF)
        existing_key = db.query(NfeImport).filter(NfeImport.access_key == parsed.access_key).first()
        if existing_key:
            return jsonify({
                "success": False, 
                "error": f"XML/NF already imported (Access Key {parsed.access_key})",
                "id": existing_key.id
            }), 409

        # Map to SQLAlchemy
        nfe_db = NfeImport(
            access_key=parsed.access_key,
            nfe_number=parsed.metadata.nfe_number,
            series=parsed.metadata.series,
            model=parsed.metadata.model,
            operation_nature=parsed.metadata.operation_nature,
            environment=parsed.metadata.environment,
            protocol_number=parsed.metadata.protocol_number,
            issue_date=parsed.issue_date,
            issuer_cnpj=parsed.issuer.cnpj,
            issuer_name=parsed.issuer.name,
            total_products_value=parsed.totals.products_value,
            total_invoice_value=parsed.totals.invoice_value,
            total_freight=parsed.totals.freight,
            total_insurance=parsed.totals.insurance,
            total_discount=parsed.totals.discount,
            total_other=parsed.totals.other,
            raw_xml=xml_content,
            xml_sha256=xml_sha256,
            parse_status=parsed.parse_status.value,
            parse_error=parsed.parse_error,
            imported_by="system", # TODO: Get from JWT Auth if available
            import_source="manual_upload"
        )
        db.add(nfe_db)
        db.flush() # get ID

        for i, item in enumerate(parsed.items):
            db_item = NfeItem(
                nfe_id=nfe_db.id,
                n_item=item.n_item,
                sku_supplier=item.sku_supplier,
                description=item.description,
                ean=item.ean,
                ncm=item.ncm,
                cest=item.cest,
                cfop=item.cfop,
                cst_csosn=item.cst_csosn,
                unit=item.unit,
                quantity=item.quantity,
                unit_value=item.unit_value,
                product_value=item.product_value,
                unit_trib=item.unit_trib,
                quantity_trib=item.quantity_trib,
                unit_value_trib=item.unit_value_trib,
                freight_allocated=item.allocations.freight,
                insurance_allocated=item.allocations.insurance,
                discount_allocated=item.allocations.discount,
                other_allocated=item.allocations.other,
                ipi_value=item.taxes.get("ipi").value if item.taxes.get("ipi") else 0,
                ipi_rate=item.taxes.get("ipi").rate if item.taxes.get("ipi") else 0,
                icms_value=item.taxes.get("icms").value if item.taxes.get("icms") else 0,
                icms_rate=item.taxes.get("icms").rate if item.taxes.get("icms") else 0,
                icms_base=item.taxes.get("icms").base if item.taxes.get("icms") else 0,
                st_value=item.taxes.get("st").value if item.taxes.get("st") else 0,
                st_rate=item.taxes.get("st").rate if item.taxes.get("st") else 0,
                st_base=item.taxes.get("st").base if item.taxes.get("st") else 0,
                total_item_cost_nf=item.calculated_costs.get("total_item_cost_nf", 0),
                unit_cost_nf=item.calculated_costs.get("unit_cost_nf", 0),
                link_status="pending"
            )
            db.add(db_item)

        db.commit()

        if parsed.parse_status == ParseStatusEnum.error:
            return jsonify({
                "success": False,
                "error": "Saved with parsing errors",
                "id": nfe_db.id,
                "parse_error": parsed.parse_error
            }), 201

        return jsonify({
            "success": True,
            "message": "NFe imported successfully",
            "id": nfe_db.id,
            "access_key": nfe_db.access_key,
            "items_count": len(parsed.items)
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
    finally:
        db.close()


@api_bp.route("/nfe", methods=["GET"])
@require_auth
def list_nfe():
    db = SessionLocal()
    try:
        nfes = db.query(NfeImport).order_by(NfeImport.issue_date.desc()).limit(100).all()
        result = []
        for nfe in nfes:
            total_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe.id).count()
            linked_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe.id, NfeItem.link_status == 'confirmed').count()
            
            result.append({
                "id": nfe.id,
                "access_key": nfe.access_key,
                "nfe_number": nfe.nfe_number,
                "series": nfe.series,
                "issue_date": nfe.issue_date,
                "issuer_name": nfe.issuer_name,
                "issuer_cnpj": nfe.issuer_cnpj,
                "total_invoice_value": float(nfe.total_invoice_value),
                "status": nfe.status,
                "parse_status": nfe.parse_status,
                "items_count": total_items,
                "linked_items": linked_items,
                "created_at": nfe.created_at
            })
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/nfe/<int:nfe_id>", methods=["GET"])
@require_auth
def get_nfe_detail(nfe_id):
    db = SessionLocal()
    try:
        nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
        if not nfe:
            return jsonify({"success": False, "error": "NFe not found"}), 404

        items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id).order_by(NfeItem.n_item).all()
        
        items_list = []
        for item in items:
            items_list.append({
                "id": item.id,
                "n_item": item.n_item,
                "sku_supplier": item.sku_supplier,
                "description": item.description,
                "ean": item.ean,
                "ncm": item.ncm,
                "quantity": float(item.quantity),
                "unit_value": float(item.unit_value),
                "product_value": float(item.product_value),
                "unit_cost_nf": float(item.unit_cost_nf),
                "freight_allocated": float(item.freight_allocated),
                "ipi_value": float(item.ipi_value),
                "st_value": float(item.st_value),
                "icms_value": float(item.icms_value),
                "linked_sku": item.linked_sku,
                "linked_mlb_id": item.linked_mlb_id,
                "link_status": item.link_status,
                "link_confidence": item.link_confidence,
                "link_method": item.link_method
            })

        return jsonify({
            "success": True,
            "data": {
                "id": nfe.id,
                "access_key": nfe.access_key,
                "nfe_number": nfe.nfe_number,
                "issue_date": nfe.issue_date,
                "issuer_name": nfe.issuer_name,
                "issuer_cnpj": nfe.issuer_cnpj,
                "total_invoice_value": float(nfe.total_invoice_value),
                "total_freight": float(nfe.total_freight),
                "status": nfe.status,
                "parse_status": nfe.parse_status,
                "parse_error": nfe.parse_error,
                "items": items_list
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/nfe/<int:nfe_id>/reconciliation", methods=["GET"])
@require_auth
def get_nfe_reconciliation(nfe_id):
    db = SessionLocal()
    try:
        recon = db.query(NfeReconciliation).filter(
            NfeReconciliation.nfe_id == nfe_id,
            NfeReconciliation.is_active == True
        ).first()
        
        if not recon:
            return jsonify({"success": True, "data": None})
            
        return jsonify({
            "success": True,
            "data": {
                "id": recon.id,
                "nfe_id": recon.nfe_id,
                "supplier_cnpj": recon.supplier_cnpj,
                "fiscal_value_xml": float(recon.fiscal_value_xml),
                "financial_value_real": float(recon.financial_value_real),
                "coverage_percent": float(recon.coverage_percent),
                "financial_multiplier": float(recon.financial_multiplier),
                "reconciliation_status": recon.reconciliation_status,
                "source_type": recon.source_type,
                "evidence_reference": recon.evidence_reference,
                "notes": recon.notes,
                "confirmed_by": recon.confirmed_by,
                "confirmed_at": recon.confirmed_at,
                "payment_date": recon.payment_date.isoformat() if recon.payment_date else None,
                "due_date": recon.due_date.isoformat() if recon.due_date else None,
                "financial_document_id": recon.financial_document_id,
                "confidence": recon.confidence
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/nfe/<int:nfe_id>/reconciliation", methods=["POST"])
@require_auth
def create_nfe_reconciliation(nfe_id):
    data = request.json
    if not data or 'financial_value_real' not in data:
        return jsonify({"success": False, "error": "Missing financial_value_real"}), 400
        
    try:
        financial_value_real = float(data.get('financial_value_real'))
    except ValueError:
        return jsonify({"success": False, "error": "Invalid financial_value_real"}), 400
        
    if financial_value_real <= 0:
        return jsonify({"success": False, "error": "Financial value must be greater than zero"}), 400
        
    db = SessionLocal()
    try:
        nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
        if not nfe:
            return jsonify({"success": False, "error": "NFe not found"}), 404
            
        fiscal_value = float(nfe.total_invoice_value)
        if fiscal_value <= 0:
            return jsonify({"success": False, "error": "Cannot reconcile an NFe with 0 fiscal value"}), 400
            
        # Calcula as métricas
        coverage_percent = (fiscal_value / financial_value_real) * 100
        financial_multiplier = financial_value_real / fiscal_value
        
        source_type = data.get('source_type', 'user_input')
        
        # Desativa ativas anteriores
        db.query(NfeReconciliation).filter(
            NfeReconciliation.nfe_id == nfe_id,
            NfeReconciliation.is_active == True
        ).update({"is_active": False})
        
        # Cria a nova ativa
        new_recon = NfeReconciliation(
            nfe_id=nfe_id,
            supplier_cnpj=nfe.issuer_cnpj,
            is_active=True,
            fiscal_value_xml=fiscal_value,
            financial_value_real=financial_value_real,
            coverage_percent=coverage_percent,
            financial_multiplier=financial_multiplier,
            reconciliation_status='confirmed',
            source_type=source_type,
            evidence_reference=data.get('evidence_reference'),
            notes=data.get('notes'),
            confirmed_by="system", # TODO user from JWT
            confirmed_at=datetime.utcnow(),
            financial_document_id=data.get('financial_document_id')
        )
        
        db.add(new_recon)
        db.commit()
        db.refresh(new_recon)
        
        return jsonify({
            "success": True, 
            "message": "Reconciliation saved successfully",
            "id": new_recon.id,
            "financial_multiplier": float(new_recon.financial_multiplier)
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/nfe/<int:nfe_id>/linker/run", methods=["POST"])
@require_auth
def run_nfe_linker(nfe_id):
    from app.services.nfe_linker_service import NfeLinkerService
    try:
        summary = NfeLinkerService.run_linker(nfe_id)
        if "error" in summary:
            return jsonify({"success": False, "error": summary["error"]}), 404
            
        return jsonify({
            "success": True,
            "data": summary
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route("/nfe/<int:nfe_id>/items/<int:item_id>/confirm", methods=["POST"])
@require_auth
def confirm_nfe_item_link(nfe_id, item_id):
    data = request.json
    linked_sku = data.get('linked_sku')
    linked_mlb_id = data.get('linked_mlb_id')
    linked_variation_id = data.get('linked_variation_id')
    linked_catalog_product_id = data.get('linked_catalog_product_id')
    
    if not linked_sku:
        return jsonify({"success": False, "error": "linked_sku is required"}), 400
        
    db = SessionLocal()
    try:
        item = db.query(NfeItem).filter(NfeItem.id == item_id, NfeItem.nfe_id == nfe_id).first()
        if not item:
            return jsonify({"success": False, "error": "Item not found"}), 404
            
        item.linked_sku = linked_sku
        item.linked_mlb_id = linked_mlb_id
        item.linked_variation_id = linked_variation_id
        item.linked_catalog_product_id = linked_catalog_product_id
        item.link_status = 'confirmed'
        item.link_confidence = 'high'
        item.link_method = 'user_confirmed'
        
        # Ensure Nfe status is updated to linked if all items are confirmed
        nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
        total_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id).count()
        confirmed_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id, NfeItem.link_status == 'confirmed').count()
        
        # If this item makes it fully confirmed
        if confirmed_items + 1 == total_items:
            nfe.status = 'linked'
            
        db.commit()
        
        return jsonify({
            "success": True,
            "message": "Item link confirmed"
        })
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/nfe/<int:nfe_id>/items/<int:item_id>/unlink", methods=["POST"])
@require_auth
def unlink_nfe_item(nfe_id, item_id):
    db = SessionLocal()
    try:
        item = db.query(NfeItem).filter(NfeItem.id == item_id, NfeItem.nfe_id == nfe_id).first()
        if not item:
            return jsonify({"success": False, "error": "Item not found"}), 404
            
        item.linked_sku = None
        item.linked_mlb_id = None
        item.linked_variation_id = None
        item.linked_catalog_product_id = None
        item.link_status = 'pending'
        item.link_confidence = None
        item.link_method = 'unlinked_by_user'
        
        # Se a NF estava totalmente vinculada, ela volta para pending_link
        nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
        if nfe and nfe.status == 'linked':
            nfe.status = 'pending_link'
            
        db.commit()
        
        return jsonify({"success": True, "message": "Item unlinked successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route("/nfe/<int:nfe_id>/linker/confirm_batch", methods=["POST"])
@require_auth
def confirm_nfe_batch_link(nfe_id):
    db = SessionLocal()
    try:
        # Confirm only high confidence, suggested items
        items = db.query(NfeItem).filter(
            NfeItem.nfe_id == nfe_id,
            NfeItem.link_status == 'suggested',
            NfeItem.link_confidence == 'high'
        ).all()
        
        count = 0
        for item in items:
            if item.linked_sku:
                item.link_status = 'confirmed'
                item.link_method = 'batch_confirmed'
                count += 1
                
        # Ensure Nfe status is updated to linked if all items are confirmed
        nfe = db.query(NfeImport).filter(NfeImport.id == nfe_id).first()
        total_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id).count()
        confirmed_items = db.query(NfeItem).filter(NfeItem.nfe_id == nfe_id, NfeItem.link_status == 'confirmed').count()
        
        if confirmed_items == total_items:
            nfe.status = 'linked'
            
        db.commit()
        
        return jsonify({
            "success": True,
            "message": f"{count} items confirmed in batch",
            "confirmed_count": count
        })
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@api_bp.route("/nfe/linker/search", methods=["GET"])
@require_auth
def search_linker_candidates():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"success": True, "data": []})
        
    db = SessionLocal()
    try:
        from app.models.ad import Ad
        from app.models.ad_variation import AdVariation
        from sqlalchemy import or_, and_, func
        
        query_words = query.split()
        
        # 1. Busca por texto combinado (Pai + Variação)
        # Assumindo que queremos itens onde TODAS as palavras batem em algum lugar da tupla (Pai, Variação)
        base_query = db.query(Ad, AdVariation).outerjoin(AdVariation, Ad.id == AdVariation.ad_id)
        
        for w in query_words:
            pattern = f"%{w}%"
            combined_text = func.concat(
                func.coalesce(Ad.title, ''), ' ', 
                func.coalesce(Ad.sku, ''), ' ', 
                func.coalesce(AdVariation.sku, ''), ' ', 
                func.coalesce(AdVariation.attribute_combination, '')
            )
            base_query = base_query.filter(combined_text.ilike(pattern))
            
        matched_pairs = base_query.limit(100).all()
        
        # 2. Busca por IDs exatos
        exact_ads = db.query(Ad).filter(or_(Ad.id == query, Ad.gtin == query)).all()
        exact_vars = db.query(AdVariation).filter(or_(AdVariation.id == query, AdVariation.ad_id == query)).all()
        
        ad_ids = {ad.id for ad in exact_ads}
        for v in exact_vars:
            if v.ad_id: ad_ids.add(v.ad_id)
        for ad, var in matched_pairs:
            ad_ids.add(ad.id)
            
        all_ads_involved = db.query(Ad).filter(Ad.id.in_(ad_ids)).all()
        all_variations_involved = db.query(AdVariation).filter(AdVariation.ad_id.in_(ad_ids)).all()
        
        ad_map = {a.id: a for a in all_ads_involved}
        var_by_ad = {}
        for v in all_variations_involved:
            if v.ad_id not in var_by_ad:
                var_by_ad[v.ad_id] = []
            var_by_ad[v.ad_id].append(v)
            
        results = []
        for ad_id, ad in ad_map.items():
            vars_for_ad = var_by_ad.get(ad_id, [])
            if vars_for_ad:
                for v in vars_for_ad:
                    # Aplicar filtro em memória para os resultados exact match não poluírem muito,
                    # mas como limitamos no banco, podemos retornar tudo das ads envolvidas.
                    results.append({
                        "mlb_id": ad.id,
                        "variation_id": v.id,
                        "catalog_product_id": None,
                        "sku": v.sku,
                        "title": ad.title,
                        "variation_name": v.attribute_combination,
                        "price": v.price,
                        "thumbnail": ad.thumbnail,
                        "available_quantity": v.available_quantity
                    })
            else:
                results.append({
                    "mlb_id": ad.id,
                    "variation_id": None,
                    "catalog_product_id": None,
                    "sku": ad.sku,
                    "title": ad.title,
                    "variation_name": None,
                    "price": ad.price,
                    "thumbnail": ad.thumbnail,
                    "available_quantity": ad.available_quantity
                })
                
        # Also could search TinyProduct if needed, but for now ML ads is fine.
        return jsonify({
            "success": True,
            "data": results[:100]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
