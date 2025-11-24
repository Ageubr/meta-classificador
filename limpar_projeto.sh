#!/bin/bash
# Script para limpar e organizar o projeto

echo "🧹 Limpando e Organizando Projeto Meta-Classificador"
echo "======================================================"
echo ""

# Criar pasta para arquivos antigos/não usados
echo "📁 Criando pasta de arquivos antigos..."
mkdir -p .backup_old_files

# Mover arquivos não utilizados
echo "📦 Movendo arquivos não utilizados..."

# Scripts de exemplo/demo não usados
[ -f "demo_sistema_completo.py" ] && mv demo_sistema_completo.py .backup_old_files/
[ -f "exemplo_completo.py" ] && mv exemplo_completo.py .backup_old_files/
[ -f "exemplo_uso_llm.py" ] && mv exemplo_uso_llm.py .backup_old_files/

# Scripts de configuração redundantes
[ -f "configurar_env.py" ] && mv configurar_env.py .backup_old_files/
[ -f "fix_formatting.py" ] && mv fix_formatting.py .backup_old_files/
[ -f "inicializar.sh" ] && mv inicializar.sh .backup_old_files/
[ -f "start.sh" ] && mv start.sh .backup_old_files/
[ -f "setup_gemini.sh" ] && mv setup_gemini.sh .backup_old_files/

# Arquivos não usados no src
[ -f "src/adaptar_dados_reais.py" ] && mv src/adaptar_dados_reais.py .backup_old_files/
[ -f "src/validador_sistema.py" ] && mv src/validador_sistema.py .backup_old_files/
[ -f "src/api.py.backup" ] && mv src/api.py.backup .backup_old_files/

# READMEs antigos
[ -f "README.old.md" ] && mv README.old.md .backup_old_files/
[ -f "RELATORIO_ANALISE.md" ] && mv RELATORIO_ANALISE.md .backup_old_files/
[ -f "RESULTADO_ANALISE.md" ] && mv RESULTADO_ANALISE.md .backup_old_files/

# Documentação redundante em docs/
[ -f "docs/CONVERSOR_DADOS_GOVERNO.md" ] && mv docs/CONVERSOR_DADOS_GOVERNO.md .backup_old_files/
[ -f "docs/MAPEAMENTO_DADOS.md" ] && mv docs/MAPEAMENTO_DADOS.md .backup_old_files/
[ -f "docs/VISUALIZACAO_DADOS.md" ] && mv docs/VISUALIZACAO_DADOS.md .backup_old_files/

# Limpar cache e arquivos temporários
echo "🗑️  Removendo cache e arquivos temporários..."
rm -rf src/__pycache__
rm -rf tests/__pycache__
rm -rf .pytest_cache
rm -rf htmlcov
rm -f .coverage
rm -f api.log

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📊 Estrutura final do projeto:"
echo ""
tree -L 2 -I '__pycache__|*.pyc|.git' || ls -R

echo ""
echo "💾 Arquivos antigos movidos para: .backup_old_files/"
echo "   (Você pode deletar essa pasta se não precisar mais)"
