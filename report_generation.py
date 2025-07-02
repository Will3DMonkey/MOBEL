import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from src.models.data_models import db, BusinessOpportunity, CollectedData
from src.services.opportunity_analysis import OpportunityAnalysisService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerationService:
    """Serviço responsável pela geração automática de relatórios"""
    
    def __init__(self):
        self.analysis_service = OpportunityAnalysisService()
        self.report_templates = {
            'executive_summary': 'Resumo Executivo',
            'detailed_analysis': 'Análise Detalhada',
            'investment_guide': 'Guia de Investimento',
            'market_comparison': 'Comparação de Mercado'
        }
    
    def generate_executive_report(self, region: str, business_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera relatório executivo para uma região específica
        """
        try:
            logger.info(f"Gerando relatório executivo para {region}")
            
            # Buscar oportunidades da região
            query = BusinessOpportunity.query.filter(
                BusinessOpportunity.region.ilike(f'%{region}%')
            )
            
            if business_type:
                query = query.filter(
                    BusinessOpportunity.business_type.ilike(f'%{business_type}%')
                )
            
            opportunities = query.order_by(
                BusinessOpportunity.opportunity_score.desc()
            ).all()
            
            if not opportunities:
                return {
                    'status': 'no_data',
                    'message': f'Nenhuma oportunidade encontrada para {region}'
                }
            
            # Calcular métricas do relatório
            total_opportunities = len(opportunities)
            excellent_count = len([o for o in opportunities if o.opportunity_score >= 80])
            good_count = len([o for o in opportunities if 65 <= o.opportunity_score < 80])
            moderate_count = len([o for o in opportunities if 50 <= o.opportunity_score < 65])
            low_count = len([o for o in opportunities if o.opportunity_score < 50])
            
            avg_score = sum(o.opportunity_score for o in opportunities) / total_opportunities
            top_opportunities = opportunities[:5]
            
            # Análise por categoria
            categories_analysis = {}
            for opp in opportunities:
                category = opp.business_type
                if category not in categories_analysis:
                    categories_analysis[category] = {
                        'count': 0,
                        'avg_score': 0,
                        'best_score': 0,
                        'total_score': 0
                    }
                
                categories_analysis[category]['count'] += 1
                categories_analysis[category]['total_score'] += opp.opportunity_score
                categories_analysis[category]['best_score'] = max(
                    categories_analysis[category]['best_score'], 
                    opp.opportunity_score
                )
            
            # Calcular médias
            for category in categories_analysis:
                cat_data = categories_analysis[category]
                cat_data['avg_score'] = round(cat_data['total_score'] / cat_data['count'], 1)
            
            # Gerar insights e recomendações
            insights = self._generate_insights(opportunities, region)
            recommendations = self._generate_recommendations(opportunities, region)
            
            # Compilar relatório
            report = {
                'metadata': {
                    'region': region,
                    'business_type': business_type,
                    'generated_at': datetime.utcnow().isoformat(),
                    'report_type': 'executive_summary',
                    'total_opportunities_analyzed': total_opportunities
                },
                'executive_summary': {
                    'region_overview': {
                        'total_opportunities': total_opportunities,
                        'average_score': round(avg_score, 1),
                        'score_distribution': {
                            'excellent': excellent_count,
                            'good': good_count,
                            'moderate': moderate_count,
                            'low': low_count
                        }
                    },
                    'top_opportunities': [
                        {
                            'business_type': opp.business_type,
                            'opportunity_score': opp.opportunity_score,
                            'competition_level': opp.competition_level,
                            'estimated_demand': opp.estimated_demand,
                            'recommendation': self._get_recommendation_by_score(opp.opportunity_score)
                        }
                        for opp in top_opportunities
                    ],
                    'categories_analysis': categories_analysis,
                    'key_insights': insights,
                    'strategic_recommendations': recommendations
                },
                'detailed_analysis': {
                    'market_gaps': self._identify_market_gaps(opportunities),
                    'competition_landscape': self._analyze_competition_landscape(opportunities),
                    'demand_patterns': self._analyze_demand_patterns(opportunities),
                    'risk_assessment': self._assess_risks(opportunities, region)
                },
                'investment_priorities': self._generate_investment_priorities(opportunities),
                'next_steps': self._generate_next_steps(opportunities, region)
            }
            
            logger.info(f"Relatório executivo gerado com sucesso para {region}")
            return {
                'status': 'success',
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório executivo: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_detailed_analysis_report(self, region: str, business_type: str) -> Dict[str, Any]:
        """
        Gera relatório de análise detalhada para um tipo específico de negócio
        """
        try:
            logger.info(f"Gerando análise detalhada para {business_type} em {region}")
            
            # Buscar oportunidade específica
            opportunity = BusinessOpportunity.query.filter(
                BusinessOpportunity.region.ilike(f'%{region}%'),
                BusinessOpportunity.business_type.ilike(f'%{business_type}%')
            ).first()
            
            if not opportunity:
                return {
                    'status': 'no_data',
                    'message': f'Nenhuma análise encontrada para {business_type} em {region}'
                }
            
            # Extrair dados da análise
            analysis_data = opportunity.get_analysis_data() or {}
            density_analysis = analysis_data.get('density_analysis', {})
            demand_analysis = analysis_data.get('demand_analysis', {})
            competition_analysis = analysis_data.get('competition_analysis', {})
            sentiment_analysis = analysis_data.get('sentiment_analysis', {})
            
            # Gerar análise detalhada
            report = {
                'metadata': {
                    'region': region,
                    'business_type': business_type,
                    'generated_at': datetime.utcnow().isoformat(),
                    'report_type': 'detailed_analysis',
                    'opportunity_score': opportunity.opportunity_score
                },
                'opportunity_overview': {
                    'business_type': business_type,
                    'region': region,
                    'opportunity_score': opportunity.opportunity_score,
                    'classification': self._classify_opportunity(opportunity.opportunity_score),
                    'recommendation': self._get_recommendation_by_score(opportunity.opportunity_score)
                },
                'market_analysis': {
                    'density_analysis': {
                        'current_establishments': density_analysis.get('current_count', 0),
                        'ideal_establishments': density_analysis.get('ideal_count', 0),
                        'market_gap_percentage': density_analysis.get('gap_percentage', 0),
                        'density_per_1000_inhabitants': density_analysis.get('density_per_1000', 0),
                        'has_opportunity': density_analysis.get('has_opportunity', False)
                    },
                    'demand_analysis': {
                        'demand_score': demand_analysis.get('demand_score', 0),
                        'estimated_monthly_customers': demand_analysis.get('estimated_monthly_customers', 0),
                        'population_factor': demand_analysis.get('population_factor', 0),
                        'density_factor': demand_analysis.get('density_factor', 0),
                        'rent_factor': demand_analysis.get('rent_factor', 0)
                    },
                    'competition_analysis': {
                        'competition_level': competition_analysis.get('competition_level', 'unknown'),
                        'competition_score': competition_analysis.get('competition_score', 0),
                        'market_saturation': competition_analysis.get('market_saturation', 0),
                        'growth_trend': competition_analysis.get('growth_trend', 0),
                        'establishment_count': competition_analysis.get('establishment_count', 0)
                    },
                    'sentiment_analysis': {
                        'sentiment_score': sentiment_analysis.get('sentiment_score', 50),
                        'sentiment_impact': sentiment_analysis.get('sentiment_impact', 'neutral'),
                        'main_complaints': sentiment_analysis.get('main_complaints', []),
                        'opportunity_indicators': sentiment_analysis.get('opportunity_indicators', [])
                    }
                },
                'financial_projections': self._generate_financial_projections(opportunity, analysis_data),
                'implementation_plan': self._generate_implementation_plan(opportunity, analysis_data),
                'risk_mitigation': self._generate_risk_mitigation_plan(opportunity, analysis_data),
                'success_factors': self._identify_success_factors(opportunity, analysis_data)
            }
            
            logger.info(f"Análise detalhada gerada com sucesso para {business_type} em {region}")
            return {
                'status': 'success',
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise detalhada: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """
        Converte dados do relatório para formato Markdown
        """
        try:
            report = report_data.get('report', {})
            metadata = report.get('metadata', {})
            
            # Determinar tipo de relatório
            report_type = metadata.get('report_type', 'executive_summary')
            
            if report_type == 'executive_summary':
                return self._generate_executive_markdown(report)
            elif report_type == 'detailed_analysis':
                return self._generate_detailed_markdown(report)
            else:
                return self._generate_generic_markdown(report)
                
        except Exception as e:
            logger.error(f"Erro ao gerar Markdown: {str(e)}")
            return f"# Erro na Geração do Relatório\n\nErro: {str(e)}"
    
    def _generate_executive_markdown(self, report: Dict[str, Any]) -> str:
        """Gera relatório executivo em Markdown"""
        metadata = report.get('metadata', {})
        summary = report.get('executive_summary', {})
        overview = summary.get('region_overview', {})
        
        markdown = f"""# Relatório Executivo - Mapa de Oportunidades

## Informações Gerais

**Região Analisada:** {metadata.get('region', 'N/A')}  
**Data de Geração:** {datetime.fromisoformat(metadata.get('generated_at', '')).strftime('%d/%m/%Y %H:%M') if metadata.get('generated_at') else 'N/A'}  
**Tipo de Negócio:** {metadata.get('business_type', 'Todos os tipos')}  
**Total de Oportunidades:** {overview.get('total_opportunities', 0)}

## Resumo Executivo

### Visão Geral da Região

A análise identificou **{overview.get('total_opportunities', 0)} oportunidades** de negócio na região {metadata.get('region', '')}, com um score médio de **{overview.get('average_score', 0)}** pontos.

### Distribuição por Qualidade

"""
        
        # Distribuição de scores
        distribution = overview.get('score_distribution', {})
        markdown += f"""
| Categoria | Quantidade | Descrição |
|-----------|------------|-----------|
| 🟢 Excelentes | {distribution.get('excellent', 0)} | Score ≥ 80 pontos |
| 🔵 Boas | {distribution.get('good', 0)} | Score 65-79 pontos |
| 🟡 Moderadas | {distribution.get('moderate', 0)} | Score 50-64 pontos |
| 🔴 Baixas | {distribution.get('low', 0)} | Score < 50 pontos |

"""
        
        # Top oportunidades
        top_opportunities = summary.get('top_opportunities', [])
        if top_opportunities:
            markdown += "## Top 5 Oportunidades\n\n"
            for i, opp in enumerate(top_opportunities, 1):
                markdown += f"""### {i}. {opp.get('business_type', 'N/A')}

**Score de Oportunidade:** {opp.get('opportunity_score', 0)} pontos  
**Nível de Concorrência:** {opp.get('competition_level', 'N/A')}  
**Demanda Estimada:** {opp.get('estimated_demand', 0):,} clientes/mês  
**Recomendação:** {opp.get('recommendation', 'N/A')}

"""
        
        # Análise por categorias
        categories = summary.get('categories_analysis', {})
        if categories:
            markdown += "## Análise por Categoria de Negócio\n\n"
            markdown += "| Categoria | Oportunidades | Score Médio | Melhor Score |\n"
            markdown += "|-----------|---------------|-------------|-------------|\n"
            
            for category, data in sorted(categories.items(), key=lambda x: x[1]['avg_score'], reverse=True):
                markdown += f"| {category} | {data.get('count', 0)} | {data.get('avg_score', 0)} | {data.get('best_score', 0)} |\n"
            
            markdown += "\n"
        
        # Insights principais
        insights = summary.get('key_insights', [])
        if insights:
            markdown += "## Principais Insights\n\n"
            for insight in insights:
                markdown += f"- {insight}\n"
            markdown += "\n"
        
        # Recomendações estratégicas
        recommendations = summary.get('strategic_recommendations', [])
        if recommendations:
            markdown += "## Recomendações Estratégicas\n\n"
            for i, rec in enumerate(recommendations, 1):
                markdown += f"{i}. {rec}\n"
            markdown += "\n"
        
        # Análise detalhada
        detailed = report.get('detailed_analysis', {})
        if detailed:
            markdown += "## Análise Detalhada\n\n"
            
            # Lacunas de mercado
            gaps = detailed.get('market_gaps', [])
            if gaps:
                markdown += "### Principais Lacunas de Mercado\n\n"
                for gap in gaps:
                    markdown += f"- {gap}\n"
                markdown += "\n"
            
            # Paisagem competitiva
            competition = detailed.get('competition_landscape', [])
            if competition:
                markdown += "### Paisagem Competitiva\n\n"
                for comp in competition:
                    markdown += f"- {comp}\n"
                markdown += "\n"
        
        # Prioridades de investimento
        priorities = report.get('investment_priorities', [])
        if priorities:
            markdown += "## Prioridades de Investimento\n\n"
            for i, priority in enumerate(priorities, 1):
                markdown += f"{i}. {priority}\n"
            markdown += "\n"
        
        # Próximos passos
        next_steps = report.get('next_steps', [])
        if next_steps:
            markdown += "## Próximos Passos\n\n"
            for i, step in enumerate(next_steps, 1):
                markdown += f"{i}. {step}\n"
            markdown += "\n"
        
        markdown += """
---

*Relatório gerado automaticamente pelo Sistema de Mapa de Oportunidades por Bairro*  
*Para mais informações ou análises personalizadas, entre em contato conosco.*
"""
        
        return markdown
    
    def _generate_detailed_markdown(self, report: Dict[str, Any]) -> str:
        """Gera relatório detalhado em Markdown"""
        metadata = report.get('metadata', {})
        overview = report.get('opportunity_overview', {})
        market = report.get('market_analysis', {})
        
        markdown = f"""# Análise Detalhada - {overview.get('business_type', 'N/A')}

## Informações da Oportunidade

**Tipo de Negócio:** {overview.get('business_type', 'N/A')}  
**Região:** {overview.get('region', 'N/A')}  
**Score de Oportunidade:** {overview.get('opportunity_score', 0)} pontos  
**Classificação:** {overview.get('classification', 'N/A')}  
**Data de Análise:** {datetime.fromisoformat(metadata.get('generated_at', '')).strftime('%d/%m/%Y %H:%M') if metadata.get('generated_at') else 'N/A'}

## Recomendação Principal

{overview.get('recommendation', 'N/A')}

## Análise de Mercado

### Análise de Densidade

"""
        
        density = market.get('density_analysis', {})
        markdown += f"""
| Métrica | Valor |
|---------|-------|
| Estabelecimentos Atuais | {density.get('current_establishments', 0)} |
| Estabelecimentos Ideais | {density.get('ideal_establishments', 0)} |
| Lacuna de Mercado | {density.get('market_gap_percentage', 0)}% |
| Densidade por 1.000 hab | {density.get('density_per_1000_inhabitants', 0)} |
| Tem Oportunidade | {'✅ Sim' if density.get('has_opportunity') else '❌ Não'} |

"""
        
        # Análise de demanda
        demand = market.get('demand_analysis', {})
        markdown += f"""### Análise de Demanda

| Métrica | Valor |
|---------|-------|
| Score de Demanda | {demand.get('demand_score', 0)} pontos |
| Clientes Estimados/Mês | {demand.get('estimated_monthly_customers', 0):,} |
| Fator População | {demand.get('population_factor', 0)} |
| Fator Densidade | {demand.get('density_factor', 0)} |
| Fator Aluguel | {demand.get('rent_factor', 0)} |

"""
        
        # Análise de concorrência
        competition = market.get('competition_analysis', {})
        markdown += f"""### Análise de Concorrência

| Métrica | Valor |
|---------|-------|
| Nível de Concorrência | {competition.get('competition_level', 'N/A')} |
| Score de Concorrência | {competition.get('competition_score', 0)} pontos |
| Saturação do Mercado | {competition.get('market_saturation', 0)} |
| Tendência de Crescimento | {competition.get('growth_trend', 0)}% |
| Total de Estabelecimentos | {competition.get('establishment_count', 0)} |

"""
        
        # Análise de sentimento
        sentiment = market.get('sentiment_analysis', {})
        markdown += f"""### Análise de Sentimento

**Score de Sentimento:** {sentiment.get('sentiment_score', 50)} pontos  
**Impacto:** {sentiment.get('sentiment_impact', 'neutral')}

"""
        
        complaints = sentiment.get('main_complaints', [])
        if complaints:
            markdown += "**Principais Reclamações:**\n"
            for complaint in complaints:
                markdown += f"- {complaint}\n"
            markdown += "\n"
        
        indicators = sentiment.get('opportunity_indicators', [])
        if indicators:
            markdown += "**Indicadores de Oportunidade:**\n"
            for indicator in indicators:
                markdown += f"- {indicator}\n"
            markdown += "\n"
        
        # Projeções financeiras
        financial = report.get('financial_projections', {})
        if financial:
            markdown += "## Projeções Financeiras\n\n"
            markdown += f"**Investimento Inicial Estimado:** R$ {financial.get('initial_investment', 0):,.2f}\n"
            markdown += f"**Receita Mensal Projetada:** R$ {financial.get('monthly_revenue', 0):,.2f}\n"
            markdown += f"**Payback Estimado:** {financial.get('payback_months', 0)} meses\n"
            markdown += f"**ROI Anual Projetado:** {financial.get('annual_roi', 0)}%\n\n"
        
        # Plano de implementação
        implementation = report.get('implementation_plan', {})
        if implementation:
            markdown += "## Plano de Implementação\n\n"
            phases = implementation.get('phases', [])
            for i, phase in enumerate(phases, 1):
                markdown += f"### Fase {i}: {phase.get('name', 'N/A')}\n"
                markdown += f"**Duração:** {phase.get('duration', 'N/A')}\n"
                markdown += f"**Descrição:** {phase.get('description', 'N/A')}\n\n"
        
        # Fatores de sucesso
        success_factors = report.get('success_factors', [])
        if success_factors:
            markdown += "## Fatores Críticos de Sucesso\n\n"
            for factor in success_factors:
                markdown += f"- {factor}\n"
            markdown += "\n"
        
        markdown += """
---

*Análise detalhada gerada pelo Sistema de Mapa de Oportunidades por Bairro*  
*Esta análise é baseada em dados coletados e algoritmos de análise de mercado.*
"""
        
        return markdown
    
    def _generate_insights(self, opportunities: List[BusinessOpportunity], region: str) -> List[str]:
        """Gera insights baseados nas oportunidades"""
        insights = []
        
        if not opportunities:
            return insights
        
        # Insight sobre score médio
        avg_score = sum(o.opportunity_score for o in opportunities) / len(opportunities)
        if avg_score >= 60:
            insights.append(f"A região {region} apresenta potencial acima da média para novos negócios")
        elif avg_score >= 40:
            insights.append(f"A região {region} tem potencial moderado, requerendo estratégias diferenciadas")
        else:
            insights.append(f"A região {region} apresenta desafios significativos para novos empreendimentos")
        
        # Insight sobre melhores categorias
        best_opportunity = max(opportunities, key=lambda x: x.opportunity_score)
        insights.append(f"A categoria '{best_opportunity.business_type}' apresenta a melhor oportunidade com score {best_opportunity.opportunity_score}")
        
        # Insight sobre concorrência
        low_competition = [o for o in opportunities if o.competition_level == 'low']
        if low_competition:
            insights.append(f"{len(low_competition)} categorias apresentam baixa concorrência, facilitando entrada no mercado")
        
        return insights
    
    def _generate_recommendations(self, opportunities: List[BusinessOpportunity], region: str) -> List[str]:
        """Gera recomendações estratégicas"""
        recommendations = []
        
        if not opportunities:
            return recommendations
        
        # Recomendação baseada nas melhores oportunidades
        excellent_opps = [o for o in opportunities if o.opportunity_score >= 80]
        good_opps = [o for o in opportunities if 65 <= o.opportunity_score < 80]
        
        if excellent_opps:
            recommendations.append(f"Priorizar investimento em {excellent_opps[0].business_type} devido ao alto potencial identificado")
        elif good_opps:
            recommendations.append(f"Considerar {good_opps[0].business_type} como primeira opção de investimento")
        
        # Recomendação sobre diversificação
        if len(opportunities) >= 3:
            recommendations.append("Considerar diversificação de portfólio com 2-3 tipos de negócio diferentes")
        
        # Recomendação sobre timing
        recommendations.append("Realizar análise de viabilidade detalhada antes do investimento")
        recommendations.append("Monitorar mudanças no mercado local trimestralmente")
        
        return recommendations
    
    def _identify_market_gaps(self, opportunities: List[BusinessOpportunity]) -> List[str]:
        """Identifica lacunas de mercado"""
        gaps = []
        
        for opp in opportunities:
            analysis_data = opp.get_analysis_data() or {}
            density_analysis = analysis_data.get('density_analysis', {})
            gap_percentage = density_analysis.get('gap_percentage', 0)
            
            if gap_percentage > 50:
                gaps.append(f"{opp.business_type}: {gap_percentage}% de lacuna na densidade ideal")
        
        return gaps
    
    def _analyze_competition_landscape(self, opportunities: List[BusinessOpportunity]) -> List[str]:
        """Analisa paisagem competitiva"""
        landscape = []
        
        competition_levels = {}
        for opp in opportunities:
            level = opp.competition_level
            if level not in competition_levels:
                competition_levels[level] = []
            competition_levels[level].append(opp.business_type)
        
        for level, businesses in competition_levels.items():
            landscape.append(f"Concorrência {level}: {', '.join(businesses)}")
        
        return landscape
    
    def _analyze_demand_patterns(self, opportunities: List[BusinessOpportunity]) -> List[str]:
        """Analisa padrões de demanda"""
        patterns = []
        
        high_demand = [o for o in opportunities if o.estimated_demand and o.estimated_demand > 15000]
        if high_demand:
            patterns.append(f"Alta demanda identificada em: {', '.join([o.business_type for o in high_demand])}")
        
        return patterns
    
    def _assess_risks(self, opportunities: List[BusinessOpportunity], region: str) -> List[str]:
        """Avalia riscos da região"""
        risks = []
        
        # Risco baseado em scores baixos
        low_scores = [o for o in opportunities if o.opportunity_score < 35]
        if len(low_scores) > len(opportunities) * 0.7:
            risks.append("Alto risco: Maioria das categorias apresenta baixo potencial")
        
        # Risco de alta concorrência
        high_competition = [o for o in opportunities if o.competition_level in ['high', 'very_high']]
        if len(high_competition) > len(opportunities) * 0.5:
            risks.append("Risco de concorrência: Mercado saturado em várias categorias")
        
        return risks
    
    def _generate_investment_priorities(self, opportunities: List[BusinessOpportunity]) -> List[str]:
        """Gera prioridades de investimento"""
        priorities = []
        
        # Ordenar por score
        sorted_opps = sorted(opportunities, key=lambda x: x.opportunity_score, reverse=True)
        
        for i, opp in enumerate(sorted_opps[:3], 1):
            priorities.append(f"Prioridade {i}: {opp.business_type} (Score: {opp.opportunity_score})")
        
        return priorities
    
    def _generate_next_steps(self, opportunities: List[BusinessOpportunity], region: str) -> List[str]:
        """Gera próximos passos"""
        steps = [
            "Realizar pesquisa de campo na região para validar dados",
            "Analisar pontos comerciais disponíveis",
            "Estudar perfil demográfico detalhado do público-alvo",
            "Desenvolver plano de negócios específico",
            "Buscar parcerias locais estratégicas"
        ]
        
        return steps
    
    def _generate_financial_projections(self, opportunity: BusinessOpportunity, analysis_data: Dict) -> Dict[str, Any]:
        """Gera projeções financeiras básicas"""
        demand_analysis = analysis_data.get('demand_analysis', {})
        estimated_customers = demand_analysis.get('estimated_monthly_customers', 1000)
        
        # Estimativas básicas por tipo de negócio
        business_metrics = {
            'Pet Shop': {'ticket_medio': 80, 'investimento_inicial': 150000},
            'Barbearia': {'ticket_medio': 25, 'investimento_inicial': 80000},
            'Restaurante': {'ticket_medio': 35, 'investimento_inicial': 200000},
            'Farmácia': {'ticket_medio': 45, 'investimento_inicial': 300000},
            'Padaria': {'ticket_medio': 15, 'investimento_inicial': 120000}
        }
        
        metrics = business_metrics.get(opportunity.business_type, {
            'ticket_medio': 40, 
            'investimento_inicial': 150000
        })
        
        monthly_revenue = estimated_customers * metrics['ticket_medio'] * 0.3  # 30% de conversão
        annual_revenue = monthly_revenue * 12
        initial_investment = metrics['investimento_inicial']
        
        return {
            'initial_investment': initial_investment,
            'monthly_revenue': monthly_revenue,
            'annual_revenue': annual_revenue,
            'payback_months': round(initial_investment / monthly_revenue) if monthly_revenue > 0 else 0,
            'annual_roi': round((annual_revenue - initial_investment) / initial_investment * 100) if initial_investment > 0 else 0
        }
    
    def _generate_implementation_plan(self, opportunity: BusinessOpportunity, analysis_data: Dict) -> Dict[str, Any]:
        """Gera plano de implementação"""
        phases = [
            {
                'name': 'Planejamento e Pesquisa',
                'duration': '2-4 semanas',
                'description': 'Validação de mercado, escolha do ponto comercial e elaboração do plano de negócios'
            },
            {
                'name': 'Licenciamento e Estruturação',
                'duration': '4-8 semanas',
                'description': 'Obtenção de licenças, reforma do espaço e compra de equipamentos'
            },
            {
                'name': 'Lançamento e Operação',
                'duration': '2-4 semanas',
                'description': 'Contratação de equipe, marketing de lançamento e início das operações'
            }
        ]
        
        return {'phases': phases}
    
    def _generate_risk_mitigation_plan(self, opportunity: BusinessOpportunity, analysis_data: Dict) -> List[str]:
        """Gera plano de mitigação de riscos"""
        mitigation = [
            "Realizar teste de mercado com investimento mínimo inicial",
            "Estabelecer parcerias com fornecedores locais",
            "Implementar sistema de gestão financeira rigoroso",
            "Desenvolver estratégias de diferenciação competitiva"
        ]
        
        return mitigation
    
    def _identify_success_factors(self, opportunity: BusinessOpportunity, analysis_data: Dict) -> List[str]:
        """Identifica fatores críticos de sucesso"""
        factors = [
            "Localização estratégica com alta visibilidade",
            "Atendimento diferenciado e personalizado",
            "Preços competitivos alinhados ao mercado local",
            "Marketing digital efetivo para alcance local",
            "Gestão eficiente de estoque e fornecedores"
        ]
        
        return factors
    
    def _get_recommendation_by_score(self, score: float) -> str:
        """Retorna recomendação baseada no score"""
        if score >= 80:
            return "EXCELENTE OPORTUNIDADE: Alta demanda, baixa concorrência e boa aceitação do mercado."
        elif score >= 65:
            return "BOA OPORTUNIDADE: Mercado promissor com potencial de crescimento."
        elif score >= 50:
            return "OPORTUNIDADE MODERADA: Requer análise mais detalhada e estratégia diferenciada."
        elif score >= 35:
            return "BAIXA OPORTUNIDADE: Mercado saturado ou com baixa demanda."
        else:
            return "NÃO RECOMENDADO: Alto risco devido à saturação do mercado ou baixa demanda."
    
    def _classify_opportunity(self, score: float) -> str:
        """Classifica oportunidade baseada no score"""
        if score >= 80:
            return "Excelente"
        elif score >= 65:
            return "Boa"
        elif score >= 50:
            return "Moderada"
        elif score >= 35:
            return "Baixa"
        else:
            return "Não Recomendada"
    
    def _generate_generic_markdown(self, report: Dict[str, Any]) -> str:
        """Gera relatório genérico em Markdown"""
        return f"""# Relatório de Oportunidades

## Dados do Relatório

{json.dumps(report, indent=2, ensure_ascii=False)}

---

*Relatório gerado automaticamente*
"""

