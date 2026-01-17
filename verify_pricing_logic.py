import unittest
from unittest.mock import MagicMock
from datetime import datetime
import sys
import os

# Adicionar o diretório raiz ao path para importar app corretamente
sys.path.append(os.getcwd())

from app.services.pricing_engine import PricingEngine

class TestPricingEngineLogic(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.engine = PricingEngine(self.mock_db)

    def test_calculate_safe_steps_elastic_product(self):
        """
        Testa steps para produto ELASTICO (>1.5).
        Espera-se steps conservadores de 3%.
        """
        # Mock elasticity return
        # calculate_elasticity retorna dict com 'score'
        self.engine.calculate_elasticity = MagicMock(return_value={"score": 2.0, "classification": "Elastic"})

        current_price = 100.0
        target_price = 110.0 # 10% de aumento

        result = self.engine.calculate_safe_price_steps("item_123", current_price, target_price)
        
        steps = result['steps']
        step_pct = result['step_size_pct']

        print(f"\n[ELASTIC] Steps: {len(steps)}, Step Size: {step_pct}%")
        for s in steps:
            print(f"  - {s['price']} (+{s['increase_pct']}%)")
            # Validação: Aumento percentual de cada passo em relação ao ANTERIOR deve ser ~3%
            # Mas o output do método mostra increase_pct acumulado ou do step?
            # A lógica no código é: new_price = price * (1 + step_pct)
        
        self.assertAlmostEqual(step_pct, 3.0, delta=0.1, msg="Produto elástico deve ter steps de 3%")
        self.assertTrue(len(steps) > 1, "Deve ter múltiplos steps para um aumento de 10%")

    def test_calculate_safe_steps_inelastic_product(self):
        """
        Testa steps para produto INELASTICO (<0.8).
        Espera-se steps agressivos de 5%.
        """
        self.engine.calculate_elasticity = MagicMock(return_value={"score": 0.5, "classification": "Inelastic"})

        current_price = 100.0
        target_price = 115.0 

        result = self.engine.calculate_safe_price_steps("item_456", current_price, target_price)
        
        step_pct = result['step_size_pct']
        print(f"\n[INELASTIC] Steps: {len(result['steps'])}, Step Size: {step_pct}%")
        
        self.assertAlmostEqual(step_pct, 5.0, delta=0.1, msg="Produto inelástico deve ter steps de 5%")

    def test_calculate_safe_steps_unitary_product(self):
        """
        Testa steps para produto UNITARIO (0.8 - 1.5).
        Espera-se steps padrão de 4%.
        """
        self.engine.calculate_elasticity = MagicMock(return_value={"score": 1.0, "classification": "Unitary"})

        current_price = 100.0
        target_price = 108.0

        result = self.engine.calculate_safe_price_steps("item_789", current_price, target_price)
        
        step_pct = result['step_size_pct']
        print(f"\n[UNITARY] Steps: {len(result['steps'])}, Step Size: {step_pct}%")
        
        self.assertAlmostEqual(step_pct, 4.0, delta=0.1, msg="Produto unitário deve ter steps de 4%")

if __name__ == '__main__':
    unittest.main()
