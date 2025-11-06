# Sistema de Análise de Vulnerabilidade Social

Sistema avançado para análise de vulnerabilidade social usando dados públicos do CadÚnico e Bolsa Família, combinando modelos de Machine Learning tradicionais com Large Language Models (LLMs) para classificações mais interpretáveis e explicações detalhadas.

## 🎯 Objetivos

- **Classificação automática** de níveis de vulnerabilidade social (Baixa, Média, Alta, Muito Alta)
- **Análise interpretável** usando LLMs para explicações detalhadas 
- **Identificação de fatores de risco** e protetivos para cada indivíduo
- **Recomendações personalizadas** de políticas públicas e intervenções
- **Monitoramento** de indicadores sociais para acompanhamento

## 🏗️ Arquitetura do Sistema

```
sistema-vulnerabilidade-social/
├── data/                    # Dados de entrada (CSV)
│   ├── cadunico.csv        # Dados do CadÚnico
│   └── bolsa_familia.csv   # Dados do Bolsa Família
├── src/                    # Código fonte
│   ├── preprocessamento.py     # Limpeza e preparação dos dados
│   ├── modelos_ml.py          # Modelos Random Forest e XGBoost
│   └── meta_classificador_llm.py # Meta-classificador com LLM
├── outputs/                # Resultados e modelos treinados
│   ├── modelos/           # Modelos ML salvos
│   └── relatorios/        # Relatórios e visualizações
├── requirements.txt       # Dependências Python
└── README.md             # Esta documentação
```

## 🚀 Principais Funcionalidades

### 1. Preprocessamento de Dados (`preprocessamento.py`)
- **Carregamento automático** de dados do CadÚnico e Bolsa Família
- **Geração de dados fictícios** para testes quando arquivos reais não estão disponíveis
- **Tratamento de dados faltantes** com múltiplas estratégias
- **Engenharia de features** para vulnerabilidade social:
  - Renda per capita
  - Vulnerabilidade por idade (crianças/idosos)
  - Infraestrutura adequada (água/esgoto)
  - Escolaridade baixa
  - Situação de trabalho precária
  - Superlotação familiar
- **Score de vulnerabilidade** baseado em fatores ponderados

### 2. Modelos de Machine Learning (`modelos_ml.py`)
- **Random Forest** com otimização de hiperparâmetros
- **XGBoost** com early stopping e validação
- **Comparação automática** de performance entre modelos
- **Validação cruzada** para robustez das métricas
- **Salvamento/carregamento** de modelos treinados
- **Relatórios visuais** de importância das features

### 3. Meta-Classificador com LLM (`meta_classificador_llm.py`)
- **Integração com OpenAI** GPT-3.5/GPT-4
- **Combinação inteligente** de predições ML com análise LLM
- **Análises estruturadas** contendo:
  - Classificação final de vulnerabilidade
  - Fatores de risco identificados
  - Fatores protetivos
  - Recomendações de políticas públicas
  - Indicadores para monitoramento
- **Processamento em lote** para grandes volumes
- **Histórico de predições** para auditoria

## 📋 Pré-requisitos

- **Python 3.8+**
- **Chave da API OpenAI** (para funcionalidades de LLM)
- **8GB+ RAM** recomendado para processamento de grandes datasets

## 🛠️ Instalação

1. **Clone o repositório** (ou crie a estrutura de pastas):
```bash
mkdir sistema-vulnerabilidade-social
cd sistema-vulnerabilidade-social
```

2. **Crie e ative um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Configure a chave da API OpenAI** (opcional):
```bash
export OPENAI_API_KEY="sua-chave-api-aqui"
# No Windows: set OPENAI_API_KEY=sua-chave-api-aqui
```

## 🚀 Como Usar

### Uso Básico - Treinar Modelos

```python
# Executar do diretório raiz do projeto
cd src

# 1. Preprocessar dados e treinar modelos ML
python modelos_ml.py

# 2. Testar meta-classificador (modo simulação)
python meta_classificador_llm.py
```

### Uso Programático

```python
import sys
sys.path.append('src')

from preprocessamento import *
from modelos_ml import *
from meta_classificador_llm import MetaClassificadorLLM

# 1. Carregar e preparar dados
df_cadunico = carregar_dados_cadunico("data/cadunico.csv")
df_bolsa_familia = carregar_dados_bolsa_familia("data/bolsa_familia.csv")
df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa_familia)
X, y = preparar_dados_para_ml(df_features)

# 2. Treinar modelos ML
treinar_e_salvar_modelos(X, y)

# 3. Usar meta-classificador com LLM
meta_classificador = MetaClassificadorLLM()
meta_classificador.carregar_modelos_ml()

# Analisar uma pessoa específica
pessoa = df_features.iloc[0]  # Primeira pessoa do dataset
resultado = meta_classificador.classificar_vulnerabilidade(pessoa)

print("Análise completa:")
print(resultado['analise_llm'])
```

### Análise em Lote

```python
# Analisar múltiplas pessoas
resultados = meta_classificador.analisar_lote(df_features.head(10))

# Gerar relatório consolidado
relatorio = meta_classificador.gerar_relatorio_consolidado(resultados)
print(f"Total analisado: {relatorio['total_analisados']} pessoas")
```

## 📊 Formato dos Dados

### CadÚnico (`data/cadunico.csv`)
```csv
nis,nome,idade,sexo,escolaridade,renda_familiar,qtd_pessoas_familia,possui_deficiencia,situacao_trabalho,tipo_moradia,acesso_agua,acesso_esgoto,municipio
12345678901,João Silva,35,M,2,800.00,4,0,1,1,1,1,São Paulo
```

### Bolsa Família (`data/bolsa_familia.csv`)
```csv
nis,valor_beneficio,data_inicio_beneficio,status_beneficio,modalidade,municipio
12345678901,200.00,2023-01-15,ativo,básico,São Paulo
```

## 🔧 Configurações Avançadas

### Personalizando Modelos ML

```python
# Random Forest customizado
rf_custom = RandomForestVulnerabilidade(
    n_estimators=200,
    max_depth=15,
    random_state=42
)

# XGBoost customizado  
xgb_custom = XGBoostVulnerabilidade(
    n_estimators=150,
    max_depth=8,
    learning_rate=0.05
)
```

### Configurando LLM

```python
# Usar GPT-4 em vez de GPT-3.5
meta_classificador = MetaClassificadorLLM(
    modelo_llm="gpt-4",
    api_key="sua-chave-api"
)
```

## 📈 Métricas e Avaliação

O sistema gera automaticamente:

- **Acurácia de classificação** para cada modelo
- **Relatórios de classificação** detalhados (precision, recall, F1-score)
- **Matrizes de confusão** para análise de erros
- **Importância das features** para interpretabilidade
- **Validação cruzada** para robustez dos resultados

### Interpretando Resultados

- **Baixa vulnerabilidade**: Renda adequada, boa infraestrutura, emprego formal
- **Média vulnerabilidade**: Alguns fatores de risco presentes, mas situação estável
- **Alta vulnerabilidade**: Múltiplos fatores de risco, necessita intervenção
- **Muito Alta vulnerabilidade**: Situação crítica, necessita intervenção urgente

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## ⚠️ Considerações Éticas

- **Privacidade**: Todos os dados devem ser anonimizados antes do processamento
- **Viés**: Modelos devem ser regularmente auditados para evitar discriminação
- **Transparência**: Decisões automatizadas devem ser explicáveis e auditáveis
- **Consentimento**: Uso deve estar em conformidade com LGPD e regulamentações aplicáveis

## 📞 Suporte

Para questões, sugestões ou problemas:

- Abra uma **issue** no repositório
- Entre em contato com a equipe de desenvolvimento
- Consulte a documentação técnica nos comentários do código

## 🔄 Roadmap

- [ ] Interface web para análise interativa
- [ ] Integração com APIs governamentais
- [ ] Modelos de deep learning para melhor performance  
- [ ] Dashboard de monitoramento em tempo real
- [ ] Exportação para diferentes formatos (Excel, PDF)
- [ ] Testes automatizados e CI/CD

---

**Desenvolvido para apoiar políticas públicas baseadas em evidências e promover maior efetividade na redução da vulnerabilidade social no Brasil.**
Sistema Inteligente de Priorização e Análise de Vulnerabilidade Social
