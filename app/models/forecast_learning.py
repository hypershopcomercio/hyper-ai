"""
Hyper Forecast Learning System - Database Models
Models for logging predictions and tracking calibration history
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base


class ForecastLog(Base):
    """
    Logs every prediction made by the Hyper Forecast engine.
    This is the CRITICAL table for the learning system.
    
    Flow:
    1. Engine makes prediction -> saves entry with valor_previsto
    2. Daily job runs at 03:00 -> fills valor_real from actual orders
    3. Weekly job analyzes -> uses erro_percentual to calibrate multipliers
    """
    __tablename__ = 'forecast_logs'
    
    id = Column(Integer, primary_key=True)
    
    # When the prediction was made
    timestamp_previsao = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # The target hour being predicted
    hora_alvo = Column(DateTime, nullable=False, index=True)
    
    # Predicted revenue for that hour
    valor_previsto = Column(Numeric(10, 2), nullable=False)
    
    # Actual revenue (filled by reconciliation job)
    valor_real = Column(Numeric(10, 2), nullable=True)
    
    # Error percentage: ((previsto - real) / real) * 100
    # Positive = overestimated, Negative = underestimated
    erro_percentual = Column(Numeric(5, 2), nullable=True)
    
    # Snapshot of all multipliers/factors used in this prediction
    # Example: {"dia_semana": 1.15, "hora": 0.8, "momentum": 1.05}
    fatores_usados = Column(JSONB, nullable=False, default={})
    
    # Additional context for analysis
    baseline_usado = Column(Numeric(10, 2), nullable=True)  # Base value before multipliers
    modelo_versao = Column(String(50), default='heuristic_v1')  # Model version for tracking
    
    def __repr__(self):
        return f"<ForecastLog {self.id}: {self.hora_alvo} prev={self.valor_previsto} real={self.valor_real}>"


class CalibrationHistory(Base):
    """
    Tracks all automatic calibration adjustments made to multipliers.
    Provides audit trail and allows reverting if needed.
    """
    __tablename__ = 'calibration_history'
    
    id = Column(Integer, primary_key=True)
    
    # When calibration was performed
    data_calibracao = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Type of factor being calibrated
    # 'dia_semana', 'hora', 'periodo_mes', 'feriado', 'momentum'
    tipo_fator = Column(String(50), nullable=False, index=True)
    
    # Specific key within that factor type
    # 'Monday', '14', 'inicio', 'Natal', etc.
    fator_chave = Column(String(100), nullable=False)
    
    # Previous multiplier value
    valor_anterior = Column(Numeric(5, 3), nullable=False)
    
    # New calibrated multiplier value
    valor_novo = Column(Numeric(5, 3), nullable=False)
    
    # Average error that triggered this adjustment
    erro_medio = Column(Numeric(5, 2), nullable=False)
    
    # Number of samples (predictions) used in calculation
    amostras = Column(Integer, nullable=False)
    
    # Direction and magnitude of change
    ajuste_percentual = Column(Numeric(5, 2), nullable=True)  # +2% or -2%
    
    # Notes or reason for calibration
    notas = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<CalibrationHistory {self.tipo_fator}.{self.fator_chave}: {self.valor_anterior} -> {self.valor_novo}>"


class MultiplierConfig(Base):
    """
    Stores current multiplier values that can be auto-updated.
    This replaces hardcoded constants with database-driven values.
    """
    __tablename__ = 'multiplier_config'
    
    id = Column(Integer, primary_key=True)
    
    # Type of multiplier
    tipo = Column(String(50), nullable=False, index=True)
    
    # Specific key
    chave = Column(String(100), nullable=False)
    
    # Current multiplier value
    valor = Column(Numeric(5, 3), nullable=False, default=1.0)
    
    # Confidence level based on sample size (0-100)
    confianca = Column(Integer, default=50)
    
    # Last time this multiplier was updated
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Is this value calibrated from data or still using default?
    calibrado = Column(String(20), default='default')  # 'default', 'manual', 'auto'
    
    __table_args__ = (
        # Unique constraint on type + key
        {'schema': None},
    )
    
    def __repr__(self):
        return f"<MultiplierConfig {self.tipo}.{self.chave}={self.valor}>"
