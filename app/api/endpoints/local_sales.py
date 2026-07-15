"""API for quick physical-store sales and the local price list."""

from collections import Counter, defaultdict
from datetime import datetime
from uuid import uuid4

from flask import jsonify, request

from app.api import api_bp
from app.api.endpoints.auth import require_auth
from app.core.database import SessionLocal
from app.models.ad import Ad
from app.models.fiscal import MonthlyTaxConfig, ProductTaxProfile
from app.models.local_sales import (
    InventoryMovement,
    LocalProductPrice,
    LocalSale,
    LocalSaleItem,
    SalesChannel,
)
from app.models.tiny_product import TinyProduct
from app.models.tiny_stock import TinyStock
from app.services.pricing.resolver import PricingDataResolver


DEFAULT_MARGIN_PERCENT = 10.0


def _money(value):
    return round(float(value or 0), 2)


def _ensure_local_channel(db):
    channel = db.query(SalesChannel).filter(SalesChannel.key == "local").first()
    if not channel:
        channel = SalesChannel(key="local", name="Loja física", channel_type="local", is_active=True)
        db.add(channel)
        db.flush()
    return channel


def _product_maps(db):
    """Return the one local product catalog keyed by SKU.

    Tiny is the catalog and stock source. Ads are optional enrichments used to
    resolve the existing fiscal cost profile.
    """
    products = db.query(TinyProduct).filter(TinyProduct.sku.isnot(None), TinyProduct.sku != "").all()
    ads_by_sku = {}
    for ad in db.query(Ad).filter(Ad.sku.isnot(None), Ad.sku != "").all():
        ads_by_sku.setdefault(ad.sku.strip(), ad)

    stock_by_sku = defaultdict(int)
    for row in db.query(TinyStock).filter(TinyStock.sku.isnot(None), TinyStock.sku != "").all():
        stock_by_sku[row.sku.strip()] += int(row.available if row.available is not None else (row.quantity or 0))

    products_by_sku = {}
    for product in products:
        sku = product.sku.strip()
        # Keep the first matching Tiny catalog entry; duplicate SKUs are
        # catalog-quality problems and must not become duplicate POS lines.
        products_by_sku.setdefault(sku, product)
    return products_by_sku, ads_by_sku, stock_by_sku


def _price_for_product(db, product, ad, saved_price=None, requested_margin=None):
    """Resolve local selling price using existing fiscal data, without ML fees."""
    warnings = []
    cost = 0.0
    tax_rate = 0.0
    fiscal_status = "ready"

    config = db.query(MonthlyTaxConfig).filter(MonthlyTaxConfig.is_active == True).order_by(
        MonthlyTaxConfig.reference_month.desc()
    ).first()
    if not config:
        fiscal_status = "fiscal_pending"
        warnings.append("Cadastre a alíquota mensal para calcular o imposto da venda.")

    profile = None
    if ad:
        profile = db.query(ProductTaxProfile).filter(
            ProductTaxProfile.mlb_id == ad.id,
            ProductTaxProfile.is_active == True,
        ).first()
        try:
            resolved = PricingDataResolver(db).resolve(ad.id)
            resolved_cost = float(resolved.get("calculator_inputs", {}).get("final_product_cost") or 0)
            if resolved_cost > 0:
                cost = resolved_cost
            warnings.extend(resolved.get("warnings") or [])
        except Exception:
            warnings.append("Não foi possível resolver todo o custo fiscal; usando o custo do ERP quando disponível.")

    if cost <= 0:
        cost = float(product.cost or (ad.cost if ad else 0) or 0)

    if config:
        tax_rate = float(config.das_without_icms_rate if profile and profile.has_st else config.full_das_rate)
        if not profile:
            warnings.append("Perfil fiscal do produto não cadastrado; aplicado DAS padrão sem ST.")

    if cost <= 0:
        fiscal_status = "cost_pending"
        warnings.append("Produto sem custo. Informe o custo no Tiny ou concilie a NF-e antes de automatizar o preço.")

    margin = float(requested_margin if requested_margin is not None else (
        saved_price.target_margin_percent if saved_price else DEFAULT_MARGIN_PERCENT
    ))
    margin = max(0.0, min(margin, 95.0))

    denominator = 1 - (margin / 100.0) - (tax_rate / 100.0)
    suggested_price = 0.0
    if cost > 0 and denominator > 0:
        suggested_price = _money(cost / denominator)
    elif denominator <= 0:
        fiscal_status = "invalid_margin"
        warnings.append("Margem e imposto somam 100% ou mais; reduza a margem desejada.")

    selling_price = suggested_price
    if saved_price and saved_price.is_manual_price:
        selling_price = float(saved_price.selling_price)
    elif saved_price and requested_margin is None and saved_price.status == "ready":
        selling_price = float(saved_price.selling_price)

    return {
        "selling_price": _money(selling_price),
        "suggested_price": suggested_price,
        "target_margin_percent": margin,
        "calculated_cost": _money(cost),
        "tax_rate_percent": _money(tax_rate),
        "status": fiscal_status,
        "warnings": list(dict.fromkeys(warnings)),
        "is_manual_price": bool(saved_price and saved_price.is_manual_price),
    }


def _catalog_rows(db, search=None, only_bac=False, requested_margin=None):
    products_by_sku, ads_by_sku, stock_by_sku = _product_maps(db)
    prices_by_sku = {
        p.sku: p for p in db.query(LocalProductPrice).filter(LocalProductPrice.channel_key == "local").all()
    }
    term = (search or "").strip().lower()
    result = []
    for sku, product in products_by_sku.items():
        name = product.name or sku
        searchable = f"{sku} {name}".lower()
        if term and term not in searchable:
            continue
        if only_bac and "bac" not in searchable:
            continue
        ad = ads_by_sku.get(sku)
        pricing = _price_for_product(db, product, ad, prices_by_sku.get(sku), requested_margin)
        result.append({
            "sku": sku,
            "name": name,
            "tiny_product_id": product.id,
            "ad_id": ad.id if ad else None,
            "stock_available": stock_by_sku.get(sku, int(product.stock or 0)),
            "tiny_cost": _money(product.cost),
            "has_fiscal_profile": bool(ad and db.query(ProductTaxProfile.id).filter(
                ProductTaxProfile.mlb_id == ad.id, ProductTaxProfile.is_active == True
            ).first()),
            **pricing,
        })
    return sorted(result, key=lambda item: item["name"].lower())


@api_bp.route("/local/products", methods=["GET"])
@require_auth
def list_local_products():
    db = SessionLocal()
    try:
        margin = request.args.get("margin", type=float)
        rows = _catalog_rows(
            db,
            search=request.args.get("q"),
            only_bac=request.args.get("only_bac", "false").lower() == "true",
            requested_margin=margin,
        )
        return jsonify({"success": True, "data": rows, "count": len(rows)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()


@api_bp.route("/local/pricing/bulk", methods=["POST"])
@require_auth
def apply_local_pricing_bulk():
    data = request.get_json(silent=True) or {}
    margin = float(data.get("target_margin_percent", DEFAULT_MARGIN_PERCENT))
    if margin < 0 or margin >= 100:
        return jsonify({"success": False, "error": "A margem deve estar entre 0% e 99,99%."}), 400
    selected_skus = set(data.get("skus") or [])
    db = SessionLocal()
    try:
        _ensure_local_channel(db)
        rows = _catalog_rows(db, requested_margin=margin)
        updated = 0
        pending = 0
        for row in rows:
            if selected_skus and row["sku"] not in selected_skus:
                continue
            price = db.query(LocalProductPrice).filter(
                LocalProductPrice.sku == row["sku"], LocalProductPrice.channel_key == "local"
            ).first()
            if not price:
                price = LocalProductPrice(sku=row["sku"], channel_key="local", selling_price=0)
                db.add(price)
            price.ad_id = row["ad_id"]
            price.target_margin_percent = margin
            price.calculated_cost = row["calculated_cost"]
            price.tax_rate_percent = row["tax_rate_percent"]
            price.status = row["status"]
            price.is_manual_price = False
            price.selling_price = row["suggested_price"]
            if row["status"] == "ready":
                updated += 1
            else:
                pending += 1
        db.commit()
        return jsonify({"success": True, "updated": updated, "pending": pending, "margin": margin})
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()


@api_bp.route("/local/pricing/<sku>", methods=["PUT"])
@require_auth
def update_local_product_price(sku):
    data = request.get_json(silent=True) or {}
    db = SessionLocal()
    try:
        _ensure_local_channel(db)
        products_by_sku, ads_by_sku, _ = _product_maps(db)
        product = products_by_sku.get(sku)
        if not product:
            return jsonify({"success": False, "error": "Produto não encontrado para este SKU."}), 404
        price = db.query(LocalProductPrice).filter(
            LocalProductPrice.sku == sku, LocalProductPrice.channel_key == "local"
        ).first()
        if not price:
            price = LocalProductPrice(sku=sku, channel_key="local", selling_price=0)
            db.add(price)

        margin = data.get("target_margin_percent")
        pricing = _price_for_product(db, product, ads_by_sku.get(sku), price, margin)
        price.ad_id = ads_by_sku[sku].id if sku in ads_by_sku else None
        price.target_margin_percent = pricing["target_margin_percent"]
        price.calculated_cost = pricing["calculated_cost"]
        price.tax_rate_percent = pricing["tax_rate_percent"]
        price.status = pricing["status"]
        price.notes = data.get("notes")
        if data.get("selling_price") is not None:
            selling_price = float(data["selling_price"])
            if selling_price <= 0:
                return jsonify({"success": False, "error": "O preço local deve ser maior que zero."}), 400
            price.selling_price = _money(selling_price)
            price.is_manual_price = True
        else:
            price.selling_price = pricing["suggested_price"]
            price.is_manual_price = False
        db.commit()
        return jsonify({"success": True, "data": {"sku": sku, **_price_for_product(db, product, ads_by_sku.get(sku), price)}})
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()


@api_bp.route("/local/sales", methods=["GET"])
@require_auth
def list_local_sales():
    db = SessionLocal()
    try:
        limit = min(max(request.args.get("limit", 30, type=int), 1), 100)
        sales = db.query(LocalSale).order_by(LocalSale.completed_at.desc()).limit(limit).all()
        sale_ids = [sale.id for sale in sales]
        items_by_sale = defaultdict(list)
        if sale_ids:
            for item in db.query(LocalSaleItem).filter(LocalSaleItem.sale_id.in_(sale_ids)).all():
                items_by_sale[item.sale_id].append({
                    "sku": item.sku, "product_name": item.product_name, "quantity": item.quantity,
                    "unit_price": _money(item.unit_price), "line_total": _money(item.line_total),
                })
        data = [{
            "id": sale.id, "customer_name": sale.customer_name, "payment_method": sale.payment_method,
            "subtotal": _money(sale.subtotal), "discount_amount": _money(sale.discount_amount),
            "total_amount": _money(sale.total_amount), "status": sale.status,
            "completed_at": sale.completed_at.isoformat() if sale.completed_at else None,
            "items": items_by_sale[sale.id],
        } for sale in sales]
        return jsonify({"success": True, "data": data})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()


@api_bp.route("/local/sales", methods=["POST"])
@require_auth
def create_local_sale():
    data = request.get_json(silent=True) or {}
    raw_items = data.get("items") or []
    if not raw_items:
        return jsonify({"success": False, "error": "Adicione ao menos um produto ao carrinho."}), 400

    requested_quantities = Counter()
    for raw in raw_items:
        sku = str(raw.get("sku") or "").strip()
        quantity = int(raw.get("quantity") or 0)
        if not sku or quantity <= 0:
            return jsonify({"success": False, "error": "Cada item precisa de SKU e quantidade positiva."}), 400
        requested_quantities[sku] += quantity

    db = SessionLocal()
    try:
        _ensure_local_channel(db)
        products_by_sku, ads_by_sku, _ = _product_maps(db)
        locked_stock = {}
        for sku, quantity in requested_quantities.items():
            product = products_by_sku.get(sku)
            if not product:
                return jsonify({"success": False, "error": f"Produto {sku} não encontrado no catálogo Tiny."}), 404
            stock = db.query(TinyStock).filter(TinyStock.sku == sku).with_for_update().first()
            available = int((stock.available if stock and stock.available is not None else (product.stock or 0)))
            if available < quantity:
                return jsonify({"success": False, "error": f"Estoque insuficiente para {product.name or sku}. Disponível: {available}."}), 409
            locked_stock[sku] = (stock, product, available)

        # Materialize missing local-stock rows before processing individual
        # cart lines. This also keeps repeated SKUs in one cart consistent.
        for sku, (stock, product, available) in list(locked_stock.items()):
            if not stock:
                stock = TinyStock(
                    sku=sku, warehouse="Local (Tiny + Hyper)", quantity=available,
                    reserved=0, available=available,
                )
                db.add(stock)
                locked_stock[sku] = (stock, product, available)

        sale = LocalSale(
            id=f"LS-{uuid4().hex[:16].upper()}",
            customer_name=(data.get("customer_name") or "").strip() or None,
            payment_method=(data.get("payment_method") or "").strip() or None,
            notes=(data.get("notes") or "").strip() or None,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db.add(sale)
        db.flush()

        subtotal = 0.0
        for raw in raw_items:
            sku = str(raw["sku"]).strip()
            quantity = int(raw["quantity"])
            stock, product, _ = locked_stock[sku]
            saved_price = db.query(LocalProductPrice).filter(
                LocalProductPrice.sku == sku, LocalProductPrice.channel_key == "local"
            ).first()
            pricing = _price_for_product(db, product, ads_by_sku.get(sku), saved_price)
            unit_price = _money(raw.get("unit_price") if raw.get("unit_price") is not None else pricing["selling_price"])
            if unit_price <= 0:
                return jsonify({"success": False, "error": f"{product.name or sku} não possui preço local válido."}), 400
            line_total = _money(unit_price * quantity)
            subtotal += line_total
            tax_amount = _money(line_total * pricing["tax_rate_percent"] / 100.0)
            db.add(LocalSaleItem(
                sale_id=sale.id, sku=sku, product_name=product.name or sku, tiny_product_id=product.id,
                ad_id=ads_by_sku[sku].id if sku in ads_by_sku else None, quantity=quantity,
                unit_price=unit_price, unit_cost=pricing["calculated_cost"],
                target_margin_percent=pricing["target_margin_percent"], tax_rate_percent=pricing["tax_rate_percent"],
                tax_amount=tax_amount, line_total=line_total,
            ))
            before = int(stock.available if stock and stock.available is not None else (product.stock or 0))
            after = before - quantity
            stock.available = after
            db.add(InventoryMovement(
                id=f"IM-{uuid4().hex[:16].upper()}", sku=sku, movement_type="local_sale",
                quantity_delta=-quantity, quantity_before=before, quantity_after=after,
                reference_type="local_sale", reference_id=sale.id, sync_status="pending",
                notes="Baixa por venda local; aguardando integração de escrita com Tiny.",
            ))

        discount = _money(data.get("discount_amount"))
        if discount < 0 or discount > subtotal:
            return jsonify({"success": False, "error": "Desconto inválido para o total do carrinho."}), 400
        sale.subtotal = _money(subtotal)
        sale.discount_amount = discount
        sale.total_amount = _money(subtotal - discount)
        db.commit()
        return jsonify({"success": True, "data": {"id": sale.id, "total_amount": sale.total_amount, "status": sale.status}}), 201
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()


@api_bp.route("/local/sales/<sale_id>/cancel", methods=["POST"])
@require_auth
def cancel_local_sale(sale_id):
    db = SessionLocal()
    try:
        sale = db.query(LocalSale).filter(LocalSale.id == sale_id).with_for_update().first()
        if not sale:
            return jsonify({"success": False, "error": "Venda não encontrada."}), 404
        if sale.status == "cancelled":
            return jsonify({"success": False, "error": "Esta venda já foi cancelada."}), 409
        items = db.query(LocalSaleItem).filter(LocalSaleItem.sale_id == sale.id).all()
        for item in items:
            stock = db.query(TinyStock).filter(TinyStock.sku == item.sku).with_for_update().first()
            before = int(stock.available if stock and stock.available is not None else 0)
            after = before + item.quantity
            if not stock:
                stock = TinyStock(sku=item.sku, warehouse="Local (Tiny + Hyper)", quantity=0, reserved=0, available=0)
                db.add(stock)
            stock.available = after
            db.add(InventoryMovement(
                id=f"IM-{uuid4().hex[:16].upper()}", sku=item.sku, movement_type="local_sale_cancel",
                quantity_delta=item.quantity, quantity_before=before, quantity_after=after,
                reference_type="local_sale", reference_id=sale.id, sync_status="pending",
                notes="Estorno por cancelamento de venda local; aguardando integração de escrita com Tiny.",
            ))
        sale.status = "cancelled"
        sale.cancelled_at = datetime.utcnow()
        db.commit()
        return jsonify({"success": True, "data": {"id": sale.id, "status": sale.status}})
    except Exception as exc:
        db.rollback()
        return jsonify({"success": False, "error": str(exc)}), 500
    finally:
        db.close()
