#!/bin/bash
# Script para configuração rápida do Google Gemini

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           CONFIGURAÇÃO GOOGLE GEMINI - 100% GRATUITO!               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🆓 VANTAGENS DO GEMINI:"
echo "  ✅ Completamente GRATUITO"
echo "  ✅ 1 milhão de tokens por mês grátis"
echo "  ✅ Sem cartão de crédito necessário"
echo "  ✅ 1.500 requisições por dia"
echo ""
echo "📝 PASSOS PARA OBTER A CHAVE:"
echo ""
echo "  1. Acesse: https://makersuite.google.com/app/apikey"
echo "  2. Faça login com sua conta Google"
echo "  3. Clique em 'Create API Key'"
echo "  4. Copie a chave (começa com 'AIza')"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Opção 1: Script Python interativo
echo "Escolha uma opção:"
echo "  1. Configurar via script interativo (recomendado)"
echo "  2. Editar arquivo .env manualmente"
echo ""
read -p "Opção (1-2): " opcao

if [ "$opcao" = "1" ]; then
    python configurar_env.py
elif [ "$opcao" = "2" ]; then
    echo ""
    echo "📝 Edite o arquivo .env e adicione:"
    echo "   GEMINI_API_KEY=AIza..."
    echo ""
    echo "Abrindo .env..."
    ${EDITOR:-nano} .env
else
    echo "❌ Opção inválida"
    exit 1
fi

echo ""
echo "✅ Pronto! Agora você pode usar o sistema:"
echo "   python demo_sistema_completo.py"
