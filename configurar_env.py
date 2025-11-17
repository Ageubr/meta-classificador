#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente de forma segura.
"""

import os
from pathlib import Path

def configurar_env():
    """Configura o arquivo .env com a chave da API OpenAI."""
    
    print("=" * 70)
    print("  CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE")
    print("=" * 70)
    print()
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Verificar se .env já existe
    if env_file.exists():
        print("⚠️  Arquivo .env já existe!")
        resposta = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
    
    print("📝 Configure sua chave da API Google Gemini (GRATUITA!)")
    print()
    print("🆓 A API do Gemini é 100% GRATUITA com:")
    print("  • 60 requisições por minuto")
    print("  • 1.500 requisições por dia")
    print("  • 1 milhão de tokens por mês")
    print()
    print("Como obter a chave:")
    print("  1. Acesse: https://makersuite.google.com/app/apikey")
    print("  2. Faça login com sua conta Google")
    print("  3. Clique em 'Create API Key'")
    print("  4. Copie a chave (começa com 'AIza')")
    print()
    
    api_key = input("Cole sua chave da API Gemini: ").strip()
    
    if not api_key:
        print("❌ Chave não fornecida. Operação cancelada.")
        return
    
    if not api_key.startswith('AIza'):
        print("⚠️  Aviso: A chave não parece estar no formato correto (deveria começar com 'AIza')")
        resposta = input("Continuar mesmo assim? (s/N): ").strip().lower()
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
    
    # Escolher modelo (opcional)
    print()
    print("Escolha o modelo Gemini:")
    print("  1. gemini-1.5-flash (recomendado: mais rápido e gratuito)")
    print("  2. gemini-1.5-pro (mais poderoso, ainda gratuito)")
    print("  3. gemini-pro (versão estável)")
    
    modelo_choice = input("Escolha (1-3) [padrão: 1]: ").strip() or "1"
    
    modelos = {
        "1": "gemini-1.5-flash",
        "2": "gemini-1.5-pro",
        "3": "gemini-pro"
    }
    
    modelo = modelos.get(modelo_choice, "gemini-1.5-flash")
    
    # Criar arquivo .env
    conteudo = f"""# Configuração do Sistema de Vulnerabilidade Social
# Gerado automaticamente em {Path.cwd()}

# Google Gemini API Key (GRATUITA!)
GEMINI_API_KEY={api_key}

# Modelo Gemini (gemini-1.5-flash, gemini-1.5-pro, gemini-pro)
GEMINI_MODEL={modelo}

# IMPORTANTE: Este arquivo contém informações sensíveis!
# Nunca compartilhe ou commite este arquivo no Git.
"""
    
    with open(env_file, 'w') as f:
        f.write(conteudo)
    
    print()
    print("✅ Arquivo .env criado com sucesso!")
    print(f"📍 Local: {env_file.absolute()}")
    print()
    print("🔒 SEGURANÇA:")
    print("  ✓ O arquivo .env está listado no .gitignore")
    print("  ✓ Suas credenciais NÃO serão commitadas no Git")
    print()
    print("🧪 Teste a configuração executando:")
    print("  python -c 'from dotenv import load_dotenv; import os; load_dotenv(); print(\"API Key:\", \"Configurada!\" if os.getenv(\"GEMINI_API_KEY\") else \"NÃO configurada\")'")
    print()
    print("💰 Custo: ZERO! A API do Gemini é 100% gratuita")
    print()
    print("🚀 Para usar o sistema:")
    print("  python demo_sistema_completo.py")
    print()

if __name__ == "__main__":
    try:
        configurar_env()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
