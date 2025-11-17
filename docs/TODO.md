# 📋 Lista de Tarefas - Meta-Classificador de Vulnerabilidade Social

## 🚀 Próximos Passos

### ⚠️ Prioridade Alta

- [ ] **1. Configurar OPENAI_API_KEY para análise LLM completa**
  - Obter chave de API da OpenAI
  - Configurar variável de ambiente: `export OPENAI_API_KEY='sk-...'`
  - Testar análise completa com ChatGPT
  - Validar resposta do LLM para casos de teste
  - Documentar custo estimado por análise

- [ ] **2. Testar API REST em execução**
  - Iniciar servidor FastAPI: `python src/api.py`
  - Testar endpoint `/health`
  - Testar endpoint `/predict` com dados reais
  - Testar endpoint `/analyze` (com API key configurada)
  - Testar endpoint `/predict-batch`
  - Validar documentação automática em `/docs`
  - Medir tempo de resposta
  - Testar limites de concorrência

### 📝 Prioridade Média

- [ ] **3. Implementar testes automatizados**
  - Criar testes unitários para `preprocessamento.py`
    - Teste de carregamento de dados
    - Teste de geração de features
    - Teste de tratamento de dados faltantes
  - Criar testes unitários para `modelos_ml.py`
    - Teste de treinamento de modelos
    - Teste de predições
    - Teste de salvamento/carregamento
  - Criar testes unitários para `meta_classificador_llm.py`
    - Teste de carregamento de modelos
    - Teste de geração de prompts
    - Mock para testes sem API key
  - Criar testes de integração
    - Teste de pipeline completo
    - Teste de API endpoints
  - Configurar cobertura de código (pytest-cov)
  - Meta: atingir 80%+ de cobertura

### 🎨 Prioridade Baixa

- [ ] **4. Criar interface web para usuários finais**
  - **Backend:**
    - Criar endpoints adicionais se necessário
    - Implementar autenticação de usuários
    - Implementar upload de arquivos CSV
  - **Frontend:**
    - Escolher framework (React, Vue, ou Streamlit)
    - Criar página de análise individual
    - Criar página de análise em lote
    - Criar dashboard com estatísticas
    - Implementar visualizações interativas
    - Criar página de histórico de análises
  - **Deploy:**
    - Containerizar aplicação (Docker)
    - Configurar CI/CD
    - Deploy em ambiente de produção

- [ ] **5. Adicionar mais dados para treinamento contínuo**
  - Buscar mais dados públicos do CadÚnico
  - Integrar com API do Bolsa Família (se disponível)
  - Implementar pipeline de atualização de dados
  - Criar script de retreinamento automático
  - Implementar versionamento de modelos
  - Monitorar drift de dados
  - Criar alertas de degradação de performance

## 📊 Melhorias Futuras

### Performance
- [ ] Otimizar tempo de resposta da API
- [ ] Implementar cache para predições recorrentes
- [ ] Paralelizar processamento em lote

### Funcionalidades
- [ ] Adicionar explicabilidade (SHAP, LIME)
- [ ] Implementar análise de série temporal
- [ ] Criar relatórios em PDF
- [ ] Adicionar exportação para Excel
- [ ] Implementar sistema de alertas

### Monitoramento
- [ ] Implementar logging estruturado
- [ ] Adicionar métricas de uso (Prometheus)
- [ ] Criar dashboard de monitoramento
- [ ] Implementar alertas de erro

### Segurança
- [ ] Implementar rate limiting
- [ ] Adicionar validação de entrada
- [ ] Implementar criptografia de dados sensíveis
- [ ] Auditoria de acessos
- [ ] Conformidade com LGPD

## ✅ Concluídas

- [x] Análise completa do sistema
- [x] Carregamento de dados reais do CSV
- [x] Treinamento de modelos ML (RF e XGBoost)
- [x] Implementação do meta-classificador LLM
- [x] Correção de bug no carregamento de modelos
- [x] Implementação da API REST
- [x] Criação de documentação técnica
- [x] Criação de script de demonstração

---

**Última atualização:** 14 de novembro de 2025
