"""
patch_sync.py - Populates ml_ads_metrics from ML Ads API.
Uses seller_id from oauth_tokens as advertiser_id (no API call needed).
"""
import datetime
import time


def main():
    from app.core.database import engine, Base, SessionLocal
    import app.models.ml_ads_metrics

    print("Creating ml_ads_metrics table if not exists...")
    Base.metadata.create_all(bind=engine)
    print("Table ready.")

    db = SessionLocal()
    try:
        from app.models.ml_ads_metrics import MlAdsMetric
        from app.models.system_config import SystemConfig
        from app.models.oauth_token import OAuthToken
        from app.services.meli_api import MeliApiService

        meli = MeliApiService(db)

        # Step 1: Get advertiser_id from DB (NO API call)
        # For ML Product Ads, advertiser_id = seller_id
        advertiser_id = None

        # Check cache first
        cached = db.query(SystemConfig).filter_by(key="ml_advertiser_id").first()
        if cached and cached.value:
            advertiser_id = cached.value
            print(f"Cached advertiser_id: {advertiser_id}")
        else:
            # Read seller_id from oauth_tokens (already saved from ML login)
            token = db.query(OAuthToken).filter_by(provider="mercadolivre").first()
            if token and token.seller_id:
                advertiser_id = str(token.seller_id)
                print(f"Using seller_id as advertiser_id: {advertiser_id}")
            elif token and token.user_id:
                advertiser_id = str(token.user_id)
                print(f"Using user_id as advertiser_id: {advertiser_id}")

            if advertiser_id:
                # Cache it permanently
                if cached:
                    cached.value = advertiser_id
                else:
                    db.add(SystemConfig(key="ml_advertiser_id", value=advertiser_id, group="cache"))
                db.commit()
                print(f"Cached advertiser_id: {advertiser_id}")

        if not advertiser_id:
            print("ERROR: No seller_id found in oauth_tokens. Is ML connected?")
            return

        # Step 2: Fetch ads data (ONE call for 30 days)
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=30)
        d_from = start_date.strftime("%Y-%m-%d")
        d_to = end_date.strftime("%Y-%m-%d")

        print(f"Fetching Ads {d_from} to {d_to}...")

        endpoint = f"/advertising/MLB/advertisers/{advertiser_id}/product_ads/ads/search"
        params = {
            "date_from": d_from,
            "date_to": d_to,
            "metrics": "clicks,prints,cost,cpc,acos,roas,amount",
            "limit": 100,
            "offset": 0
        }

        all_results = []
        page = 0
        while True:
            page += 1
            print(f"  Page {page} (offset={params['offset']})...")

            response = None
            for attempt in range(5):
                response = meli.request('GET', endpoint, params=params)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    wait = 60 * (attempt + 1)
                    print(f"  Rate limit. Waiting {wait}s... ({attempt+1}/5)")
                    time.sleep(wait)
                else:
                    print(f"  Error {response.status_code}: {response.text[:200]}")
                    break

            if not response or response.status_code != 200:
                print("  Stopped.")
                break

            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)

            paging = data.get("paging", {})
            total = paging.get("total", 0)
            print(f"  Got {len(results)}. Total: {len(all_results)}/{total}")

            if len(all_results) >= total or not results:
                break
            params["offset"] += len(results)
            if params["offset"] > 2000:
                break
            time.sleep(2)

        print(f"\nTotal records: {len(all_results)}")

        if not all_results:
            print("No Ads data. Table left empty. Dashboard will still load fast (with 0 ads cost).")
            return

        # Step 3: Aggregate and save
        total_cost = sum(float(r.get("metrics", {}).get("cost", 0) or 0) for r in all_results)
        total_revenue = sum(float(r.get("metrics", {}).get("amount", 0) or 0) for r in all_results)
        total_clicks = sum(int(r.get("metrics", {}).get("clicks", 0) or 0) for r in all_results)
        total_impressions = sum(int(r.get("metrics", {}).get("prints", 0) or 0) for r in all_results)

        print(f"Totals: cost=R${total_cost:.2f}, revenue=R${total_revenue:.2f}")

        days = (end_date - start_date).days + 1

        deleted = db.query(MlAdsMetric).filter(
            MlAdsMetric.date >= start_date, MlAdsMetric.date <= end_date
        ).delete()
        db.commit()
        print(f"Cleared {deleted} old records.")

        for i in range(days):
            day = start_date + datetime.timedelta(days=i)
            db.add(MlAdsMetric(
                campaign_id="PADS",
                date=day,
                cost=round(total_cost / days, 4),
                revenue=round(total_revenue / days, 4),
                clicks=total_clicks // days,
                impressions=total_impressions // days
            ))
        db.commit()

        print(f"Saved {days} daily records. Dashboard ready!")

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
