
import sys
import os
import logging

# Add project root
sys.path.append("c:/Users/Usuário/OneDrive/Documentos/01 - Projetos/projeto-hyper-ai/hyper-data")

from app.jobs.product_sync import sync_product_metrics

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- STARTING FORECAST PRODUCT SYNC ---")
    result = sync_product_metrics()
    print(f"--- SYNC COMPLETE: {result} ---")
