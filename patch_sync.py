import sys
import datetime
from app.services.sync_engine import SyncEngine
from app.models.ml_ads_metrics import MlAdsMetric

def sync_ads_metrics(self):
    print("Starting Ads Metrics Sync...")
    try:
        from datetime import timedelta
        end_date = datetime.datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        for i in range(31):
            target_date = start_date + timedelta(days=i)
            print(f"Syncing Ads for {target_date}...")
            
            should_sync = True
            if target_date < end_date - timedelta(days=3):
                count = self.db.query(MlAdsMetric).filter(MlAdsMetric.date == target_date).count()
                if count > 0:
                    should_sync = False
                    
            if not should_sync:
                print(f"Skipping {target_date}, data exists.")
                continue
                
            ads_data = self.meli_service.get_ads_performance(None, target_date, target_date)
            
            if ads_data:
                self.db.query(MlAdsMetric).filter(MlAdsMetric.date == target_date).delete()
                self.db.commit()
                
                for ad_d in ads_data:
                    metric = MlAdsMetric(
                        campaign_id="PADS",
                        date=target_date,
                        cost=ad_d.get("cost", 0),
                        revenue=ad_d.get("amount", 0),
                        clicks=ad_d.get("clicks", 0),
                        impressions=ad_d.get("prints", 0)
                    )
                    self.db.add(metric)
                self.db.commit()
        print("Ads Metrics Sync Completed!")
    except Exception as e:
        print(f"Ads Metrics Sync Failed: {e}")
        self.db.rollback()

if __name__ == "__main__":
    SyncEngine.sync_ads_metrics = sync_ads_metrics
    e = SyncEngine()
    e.sync_ads_metrics()
