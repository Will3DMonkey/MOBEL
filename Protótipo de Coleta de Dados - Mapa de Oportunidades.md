# Protótipo de Coleta de Dados - Mapa de Oportunidades

## Resumo

Este protótipo demonstra a funcionalidade de coleta de dados do sistema "Mapa de Oportunidade por Bairro". O sistema foi desenvolvido usando Flask e implementa coletores para diferentes tipos de fontes de dados, tanto públicas quanto privadas (simuladas).

## Funcionalidades Implementadas

### 1. Coleta de Dados Demográficos (IBGE)
- **Fonte**: API oficial do IBGE (servicodados.ibge.gov.br)
- **Dados coletados**: Informações de municípios, microrregiões, mesorregiões e estados
- **Status**: ✅ Funcionando com dados reais

### 2. Simulação de Dados Comerciais (CNPJ)
- **Fonte**: Simulação baseada em padrões reais
- **Dados simulados**: 
  - Categorias de negócio (Pet Shop, Barbearia, Farmácia, etc.)
  - Número de estabelecimentos por categoria
  - Densidade por 100k habitantes
  - Crescimento no último ano
  - Faturamento médio mensal
- **Status**: ✅ Funcionando com dados simulados

### 3. Simulação de Análise de Sentimento (Redes Sociais)
- **Fonte**: Simulação de dados de redes sociais
- **Dados simulados**:
  - Menções positivas, negativas e neutras por categoria
  - Score de sentimento
  - Principais reclamações
- **Status**: ✅ Funcionando com dados simulados

### 4. Simulação de Dados Imobiliários
- **Fonte**: Simulação de mercado de aluguéis
- **Dados simulados**:
  - Aluguel médio comercial e residencial por bairro
  - Taxa de vacância
  - Metros quadrados disponíveis
  - Crescimento de preços
  - Densidade populacional
- **Status**: ✅ Funcionando com dados simulados

## Arquitetura Técnica

### Modelos de Dados
- **DataSource**: Armazena informações sobre fontes de dados
- **CollectedData**: Armazena dados coletados com metadados
- **BusinessOpportunity**: Armazena oportunidades identificadas
- **CollectionLog**: Log de execuções de coleta

### Serviços
- **DataCollectorService**: Serviço principal de coleta de dados
- **API REST**: Endpoints para controle e consulta de dados

### Endpoints da API

#### Saúde do Sistema
- `GET /api/data/health` - Verificação de saúde da API

#### Coleta de Dados
- `POST /api/data/collect/ibge` - Coleta dados do IBGE
- `POST /api/data/collect/business` - Coleta dados de empresas
- `POST /api/data/collect/social` - Coleta dados de redes sociais
- `POST /api/data/collect/rental` - Coleta dados imobiliários
- `POST /api/data/collect/all` - Executa coleta completa

#### Consulta de Dados
- `GET /api/data/sources` - Lista fontes de dados
- `GET /api/data/data` - Consulta dados coletados (com filtros)
- `GET /api/data/opportunities` - Lista oportunidades identificadas
- `GET /api/data/stats` - Estatísticas de coleta

## Resultados dos Testes

### Teste de Coleta IBGE
```
✓ Dados do IBGE coletados com sucesso
Total de registros: 10
Primeiro município: Alta Floresta D'Oeste - RO
```

### Teste de Dados Comerciais
```
✓ Dados de empresas simulados com sucesso
Total de categorias: 12
Primeira categoria: Pet Shop - 10 estabelecimentos
```

### Teste de Redes Sociais
```
✓ Dados de redes sociais simulados com sucesso
Total de categorias analisadas: 9
Primeira categoria: Pet Shop - Score: 47.5
```

### Teste de Dados Imobiliários
```
✓ Dados imobiliários simulados com sucesso
Total de bairros: 10
Primeiro bairro: Vila Madalena - Aluguel comercial médio: R$ 10.156
```

## Próximos Passos

1. **Integração com APIs Reais**: Conectar com APIs reais de:
   - Receita Federal (CNPJ)
   - Google Maps API
   - APIs de redes sociais
   - Plataformas imobiliárias

2. **Processamento de Dados**: Implementar algoritmos de:
   - Limpeza e normalização
   - Análise geoespacial
   - Identificação de oportunidades

3. **Interface Web**: Desenvolver dashboard para:
   - Visualização de mapas
   - Relatórios interativos
   - Configuração de coletas

4. **Escalabilidade**: Implementar:
   - Processamento assíncrono
   - Cache distribuído
   - Monitoramento

## Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-CORS
- **Banco de Dados**: SQLite (desenvolvimento)
- **HTTP Client**: Requests
- **Logging**: Python logging
- **Containerização**: Preparado para Docker

## Estrutura do Projeto

```
mapa-oportunidades/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   └── data_models.py
│   ├── routes/
│   │   ├── user.py
│   │   └── data_routes.py
│   ├── services/
│   │   └── data_collector.py
│   ├── static/
│   ├── database/
│   │   └── app.db
│   └── main.py
├── venv/
└── requirements.txt
```

## Conclusão

O protótipo demonstra com sucesso a viabilidade técnica do sistema de coleta de dados. A arquitetura modular permite fácil expansão e integração com novas fontes de dados. Os testes confirmam que tanto a coleta de dados reais (IBGE) quanto a simulação de dados privados funcionam corretamente.

O sistema está pronto para avançar para a próxima fase: desenvolvimento dos algoritmos de análise de oportunidades.

