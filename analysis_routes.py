from flask import Blueprint, jsonify, request
from src.services.opportunity_analysis import OpportunityAnalysisService
from src.models.data_models import db, BusinessOpportunity
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
analysis_bp = Blueprint('analysis', __name__)

# Instanciar serviço de análise
analysis_service = OpportunityAnalysisService()

@analysis_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde da API de análise"""
    return jsonify({
        'status': 'healthy',
        'service': 'Opportunity Analysis Service',
        'version': '1.0.0'
    })

@analysis_bp.route('/analyze/<region>', methods=['POST'])
def analyze_region(region):
    """Analisa oportunidades para uma região específica"""
    try:
        logger.info(f"Iniciando análise para região: {region}")
        
        # Executar análise
        result = analysis_service.analyze_region_opportunities(region)
        
        if result.get('status') == 'success':
            # Salvar oportunidades no banco de dados
            saved_count = 0
            for opportunity in result.get('all_opportunities', []):
                try:
                    # Verificar se já existe uma oportunidade similar
                    existing = BusinessOpportunity.query.filter_by(
                        region=region,
                        business_type=opportunity['business_type']
                    ).first()
                    
                    if existing:
                        # Atualizar existente
                        existing.opportunity_score = opportunity['opportunity_score']
                        existing.competition_level = opportunity['competition_analysis']['competition_level']
                        existing.estimated_demand = opportunity['demand_analysis']['estimated_monthly_customers']
                        existing.set_analysis_data(opportunity)
                    else:
                        # Criar nova oportunidade
                        new_opportunity = BusinessOpportunity(
                            region=region,
                            business_type=opportunity['business_type'],
                            opportunity_score=opportunity['opportunity_score'],
                            population_density=result['region_summary']['density'],
                            competition_level=opportunity['competition_analysis']['competition_level'],
                            estimated_demand=opportunity['demand_analysis']['estimated_monthly_customers'],
                            latitude=-23.5505,  # Coordenadas padrão (São Paulo)
                            longitude=-46.6333
                        )
                        new_opportunity.set_analysis_data(opportunity)
                        db.session.add(new_opportunity)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao salvar oportunidade {opportunity['business_type']}: {str(e)}")
                    continue
            
            # Commit das mudanças
            try:
                db.session.commit()
                logger.info(f"Salvou {saved_count} oportunidades no banco de dados")
            except Exception as e:
                logger.error(f"Erro ao fazer commit: {str(e)}")
                db.session.rollback()
        
        return jsonify({
            'success': result.get('status') == 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na análise da região {region}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Retorna oportunidades analisadas com filtros"""
    try:
        # Parâmetros de filtro
        region = request.args.get('region')
        business_type = request.args.get('business_type')
        min_score = float(request.args.get('min_score', 0))
        max_score = float(request.args.get('max_score', 100))
        competition_level = request.args.get('competition_level')
        limit = int(request.args.get('limit', 50))
        
        # Construir query
        query = BusinessOpportunity.query
        
        if region:
            query = query.filter(BusinessOpportunity.region.ilike(f'%{region}%'))
        
        if business_type:
            query = query.filter(BusinessOpportunity.business_type.ilike(f'%{business_type}%'))
        
        if min_score > 0:
            query = query.filter(BusinessOpportunity.opportunity_score >= min_score)
        
        if max_score < 100:
            query = query.filter(BusinessOpportunity.opportunity_score <= max_score)
        
        if competition_level:
            query = query.filter(BusinessOpportunity.competition_level == competition_level)
        
        # Ordenar por score e aplicar limite
        opportunities = query.order_by(
            BusinessOpportunity.opportunity_score.desc()
        ).limit(limit).all()
        
        # Formatar resposta
        formatted_opportunities = []
        for opp in opportunities:
            analysis_data = opp.get_analysis_data() or {}
            
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
                'created_at': opp.created_at.isoformat(),
                'updated_at': opp.updated_at.isoformat(),
                'recommendation': analysis_data.get('recommendation', ''),
                'density_analysis': analysis_data.get('density_analysis', {}),
                'demand_analysis': analysis_data.get('demand_analysis', {}),
                'competition_analysis': analysis_data.get('competition_analysis', {}),
                'sentiment_analysis': analysis_data.get('sentiment_analysis', {})
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

@analysis_bp.route('/opportunities/top', methods=['GET'])
def get_top_opportunities():
    """Retorna as melhores oportunidades por região"""
    try:
        region = request.args.get('region')
        limit = int(request.args.get('limit', 10))
        
        # Construir query
        query = BusinessOpportunity.query
        
        if region:
            query = query.filter(BusinessOpportunity.region.ilike(f'%{region}%'))
        
        # Buscar top oportunidades
        top_opportunities = query.filter(
            BusinessOpportunity.opportunity_score >= 50
        ).order_by(
            BusinessOpportunity.opportunity_score.desc()
        ).limit(limit).all()
        
        # Agrupar por região
        opportunities_by_region = {}
        for opp in top_opportunities:
            region_key = opp.region
            if region_key not in opportunities_by_region:
                opportunities_by_region[region_key] = []
            
            analysis_data = opp.get_analysis_data() or {}
            opportunities_by_region[region_key].append({
                'business_type': opp.business_type,
                'opportunity_score': opp.opportunity_score,
                'competition_level': opp.competition_level,
                'estimated_demand': opp.estimated_demand,
                'recommendation': analysis_data.get('recommendation', '')
            })
        
        return jsonify({
            'success': True,
            'total_regions': len(opportunities_by_region),
            'opportunities_by_region': opportunities_by_region
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar top oportunidades: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/analysis/summary', methods=['GET'])
def get_analysis_summary():
    """Retorna resumo das análises realizadas"""
    try:
        # Estatísticas gerais
        total_opportunities = BusinessOpportunity.query.count()
        
        # Oportunidades por nível de score
        excellent = BusinessOpportunity.query.filter(
            BusinessOpportunity.opportunity_score >= 80
        ).count()
        
        good = BusinessOpportunity.query.filter(
            BusinessOpportunity.opportunity_score >= 65,
            BusinessOpportunity.opportunity_score < 80
        ).count()
        
        moderate = BusinessOpportunity.query.filter(
            BusinessOpportunity.opportunity_score >= 50,
            BusinessOpportunity.opportunity_score < 65
        ).count()
        
        low = BusinessOpportunity.query.filter(
            BusinessOpportunity.opportunity_score < 50
        ).count()
        
        # Oportunidades por tipo de negócio
        business_type_stats = db.session.query(
            BusinessOpportunity.business_type,
            db.func.count(BusinessOpportunity.id).label('count'),
            db.func.avg(BusinessOpportunity.opportunity_score).label('avg_score')
        ).group_by(BusinessOpportunity.business_type).all()
        
        # Oportunidades por região
        region_stats = db.session.query(
            BusinessOpportunity.region,
            db.func.count(BusinessOpportunity.id).label('count'),
            db.func.avg(BusinessOpportunity.opportunity_score).label('avg_score')
        ).group_by(BusinessOpportunity.region).all()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_opportunities': total_opportunities,
                'score_distribution': {
                    'excellent': excellent,
                    'good': good,
                    'moderate': moderate,
                    'low': low
                },
                'business_type_stats': [
                    {
                        'business_type': stat[0],
                        'count': stat[1],
                        'avg_score': round(float(stat[2]), 1) if stat[2] else 0
                    }
                    for stat in business_type_stats
                ],
                'region_stats': [
                    {
                        'region': stat[0],
                        'count': stat[1],
                        'avg_score': round(float(stat[2]), 1) if stat[2] else 0
                    }
                    for stat in region_stats
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo de análises: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis_bp.route('/business-types', methods=['GET'])
def get_business_types():
    """Retorna lista de tipos de negócio analisados"""
    try:
        return jsonify({
            'success': True,
            'business_types': analysis_service.business_categories,
            'population_thresholds': analysis_service.population_thresholds
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de negócio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

