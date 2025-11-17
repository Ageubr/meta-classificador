# 📚 Documentação do Sistema de Análise de Vulnerabilidade Social

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Instalação](#instalação)
4. [Uso da API](#uso-da-api)
5. [Interface Web](#interface-web)
6. [Modelos ML](#modelos-ml)
7. [Integração LLM](#integração-llm)
8. [Desenvolvimento](#desenvolvimento)

---

## 🎯 Visão Geral

Sistema de classificação de vulnerabilidade social utilizando:
- **Machine Learning**: Random Forest e XGBoost (99.15% acurácia)
- **LLM**: Google Gemini para análise qualitativa
- **Dados Reais**: 2.355 registros do CadÚnico
- **API REST**: FastAPI com 7 endpoints

---

## 🏗️ Arquitetura

```
meta-classificador/
├── src/                          # Código-fonte
│   ├── api.py                    # API REST (FastAPI)
│   ├── preprocessamento.py       # Processamento de dados
│   ├── modelos_ml.py            # Modelos de ML
│   └── meta_classificador_llm.py # Integração LLM
├── data/                         # Dados
│   └── cadunico_processado_100000.csv
├── outputs/                      # Resultados
│   └── modelos/                 # Modelos treinados
├── frontend/                     # Interface web
├── docs/                         # Documentação
└── tests/                        # Testes
```

---

## 🚀 Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/Ageubr/meta-classificador.git
cd meta-classificador
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar API Gemini
```bash
# Criar arquivo .env
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
echo "GEMINI_MODEL=gemini-2.0-flash" >> .env
```

### 4. Iniciar a API
```bash
python src/api.py
```

A API estará disponível em: http://localhost:8000

---

## 🌐 Uso da API

### Endpoints Disponíveis

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "models": {
    "random_forest": true,
    "xgboost": true,
    "meta_classificador": true
  }
}
```

#### 2. Predição de Vulnerabilidade
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "idade_responsavel": 28,
    "numero_membros": 4,
    "criancas": 2,
    "idosos": 0,
    "renda_per_capita": 120.00,
    "pessoas_trabalhando": 1,
    "possui_agua_encanada": true,
    "possui_esgoto": false,
    "possui_coleta_lixo": true,
    "possui_energia": true,
    "material_parede": "Madeira",
    "material_teto": "Telha",
    "comodos": 3,
    "possui_banheiro": true,
    "tempo_residencia": 18,
    "recebe_bolsa_familia": true,
    "valor_bolsa_familia": 200.00,
    "nivel_escolaridade": "Ensino Médio",
    "situacao_trabalho": "Empregado Informal"
  }'
```

**Resposta:**
```json
{
  "vulnerabilidade_rf": "Alta",
  "vulnerabilidade_xgb": "Baixa",
  "probabilidade_rf": {
    "Baixa": 0.09,
    "Média": 0.10,
    "Alta": 0.63
  },
  "probabilidade_xgb": {
    "Baixa": 0.98,
    "Média": 0.01,
    "Alta": 0.00
  }
}
```

#### 3. Análise com LLM
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{...}'
```

Retorna análise qualitativa detalhada usando Google Gemini.

---

## 🖥️ Interface Web

Acesse a interface web em: http://localhost:8000/

Recursos:
- ✅ Formulário intuitivo para entrada de dados
- ✅ Visualização de resultados em tempo real
- ✅ Gráficos de probabilidades
- ✅ Análise LLM formatada
- ✅ Design responsivo

---

## 🤖 Modelos ML

### Random Forest
- **Acurácia**: 98.73%
- **Tipo**: Ensemble de árvores de decisão
- **Features**: 15 variáveis socioeconômicas

### XGBoost
- **Acurácia**: 99.15%
- **Tipo**: Gradient Boosting
- **Otimizado**: Hiperparâmetros ajustados

### Classificação
- **Baixa**: Renda adequada, infraestrutura completa
- **Média**: Vulnerabilidades moderadas
- **Alta**: Múltiplas vulnerabilidades críticas

---

## 🧠 Integração LLM

### Google Gemini API
- **Modelo**: gemini-2.0-flash
- **Custo**: GRATUITO (1M tokens/mês)
- **Função**: Análise qualitativa e recomendações

### Configuração
```bash
# Obter chave em: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="sua_chave_aqui"
```

---

## 🔧 Desenvolvimento

### Executar testes
```bash
pytest tests/ -v
```

### Cobertura de código
```bash
pytest --cov=src tests/
```

### Documentação da API
```bash
# Acesse após iniciar a API
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## 📊 Dados

Os dados utilizados são do **CadÚnico** (Cadastro Único para Programas Sociais):
- 2.355 registros processados
- 15 features de vulnerabilidade
- Dados anonimizados

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 📞 Contato

- **Autor**: Ageubr
- **GitHub**: https://github.com/Ageubr
- **Repositório**: https://github.com/Ageubr/meta-classificador

---

## 📚 Documentos Adicionais

- [Análise Completa](ANALISE_COMPLETA.md) - Análise detalhada do sistema
- [Guia Gemini](GUIA_GEMINI.md) - Configuração do LLM
- [Mapeamento de Dados](MAPEAMENTO_DADOS.md) - Estrutura dos dados
- [TODO](TODO.md) - Lista de tarefas e melhorias
