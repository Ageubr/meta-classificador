# 📊 Visualização de Dados em Lote

## Visão Geral

O sistema agora possui uma funcionalidade completa para processar e visualizar **grandes volumes de dados** diretamente da pasta `data/`, sem necessidade de upload via frontend (que tem limite de 1MB).

## 🎯 Como Funciona

### 1. **Colocar Arquivos CSV na Pasta `data/`**

Basta colocar seus arquivos CSV na pasta `data/` do projeto:

```bash
data/
├── cadunico_processado_100000.csv  (2.355 registros - já incluído)
├── base_amostra_cad_201812/
│   ├── base_amostra_familia_201812.csv  (4.8M registros)
│   └── base_amostra_pessoa_201812.csv   (12.8M registros)
└── seu_arquivo.csv  (adicione seus arquivos aqui)
```

### 2. **Acessar Interface de Visualização**

1. Inicie a API: `python src/api.py`
2. Acesse: `http://localhost:8000/data-viewer.html`
3. Ou clique no link na página principal: **"📊 Ver Análise de Dados em Lote por Município"**

### 3. **Selecionar Arquivo para Processar**

A interface mostra todos os CSVs disponíveis com:
- 📄 Nome do arquivo
- 📊 Número de registros
- 📈 Número de colunas
- 💾 Tamanho em MB

Clique no arquivo que deseja analisar!

## 🚀 Funcionalidades

### ✅ Processamento Automático

O sistema automaticamente:

1. **Carrega o CSV** da pasta `data/`
2. **Aplica os modelos ML** (Random Forest + XGBoost) em todos os registros
3. **Classifica** cada família em: Baixa, Média, Alta ou Muito Alta vulnerabilidade
4. **Agrega por município** todas as estatísticas

### 📊 Visualização por Município

Para cada município, exibe:

- **Código do município**
- **Total de famílias** cadastradas
- **Distribuição de vulnerabilidade** (com barras coloridas):
  - 🔴 Muito Alta
  - 🟠 Alta
  - 🟡 Média
  - 🟢 Baixa
- **Indicadores socioeconômicos**:
  - 💰 Renda per capita média
  - 👥 Tamanho médio da família
  - 👴 Idade média
  - 🎫 % que recebe Bolsa Família

### 🤖 Análise Interpretativa com IA (Google Gemini)

O sistema gera uma **análise completa usando LLM** que inclui:

1. **Panorama Geral**: Visão agregada da vulnerabilidade social
2. **Municípios Críticos**: Identificação de prioridades
3. **Indicadores Socioeconômicos**: Análise de padrões
4. **Recomendações**: Sugestões de políticas públicas específicas
5. **Próximos Passos**: Orientações para gestores

## 🔗 Endpoints da API

### `GET /data/files`
Lista todos os arquivos CSV disponíveis na pasta `data/`

**Resposta:**
```json
{
  "arquivos": [
    {
      "nome": "cadunico_processado_100000.csv",
      "caminho_relativo": "cadunico_processado_100000.csv",
      "tamanho_mb": 0.24,
      "linhas": 2355,
      "colunas": 22
    }
  ],
  "total": 1,
  "timestamp": "2025-11-24T01:29:21.637005"
}
```

### `GET /data/process/{filename}`
Processa um arquivo CSV e retorna estatísticas gerais

**Parâmetros:**
- `filename`: Nome do arquivo (ex: `cadunico_processado_100000.csv`)
- `max_rows` (opcional): Limitar número de linhas

**Resposta:**
```json
{
  "arquivo": "cadunico_processado_100000.csv",
  "processado_em": "2025-11-24T01:30:00.000000",
  "estatisticas": {
    "total_registros": 2355,
    "distribuicao_rf": {
      "Muito Alta": 1294,
      "Alta": 830,
      "Média": 194,
      "Baixa": 37
    },
    "distribuicao_xgb": { ... },
    "estatisticas_gerais": {
      "idade_media": 40.3,
      "renda_per_capita_media": 171.63,
      "tamanho_familia_medio": 2.9,
      "recebem_bolsa_familia": 1216,
      "percentual_bolsa_familia": 51.6
    }
  }
}
```

### `GET /data/analyze-municipality`
Analisa dados agregados por município **com análise LLM**

**Parâmetros:**
- `filename`: Nome do arquivo (padrão: `cadunico_processado_100000.csv`)
- `max_rows` (opcional): Limitar número de linhas

**Resposta:**
```json
{
  "arquivo": "cadunico_processado_100000.csv",
  "total_registros": 2355,
  "total_municipios": 42,
  "municipios": [
    {
      "codigo_municipio": 123456,
      "total_familias": 150,
      "vulnerabilidade": {
        "Baixa": 5,
        "Média": 15,
        "Alta": 60,
        "Muito Alta": 70
      },
      "vulnerabilidade_percentual": {
        "Baixa": 3.3,
        "Média": 10.0,
        "Alta": 40.0,
        "Muito Alta": 46.7
      },
      "indicadores": {
        "idade_media": 38.5,
        "renda_per_capita_media": 150.75,
        "tamanho_familia_medio": 3.2,
        "percentual_bolsa_familia": 55.0,
        "total_bolsa_familia": 83
      }
    }
  ],
  "analise_llm": "Análise interpretativa completa gerada pelo Google Gemini...",
  "processado_em": "2025-11-24T01:35:00.000000"
}
```

## 💡 Vantagens

### ✅ **Sem Limite de Tamanho**
- Não há limite de 1MB do upload
- Processa arquivos gigantes (milhões de registros)
- Performance otimizada para grandes volumes

### ✅ **Processamento em Lote**
- Classifica todas as famílias de uma vez
- Agrega estatísticas por município automaticamente
- Gera insights agregados

### ✅ **Análise Inteligente com IA**
- LLM analisa os dados agregados
- Identifica padrões e tendências
- Fornece recomendações práticas
- Linguagem natural e acessível

### ✅ **Visualização Intuitiva**
- Cards coloridos por município
- Barras de progresso para vulnerabilidade
- Estatísticas claras e objetivas
- Interface responsiva

## 🎯 Casos de Uso

### 1. **Gestor Público Municipal**
- Analisa vulnerabilidade do seu município
- Compara com outros municípios
- Identifica áreas prioritárias
- Planeja políticas públicas

### 2. **Analista de Dados**
- Processa grandes bases do CadÚnico
- Gera relatórios agregados
- Identifica padrões regionais
- Exporta insights

### 3. **Pesquisador**
- Analisa dados socioeconômicos
- Estuda vulnerabilidade social
- Compara municípios/regiões
- Valida hipóteses com dados reais

## 📋 Requisitos

### Estrutura do CSV

O arquivo CSV deve conter as seguintes colunas:

**Obrigatórias:**
- `cod_municipio`: Código IBGE do município
- `idade`: Idade do responsável
- `renda_per_capita`: Renda per capita
- `qtd_pessoas_familia`: Número de pessoas na família
- `recebe_bolsa_familia`: 0 ou 1

**Recomendadas (para melhor análise):**
- `sexo`: M ou F
- `escolaridade`: Nível de escolaridade (0-5)
- `situacao_trabalho`: 0=desempregado, 1=informal, 2=formal
- `tipo_moradia`: Tipo de moradia
- `acesso_agua`: Acesso a água encanada
- `acesso_esgoto`: Acesso a esgoto

## 🔧 Configuração

### API Key do Google Gemini (Opcional)

Para habilitar a análise LLM:

```bash
export GEMINI_API_KEY='sua-chave-aqui'
```

Sem a API key, o sistema funciona normalmente, mas não gera a análise interpretativa com IA.

## 📈 Performance

O sistema foi otimizado para processar grandes volumes:

- ✅ **2.355 registros**: ~2-3 segundos
- ✅ **100.000 registros**: ~30-40 segundos
- ✅ **1.000.000 registros**: ~5-7 minutos

*Tempos aproximados em ambiente de desenvolvimento*

## 🚀 Próximos Passos

Possíveis melhorias futuras:

1. **Export para Excel/PDF**: Baixar relatórios
2. **Filtros avançados**: Filtrar por região, vulnerabilidade, etc.
3. **Gráficos interativos**: Visualizações com Chart.js
4. **Comparação temporal**: Analisar evolução ao longo do tempo
5. **API de webhook**: Notificar quando processamento terminar
6. **Cache de resultados**: Não reprocessar arquivos já analisados

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs da API
2. Acesse `/docs` para documentação interativa
3. Teste os endpoints manualmente
4. Verifique se a API key está configurada (para análise LLM)

---

**Desenvolvido com ❤️ para análise de vulnerabilidade social**
