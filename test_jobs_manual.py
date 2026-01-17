from app.jobs.competitor_jobs import run_competitor_metrics_collection, run_impact_analysis
import logging

logging.basicConfig(level=logging.INFO)

print("Testando exec manual dos jobs configurados...")
res_coleta = run_competitor_metrics_collection()
print(f"Resultado Coleta: {res_coleta}")

res_impacto = run_impact_analysis()
print(f"Resultado Impacto: {res_impacto}")
