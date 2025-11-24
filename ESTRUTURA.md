# 📁 Estrutura do Projeto - Meta-Classificador

## 📂 Diretórios Principais

### `/src` - Código Fonte Principal
```
src/
├── api.py                      # FastAPI - API REST principal
├── modelos_ml.py               # Random Forest & XGBoost  
├── meta_classificador_llm.py   # Google Gemini (LLM)
├── preprocessamento.py         # Processamento e features
├── mapeador_governo.py         # Mapeia dados CadÚnico
├── conversor_dados_governo.py  # Converte formatos governo
└── municipios_ibge.py          # Cache de municípios
```

### `/frontend` - Interface Web
```
frontend/
├── index.html           # 🏠 Página principal (análise individual)
├── script.js            # Lógica da página principal
├── data-viewer.html     # 📊 Visualizador em lote (municípios)
├── data-viewer.js       # Lógica do visualizador
└── styles.css           # Estilos CSS compartilhados
```

### `/data` - Dados de Entrada
```
data/
└── base_amostra_cad_201812/    # Dados CadÚnico (amostra oficial)
    └── base_amostra_familia_201812.csv
```

### `/outputs` - Saídas do Sistema
```
outputs/
├── modelos/
│   ├── random_forest_vulnerabilidade.pkl  # Modelo RF treinado
│   ├── xgboost_vulnerabilidade.pkl        # Modelo XGB treinado
│   └── metricas_modelos.json              # Métricas de performance
└── relatorios/                            # Relatórios gerados
```

### `/docs` - Documentação
```
docs/
├── README.md              # Índice da documentação
├── GUIA_GEMINI.md         # Como configurar Google Gemini
├── ANALISE_COMPLETA.md    # Análise técnica detalhada
└── TODO.md                # Melhorias futuras
```

### `/tests` - Testes Automatizados
```
tests/
├── __init__.py
├── test_modelos_ml.py         # Testes dos modelos ML
└── test_preprocessamento.py   # Testes de preprocessamento
```

## 📄 Arquivos na Raiz

### Essenciais
- **`.env`** - Configurações (API keys) - **NÃO VERSIONAR**
- **`requirements.txt`** - Dependências Python
- **`pyproject.toml`** - Configuração do projeto
- **`README.md`** - Documentação principal

### Scripts Úteis
- **`iniciar.sh`** - Iniciar sistema (com verificações)
- **`run_frontend.sh`** - Atalho para iniciar apenas frontend
- **`limpar_projeto.sh`** - Limpar cache e arquivos temporários

### Configuração
- **`.gitignore`** - Arquivos ignorados no Git
- **`.pylintrc`** - Configuração do linter
- **`.env.example`** - Template para .env

## 🗑️ Arquivos Removidos (em `.backup_old_files/`)

Arquivos movidos para backup durante a limpeza:

### Scripts de Exemplo (não usados)
- `demo_sistema_completo.py`
- `exemplo_completo.py`
- `exemplo_uso_llm.py`

### Scripts Redundantes
- `configurar_env.py`
- `fix_formatting.py`
- `inicializar.sh` (antigo)
- `start.sh` (antigo)
- `setup_gemini.sh`

### Código Não Utilizado
- `src/adaptar_dados_reais.py`
- `src/validador_sistema.py`
- `src/api.py.backup`

### Documentação Antiga
- `README.old.md`
- `RELATORIO_ANALISE.md`
- `RESULTADO_ANALISE.md`
- Documentos redundantes em `docs/`

### Cache e Temporários (removidos)
- `src/__pycache__/`
- `tests/__pycache__/`
- `.pytest_cache/`
- `htmlcov/`
- `.coverage`
- `api.log`

## 🎯 Como Navegar no Projeto

### Para Desenvolver:
1. **Backend/API**: Comece em `src/api.py`
2. **Modelos ML**: Veja `src/modelos_ml.py`
3. **LLM**: Explore `src/meta_classificador_llm.py`
4. **Frontend**: Arquivos em `frontend/`

### Para Usar:
1. Execute: `./iniciar.sh`
2. Acesse: `http://localhost:8000`
3. Consulte: `README.md` para instruções

### Para Testar:
```bash
pytest tests/
```

### Para Limpar:
```bash
./limpar_projeto.sh
```

## 📊 Métricas da Limpeza

**Antes:**
- ✗ 35+ arquivos na raiz
- ✗ Múltiplos scripts redundantes
- ✗ Documentação espalhada
- ✗ Cache misturado com código

**Depois:**
- ✓ 25 arquivos essenciais
- ✓ Estrutura clara e organizada
- ✓ Documentação centralizada
- ✓ Cache limpo automaticamente

## 🔍 Encontrando Funcionalidades

| Funcionalidade | Arquivo |
|----------------|---------|
| Iniciar sistema | `iniciar.sh` |
| API REST | `src/api.py` |
| Treinar modelos | `src/modelos_ml.py` |
| Análise com IA | `src/meta_classificador_llm.py` |
| Processar dados | `src/preprocessamento.py` |
| Frontend individual | `frontend/index.html` |
| Frontend em lote | `frontend/data-viewer.html` |
| Testes | `tests/*.py` |
| Documentação | `docs/*.md` |

---

**Última atualização:** Novembro 2025
**Status:** 🟢 Organizado e limpo
