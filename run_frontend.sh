#!/bin/bash
# Script para iniciar o sistema completo

echo "🚀 Iniciando Meta-Classificador..."

# Verifica se a API já está rodando
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API já está rodando na porta 8000"
else
    echo "🔄 Iniciando API..."
    cd /workspaces/meta-classificador
    python src/api.py &
    API_PID=$!
    echo "⏳ Aguardando API inicializar..."
    sleep 3
fi

# Abre o frontend
echo "🌐 Abrindo frontend no navegador..."
"$BROWSER" http://localhost:8000/

echo "✅ Sistema iniciado!"
echo "📍 Acesse: http://localhost:8000/"
echo "📊 Visualizador de dados: http://localhost:8000/data-viewer.html"
