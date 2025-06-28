import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging
from src.models.data_models import db, CollectedData, BusinessOpportunity, DataSource
import json
import math

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpportunityAnalysisService:
    """Serviço responsável pela análise de oportunidades de negócio"""
    
    def __init__(self):
        # Configurações padrão para análise
        self.business_categories = [
            'Pet Shop', 'Barbearia', 'Farmácia', 'Padaria', 'Restaurante',
            'Loja de Roupas', 'Supermercado', 'Academia', 'Salão de Beleza',
            'Loja de Eletrônicos', 'Posto de Gasolina', 'Banco'
        ]
        
        # Parâmetros de análise
        self.population_thresholds = {
            'Pet Shop': 5000,      # 1 pet shop para cada 5.000 habitantes
            'Barbearia': 3000,     # 1 barbearia para cada 3.000 habitantes
            'Farmácia': 8000,      # 1 farmácia para cada 8.000 habitantes
            'Padaria': 2000,       # 1 padaria para cada 2.000 habitantes
            'Restaurante': 1500,   # 1 restaurante para cada 1.500 habitantes
            'Loja de Roupas': 4000,
            'Supermercado': 10000,
            'Academia': 6000,
            'Salão de Beleza': 2500,
            'Loja de Eletrônicos': 15000,
            'Posto de Gasolina': 20000,
            'Banco': 25000
        }
        
        # Pesos para cálculo do score de oportunidade
        self.score_weights = {
            'density_gap': 0.3,      # Lacuna de densidade
            'demand_potential': 0.25, # Potencial de demanda
            'competition_level': 0.2, # Nível de concorrência
            'economic_indicators': 0.15, # Indicadores econômicos
            'sentiment_score': 0.1    # Score de sentimento
        }
    
    def calculate_business_density(self, business_data: List[Dict], population: int, 
                                 business_type: str) -> Dict[str, float]:
        """
        Calcula a densidade de negócios por tipo em relação à população
        """
        try:
            # Filtrar dados do tipo de negócio específico
            business_count = 0
            for business in business_data:
                if business.get('categoria', '').lower() == business_type.lower():
                    business_count = business.get('total_estabelecimentos', 0)
                    break
            
            # Calcular densidade
            if population > 0:
                density_per_1000 = (business_count / population) * 1000
                density_per_10000 = (business_count / population) * 10000
            else:
                density_per_1000 = 0
                density_per_10000 = 0
            
            # Calcular lacuna baseada no threshold ideal
            ideal_count = population / self.population_thresholds.get(business_type, 5000)
            gap_percentage = max(0, (ideal_count - business_count) / ideal_count * 100) if ideal_count > 0 else 0
            
            return {
                'current_count': business_count,
                'ideal_count': round(ideal_count, 1),
                'density_per_1000': round(density_per_1000, 2),
                'density_per_10000': round(density_per_10000, 2),
                'gap_percentage': round(gap_percentage, 1),
                'has_opportunity': gap_percentage > 20  # Oportunidade se gap > 20%
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular densidade de negócios: {str(e)}")
            return {
                'current_count': 0,
                'ideal_count': 0,
                'density_per_1000': 0,
                'density_per_10000': 0,
                'gap_percentage': 0,
                'has_opportunity': False
            }
    
    def analyze_demand_potential(self, demographic_data: Dict, rental_data: Dict, 
                               business_type: str) -> Dict[str, Any]:
        """
        Analisa o potencial de demanda baseado em dados demográficos e imobiliários
        """
        try:
            # Fatores demográficos
            population = demographic_data.get('population', 0)
            density = demographic_data.get('density', 0)
            
            # Fatores econômicos do mercado imobiliário
            avg_rent = rental_data.get('aluguel_medio_comercial', 0)
            vacancy_rate = rental_data.get('taxa_vacancia', 0)
            
            # Calcular score de demanda baseado no tipo de negócio
            demand_factors = {
                'Pet Shop': {
                    'population_factor': min(population / 10000, 1.0),
                    'density_factor': min(density / 15000, 1.0),
                    'rent_factor': max(0, 1 - (avg_rent / 20000))  # Menor aluguel = melhor
                },
                'Barbearia': {
                    'population_factor': min(population / 5000, 1.0),
                    'density_factor': min(density / 10000, 1.0),
                    'rent_factor': max(0, 1 - (avg_rent / 15000))
                },
                'Restaurante': {
                    'population_factor': min(population / 8000, 1.0),
                    'density_factor': min(density / 12000, 1.0),
                    'rent_factor': max(0, 1 - (avg_rent / 25000))
                }
            }
            
            # Usar fatores padrão se o tipo não estiver definido
            factors = demand_factors.get(business_type, {
                'population_factor': min(population / 8000, 1.0),
                'density_factor': min(density / 12000, 1.0),
                'rent_factor': max(0, 1 - (avg_rent / 18000))
            })
            
            # Calcular score de demanda (0-100)
            demand_score = (
                factors['population_factor'] * 40 +
                factors['density_factor'] * 35 +
                factors['rent_factor'] * 25
            )
            
            # Ajustar baseado na taxa de vacância
            vacancy_adjustment = max(0, (20 - vacancy_rate) / 20)  # Menor vacância = melhor
            demand_score *= vacancy_adjustment
            
            return {
                'demand_score': round(demand_score, 1),
                'population_factor': round(factors['population_factor'], 2),
                'density_factor': round(factors['density_factor'], 2),
                'rent_factor': round(factors['rent_factor'], 2),
                'vacancy_adjustment': round(vacancy_adjustment, 2),
                'estimated_monthly_customers': round(population * factors['population_factor'] * 0.1)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar potencial de demanda: {str(e)}")
            return {
                'demand_score': 0,
                'population_factor': 0,
                'density_factor': 0,
                'rent_factor': 0,
                'vacancy_adjustment': 0,
                'estimated_monthly_customers': 0
            }
    
    def analyze_competition_level(self, business_data: List[Dict], 
                                business_type: str) -> Dict[str, Any]:
        """
        Analisa o nível de concorrência para um tipo de negócio
        """
        try:
            # Encontrar dados do tipo de negócio
            target_business = None
            for business in business_data:
                if business.get('categoria', '').lower() == business_type.lower():
                    target_business = business
                    break
            
            if not target_business:
                return {
                    'competition_level': 'unknown',
                    'competition_score': 50,
                    'market_saturation': 0,
                    'growth_trend': 0
                }
            
            # Analisar métricas de concorrência
            establishment_count = target_business.get('total_estabelecimentos', 0)
            density_per_100k = target_business.get('densidade_por_100k_hab', 0)
            growth_rate = target_business.get('crescimento_ultimo_ano', 0)
            
            # Calcular saturação do mercado
            # Baseado na densidade em relação à média nacional (estimativa)
            avg_density_national = 50  # Estimativa de densidade média nacional
            saturation_ratio = density_per_100k / avg_density_national if avg_density_national > 0 else 0
            
            # Determinar nível de concorrência
            if saturation_ratio < 0.5:
                competition_level = 'low'
                competition_score = 80
            elif saturation_ratio < 1.0:
                competition_level = 'medium'
                competition_score = 60
            elif saturation_ratio < 1.5:
                competition_level = 'high'
                competition_score = 40
            else:
                competition_level = 'very_high'
                competition_score = 20
            
            # Ajustar score baseado no crescimento
            if growth_rate > 10:
                competition_score -= 10  # Mercado em crescimento = mais concorrência
            elif growth_rate < 0:
                competition_score += 10  # Mercado em declínio = menos concorrência
            
            competition_score = max(0, min(100, competition_score))
            
            return {
                'competition_level': competition_level,
                'competition_score': round(competition_score, 1),
                'market_saturation': round(saturation_ratio, 2),
                'growth_trend': growth_rate,
                'establishment_count': establishment_count,
                'density_per_100k': density_per_100k
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar concorrência: {str(e)}")
            return {
                'competition_level': 'unknown',
                'competition_score': 50,
                'market_saturation': 0,
                'growth_trend': 0,
                'establishment_count': 0,
                'density_per_100k': 0
            }
    
    def analyze_sentiment_impact(self, social_data: List[Dict], 
                               business_type: str) -> Dict[str, Any]:
        """
        Analisa o impacto do sentimento das redes sociais
        """
        try:
            # Encontrar dados de sentimento para o tipo de negócio
            sentiment_data = None
            for data in social_data:
                if data.get('categoria', '').lower() == business_type.lower():
                    sentiment_data = data
                    break
            
            if not sentiment_data:
                return {
                    'sentiment_score': 50,
                    'sentiment_impact': 'neutral',
                    'main_complaints': [],
                    'opportunity_indicators': []
                }
            
            # Extrair métricas de sentimento
            sentiment_score = sentiment_data.get('score_sentimento', 0)
            complaints = sentiment_data.get('principais_reclamacoes', [])
            total_mentions = sentiment_data.get('total_mencoes', 0)
            
            # Determinar impacto do sentimento
            if sentiment_score > 20:
                sentiment_impact = 'positive'
            elif sentiment_score > -20:
                sentiment_impact = 'neutral'
            else:
                sentiment_impact = 'negative'
            
            # Identificar indicadores de oportunidade baseados nas reclamações
            opportunity_indicators = []
            if 'Atendimento demorado' in complaints:
                opportunity_indicators.append('Oportunidade para serviço mais rápido')
            if 'Preços altos' in complaints:
                opportunity_indicators.append('Oportunidade para preços competitivos')
            if 'Falta de variedade' in complaints:
                opportunity_indicators.append('Oportunidade para maior variedade')
            
            # Converter score de sentimento para escala 0-100
            normalized_score = max(0, min(100, (sentiment_score + 100) / 2))
            
            return {
                'sentiment_score': round(normalized_score, 1),
                'sentiment_impact': sentiment_impact,
                'main_complaints': complaints,
                'opportunity_indicators': opportunity_indicators,
                'total_mentions': total_mentions,
                'raw_sentiment_score': sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {str(e)}")
            return {
                'sentiment_score': 50,
                'sentiment_impact': 'neutral',
                'main_complaints': [],
                'opportunity_indicators': [],
                'total_mentions': 0,
                'raw_sentiment_score': 0
            }
    
    def calculate_opportunity_score(self, density_analysis: Dict, demand_analysis: Dict,
                                  competition_analysis: Dict, sentiment_analysis: Dict) -> float:
        """
        Calcula o score final de oportunidade baseado em todos os fatores
        """
        try:
            # Extrair scores individuais
            density_score = density_analysis.get('gap_percentage', 0)
            demand_score = demand_analysis.get('demand_score', 0)
            competition_score = competition_analysis.get('competition_score', 50)
            sentiment_score = sentiment_analysis.get('sentiment_score', 50)
            
            # Normalizar density_score (gap_percentage) para escala 0-100
            normalized_density_score = min(100, density_score)
            
            # Calcular score ponderado
            final_score = (
                normalized_density_score * self.score_weights['density_gap'] +
                demand_score * self.score_weights['demand_potential'] +
                competition_score * self.score_weights['competition_level'] +
                demand_score * self.score_weights['economic_indicators'] +  # Usar demand como proxy
                sentiment_score * self.score_weights['sentiment_score']
            )
            
            return round(final_score, 1)
            
        except Exception as e:
            logger.error(f"Erro ao calcular score de oportunidade: {str(e)}")
            return 0.0
    
    def analyze_region_opportunities(self, region: str) -> Dict[str, Any]:
        """
        Analisa oportunidades para uma região específica
        """
        try:
            logger.info(f"Iniciando análise de oportunidades para região: {region}")
            
            # Buscar dados coletados para a região
            demographic_data = self._get_demographic_data(region)
            business_data = self._get_business_data(region)
            social_data = self._get_social_data(region)
            rental_data = self._get_rental_data(region)
            
            if not any([demographic_data, business_data, social_data, rental_data]):
                logger.warning(f"Nenhum dado encontrado para região: {region}")
                return {
                    'region': region,
                    'status': 'no_data',
                    'message': 'Dados insuficientes para análise'
                }
            
            # Analisar oportunidades para cada categoria de negócio
            opportunities = []
            
            for business_type in self.business_categories:
                logger.info(f"Analisando oportunidades para: {business_type}")
                
                # Executar análises individuais
                density_analysis = self.calculate_business_density(
                    business_data, demographic_data.get('population', 50000), business_type
                )
                
                demand_analysis = self.analyze_demand_potential(
                    demographic_data, rental_data, business_type
                )
                
                competition_analysis = self.analyze_competition_level(
                    business_data, business_type
                )
                
                sentiment_analysis = self.analyze_sentiment_impact(
                    social_data, business_type
                )
                
                # Calcular score final
                opportunity_score = self.calculate_opportunity_score(
                    density_analysis, demand_analysis, competition_analysis, sentiment_analysis
                )
                
                # Compilar resultado
                opportunity = {
                    'business_type': business_type,
                    'opportunity_score': opportunity_score,
                    'density_analysis': density_analysis,
                    'demand_analysis': demand_analysis,
                    'competition_analysis': competition_analysis,
                    'sentiment_analysis': sentiment_analysis,
                    'recommendation': self._generate_recommendation(
                        opportunity_score, density_analysis, demand_analysis, 
                        competition_analysis, sentiment_analysis
                    )
                }
                
                opportunities.append(opportunity)
            
            # Ordenar por score de oportunidade
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            # Compilar resultado final
            result = {
                'region': region,
                'status': 'success',
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'total_opportunities': len(opportunities),
                'top_opportunities': opportunities[:5],  # Top 5
                'all_opportunities': opportunities,
                'region_summary': {
                    'population': demographic_data.get('population', 0),
                    'density': demographic_data.get('density', 0),
                    'avg_commercial_rent': rental_data.get('aluguel_medio_comercial', 0),
                    'vacancy_rate': rental_data.get('taxa_vacancia', 0)
                }
            }
            
            logger.info(f"Análise concluída para {region}. {len(opportunities)} oportunidades identificadas.")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de oportunidades para {region}: {str(e)}")
            return {
                'region': region,
                'status': 'error',
                'error': str(e)
            }
    
    def _get_demographic_data(self, region: str) -> Dict[str, Any]:
        """Busca dados demográficos para a região"""
        try:
            # Simular dados demográficos baseados na região
            # Em um sistema real, isso viria do banco de dados
            base_population = 50000
            if 'São Paulo' in region:
                base_population = 200000
            elif 'Rio' in region:
                base_population = 150000
            elif 'Belo Horizonte' in region:
                base_population = 100000
            
            return {
                'population': base_population,
                'density': base_population / 10,  # Densidade por km²
                'region': region
            }
        except Exception as e:
            logger.error(f"Erro ao buscar dados demográficos: {str(e)}")
            return {}
    
    def _get_business_data(self, region: str) -> List[Dict[str, Any]]:
        """Busca dados de empresas para a região"""
        try:
            # Simular dados de empresas
            # Em um sistema real, isso viria do banco de dados
            business_data = []
            for i, category in enumerate(self.business_categories):
                count = (i * 15) + 10 + (hash(region) % 20)  # Variação por região
                business_data.append({
                    'categoria': category,
                    'total_estabelecimentos': count,
                    'densidade_por_100k_hab': round((count / 50000) * 100000, 2),
                    'crescimento_ultimo_ano': round((i * 2.5) - 5 + (hash(region) % 10), 1)
                })
            return business_data
        except Exception as e:
            logger.error(f"Erro ao buscar dados de empresas: {str(e)}")
            return []
    
    def _get_social_data(self, region: str) -> List[Dict[str, Any]]:
        """Busca dados de redes sociais para a região"""
        try:
            import random
            random.seed(hash(region))  # Seed baseado na região para consistência
            
            social_data = []
            for category in self.business_categories[:9]:  # Primeiras 9 categorias
                positive = random.randint(50, 500)
                negative = random.randint(10, 100)
                neutral = random.randint(20, 200)
                total = positive + negative + neutral
                score = round((positive - negative) / total * 100, 2)
                
                social_data.append({
                    'categoria': category,
                    'total_mencoes': total,
                    'score_sentimento': score,
                    'principais_reclamacoes': random.sample([
                        'Atendimento demorado', 'Preços altos', 'Falta de variedade'
                    ], random.randint(1, 3))
                })
            return social_data
        except Exception as e:
            logger.error(f"Erro ao buscar dados sociais: {str(e)}")
            return []
    
    def _get_rental_data(self, region: str) -> Dict[str, Any]:
        """Busca dados imobiliários para a região"""
        try:
            import random
            random.seed(hash(region))
            
            base_rent = 5000
            if 'São Paulo' in region:
                base_rent = 12000
            elif 'Rio' in region:
                base_rent = 8000
            
            return {
                'aluguel_medio_comercial': base_rent + random.randint(-2000, 5000),
                'taxa_vacancia': round(random.uniform(5.0, 15.0), 1),
                'regiao': region
            }
        except Exception as e:
            logger.error(f"Erro ao buscar dados imobiliários: {str(e)}")
            return {}
    
    def _generate_recommendation(self, score: float, density_analysis: Dict,
                               demand_analysis: Dict, competition_analysis: Dict,
                               sentiment_analysis: Dict) -> str:
        """Gera recomendação baseada na análise"""
        try:
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
        except Exception as e:
            logger.error(f"Erro ao gerar recomendação: {str(e)}")
            return "Análise inconclusiva."

