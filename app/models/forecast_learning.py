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
    
    # Calibration tracking
    calibrated = Column(String(1), default='N')  # 'Y' = used in calibration, 'N' = not yet
    calibration_impact = Column(JSONB, nullable=True)  # Details of calibration adjustments made using this log
    
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
    
    # If locked, auto-calibration will skip this multiplier
    locked = Column(String(1), default='N')  # 'Y' = locked, 'N' = unlocked
    
    __table_args__ = (
        # Unique constraint on type + key
        {'schema': None},
    )
    
    def __repr__(self):
        return f"<MultiplierConfig {self.tipo}.{self.chave}={self.valor}>"


class LearningSnapshot(Base):
    """
    Daily snapshot of learning metrics for historical analysis.
    Created at 23:55 each day to capture the day's performance.
    """
    __tablename__ = 'learning_snapshots'
    
    id = Column(Integer, primary_key=True)
    
    # Date of snapshot (unique per day)
    data = Column(Date, nullable=False, unique=True, index=True)
    
    # General metrics
    total_previsoes = Column(Integer, default=0)
    erro_medio = Column(Numeric(6, 2), nullable=True)  # Signed average error
    erro_absoluto_medio = Column(Numeric(6, 2), nullable=True)  # Absolute average error
    acuracia = Column(Numeric(5, 2), nullable=True)  # 100 - abs error
    
    # Revenue comparison
    receita_prevista_total = Column(Numeric(12, 2), default=0)
    receita_real_total = Column(Numeric(12, 2), default=0)
    
    # Factor performance (JSON with error per factor type/key)
    # {"day_of_week": {"seg": 5.2, "ter": -3.1}, "hour": {"11": -15.2, "15": 3.4}}
    fatores_performance = Column(JSONB, default={})
    
    # Calibrations made today
    ajustes_realizados = Column(Integer, default=0)
    detalhes_ajustes = Column(JSONB, default=[])
    
    # Best/Worst performers
    melhor_fator = Column(String(100), nullable=True)  # "hour.15" (lowest error)
    pior_fator = Column(String(100), nullable=True)  # "hour.11" (highest error)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningSnapshot {self.data}: acc={self.acuracia}%>"


class ForecastEvent(Base):
    """
    Special events that affect sales predictions.
    Examples: Black Friday, Natal, Dia das Mães, promoções, etc.
    """
    __tablename__ = 'forecast_events'
    
    id = Column(Integer, primary_key=True)
    
    # Event identification
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Date range
    data_inicio = Column(Date, nullable=False, index=True)
    data_fim = Column(Date, nullable=False)
    
    # Impact multiplier (1.0 = no impact, 1.5 = +50%, 0.8 = -20%)
    multiplicador = Column(Numeric(4, 2), nullable=False, default=1.0)
    
    # Event type for categorization
    tipo = Column(String(50), default='manual')  # 'feriado', 'promocao', 'sazonal', 'manual'
    
    # Recurrence
    recorrente = Column(String(1), default='N')  # 'Y' = yearly, 'N' = one-time
    
    # Status
    ativo = Column(String(1), default='Y')  # 'Y' = active, 'N' = inactive
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ForecastEvent {self.nome}: {self.data_inicio} - {self.data_fim} ({self.multiplicador}x)>"


class AllowedFactor(Base):
    """
    Whitelist for allowed factor keys to prevent garbage data.
    E.g. factor_type='momentum', factor_key='up'
    """
    __tablename__ = 'allowed_factors'
    
    id = Column(Integer, primary_key=True)
    factor_type = Column(String(50), nullable=False, index=True)
    factor_key = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    is_active = Column(String(1), default='Y')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint handled implicitly or can be explicit
    
    def __repr__(self):
        return f"<AllowedFactor {self.factor_type}.{self.factor_key}>"
