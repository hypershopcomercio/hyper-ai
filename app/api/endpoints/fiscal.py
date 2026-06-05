from flask import jsonify, request
from app.api import api_bp
from app.core.database import SessionLocal
from app.models.fiscal import MonthlyTaxConfig, ProductTaxProfile, ProductPurchaseCost
from app.models.ad import Ad
from app.api.endpoints.auth import require_auth
from datetime import datetime

@api_bp.route("/finance/tax-configs", methods=["GET"])
@require_auth
def get_tax_configs():
    db = SessionLocal()
    try:
        configs = db.query(MonthlyTaxConfig).order_by(MonthlyTaxConfig.reference_month.desc()).all()
        result = [
            {
                "id": c.id,
                "reference_month": c.reference_month,
                "full_das_rate": float(c.full_das_rate),
                "das_without_icms_rate": float(c.das_without_icms_rate),
                "notes": c.notes,
                "is_active": c.is_active
            } for c in configs
        ]
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/finance/tax-configs", methods=["POST"])
@require_auth
def create_or_update_tax_config():
    data = request.json
    db = SessionLocal()
    try:
        ref_month = data.get("reference_month")
        if not ref_month:
            return jsonify({"success": False, "error": "reference_month is required"}), 400

        config = db.query(MonthlyTaxConfig).filter(MonthlyTaxConfig.reference_month == ref_month).first()
        
        if not config:
            config = MonthlyTaxConfig(reference_month=ref_month)
            db.add(config)
        
        config.full_das_rate = float(data.get("full_das_rate", 0))
        config.das_without_icms_rate = float(data.get("das_without_icms_rate", 0))
        config.notes = data.get("notes", "")
        config.is_active = data.get("is_active", True)
        config.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(config)
        
        return jsonify({
            "success": True,
            "data": {
                "id": config.id,
                "reference_month": config.reference_month,
                "full_das_rate": float(config.full_das_rate),
                "das_without_icms_rate": float(config.das_without_icms_rate)
            }
        })
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/ads/<ad_id>/fiscal-profile", methods=["GET"])
@require_auth
def get_fiscal_profile(ad_id):
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"success": False, "error": "Ad not found"}), 404

        profile = db.query(ProductTaxProfile).filter(ProductTaxProfile.mlb_id == ad_id).first()
        cost = db.query(ProductPurchaseCost).filter(
            ProductPurchaseCost.mlb_id == ad_id,
            ProductPurchaseCost.is_active == True
        ).first()

        tax_profile_data = None
        if profile:
            tax_profile_data = {
                "sku": profile.sku,
                "product_origin": profile.product_origin,
                "origin_uf": profile.origin_uf,
                "destination_uf_default": profile.destination_uf_default,
                "ncm": profile.ncm,
                "cest": profile.cest,
                "has_st": profile.has_st,
                "has_ipi": profile.has_ipi,
                "has_difal": profile.has_difal,
                "mva_rate": float(profile.mva_rate) if profile.mva_rate is not None else None,
                "ipi_rate": float(profile.ipi_rate) if profile.ipi_rate is not None else None,
                "origin_icms_rate": float(profile.origin_icms_rate) if profile.origin_icms_rate is not None else None,
                "destination_icms_rate": float(profile.destination_icms_rate) if profile.destination_icms_rate is not None else None,
                "notes": profile.notes,
                "is_active": profile.is_active
            }

        purchase_cost_data = None
        if cost:
            purchase_cost_data = {
                "sku": cost.sku,
                "real_cost": float(cost.real_cost),
                "nf_value": float(cost.nf_value) if cost.nf_value is not None else None,
                "freight_cost": float(cost.freight_cost) if cost.freight_cost is not None else 0.0,
                "packaging_cost": float(cost.packaging_cost) if cost.packaging_cost is not None else 0.0,
                "other_costs": float(cost.other_costs) if cost.other_costs is not None else 0.0,
                "supplier_name": cost.supplier_name,
                "nf_number": cost.nf_number,
                "data_source": cost.data_source,
                "is_active": cost.is_active
            }

        return jsonify({
            "success": True,
            "data": {
                "tax_profile": tax_profile_data,
                "purchase_cost": purchase_cost_data
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

@api_bp.route("/ads/<ad_id>/fiscal-profile", methods=["PUT"])
@require_auth
def update_fiscal_profile(ad_id):
    data = request.json
    db = SessionLocal()
    try:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            return jsonify({"success": False, "error": "Ad not found"}), 404

        tax_data = data.get("tax_profile")
        cost_data = data.get("purchase_cost")

        # Upsert ProductTaxProfile
        if tax_data:
            profile = db.query(ProductTaxProfile).filter(ProductTaxProfile.mlb_id == ad_id).first()
            if not profile:
                profile = ProductTaxProfile(mlb_id=ad_id)
                db.add(profile)
            
            profile.sku = tax_data.get("sku")
            profile.product_origin = tax_data.get("product_origin", "nacional")
            profile.origin_uf = tax_data.get("origin_uf")
            profile.destination_uf_default = tax_data.get("destination_uf_default")
            profile.ncm = tax_data.get("ncm")
            profile.cest = tax_data.get("cest")
            profile.has_st = tax_data.get("has_st", False)
            profile.has_ipi = tax_data.get("has_ipi", False)
            profile.has_difal = tax_data.get("has_difal", False)
            profile.mva_rate = float(tax_data.get("mva_rate")) if tax_data.get("mva_rate") is not None else None
            profile.ipi_rate = float(tax_data.get("ipi_rate")) if tax_data.get("ipi_rate") is not None else None
            profile.origin_icms_rate = float(tax_data.get("origin_icms_rate")) if tax_data.get("origin_icms_rate") is not None else None
            profile.destination_icms_rate = float(tax_data.get("destination_icms_rate")) if tax_data.get("destination_icms_rate") is not None else None
            profile.notes = tax_data.get("notes")
            profile.is_active = tax_data.get("is_active", True)
            profile.updated_at = datetime.utcnow()

        # Handle ProductPurchaseCost (Versioning)
        if cost_data:
            real_cost = float(cost_data.get("real_cost", 0))
            nf_value = float(cost_data.get("nf_value")) if cost_data.get("nf_value") is not None else None
            
            nf_percentage = None
            if nf_value is not None and real_cost > 0:
                nf_percentage = (nf_value / real_cost) * 100.0

            # Deactivate current active costs
            active_costs = db.query(ProductPurchaseCost).filter(
                ProductPurchaseCost.mlb_id == ad_id,
                ProductPurchaseCost.is_active == True
            ).all()
            
            for ac in active_costs:
                ac.is_active = False
                ac.effective_until = datetime.utcnow()

            # Create new active cost
            new_cost = ProductPurchaseCost(
                mlb_id=ad_id,
                sku=cost_data.get("sku"),
                real_cost=real_cost,
                nf_value=nf_value,
                nf_percentage=nf_percentage,
                freight_cost=float(cost_data.get("freight_cost", 0)),
                packaging_cost=float(cost_data.get("packaging_cost", 0)),
                other_costs=float(cost_data.get("other_costs", 0)),
                supplier_name=cost_data.get("supplier_name"),
                nf_number=cost_data.get("nf_number"),
                data_source=cost_data.get("data_source", "manual"),
                is_active=True,
                effective_from=datetime.utcnow()
            )
            db.add(new_cost)

        db.commit()
        return jsonify({"success": True, "message": "Fiscal profile updated successfully"})

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
