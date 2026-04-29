"""
patch_sync.py - Populates ml_ads_metrics table from Mercado Livre Ads API.
Runs once (or after deployment) to backfill the last 30 days.
Optimized: fetches all data in ONE API call instead of 30 separate calls.
"""
import sys
import datetime
import time

def main():
    from app.core.database import engine, Base, SessionLocal
    import app.models.ml_ads_metrics  # Register model

    print("Creating ml_ads_metrics table if not exists...")
    Base.metadata.create_all(bind=engine)
    print("Table ready.")

    db = SessionLocal()
    try:
        from app.models.ml_ads_metrics import MlAdsMetric
        from app.services.meli_api import MeliApiService

        meli = MeliApiService(db)

        # Step 1: Get advertiser_id ONCE (avoids 30 extra API calls)
        print("Fetching advertiser_id...")
        advertiser_id = None
        for attempt in range(3):
            try:
                response = meli.request('GET', "/advertising/advertisers", params={"product_id": "PADS"})
                if response.status_code == 200:
                    advertisers = response.json().get("advertisers", [])
                    if advertisers:
                        advertiser_id = advertisers[0].get("advertiser_id")
                        break
                elif response.status_code == 429:
                    wait = 30 * (attempt + 1)
                    print(f"Rate limit hit for advertiser_id. Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"Error fetching advertiser_id: {response.status_code}")
                    break
            except Exception as e:
                print(f"Exception fetching advertiser_id: {e}")
                break

        if not advertiser_id:
            print("ERROR: Could not get advertiser_id. Aborting.")
            return

        print(f"Advertiser ID: {advertiser_id}")

        # Step 2: Fetch ALL ads data for last 30 days in ONE call
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=30)
        d_from = start_date.strftime("%Y-%m-%d")
        d_to = end_date.strftime("%Y-%m-%d")

        print(f"Fetching Ads data from {d_from} to {d_to} in one request...")

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
            print(f"  Fetching page {page} (offset={params['offset']})...")
            
            for attempt in range(3):
                response = meli.request('GET', endpoint, params=params)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    wait = 30 * (attempt + 1)
                    print(f"  Rate limit hit. Waiting {wait}s... (attempt {attempt+1}/3)")
                    time.sleep(wait)
                else:
                    print(f"  Error {response.status_code}: {response.text[:200]}")
                    break
            else:
                print("  Max retries reached. Stopping.")
                break

            if response.status_code != 200:
                break

            data = response.json()
            results = data.get("results", [])
            all_results.extend(results)
            
            paging = data.get("paging", {})
            total = paging.get("total", 0)
            print(f"  Got {len(results)} records. Total so far: {len(all_results)}/{total}")
            
            if len(all_results) >= total or not results:
                break
            
            params["offset"] += len(results)
            if params["offset"] > 2000:
                print("  Reached offset limit of 2000. Stopping.")
                break
            
            time.sleep(1)  # Small delay between pages

        print(f"\nTotal Ads records fetched: {len(all_results)}")

        if not all_results:
            print("No Ads data found for this period.")
            return

        # Step 3: Aggregate totals per day
        # The API returns aggregate data for the whole period, not per day
        # We store as a single row for the period range
        # Group by item (or store total)
        total_cost = sum(float(r.get("metrics", {}).get("cost", 0) or 0) for r in all_results)
        total_revenue = sum(float(r.get("metrics", {}).get("amount", 0) or 0) for r in all_results)
        total_clicks = sum(int(r.get("metrics", {}).get("clicks", 0) or 0) for r in all_results)
        total_impressions = sum(int(r.get("metrics", {}).get("prints", 0) or 0) for r in all_results)

        print(f"Totals: cost=R${total_cost:.2f}, revenue=R${total_revenue:.2f}, clicks={total_clicks}, impressions={total_impressions}")

        # Step 4: Store in DB - one row per day (distribute evenly for now,
        # or store as a single aggregate for today)
        # Better: Store one record covering the period with today's date,
        # but mark as an aggregate. The dashboard will just sum what's in the table.
        
        # Clear existing records in range and insert aggregate
        days_in_range = (end_date - start_date).days + 1
        daily_cost = total_cost / days_in_range
        daily_revenue = total_revenue / days_in_range
        daily_clicks = total_clicks // days_in_range
        daily_impressions = total_impressions // days_in_range

        print(f"Distributing across {days_in_range} days...")
        
        # Clear all existing in period
        deleted = db.query(MlAdsMetric).filter(
            MlAdsMetric.date >= start_date,
            MlAdsMetric.date <= end_date
        ).delete()
        db.commit()
        print(f"Cleared {deleted} old records.")

        # Insert one record per day
        for i in range(days_in_range):
            day = start_date + datetime.timedelta(days=i)
            metric = MlAdsMetric(
                campaign_id="PADS",
                date=day,
                cost=round(daily_cost, 4),
                revenue=round(daily_revenue, 4),
                clicks=daily_clicks,
                impressions=daily_impressions
            )
            db.add(metric)
        
        db.commit()
        print(f"Saved {days_in_range} daily records to ml_ads_metrics.")
        print("Done! Dashboard will now load instantly.")

    except Exception as e:
        import traceback
        print(f"FATAL ERROR: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
