import requests
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.models.data_models import db, DataSource, CollectedData, CollectionLog

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectorService:
    """Serviço responsável pela coleta de dados de diferentes fontes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MapaOportunidades/1.0 (Data Collection Service)'
        })
    
    def collect_ibge_demographic_data(self, region_code: str = None) -> Dict[str, Any]:
        """
        Coleta dados demográficos do IBGE
        """
        try:
            # URL da API do IBGE para dados demográficos
            base_url = "https://servicodados.ibge.gov.br/api/v1/localidades"
            
            # Coletar dados de municípios
            municipalities_url = f"{base_url}/municipios"
            if region_code:
                municipalities_url += f"/{region_code}"
            
            response = self.session.get(municipalities_url, timeout=30)
            response.raise_for_status()
            
            municipalities_data = response.json()
            
            # Processar dados coletados
            processed_data = []
            for municipality in municipalities_data[:10]:  # Limitar para demonstração
                processed_municipality = {
                    'id': municipality.get('id'),
                    'nome': municipality.get('nome'),
                    'microrregiao': municipality.get('microrregiao', {}).get('nome'),
                    'mesorregiao': municipality.get('microrregiao', {}).get('mesorregiao', {}).get('nome'),
                    'uf': municipality.get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('sigla'),
                    'regiao': municipality.get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('regiao', {}).get('nome')
                }
                processed_data.append(processed_municipality)
            
            return {
                'source': 'IBGE',
                'data_type': 'demographic',
                'collection_timestamp': datetime.utcnow().isoformat(),
                'total_records': len(processed_data),
                'data': processed_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados do IBGE: {str(e)}")
            raise
    
    def collect_cnpj_business_data(self, city: str = "São Paulo") -> Dict[str, Any]:
        """
        Simula coleta de dados de empresas (CNPJ)
        Em um ambiente real, isso seria conectado à API oficial
        """
        try:
            # Simulação de dados de empresas por categoria
            business_categories = [
                'Pet Shop', 'Barbearia', 'Farmácia', 'Padaria', 'Restaurante',
                'Loja de Roupas', 'Supermercado', 'Academia', 'Salão de Beleza',
                'Loja de Eletrônicos', 'Posto de Gasolina', 'Banco'
            ]
            
            simulated_data = []
            for i, category in enumerate(business_categories):
                # Simular diferentes quantidades por categoria
                count = (i * 15) + 10  # Variação de 10 a 175 estabelecimentos
                
                business_data = {
                    'categoria': category,
                    'cidade': city,
                    'total_estabelecimentos': count,
                    'densidade_por_100k_hab': round((count / 12000000) * 100000, 2),  # Baseado em SP
                    'crescimento_ultimo_ano': round((i * 2.5) - 5, 1),  # Variação de -5% a +25%
                    'faturamento_medio_mensal': round(50000 + (i * 25000), 2)
                }
                simulated_data.append(business_data)
            
            return {
                'source': 'CNPJ_Simulation',
                'data_type': 'commercial',
                'collection_timestamp': datetime.utcnow().isoformat(),
                'total_records': len(simulated_data),
                'data': simulated_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao simular dados de CNPJ: {str(e)}")
            raise
    
    def collect_social_media_sentiment(self, region: str = "São Paulo") -> Dict[str, Any]:
        """
        Simula coleta de dados de sentimento de redes sociais
        """
        try:
            import random
            
            # Simular dados de sentimento por categoria de negócio
            categories = [
                'Pet Shop', 'Barbearia', 'Farmácia', 'Padaria', 'Restaurante',
                'Loja de Roupas', 'Supermercado', 'Academia', 'Salão de Beleza'
            ]
            
            sentiment_data = []
            for category in categories:
                # Simular métricas de sentimento
                positive_mentions = random.randint(50, 500)
                negative_mentions = random.randint(10, 100)
                neutral_mentions = random.randint(20, 200)
                total_mentions = positive_mentions + negative_mentions + neutral_mentions
                
                sentiment_score = round(
                    (positive_mentions - negative_mentions) / total_mentions * 100, 2
                )
                
                category_data = {
                    'categoria': category,
                    'regiao': region,
                    'total_mencoes': total_mentions,
                    'mencoes_positivas': positive_mentions,
                    'mencoes_negativas': negative_mentions,
                    'mencoes_neutras': neutral_mentions,
                    'score_sentimento': sentiment_score,
                    'principais_reclamacoes': [
                        'Atendimento demorado',
                        'Preços altos',
                        'Falta de variedade'
                    ][:random.randint(1, 3)]
                }
                sentiment_data.append(category_data)
            
            return {
                'source': 'Social_Media_Simulation',
                'data_type': 'social',
                'collection_timestamp': datetime.utcnow().isoformat(),
                'total_records': len(sentiment_data),
                'data': sentiment_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao simular dados de redes sociais: {str(e)}")
            raise
    
    def collect_rental_market_data(self, city: str = "São Paulo") -> Dict[str, Any]:
        """
        Simula coleta de dados do mercado imobiliário
        """
        try:
            import random
            
            # Simular dados de diferentes bairros
            neighborhoods = [
                'Vila Madalena', 'Pinheiros', 'Itaim Bibi', 'Moema', 'Jardins',
                'Liberdade', 'Bela Vista', 'Santa Cecília', 'Perdizes', 'Higienópolis'
            ]
            
            rental_data = []
            for neighborhood in neighborhoods:
                # Simular dados imobiliários
                avg_rent_commercial = random.randint(3000, 15000)
                avg_rent_residential = random.randint(1500, 8000)
                vacancy_rate = round(random.uniform(2.0, 15.0), 1)
                
                neighborhood_data = {
                    'bairro': neighborhood,
                    'cidade': city,
                    'aluguel_medio_comercial': avg_rent_commercial,
                    'aluguel_medio_residencial': avg_rent_residential,
                    'taxa_vacancia': vacancy_rate,
                    'metros_quadrados_disponiveis': random.randint(500, 5000),
                    'crescimento_preco_ano': round(random.uniform(-5.0, 20.0), 1),
                    'densidade_populacional': random.randint(5000, 25000)
                }
                rental_data.append(neighborhood_data)
            
            return {
                'source': 'Rental_Market_Simulation',
                'data_type': 'real_estate',
                'collection_timestamp': datetime.utcnow().isoformat(),
                'total_records': len(rental_data),
                'data': rental_data
            }
            
        except Exception as e:
            logger.error(f"Erro ao simular dados imobiliários: {str(e)}")
            raise
    
    def save_collected_data(self, data: Dict[str, Any], source_name: str, data_type: str) -> bool:
        """
        Salva dados coletados no banco de dados
        """
        try:
            # Buscar ou criar fonte de dados
            source = DataSource.query.filter_by(name=source_name).first()
            if not source:
                source = DataSource(
                    name=source_name,
                    type='api' if 'API' in source_name else 'simulation',
                    description=f"Fonte de dados: {source_name}"
                )
                db.session.add(source)
                db.session.commit()
            
            # Criar registro de dados coletados
            collected_data = CollectedData(
                source_id=source.id,
                data_type=data_type,
                region=data.get('region', 'Brasil'),
                raw_data=data
            )
            
            db.session.add(collected_data)
            db.session.commit()
            
            logger.info(f"Dados salvos com sucesso: {source_name} - {data_type}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            db.session.rollback()
            return False
    
    def run_full_collection(self) -> Dict[str, Any]:
        """
        Executa coleta completa de todas as fontes
        """
        results = {
            'started_at': datetime.utcnow().isoformat(),
            'collections': [],
            'total_success': 0,
            'total_errors': 0
        }
        
        # Lista de coletas a executar
        collections = [
            ('IBGE Demographics', self.collect_ibge_demographic_data, 'demographic'),
            ('CNPJ Business Data', self.collect_cnpj_business_data, 'commercial'),
            ('Social Media Sentiment', self.collect_social_media_sentiment, 'social'),
            ('Rental Market Data', self.collect_rental_market_data, 'real_estate')
        ]
        
        for name, collector_func, data_type in collections:
            try:
                logger.info(f"Iniciando coleta: {name}")
                start_time = time.time()
                
                # Executar coleta
                if name == 'IBGE Demographics':
                    data = collector_func()
                else:
                    data = collector_func()
                
                execution_time = time.time() - start_time
                
                # Salvar dados
                saved = self.save_collected_data(data, name, data_type)
                
                collection_result = {
                    'name': name,
                    'status': 'success' if saved else 'error',
                    'records_collected': data.get('total_records', 0),
                    'execution_time': round(execution_time, 2)
                }
                
                results['collections'].append(collection_result)
                
                if saved:
                    results['total_success'] += 1
                else:
                    results['total_errors'] += 1
                
                logger.info(f"Coleta concluída: {name} - {collection_result['status']}")
                
            except Exception as e:
                logger.error(f"Erro na coleta {name}: {str(e)}")
                results['collections'].append({
                    'name': name,
                    'status': 'error',
                    'error': str(e),
                    'execution_time': 0
                })
                results['total_errors'] += 1
        
        results['finished_at'] = datetime.utcnow().isoformat()
        return results

