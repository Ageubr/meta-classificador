# 🆓 Google Gemini - Guia Rápido

## ✅ Sistema Adaptado para Google Gemini API (GRATUITO!)

O sistema agora usa a **Google Gemini API** ao invés da OpenAI. Principais vantagens:

### 💰 100% Gratuito
- ✅ **Sem custo algum**
- ✅ **1 milhão de tokens por mês grátis**
- ✅ **1.500 requisições por dia**
- ✅ **60 requisições por minuto**
- ✅ **Sem cartão de crédito necessário**

### 🚀 Como Configurar (3 passos)

#### 1️⃣ Obter a Chave da API (GRÁTIS)

Acesse: **https://makersuite.google.com/app/apikey**

1. Faça login com sua conta Google
2. Clique em "Create API Key"
3. Copie a chave (começa com `AIza...`)

#### 2️⃣ Configurar no Sistema

**Opção A: Script Interativo** (mais fácil)
```bash
python configurar_env.py
```

**Opção B: Script Shell**
```bash
./setup_gemini.sh
```

**Opção C: Manual**
Edite o arquivo `.env`:
```bash
GEMINI_API_KEY=AIzaSy...sua-chave-aqui
GEMINI_MODEL=gemini-1.5-flash
```

#### 3️⃣ Testar

```bash
python demo_sistema_completo.py
```

## 📊 Modelos Disponíveis (todos gratuitos)

| Modelo | Características | Recomendação |
|--------|-----------------|--------------|
| **gemini-1.5-flash** | Mais rápido | ✅ **Recomendado** |
| gemini-1.5-pro | Mais poderoso | Para análises complexas |
| gemini-pro | Versão estável | Alternativa confiável |

## 🔧 Arquivos Modificados

```
✅ src/meta_classificador_llm.py  - Adaptado para Gemini
✅ requirements.txt                - google-generativeai
✅ .env                            - Template atualizado
✅ .env.example                    - Exemplo Gemini
✅ configurar_env.py               - Script atualizado
✅ setup_gemini.sh                 - Script shell novo
```

## 💡 Exemplo de Uso

```python
from meta_classificador_llm import MetaClassificadorLLM
from preprocessamento import carregar_dados_cadunico

# Carregar dados
df = carregar_dados_cadunico()

# Inicializar com Gemini (carrega automaticamente do .env)
meta = MetaClassificadorLLM()
meta.carregar_modelos_ml()

# Analisar caso
resultado = meta.classificar_vulnerabilidade(df.iloc[0])

# Ver análise completa (GRÁTIS!)
print(resultado['analise_llm'])
```

## 🎯 Estimativa de Uso Gratuito

Com **1 milhão de tokens/mês grátis**:

- Análise de 1 pessoa: ~1.500 tokens
- **Você pode analisar ~650 pessoas por mês DE GRAÇA!**
- Ou ~20 pessoas por dia

**Para o sistema de vulnerabilidade social, isso é mais que suficiente!**

## 🔒 Segurança

- ✅ `.env` está no `.gitignore`
- ✅ Chave nunca será commitada
- ✅ `.env.example` não contém credenciais
- ✅ Totalmente seguro para produção

## 📞 Links Úteis

- **Obter API Key**: https://makersuite.google.com/app/apikey
- **Documentação Gemini**: https://ai.google.dev/
- **Limites da API**: https://ai.google.dev/pricing

## ✅ Próximos Passos

1. Obtenha sua chave grátis
2. Configure com `python configurar_env.py`
3. Teste com `python demo_sistema_completo.py`
4. Aproveite análises ilimitadas (dentro do limite gratuito)!

---

**💰 CUSTO TOTAL: R$ 0,00 (ZERO!)** 🎉
