"""
backfill_ads_item_daily.py - Backfill de metricas REAIS de Product Ads por item x dia.

Uso (na VPS, dentro do venv):
    python -m app.scripts.backfill_ads_item_daily            # ultimos 60 dias
    python -m app.scripts.backfill_ads_item_daily 30         # ultimos 30 dias

Faz 1 chamada por dia (date_from == date_to) ao endpoint product_ads/ads/search.
Dias que ja possuem dados na tabela sao PULADOS (rode com --force para reprocessar).
Rate-limit friendly: pausa 2s entre dias, o retry de 429 ja esta no MeliApiService.request.
"""
import sys
import time
import datetime


def main():
    days = 60
    force = "--force" in sys.argv
    for arg in sys.argv[1:]:
        if arg.isdigit():
            days = int(arg)

    from app.core.database import SessionLocal, engine, Base
    import app.models.ml_ads_item_daily  # noqa: F401 - registra o model
    from app.models.ml_ads_item_daily import MlAdsItemDaily
    from app.services.meli_api import MeliApiService

    # Cria a tabela se nao existir (dev local / SQLite). Em producao (MySQL)
    # a tabela deve ser criada manualmente via SQL fornecido — create_all
    # nao altera tabelas existentes, apenas cria se ausente.
    Base.metadata.create_all(bind=engine, tables=[MlAdsItemDaily.__table__])

    db = SessionLocal()
    try:
        meli = MeliApiService(db)
        today = datetime.datetime.now().date()

        total_inserted = 0
        consecutive_empty = 0
        for offset in range(days, -1, -1):  # do mais antigo ao mais recente
            day = today - datetime.timedelta(days=offset)

            if not force:
                existing = db.query(MlAdsItemDaily).filter(MlAdsItemDaily.date == day).count()
                if existing > 0:
                    print(f"{day}: ja tem {existing} registros, pulando (use --force para reprocessar).")
                    continue

            rows = meli.get_ads_performance_daily(day)
            if not rows:
                consecutive_empty += 1
                print(f"{day}: sem dados retornados.")
                # Fail-fast: se NADA foi inserido ainda e 5 dias seguidos vieram
                # vazios, provavelmente e' erro de autorizacao (401), nao ausencia
                # de campanhas. Aborta para nao gastar 60 dias em retries.
                if total_inserted == 0 and consecutive_empty >= 5:
                    print("\nABORTADO: 5 dias seguidos sem dados e nenhum registro inserido.")
                    print("Provavel problema de autorizacao na API de Ads (veja os logs acima).")
                    print("Verifique: 1) header Api-Version esta no codigo (git pull);")
                    print("2) o app no DevCenter do ML tem permissao de Advertising;")
                    print("3) teste manual com curl (fornecido pelo assistente).")
                    return
                time.sleep(2)
                continue
            consecutive_empty = 0

            db.query(MlAdsItemDaily).filter(MlAdsItemDaily.date == day).delete()
            inserted = 0
            day_cost = 0.0
            for r in rows:
                if not r.get("item_id"):
                    continue
                if not (r["cost"] or r["clicks"] or r["prints"] or r["amount"]):
                    continue
                db.add(MlAdsItemDaily(
                    item_id=r["item_id"],
                    date=day,
                    cost=round(r["cost"], 2),
                    revenue=round(r["amount"], 2),
                    clicks=r["clicks"],
                    prints=r["prints"],
                    units_quantity=r.get("units_quantity", 0)
                ))
                inserted += 1
                day_cost += r["cost"]
            db.commit()
            total_inserted += inserted
            print(f"{day}: {inserted} itens, gasto R${day_cost:.2f}")
            time.sleep(2)

        print(f"\nBackfill concluido. {total_inserted} registros inseridos.")

        # Validacao rapida
        from sqlalchemy import func as sqlfunc
        summary = db.query(
            sqlfunc.min(MlAdsItemDaily.date),
            sqlfunc.max(MlAdsItemDaily.date),
            sqlfunc.count(MlAdsItemDaily.id),
            sqlfunc.sum(MlAdsItemDaily.cost)
        ).first()
        print(f"Tabela agora: {summary[2]} linhas, {summary[0]} a {summary[1]}, gasto total R${float(summary[3] or 0):.2f}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
