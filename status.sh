#!/bin/bash
# Verificar status do sistema

echo "🔍 Status do Meta-Classificador"
echo "================================"
echo ""

# Verificar .env
if [ -f ".env" ]; then
    echo "✅ .env configurado"
else
    echo "❌ .env não encontrado"
fi

# Verificar modelos
if [ -f "outputs/modelos/random_forest_vulnerabilidade.pkl" ]; then
    echo "✅ Modelo Random Forest"
else
    echo "⚠️  Modelo Random Forest não encontrado"
fi

if [ -f "outputs/modelos/xgboost_vulnerabilidade.pkl" ]; then
    echo "✅ Modelo XGBoost"
else
    echo "⚠️  Modelo XGBoost não encontrado"
fi

# Verificar API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API rodando (porta 8000)"
else
    echo "❌ API não está rodando"
fi

# Verificar dados
if [ -d "data/base_amostra_cad_201812" ]; then
    FILES=$(ls data/base_amostra_cad_201812/*.csv 2>/dev/null | wc -l)
    echo "✅ Dados CadÚnico ($FILES arquivo(s))"
else
    echo "⚠️  Pasta de dados não encontrada"
fi

# Estatísticas
echo ""
echo "📊 Estatísticas:"
echo "   Arquivos Python: $(find src -name '*.py' | wc -l)"
echo "   Arquivos Frontend: $(find frontend -name '*.html' -o -name '*.js' -o -name '*.css' | wc -l)"
echo "   Testes: $(find tests -name 'test_*.py' | wc -l)"
echo "   Documentação: $(find docs -name '*.md' | wc -l)"

echo ""
echo "🌐 URLs:"
echo "   Interface: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Data Viewer: http://localhost:8000/static/data-viewer.html"
