import logging
import datetime
from decimal import Decimal
from sqlalchemy import func, and_
from app.core.database import SessionLocal
from app.models.ml_order import MlOrder
from app.models.system_config import SystemConfig

logger = logging.getLogger(__name__)

class TaxService:
    def __init__(self, db_session=None):
        self.db = db_session if db_session else SessionLocal()

    def calculate_rbt12(self) -> float:
        """
        Calculates RBT12 (Gross Revenue of Last 12 Months).
        Considers 'paid' orders.
        """
        try:
            today = datetime.datetime.now().date()
            # Month range: Last 12 full months + current month so far? 
            # Standard RBT12 is strictly previous 12 months.
            # But for "current" estimate, we usually take last 365 days or look at closed months.
            # Let's use last 365 days rolling for real-time estimation.
            
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=365)
            
            revenue = self.db.query(func.sum(MlOrder.total_amount)).filter(
                and_(
                    MlOrder.date_created >= start_date,
                    MlOrder.status == 'paid'
                )
            ).scalar()
            
            return float(revenue or 0.0)
        except Exception as e:
            logger.error(f"Error calculating RBT12: {e}")
            return 0.0

    def calculate_anexo_i_rate(self, rbt12: float) -> float:
        """
        Calculates effective tax rate for Simples Nacional Anexo I (Commerce).
        Formula: ((RBT12 * AliqNominal) - Ded) / RBT12
        """
        if rbt12 <= 0:
            return 4.0 # Minimum
            
        # Anexo I Tables (2024)
        # Faixa | RBT12 (max) | Aliq Nominal | Dedução
        # 1     | 180,000     | 4.00%        | 0
        # 2     | 360,000     | 7.30%        | 5,940.00
        # 3     | 720,000     | 9.50%        | 13,860.00
        # 4     | 1,800,000   | 10.70%       | 22,500.00
        # 5     | 3,600,000   | 14.30%       | 87,300.00
        # 6     | 4,800,000   | 19.00%       | 378,000.00
        
        ranges = [
            (180000.00,  0.0400, 0.00),
            (360000.00,  0.0730, 5940.00),
            (720000.00,  0.0950, 13860.00),
            (1800000.00, 0.1070, 22500.00),
            (3600000.00, 0.1430, 87300.00),
            (4800000.00, 0.1900, 378000.00),
        ]
        
        rbt12_d = float(rbt12)
        
        # Determine Range
        aliq_nominal = 0.0
        deducao = 0.0
        
        # Check Ranges
        if rbt12_d <= 180000.00:
            return 4.0
            
        found = False
        for limit, aliq, ded in ranges:
            if rbt12_d <= limit:
                aliq_nominal = aliq
                deducao = ded
                found = True
                break
        
        # If above last limit (Faixa 6 or caught by last item)
        if not found:
             # Use max Faixa 6 params if within limits, but technically if > 4.8M it exits Simples.
             # Assuming standard simple logic for now using Faixa 6 parameters even if slightly over.
             aliq_nominal = 0.19
             deducao = 378000.00

        # Effective Rate Formula
        # Rate = (((RBT12 * AliqNominal) - Dedução) / RBT12) * 100
        
        effective_rate = (((rbt12_d * aliq_nominal) - deducao) / rbt12_d) * 100
        return round(effective_rate, 2)

    def update_system_tax_rate(self) -> float:
        """
        Updates 'aliquota_simples' in SystemConfig based on current RBT12.
        Returns the new rate.
        """
        rbt12 = self.calculate_rbt12()
        new_rate = self.calculate_anexo_i_rate(rbt12)
        
        logger.info(f"Updating Tax Rate. RBT12: {rbt12:,.2f} -> Rate: {new_rate}%")
        
        # Update DB
        try:
            config = self.db.query(SystemConfig).filter(
                and_(SystemConfig.group == 'geral', SystemConfig.key == 'aliquota_simples')
            ).first()
            
            if config:
                config.value = str(new_rate)
            else:
                config = SystemConfig(
                    group='geral',
                    key='aliquota_simples',
                    value=str(new_rate),
                    description='Alíquota Simples Nacional (Automática)'
                )
                self.db.add(config)
            
            self.db.commit()
            return new_rate
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update tax rate config: {e}")
            return new_rate # Return calculated anyway
