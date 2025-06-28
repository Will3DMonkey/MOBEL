from src.models.user import db
from datetime import datetime
import json

class DataSource(db.Model):
    """Modelo para armazenar informações sobre fontes de dados"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'public', 'private', 'api'
    url = db.Column(db.String(500))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com dados coletados
    collected_data = db.relationship('CollectedData', backref='source', lazy=True)

class CollectedData(db.Model):
    """Modelo para armazenar dados coletados de diferentes fontes"""
    __tablename__ = 'collected_data'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # 'demographic', 'commercial', 'social', etc.
    region = db.Column(db.String(100))  # bairro, cidade, estado
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    raw_data = db.Column(db.Text)  # JSON string dos dados brutos
    processed_data = db.Column(db.Text)  # JSON string dos dados processados
    collection_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_raw_data(self, data):
        """Converte dados para JSON string"""
        self.raw_data = json.dumps(data, ensure_ascii=False)
    
    def get_raw_data(self):
        """Retorna dados como objeto Python"""
        if self.raw_data:
            return json.loads(self.raw_data)
        return None
    
    def set_processed_data(self, data):
        """Converte dados processados para JSON string"""
        self.processed_data = json.dumps(data, ensure_ascii=False)
    
    def get_processed_data(self):
        """Retorna dados processados como objeto Python"""
        if self.processed_data:
            return json.loads(self.processed_data)
        return None

class BusinessOpportunity(db.Model):
    """Modelo para armazenar oportunidades de negócio identificadas"""
    __tablename__ = 'business_opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)  # 'pet_shop', 'barbershop', etc.
    opportunity_score = db.Column(db.Float)  # Score de 0 a 100
    population_density = db.Column(db.Float)
    competition_level = db.Column(db.String(20))  # 'low', 'medium', 'high'
    estimated_demand = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    analysis_data = db.Column(db.Text)  # JSON com dados da análise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_analysis_data(self, data):
        """Converte dados de análise para JSON string"""
        self.analysis_data = json.dumps(data, ensure_ascii=False)
    
    def get_analysis_data(self):
        """Retorna dados de análise como objeto Python"""
        if self.analysis_data:
            return json.loads(self.analysis_data)
        return None

class CollectionLog(db.Model):
    """Modelo para log de execuções de coleta de dados"""
    __tablename__ = 'collection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'error', 'partial'
    records_collected = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # tempo em segundos
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

