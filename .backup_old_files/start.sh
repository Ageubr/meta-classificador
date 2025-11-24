#!/bin/bash

# Script de início rápido do sistema

echo "🚀 Iniciando Sistema de Meta-Classificação de Vulnerabilidade Social"
echo ""

# Verificar se a API está rodando
if pgrep -f "python src/api.py" > /dev/null; then
    echo "✅ API já está rodando"
else
    echo "🔄 Iniciando API..."
    cd "$(dirname "$0")"
    nohup python src/api.py > api.log 2>&1 &
    sleep 3
fi

# Verificar status
echo ""
echo "📊 Verificando status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API está operacional"
else
    echo "❌ API não está respondendo"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          Sistema Pronto para Uso! 🎉                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 Links de Acesso:"
echo ""
echo "   🌐 Interface Web:    http://localhost:8000"
echo "   📖 API Docs:         http://localhost:8000/docs"
echo "   💚 Health Check:     http://localhost:8000/health"
echo ""
echo "📋 Comandos Úteis:"
echo ""
echo "   Ver logs:     tail -f api.log"
echo "   Parar API:    pkill -f 'python src/api.py'"
echo "   Reiniciar:    ./start.sh"
echo ""
echo "📚 Documentação: docs/README.md"
echo ""

# Abrir no navegador (se disponível)
if command -v xdg-open &> /dev/null; then
    echo "🌐 Abrindo interface no navegador..."
    xdg-open http://localhost:8000 &
elif [ -n "$BROWSER" ]; then
    echo "🌐 Abrindo interface no navegador..."
    "$BROWSER" http://localhost:8000 &
fi
