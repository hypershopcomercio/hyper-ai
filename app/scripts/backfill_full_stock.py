"""Populate the Full snapshot and calculate its unit costs.

Run on the VPS from the project virtualenv:
    python3 -m app.scripts.backfill_full_stock

Apply app/scripts/sql/full_tables.sql first (and optionally
full_tariffs_seed.sql). This script never creates or migrates database schema;
the project requires all schema changes to be applied manually.
"""


def main():
    from app.core.database import SessionLocal
    from app.models.full import FullInventory, FullStorageTariff
    from app.services.full_service import FullService

    db = SessionLocal()
    svc = FullService(db=db)
    try:
        n_tariffs = db.query(FullStorageTariff).filter(FullStorageTariff.active == True).count()  # noqa: E712
        if n_tariffs == 0:
            print("WARNING: no active tariffs in full_storage_tariffs.")
            print("Stock can be synchronized, but Full costs require configured tariffs.\n")

        result = svc.sync_and_cost()
        stock = result["stock"]
        cost = result["cost"]
        print(f"Sync: {stock['ads_full']} Full ads, {stock['inventories']} inventory records, "
              f"{stock.get('dimensions_updated', 0)} real dimension records updated.")
        print(f"Full cost written for {cost.get('updated', 0)} SKUs. {cost.get('reason', '')}")

        from sqlalchemy import func
        total = db.query(func.count(FullInventory.id)).scalar() or 0
        available = db.query(func.sum(FullInventory.available_qty)).scalar() or 0
        in_transit = db.query(func.sum(FullInventory.in_transit_qty)).scalar() or 0
        print(f"full_inventory: {total} rows | available {available} | in transit {in_transit}.")
    except Exception:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
