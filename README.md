# 🏠 Sistema de Meta-Classificação de Vulnerabilidade Social

![Status](https://img.shields.io/badge/status-operational-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![ML](https://img.shields.io/badge/ML-99.15%25%20accuracy-success)
![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-purple)

Sistema inteligente para classificação e análise de vulnerabilidade social utilizando Machine Learning e LLMs.

## ✨ Características

- 🤖 **Modelos ML de Alta Precisão**: Random Forest (98.73%) e XGBoost (99.15%)
- 🧠 **Análise com IA**: Integração com Google Gemini para análise qualitativa
- 📊 **Dados Reais**: 2.355 registros do CadÚnico processados
- 🌐 **Interface Web Moderna**: UI responsiva e intuitiva
- 🚀 **API REST**: 7 endpoints para integração
- 📚 **Documentação Completa**: Swagger UI e ReDoc

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
| GET | `/health` | Status dos modelos |
| POST | `/predict` | Predição ML |
| POST | `/analyze` | Análise com LLM |
| GET | `/docs` | Documentação |

## 📚 Documentação Completa

Veja a documentação detalhada em [`docs/README.md`](docs/README.md)

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

**🚀 Acesse:** http://localhost:8000
