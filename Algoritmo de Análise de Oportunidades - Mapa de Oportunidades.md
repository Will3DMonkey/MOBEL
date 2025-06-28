# Algoritmo de Análise de Oportunidades - Mapa de Oportunidades

## Resumo

Este documento descreve o algoritmo desenvolvido para identificar oportunidades de negócio por bairro, cruzando dados demográficos, comerciais, imobiliários e de sentimento das redes sociais. O algoritmo utiliza uma abordagem multi-fatorial para calcular scores de oportunidade e gerar recomendações precisas.

## Metodologia de Análise

### 1. Análise de Densidade Comercial

O algoritmo calcula a densidade atual de estabelecimentos por categoria e compara com thresholds ideais baseados na população local.

**Fórmula de Densidade:**
```
Densidade = (Número de Estabelecimentos / População) × 1000
```

**Cálculo de Lacuna:**
```
Lacuna (%) = ((Ideal - Atual) / Ideal) × 100
```

**Thresholds por Categoria:**
- Pet Shop: 1 para cada 5.000 habitantes
- Barbearia: 1 para cada 3.000 habitantes
- Farmácia: 1 para cada 8.000 habitantes
- Padaria: 1 para cada 2.000 habitantes
- Restaurante: 1 para cada 1.500 habitantes
- Supermercado: 1 para cada 10.000 habitantes
- Academia: 1 para cada 6.000 habitantes

### 2. Análise de Potencial de Demanda

Avalia o potencial de demanda baseado em fatores demográficos e econômicos.

**Componentes do Score de Demanda:**
- **Fator População (40%)**: Normalizado pela população ideal para o tipo de negócio
- **Fator Densidade (35%)**: Baseado na densidade populacional da região
- **Fator Aluguel (25%)**: Inversamente proporcional ao custo do aluguel comercial

**Fórmula:**
```
Score Demanda = (Fator_Pop × 40 + Fator_Densidade × 35 + Fator_Aluguel × 25) × Ajuste_Vacância
```

### 3. Análise de Concorrência

Determina o nível de saturação do mercado e competitividade.

**Níveis de Concorrência:**
- **Baixa** (Score 80): Saturação < 50% da média nacional
- **Média** (Score 60): Saturação 50-100% da média nacional  
- **Alta** (Score 40): Saturação 100-150% da média nacional
- **Muito Alta** (Score 20): Saturação > 150% da média nacional

**Ajustes por Crescimento:**
- Crescimento > 10%: -10 pontos (mais concorrência)
- Crescimento < 0%: +10 pontos (menos concorrência)

### 4. Análise de Sentimento

Incorpora dados de redes sociais para avaliar satisfação do consumidor.

**Métricas de Sentimento:**
- Score normalizado de -100 a +100
- Principais reclamações identificadas
- Volume total de menções

**Indicadores de Oportunidade:**
- "Atendimento demorado" → Oportunidade para serviço mais rápido
- "Preços altos" → Oportunidade para preços competitivos
- "Falta de variedade" → Oportunidade para maior variedade

### 5. Score Final de Oportunidade

O score final é calculado usando pesos específicos para cada componente:

**Pesos dos Componentes:**
- Lacuna de Densidade: 30%
- Potencial de Demanda: 25%
- Nível de Concorrência: 20%
- Indicadores Econômicos: 15%
- Score de Sentimento: 10%

**Fórmula Final:**
```
Score Final = (Lacuna × 0.30) + (Demanda × 0.25) + (Concorrência × 0.20) + (Econômico × 0.15) + (Sentimento × 0.10)
```

## Classificação de Oportunidades

### Excelente Oportunidade (Score ≥ 80)
- **Recomendação**: "EXCELENTE OPORTUNIDADE: Alta demanda, baixa concorrência e boa aceitação do mercado."
- **Características**: Lacuna significativa, alta demanda, baixa concorrência

### Boa Oportunidade (Score 65-79)
- **Recomendação**: "BOA OPORTUNIDADE: Mercado promissor com potencial de crescimento."
- **Características**: Boa combinação de fatores, risco moderado

### Oportunidade Moderada (Score 50-64)
- **Recomendação**: "OPORTUNIDADE MODERADA: Requer análise mais detalhada e estratégia diferenciada."
- **Características**: Alguns fatores favoráveis, necessita estratégia específica

### Baixa Oportunidade (Score 35-49)
- **Recomendação**: "BAIXA OPORTUNIDADE: Mercado saturado ou com baixa demanda."
- **Características**: Fatores desfavoráveis predominam

### Não Recomendado (Score < 35)
- **Recomendação**: "NÃO RECOMENDADO: Alto risco devido à saturação do mercado ou baixa demanda."
- **Características**: Alto risco, múltiplos fatores negativos

## Resultados dos Testes

### Teste 1: São Paulo - Vila Madalena
```
Top 3 Oportunidades:
1. Pet Shop - Score: 62.5 (Oportunidade Moderada)
   - Lacuna de densidade: 50.0%
   - Score de demanda: 64.0
   - Nível de concorrência: medium

2. Barbearia - Score: 56.1 (Oportunidade Moderada)
   - Lacuna de densidade: 47.5%
   - Score de demanda: 60.4
   - Nível de concorrência: high

3. Restaurante - Score: 49.7 (Baixa Oportunidade)
   - Lacuna de densidade: 40.0%
   - Score de demanda: 66.2
   - Nível de concorrência: very_high
```

### Teste 2: Rio de Janeiro - Copacabana
```
Top 3 Oportunidades:
1. Pet Shop - Score: 28.3 (Não Recomendado)
   - Lacuna de densidade: 10.0%
   - Score de demanda: 23.9
   - Nível de concorrência: high

2. Barbearia - Score: 25.6 (Não Recomendado)
   - Lacuna de densidade: 16.0%
   - Score de demanda: 22.5
   - Nível de concorrência: very_high
```

### Teste 3: Análise Específica - Pet Shop em São Paulo
```
Densidade atual: 5 estabelecimentos
Densidade ideal: 10.0 estabelecimentos
Lacuna: 50.0%
Score de demanda: 40.0
Clientes estimados/mês: 5.000
Nível de concorrência: low
Score final de oportunidade: 53.0
```

## Funcionalidades da API

### Endpoints Implementados

1. **POST /api/analysis/analyze/{region}**
   - Executa análise completa para uma região
   - Salva resultados no banco de dados
   - Retorna top oportunidades identificadas

2. **GET /api/analysis/opportunities**
   - Lista oportunidades com filtros
   - Parâmetros: region, business_type, min_score, max_score, competition_level

3. **GET /api/analysis/opportunities/top**
   - Retorna melhores oportunidades por região
   - Agrupa resultados por localização

4. **GET /api/analysis/summary**
   - Estatísticas gerais das análises
   - Distribuição por score e tipo de negócio

5. **GET /api/analysis/business-types**
   - Lista tipos de negócio e thresholds

## Vantagens do Algoritmo

### 1. Abordagem Multi-Fatorial
- Combina dados quantitativos e qualitativos
- Reduz viés de análises baseadas em um único fator
- Fornece visão holística do mercado

### 2. Flexibilidade
- Thresholds ajustáveis por tipo de negócio
- Pesos configuráveis para diferentes cenários
- Adaptável a diferentes regiões e contextos

### 3. Precisão
- Baseado em dados reais quando disponíveis
- Simulações realistas para dados não acessíveis
- Validação cruzada entre diferentes fontes

### 4. Escalabilidade
- Processamento eficiente para múltiplas regiões
- Arquitetura modular permite expansão
- Cache de resultados para otimização

## Limitações e Melhorias Futuras

### Limitações Atuais
1. Dependência de dados simulados para algumas fontes
2. Thresholds baseados em estimativas gerais
3. Análise geoespacial limitada

### Melhorias Propostas
1. **Integração com APIs Reais**
   - Conectar com bases de dados oficiais
   - Dados de redes sociais em tempo real
   - Informações de tráfego e mobilidade

2. **Machine Learning Avançado**
   - Modelos preditivos para demanda
   - Clustering geoespacial automático
   - Análise de séries temporais

3. **Análise Geoespacial**
   - Cálculos de proximidade e acessibilidade
   - Análise de concorrência por raio
   - Mapas de calor de oportunidades

4. **Personalização**
   - Perfis de investimento personalizados
   - Análise de risco específica
   - Recomendações contextuais

## Conclusão

O algoritmo de análise de oportunidades demonstra eficácia na identificação de lacunas de mercado através de uma abordagem científica e baseada em dados. Os testes confirmam que o sistema consegue diferenciar entre regiões com diferentes potenciais de negócio e fornecer recomendações precisas.

A implementação modular permite evolução contínua do algoritmo, incorporando novas fontes de dados e refinando os modelos de análise conforme mais informações se tornam disponíveis.

O sistema está pronto para a próxima fase: desenvolvimento da interface web para visualização e interação com os resultados das análises.

