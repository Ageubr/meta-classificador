#!/bin/bash
# Script de Início Rápido - Meta-Classificador

echo "🏠 Meta-Classificador de Vulnerabilidade Social"
echo "=============================================="
echo ""

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo ""
    echo "📝 Para usar o sistema, você precisa configurar o Google Gemini:"
    echo "   1. Acesse: https://aistudio.google.com/apikey"
    echo "   2. Crie uma chave API (gratuita)"
    echo "   3. Crie o arquivo .env com:"
    echo ""
    echo "      GOOGLE_API_KEY=sua_chave_aqui"
    echo ""
    read -p "Deseja criar o .env agora? (s/N): " resposta
    if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
        read -p "Cole sua chave API: " api_key
        echo "GOOGLE_API_KEY=$api_key" > .env
        echo "✅ Arquivo .env criado!"
    else
        echo "❌ Sistema requer configuração do .env para funcionar"
        exit 1
    fi
fi

# Verificar se modelos existem
if [ ! -f "outputs/modelos/random_forest_vulnerabilidade.pkl" ]; then
    echo "⚠️  Modelos ML não encontrados!"
    echo "   Os modelos serão carregados automaticamente na primeira execução"
fi

# Iniciar API
echo ""
echo "🚀 Iniciando API..."
python src/api.py
