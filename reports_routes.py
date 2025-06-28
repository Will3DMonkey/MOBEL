from flask import Blueprint, jsonify, request, send_file
from src.services.report_generation import ReportGenerationService
from src.models.data_models import db, BusinessOpportunity
import os
import tempfile
import subprocess
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
reports_bp = Blueprint('reports', __name__)

# Instanciar serviço de relatórios
report_service = ReportGenerationService()

@reports_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar saúde da API de relatórios"""
    return jsonify({
        'status': 'healthy',
        'service': 'Report Generation Service',
        'version': '1.0.0'
    })

@reports_bp.route('/executive/<region>', methods=['GET'])
def generate_executive_report(region):
    """Gera relatório executivo para uma região"""
    try:
        logger.info(f"Gerando relatório executivo para região: {region}")
        
        # Parâmetros opcionais
        business_type = request.args.get('business_type')
        format_type = request.args.get('format', 'json')  # json, markdown, pdf
        
        # Gerar relatório
        result = report_service.generate_executive_report(region, business_type)
        
        if result.get('status') != 'success':
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erro na geração do relatório')
            }), 400
        
        # Retornar formato solicitado
        if format_type == 'json':
            return jsonify({
                'success': True,
                'report': result['report']
            })
        
        elif format_type == 'markdown':
            markdown_content = report_service.generate_markdown_report(result)
            return jsonify({
                'success': True,
                'markdown': markdown_content
            })
        
        elif format_type == 'pdf':
            # Gerar PDF
            pdf_path = generate_pdf_report(result, 'executive', region)
            if pdf_path:
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=f'relatorio_executivo_{region}_{datetime.now().strftime("%Y%m%d")}.pdf',
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erro na geração do PDF'
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': 'Formato não suportado. Use: json, markdown ou pdf'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao gerar relatório executivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/detailed/<region>/<business_type>', methods=['GET'])
def generate_detailed_report(region, business_type):
    """Gera relatório detalhado para um tipo específico de negócio"""
    try:
        logger.info(f"Gerando relatório detalhado para {business_type} em {region}")
        
        format_type = request.args.get('format', 'json')
        
        # Gerar relatório
        result = report_service.generate_detailed_analysis_report(region, business_type)
        
        if result.get('status') != 'success':
            return jsonify({
                'success': False,
                'error': result.get('error', 'Erro na geração do relatório')
            }), 400
        
        # Retornar formato solicitado
        if format_type == 'json':
            return jsonify({
                'success': True,
                'report': result['report']
            })
        
        elif format_type == 'markdown':
            markdown_content = report_service.generate_markdown_report(result)
            return jsonify({
                'success': True,
                'markdown': markdown_content
            })
        
        elif format_type == 'pdf':
            # Gerar PDF
            pdf_path = generate_pdf_report(result, 'detailed', f"{region}_{business_type}")
            if pdf_path:
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=f'analise_detalhada_{business_type}_{region}_{datetime.now().strftime("%Y%m%d")}.pdf',
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erro na geração do PDF'
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': 'Formato não suportado. Use: json, markdown ou pdf'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao gerar relatório detalhado: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/comparison', methods=['POST'])
def generate_comparison_report():
    """Gera relatório comparativo entre múltiplas regiões"""
    try:
        data = request.get_json()
        regions = data.get('regions', [])
        business_type = data.get('business_type')
        format_type = data.get('format', 'json')
        
        if not regions or len(regions) < 2:
            return jsonify({
                'success': False,
                'error': 'É necessário fornecer pelo menos 2 regiões para comparação'
            }), 400
        
        logger.info(f"Gerando relatório comparativo para regiões: {', '.join(regions)}")
        
        # Gerar relatório comparativo
        comparison_data = []
        
        for region in regions:
            # Buscar oportunidades da região
            query = BusinessOpportunity.query.filter(
                BusinessOpportunity.region.ilike(f'%{region}%')
            )
            
            if business_type:
                query = query.filter(
                    BusinessOpportunity.business_type.ilike(f'%{business_type}%')
                )
            
            opportunities = query.all()
            
            if opportunities:
                avg_score = sum(o.opportunity_score for o in opportunities) / len(opportunities)
                best_opportunity = max(opportunities, key=lambda x: x.opportunity_score)
                
                region_data = {
                    'region': region,
                    'total_opportunities': len(opportunities),
                    'average_score': round(avg_score, 1),
                    'best_opportunity': {
                        'business_type': best_opportunity.business_type,
                        'score': best_opportunity.opportunity_score
                    },
                    'score_distribution': {
                        'excellent': len([o for o in opportunities if o.opportunity_score >= 80]),
                        'good': len([o for o in opportunities if 65 <= o.opportunity_score < 80]),
                        'moderate': len([o for o in opportunities if 50 <= o.opportunity_score < 65]),
                        'low': len([o for o in opportunities if o.opportunity_score < 50])
                    }
                }
            else:
                region_data = {
                    'region': region,
                    'total_opportunities': 0,
                    'average_score': 0,
                    'best_opportunity': None,
                    'score_distribution': {
                        'excellent': 0,
                        'good': 0,
                        'moderate': 0,
                        'low': 0
                    }
                }
            
            comparison_data.append(region_data)
        
        # Ordenar por score médio
        comparison_data.sort(key=lambda x: x['average_score'], reverse=True)
        
        report = {
            'metadata': {
                'report_type': 'comparison',
                'regions': regions,
                'business_type': business_type,
                'generated_at': datetime.utcnow().isoformat()
            },
            'comparison_data': comparison_data,
            'summary': {
                'best_region': comparison_data[0]['region'] if comparison_data else None,
                'total_regions_analyzed': len(regions),
                'overall_average_score': round(sum(r['average_score'] for r in comparison_data) / len(comparison_data), 1) if comparison_data else 0
            }
        }
        
        if format_type == 'json':
            return jsonify({
                'success': True,
                'report': report
            })
        
        elif format_type == 'markdown':
            markdown_content = generate_comparison_markdown(report)
            return jsonify({
                'success': True,
                'markdown': markdown_content
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Formato não suportado para relatório comparativo'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao gerar relatório comparativo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/templates', methods=['GET'])
def get_report_templates():
    """Lista templates de relatórios disponíveis"""
    try:
        templates = {
            'executive_summary': {
                'name': 'Resumo Executivo',
                'description': 'Visão geral das oportunidades de uma região',
                'parameters': ['region', 'business_type (opcional)'],
                'formats': ['json', 'markdown', 'pdf']
            },
            'detailed_analysis': {
                'name': 'Análise Detalhada',
                'description': 'Análise aprofundada de um tipo específico de negócio',
                'parameters': ['region', 'business_type'],
                'formats': ['json', 'markdown', 'pdf']
            },
            'comparison': {
                'name': 'Comparação de Regiões',
                'description': 'Comparativo entre múltiplas regiões',
                'parameters': ['regions[]', 'business_type (opcional)'],
                'formats': ['json', 'markdown']
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reports_bp.route('/history', methods=['GET'])
def get_report_history():
    """Lista histórico de relatórios gerados"""
    try:
        # Buscar oportunidades recentes como proxy para relatórios
        recent_opportunities = BusinessOpportunity.query.order_by(
            BusinessOpportunity.updated_at.desc()
        ).limit(20).all()
        
        history = []
        regions_processed = set()
        
        for opp in recent_opportunities:
            if opp.region not in regions_processed:
                history.append({
                    'region': opp.region,
                    'last_analysis': opp.updated_at.isoformat(),
                    'opportunities_count': BusinessOpportunity.query.filter_by(region=opp.region).count(),
                    'avg_score': round(
                        sum(o.opportunity_score for o in BusinessOpportunity.query.filter_by(region=opp.region).all()) / 
                        BusinessOpportunity.query.filter_by(region=opp.region).count(), 1
                    )
                })
                regions_processed.add(opp.region)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_pdf_report(report_data: dict, report_type: str, identifier: str) -> str:
    """Gera PDF a partir dos dados do relatório"""
    try:
        # Gerar markdown
        markdown_content = report_service.generate_markdown_report(report_data)
        
        # Criar arquivo temporário para markdown
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
            md_file.write(markdown_content)
            md_path = md_file.name
        
        # Criar arquivo temporário para PDF
        pdf_path = tempfile.mktemp(suffix='.pdf')
        
        # Converter markdown para PDF usando manus-md-to-pdf
        try:
            result = subprocess.run(
                ['manus-md-to-pdf', md_path, pdf_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                # Limpar arquivo markdown temporário
                os.unlink(md_path)
                return pdf_path
            else:
                logger.error(f"Erro na conversão para PDF: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na conversão para PDF")
            return None
        except Exception as e:
            logger.error(f"Erro na execução do manus-md-to-pdf: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Erro na geração do PDF: {str(e)}")
        return None

def generate_comparison_markdown(report: dict) -> str:
    """Gera markdown para relatório comparativo"""
    metadata = report.get('metadata', {})
    comparison_data = report.get('comparison_data', [])
    summary = report.get('summary', {})
    
    markdown = f"""# Relatório Comparativo de Regiões

## Informações Gerais

**Regiões Analisadas:** {', '.join(metadata.get('regions', []))}  
**Tipo de Negócio:** {metadata.get('business_type', 'Todos os tipos')}  
**Data de Geração:** {datetime.fromisoformat(metadata.get('generated_at', '')).strftime('%d/%m/%Y %H:%M') if metadata.get('generated_at') else 'N/A'}

## Resumo Comparativo

**Melhor Região:** {summary.get('best_region', 'N/A')}  
**Total de Regiões:** {summary.get('total_regions_analyzed', 0)}  
**Score Médio Geral:** {summary.get('overall_average_score', 0)} pontos

## Ranking de Regiões

| Posição | Região | Score Médio | Total Oportunidades | Melhor Categoria |
|---------|--------|-------------|---------------------|------------------|
"""
    
    for i, region_data in enumerate(comparison_data, 1):
        best_opp = region_data.get('best_opportunity')
        best_category = best_opp.get('business_type', 'N/A') if best_opp else 'N/A'
        
        markdown += f"| {i} | {region_data.get('region', 'N/A')} | {region_data.get('average_score', 0)} | {region_data.get('total_opportunities', 0)} | {best_category} |\n"
    
    markdown += "\n## Análise Detalhada por Região\n\n"
    
    for region_data in comparison_data:
        region = region_data.get('region', 'N/A')
        distribution = region_data.get('score_distribution', {})
        
        markdown += f"""### {region}

**Score Médio:** {region_data.get('average_score', 0)} pontos  
**Total de Oportunidades:** {region_data.get('total_opportunities', 0)}

**Distribuição por Qualidade:**
- 🟢 Excelentes: {distribution.get('excellent', 0)}
- 🔵 Boas: {distribution.get('good', 0)}
- 🟡 Moderadas: {distribution.get('moderate', 0)}
- 🔴 Baixas: {distribution.get('low', 0)}

"""
        
        best_opp = region_data.get('best_opportunity')
        if best_opp:
            markdown += f"**Melhor Oportunidade:** {best_opp.get('business_type', 'N/A')} (Score: {best_opp.get('score', 0)})\n\n"
    
    markdown += """
---

*Relatório comparativo gerado pelo Sistema de Mapa de Oportunidades por Bairro*
"""
    
    return markdown

