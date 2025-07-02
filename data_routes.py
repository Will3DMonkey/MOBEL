from flask import Blueprint, jsonify, request
from src.models.data_models import db, DataSource, CollectedData, BusinessOpportunity, CollectionLog
from src.services.data_collector import DataCollectorService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
data_bp = Blueprint('data', __name__)

# Instanciar serviço de coleta
collector_service = DataCollectorService()

@data_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'Mapa de Oportunidades - Data Collector',
        'version': '1.0.0'
    })

@data_bp.route('/sources', methods=['GET'])
def get_data_sources():
    """Retorna lista de fontes de dados disponíveis"""
    try:
        sources = DataSource.query.all()
        sources_data = []
        
        for source in sources:
            source_data = {
                'id': source.id,
                'name': source.name,
                'type': source.type,
                'description': source.description,
                'is_active': source.is_active,
                'last_updated': source.last_updated.isoformat() if source.last_updated else None,
                'total_collections': len(source.collected_data)
            }
            sources_data.append(source_data)
        
        return jsonify({
            'success': True,
            'total_sources': len(sources_data),
            'sources': sources_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar fontes de dados: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/collect/ibge', methods=['POST'])
def collect_ibge_data():
    """Coleta dados demográficos do IBGE"""
    try:
        data = request.get_json() or {}
        region_code = data.get('region_code')
        
        # Executar coleta
        result = collector_service.collect_ibge_demographic_data(region_code)
        
        # Salvar dados
        saved = collector_service.save_collected_data(result, 'IBGE Demographics', 'demographic')
        
        return jsonify({
            'success': saved,
            'message': 'Dados do IBGE coletados com sucesso' if saved else 'Erro ao salvar dados',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta IBGE: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/collect/business', methods=['POST'])
def collect_business_data():
    """Coleta dados de empresas (simulação CNPJ)"""
    try:
        data = request.get_json() or {}
        city = data.get('city', 'São Paulo')
        
        # Executar coleta
        result = collector_service.collect_cnpj_business_data(city)
        
        # Salvar dados
        saved = collector_service.save_collected_data(result, 'CNPJ Business Data', 'commercial')
        
        return jsonify({
            'success': saved,
            'message': 'Dados de empresas coletados com sucesso' if saved else 'Erro ao salvar dados',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta de empresas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/collect/social', methods=['POST'])
def collect_social_data():
    """Coleta dados de redes sociais (simulação)"""
    try:
        data = request.get_json() or {}
        region = data.get('region', 'São Paulo')
        
        # Executar coleta
        result = collector_service.collect_social_media_sentiment(region)
        
        # Salvar dados
        saved = collector_service.save_collected_data(result, 'Social Media Sentiment', 'social')
        
        return jsonify({
            'success': saved,
            'message': 'Dados de redes sociais coletados com sucesso' if saved else 'Erro ao salvar dados',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta de redes sociais: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/collect/rental', methods=['POST'])
def collect_rental_data():
    """Coleta dados do mercado imobiliário (simulação)"""
    try:
        data = request.get_json() or {}
        city = data.get('city', 'São Paulo')
        
        # Executar coleta
        result = collector_service.collect_rental_market_data(city)
        
        # Salvar dados
        saved = collector_service.save_collected_data(result, 'Rental Market Data', 'real_estate')
        
        return jsonify({
            'success': saved,
            'message': 'Dados imobiliários coletados com sucesso' if saved else 'Erro ao salvar dados',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta imobiliária: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/collect/all', methods=['POST'])
def collect_all_data():
    """Executa coleta completa de todas as fontes"""
    try:
        # Executar coleta completa
        result = collector_service.run_full_collection()
        
        return jsonify({
            'success': True,
            'message': 'Coleta completa executada',
            'summary': result
        })
        
    except Exception as e:
        logger.error(f"Erro na coleta completa: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/data', methods=['GET'])
def get_collected_data():
    """Retorna dados coletados com filtros opcionais"""
    try:
        # Parâmetros de filtro
        data_type = request.args.get('type')
        source_name = request.args.get('source')
        region = request.args.get('region')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Construir query
        query = CollectedData.query
        
        if data_type:
            query = query.filter(CollectedData.data_type == data_type)
        
        if source_name:
            query = query.join(DataSource).filter(DataSource.name.ilike(f'%{source_name}%'))
        
        if region:
            query = query.filter(CollectedData.region.ilike(f'%{region}%'))
        
        # Aplicar paginação
        total = query.count()
        data_records = query.offset(offset).limit(limit).all()
        
        # Formatar resposta
        formatted_data = []
        for record in data_records:
            formatted_record = {
                'id': record.id,
                'source': record.source.name,
                'data_type': record.data_type,
                'region': record.region,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'collection_timestamp': record.collection_timestamp.isoformat(),
                'raw_data': record.get_raw_data(),
                'processed_data': record.get_processed_data()
            }
            formatted_data.append(formatted_record)
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'data': formatted_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados coletados: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Retorna oportunidades de negócio identificadas"""
    try:
        # Parâmetros de filtro
        business_type = request.args.get('business_type')
        region = request.args.get('region')
        min_score = float(request.args.get('min_score', 0))
        limit = int(request.args.get('limit', 50))
        
        # Construir query
        query = BusinessOpportunity.query
        
        if business_type:
            query = query.filter(BusinessOpportunity.business_type.ilike(f'%{business_type}%'))
        
        if region:
            query = query.filter(BusinessOpportunity.region.ilike(f'%{region}%'))
        
        if min_score > 0:
            query = query.filter(BusinessOpportunity.opportunity_score >= min_score)
        
        # Ordenar por score e aplicar limite
        opportunities = query.order_by(BusinessOpportunity.opportunity_score.desc()).limit(limit).all()
        
        # Formatar resposta
        formatted_opportunities = []
        for opp in opportunities:
            formatted_opp = {
                'id': opp.id,
                'region': opp.region,
                'business_type': opp.business_type,
                'opportunity_score': opp.opportunity_score,
                'population_density': opp.population_density,
                'competition_level': opp.competition_level,
                'estimated_demand': opp.estimated_demand,
                'latitude': opp.latitude,
                'longitude': opp.longitude,
                'analysis_data': opp.get_analysis_data(),
                'created_at': opp.created_at.isoformat(),
                'updated_at': opp.updated_at.isoformat()
            }
            formatted_opportunities.append(formatted_opp)
        
        return jsonify({
            'success': True,
            'total': len(formatted_opportunities),
            'opportunities': formatted_opportunities
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar oportunidades: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_bp.route('/stats', methods=['GET'])
def get_collection_stats():
    """Retorna estatísticas de coleta de dados"""
    try:
        # Estatísticas gerais
        total_sources = DataSource.query.count()
        total_collections = CollectedData.query.count()
        total_opportunities = BusinessOpportunity.query.count()
        
        # Estatísticas por tipo de dados
        data_types = db.session.query(
            CollectedData.data_type,
            db.func.count(CollectedData.id).label('count')
        ).group_by(CollectedData.data_type).all()
        
        # Estatísticas por fonte
        source_stats = db.session.query(
            DataSource.name,
            db.func.count(CollectedData.id).label('count')
        ).join(CollectedData).group_by(DataSource.name).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sources': total_sources,
                'total_collections': total_collections,
                'total_opportunities': total_opportunities,
                'data_types': [{'type': dt[0], 'count': dt[1]} for dt in data_types],
                'source_stats': [{'source': ss[0], 'count': ss[1]} for ss in source_stats]
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

