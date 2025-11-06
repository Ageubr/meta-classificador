#!/bin/bash

# Script de inicialização rápida do Sistema de Vulnerabilidade Social
# Execute com: bash inicializar.sh

echo "🏠 Sistema de Análise de Vulnerabilidade Social"
echo "============================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar instalação
echo "✅ Testando instalação..."
python -c "import pandas, numpy, sklearn, xgboost; print('Dependências principais OK')"

# Executar exemplo básico
echo ""
echo "🚀 Executando exemplo básico..."
python -c "
import sys
sys.path.append('src')
from preprocessamento import carregar_dados_cadunico, gerar_features_vulnerabilidade
print('Carregando dados de exemplo...')
df = carregar_dados_cadunico()
df_features = gerar_features_vulnerabilidade(df)
print(f'✅ Sistema funcionando! {len(df_features)} registros com {df_features.shape[1]} features')
print('Distribuição de vulnerabilidade:')
print(df_features['nivel_vulnerabilidade'].value_counts())
"

echo ""
echo "🎉 Inicialização concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Para executar exemplo completo: python exemplo_completo.py"
echo "   2. Para configurar OpenAI: export OPENAI_API_KEY='sua-chave'"
echo "   3. Para adicionar dados reais: copie CSVs para pasta data/"
echo ""
echo "📚 Consulte README.md para documentação completa"