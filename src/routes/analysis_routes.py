from flask import Blueprint, jsonify, request
# --- IMPORTS CORRIGIDOS ---
# Usamos '..' para subir um nível (de 'routes' para 'src') e depois encontrar as outras pastas.
from ..services.opportunity_analysis import OpportunityAnalysisService
from ..models.data_models import db, BusinessOpportunity
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

# --- ROTA DE ANÁLISE CORRIGIDA PARA CORRESPONDER AO FRONT-END ---
# A rota agora aceita a região diretamente no URL, como o front-end está a enviar.
@analysis_bp.route('/analyze/<region>', methods=['POST'])
def analyze_region(region):
    """Analisa oportunidades para uma região específica"""
    try:
        logger.info(f"Iniciando análise para região: {region}")
        
        # Executar análise
        result = analysis_service.analyze_region_opportunities(region)
        
        if result.get('status') == 'success':
            # Salvar oportunidades no banco de dados (lógica existente)
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
        
        # Construir query
        query = BusinessOpportunity.query
        
        if region:
            query = query.filter(BusinessOpportunity.region.ilike(f'%{region}%'))
        
        if business_type:
            query = query.filter(BusinessOpportunity.business_type.ilike(f'%{business_type}%'))
        
        if min_score > 0:
            query = query.filter(BusinessOpportunity.opportunity_score >= min_score)
        
        # Ordenar por score e aplicar limite
        opportunities = query.order_by(
            BusinessOpportunity.opportunity_score.desc()
        ).limit(50).all()
        
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
                'demand_analysis': analysis_data.get('demand_analysis', {}),
                'competition_analysis': analysis_data.get('competition_analysis', {}),
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

# Outras rotas (top, summary, business-types) podem ser mantidas como estão.
