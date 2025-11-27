# 🏠 Sistema de Meta-Classificação de Vulnerabilidade Social

![Status](https://img.shields.io/badge/status-operational-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![ML](https://img.shields.io/badge/ML-99.15%25%20accuracy-success)
![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-purple)

Sistema inteligente para classificação e análise de vulnerabilidade social utilizando Machine Learning e LLMs.

## ✨ Características


## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/Ageubr/meta-classificador.git
cd meta-classificador

# Instale as dependências
pip install -r requirements.txt

# Configure a API Gemini (gratuita)
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
echo "GEMINI_MODEL=gemini-2.0-flash" >> .env
```

### 2. Inicie o Sistema

```bash
# Inicie a API
python src/api.py
```

### 3. Acesse a Interface

Abra seu navegador em: **http://localhost:8000**

Ou acesse a documentação da API: **http://localhost:8000/docs**

## 🎯 Como Usar

### Interface Web

1. Acesse http://localhost:8000
2. Preencha os dados da família no formulário
3. Clique em "🤖 Analisar Vulnerabilidade" para predição ML
4. Clique em "🧠 Análise com IA" para análise qualitativa detalhada

### API REST

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"idade_responsavel": 28, ...}'
```

## 📡 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface web |
# Meta-Classificador de Vulnerabilidade Social

Projeto para classificação e análise de vulnerabilidade social usando modelos de Machine Learning (Random Forest, XGBoost) e análise interpretativa com LLMs.

**Objetivo:** prover predições automatizadas e relatórios interpretáveis para apoiar gestão pública e programas sociais.

**Status:** código em desenvolvimento — leia as instruções de uso e variáveis de ambiente antes de executar.

**Principais arquivos:** `src/api.py`, `src/preprocessamento.py`, `src/modelos_ml.py`, `frontend/` e `outputs/modelos/`.

**Requisitos:**

**Instalação rápida**

1. Clone o repositório e crie um ambiente virtual:

```bash
git clone https://github.com/Ageubr/meta-classificador.git
cd meta-classificador
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure variáveis de ambiente (opcional para funcionalidades LLM):

```bash
# Exemplo mínimo no arquivo .env
GOOGLE_API_KEY=SuaChaveAqui
# Outras variáveis opcionais podem ser carregadas pelo código
```

Observação: o projeto usa integração com APIs de LLM (Google Generative AI). Sem chave de API a parte de análise LLM ficará indisponível, mas endpoints ML continuam funcionais se os modelos estiverem presentes em `outputs/modelos/`.

**Como executar**


```bash
./iniciar.sh
```


```bash
python src/api.py
# ou (alternativa) uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```


```bash
./run_frontend.sh
```

Após iniciar a API, abra `http://localhost:8000/` no navegador. A documentação interativa da API fica em `http://localhost:8000/docs`.

**Principais endpoints**

Consulte `src/api.py` para documentação mais detalhada das entradas esperadas (modelos Pydantic estão definidos lá).

**Estrutura do repositório (resumo)**

**Testes**

Execute a suíte de testes com:

```bash
pytest
```

**Contribuição**

Pull requests são bem-vindos. Para grandes mudanças, abra uma issue primeiro descrevendo a proposta.

**Scripts úteis**

**Licença**

# 🏠 Meta-Classificador de Vulnerabilidade Social

Projeto para classificação e análise de vulnerabilidade social que combina modelos de Machine Learning (Random Forest, XGBoost) com uma camada interpretativa baseada em LLM (Google Gemini). O objetivo é oferecer predições robustas e explicações acionáveis para suporte a políticas públicas e programas sociais.

---

**Este README foi escrito seguindo o comportamento do código presente em `src/` (principalmente `src/api.py` e `src/meta_classificador_llm.py`).**

## Conceito e objetivo

- Conceito: o sistema opera em duas camadas complementares — uma camada ML (modelos supervisados que classificam níveis de vulnerabilidade) e uma camada LLM (um "meta-classificador" que recebe os dados e as saídas dos modelos para gerar justificativas, fatores de risco e recomendações).
- Objetivo: identificar famílias/municípios em situação de vulnerabilidade, gerar análises interpretáveis e facilitar integração via API REST.

## Principais características (alinhado ao código)

- Predição multi-modelo: Random Forest e XGBoost (arquivos esperados em `outputs/modelos/`).
- Meta-classificação por LLM: integração com Google Gemini usando variável de ambiente `GEMINI_API_KEY` (opcional).
- Endpoints REST com FastAPI (arquivo `src/api.py`).
- Processamento em lote e agregação por município (`/data/process`, `/data/analyze-municipality`).
- Frontend estático servido pela API (pasta `frontend/`).
- Scripts auxiliares: `iniciar.sh`, `run_frontend.sh`.

## Requisitos

- Python 3.10+ recomendado
- Dependências listadas em `requirements.txt` (pandas, scikit-learn, xgboost, google-generativeai, fastapi, uvicorn, python-dotenv, joblib, etc.)

## Variáveis de ambiente importantes

- `GEMINI_API_KEY` — chave da API Google Generative AI usada pelo `MetaClassificadorLLM` (nome usado no código: `GEMINI_API_KEY`).
- `GEMINI_MODEL` — (opcional) modelo Gemini a ser usado (ex.: `gemini-2.0-flash`).

Observação prática: alguns scripts no repositório (ex.: `iniciar.sh`) referenciam `GOOGLE_API_KEY`; para evitar problemas locais, você pode definir ambas (`GEMINI_API_KEY` e `GOOGLE_API_KEY`) no seu `.env` se quiser usar os scripts.

## Nomes e formato esperado dos arquivos de modelo

A API tenta carregar arquivos em `outputs/modelos/`:

- `random_forest_vulnerabilidade.pkl`
- `xgboost_vulnerabilidade.pkl`

Formato esperado (ao salvar com `joblib.dump`): um dicionário com chaves típicas:

- `modelo`: o objeto do modelo (estimator) — usado por `api.py` e por `MetaClassificadorLLM`.
- `scaler`: (opcional, usado pelo `MetaClassificadorLLM`) scaler/transfomer para aplicar às features antes de predizer.
- `features`: (opcional) lista de nomes das features usadas no modelo — usada em `api.py` para mostrar importâncias.
- `metricas`: (opcional) métricas do modelo (accuracy, f1, etc.)

Exemplo de estrutura ao salvar:

```python
joblib.dump({'modelo': clf, 'scaler': scaler, 'features': feature_names, 'metricas': metrics}, 'outputs/modelos/random_forest_vulnerabilidade.pkl')
```

Se os arquivos não estiverem presentes, a API inicializa, mas alguns endpoints retornarão status de "não carregado".

## Como executar (local)

1. Crie ambiente e instale dependências:

```bash
git clone https://github.com/Ageubr/meta-classificador.git
cd meta-classificador
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure o `.env` (opcional, necessário para LLM):

```bash
# Exemplo mínimo
GEMINI_API_KEY=SuaChaveAqui
GEMINI_MODEL=gemini-2.0-flash
# (opcional) GOOGLE_API_KEY=SuaChaveAqui  # para compatibilidade com scripts
```

3. Inicie a API:

```bash
# Usando o script
./iniciar.sh
# Ou diretamente
python src/api.py
# Alternativamente (uvicorn):
# uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

4. Acesse:

- Frontend: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints principais (resumo e exemplos)

### 1) `GET /health`
Retorna o status geral e se os modelos foram carregados. Exemplo de resposta:

```json
{
  "status": "healthy",
  "models": {
    "random_forest": true,
    "xgboost": true,
    "meta_classificador": true
  },
  "timestamp": "2025-11-26T..."
}
```

### 2) `POST /predict`
Predição ML para um único registro. O corpo deve seguir o Pydantic `DadosFamilia` definido em `src/api.py` — campos essenciais:

- `idade_responsavel` (int)
- `numero_membros` (int)
- `criancas` (int)
- `idosos` (int)
- `renda_per_capita` (float)
- `pessoas_trabalhando` (int)
- `possui_agua_encanada`, `possui_esgoto`, `possui_coleta_lixo`, `possui_energia` (bool)
- `material_parede`, `material_teto` (str)
- `comodos` (int)
- `possui_banheiro` (bool)
- `tempo_residencia` (int, meses)
- `recebe_bolsa_familia` (bool)
- `valor_bolsa_familia` (float)
- `nivel_escolaridade` (str)
- `situacao_trabalho` (str)

Exemplo de request:

```json
{
  "idade_responsavel": 35,
  "numero_membros": 4,
  "criancas": 1,
  "idosos": 0,
  "renda_per_capita": 250.0,
  "pessoas_trabalhando": 1,
  "possui_agua_encanada": true,
  "possui_esgoto": false,
  "possui_coleta_lixo": true,
  "possui_energia": true,
  "material_parede": "Alvenaria",
  "material_teto": "Telha",
  "comodos": 3,
  "possui_banheiro": true,
  "tempo_residencia": 36,
  "recebe_bolsa_familia": false,
  "valor_bolsa_familia": 0.0,
  "nivel_escolaridade": "Fundamental",
  "situacao_trabalho": "Informal"
}
```

Exemplo de resposta (modelo `PredictionResponse` em `src/api.py`):

```json
{
  "vulnerabilidade_rf": "Média",
  "vulnerabilidade_xgb": "Alta",
  "probabilidade_rf": {"Baixa": 0.1, "Média": 0.7, "Alta": 0.2},
  "probabilidade_xgb": {"Baixa": 0.05, "Média": 0.25, "Alta": 0.7},
  "features_importantes": {"renda_per_capita": 0.35, "idade": 0.25},
  "timestamp": "2025-11-26T..."
}
```

> Observação: o `api.py` mapeia alguns campos de entrada para os nomes de feature esperados pelo preprocessamento (ex.: `idade_responsavel` → `idade`, `numero_membros` → `qtd_pessoas_familia`, etc.).

### 3) `POST /analyze`
Executa predições ML e, se configurado, chama o meta-classificador LLM para gerar uma análise interpretativa. Resposta inclui `analise_llm` com o texto gerado (ou mensagem informando indisponibilidade se a chave não estiver configurada).

Exemplo (resumo):

```json
{
  "predicao_rf": "Média",
  "predicao_xgb": "Alta",
  "probabilidades_rf": {"Baixa": 0.1, "Média": 0.7, "Alta": 0.2},
  "probabilidades_xgb": {"Baixa": 0.05, "Média": 0.25, "Alta": 0.7},
  "analise_llm": "<texto gerado pela LLM com justificativa e recomendações>",
  "timestamp": "2025-11-26T..."
}
```

### 4) Endpoints de processamento em lote
- `GET /data/files` — lista arquivos CSV em `data/`.
- `GET /data/process?filepath=<caminho>` — processa um CSV e aplica predições ML.
- `GET /data/analyze-municipality?filepath=<caminho>` — agrega resultados por município e, se disponível, gera análise LLM consolidada.

Consulte `src/api.py` para parâmetros adicionais (por exemplo `max_rows`).

## Detalhes técnicos úteis (para desenvolvedores)

- O `startup_event` em `src/api.py` tenta carregar os modelos em `outputs/modelos/` usando `joblib` ao inicializar a API. Se os arquivos não existirem, a API ainda roda, mas endpoints que dependem dos modelos devolverão erro de serviço (`503`).
- O `MetaClassificadorLLM` (arquivo `src/meta_classificador_llm.py`) busca `GEMINI_API_KEY` e só tenta chamar a API Gemini se o pacote `google.generativeai` estiver instalado e a chave estiver disponível.
- A função `predizer_modelos_ml` no meta-classificador espera um conjunto de features nomeadas (lista definida no código). Se você treinar novos modelos, garanta que o conjunto de features e os scalers usados sejam consistentes com o que o código espera.

Features esperadas (exemplo retirado do código):

```
['idade', 'escolaridade', 'renda_per_capita', 'qtd_pessoas_familia',
 'possui_deficiencia', 'situacao_trabalho', 'tipo_moradia',
 'acesso_agua', 'acesso_esgoto', 'vulnerabilidade_idade',
 'infraestrutura_adequada', 'escolaridade_baixa',
 'situacao_trabalho_precaria', 'superlotacao', 'recebe_bolsa_familia']
```

## Boas práticas e privacidade

- Não comite chaves de API no repositório. Use `.env` e `.gitignore`.
- Ao processar dados pessoais, assegure anonimização e conformidade com a legislação aplicável.

## Testes

- Há testes em `tests/`. Execute com `pytest`.

## Próximos passos que posso ajudar a implementar

- Incluir exemplos de `response` mais detalhados para cada endpoint;
- Adicionar um exemplo de script para treinar e salvar modelos no formato esperado;
- Adicionar um `Dockerfile` e `docker-compose.yml` para deploy local.

---

Se quiser, atualizo o `iniciar.sh` para usar `GEMINI_API_KEY` (atualmente o script referencia `GOOGLE_API_KEY`) e adiciono um exemplo de como salvar modelos (`joblib.dump`) com a estrutura esperada — quer que eu faça isso agora?

## Informações do sistema (resumo das notas do desenvolvedor)

Estas informações foram fornecidas pela equipe de desenvolvimento e refletem decisões de modelagem, parâmetros de treino e comportamento do sistema:

- Dados: o sistema processa dados REAIS do governo (CadÚnico) para gerar features e alimentar os modelos.
- Classificação em 4 níveis (mapeamento a partir de um score):
  - Score < -0.5 → **Baixa**
  - -0.5 a 0 → **Média**
  - 0 a 0.5 → **Alta**
  - Score > 0.5 → **Muito Alta**

- Treinamento Random Forest (configuração utilizada):
  - 100 árvores de decisão
  - Split: 80% treino / 20% teste
  - Validação: cross-validation com 5 folds
  - Objetivo: aprender padrões nos dados para prever vulnerabilidade sem precisar calcular score manualmente

- Configuração e diferenças entre modelos (Random Forest vs XGBoost):
  - Random Forest
    - Método: Bagging (árvores paralelas independentes)
    - 100 árvores construídas ao mesmo tempo
    - Cada árvore vota; a maioria decide a classe final
    - Vantagem: mais robusto e menos propenso a overfitting em muitos cenários
  - XGBoost (Extreme Gradient Boosting)
    - Método: Boosting (árvores sequenciais)
    - 100 árvores construídas em sequência
    - Cada nova árvore corrige erros das anteriores
    - Otimização via gradient descent
    - Parâmetros típicos: learning_rate = 0.1, early stopping (para interromper quando não houver melhora)

- Features mais importantes identificadas (exemplos):
  - `renda_per_capita`
  - `idade`
  - `nivel_escolaridade` / `escolaridade`
  - `acesso_agua` / `acesso_esgoto` / infraestrutura
  - `situacao_trabalho`

- Comportamento: o modelo fornece predições diretas (classes) baseadas nas features, dispensando cálculo manual do score para classificar famílias.

- Comandos úteis (scripts existentes):
  - `./iniciar.sh` — iniciar o sistema (API + verificações)
  - `./status.sh` — checar status dos serviços/modelos

- Checklist fornecido pela equipe (status do projeto):
  - ✅ Frontend rodando (`index.html`, `data-viewer.html`)
  - ✅ API com Random Forest + XGBoost
  - ✅ Meta-classificador LLM (Google Gemini)
  - ✅ Análise individual e em lote por município
  - ✅ Código limpo e documentado
  - ✅ Scripts úteis (`iniciar.sh`, `status.sh`)
