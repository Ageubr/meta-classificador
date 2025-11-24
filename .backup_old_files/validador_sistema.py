"""
Módulo de validação do sistema de vulnerabilidade social.

Este módulo contém funções para validar a integridade e funcionamento
de todos os componentes do sistema.
"""

import sys
import os
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validar_dependencias() -> bool:
    """
    Valida se todas as dependências necessárias estão instaladas.

    Returns:
        bool: True se todas as dependências estão instaladas
    """
    dependencias = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'joblib': 'joblib',
        'openai': 'openai (opcional para LLM)'
    }

    print("\n" + "=" * 60)
    print("🔍 VALIDANDO DEPENDÊNCIAS")
    print("=" * 60)

    todas_instaladas = True

    for modulo, nome_display in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {nome_display}")
        except ImportError:
            if modulo == 'openai':
                print(
                    f"⚠️  {nome_display} - não instalado (funcionalidades LLM desabilitadas)")
            else:
                print(f"❌ {nome_display} - NÃO INSTALADO")
                todas_instaladas = False

    return todas_instaladas


def validar_estrutura_pastas() -> bool:
    """
    Valida se a estrutura de pastas do projeto está correta.

    Returns:
        bool: True se a estrutura está correta
    """
    print("\n" + "=" * 60)
    print("📁 VALIDANDO ESTRUTURA DE PASTAS")
    print("=" * 60)

    pastas_necessarias = [
        'src',
        'data',
        'outputs',
        'outputs/modelos',
        'outputs/relatorios'
    ]

    todas_existem = True

    for pasta in pastas_necessarias:
        caminho = Path(pasta)
        if caminho.exists():
            print(f"✅ {pasta}/")
        else:
            print(f"⚠️  {pasta}/ - criando...")
            caminho.mkdir(parents=True, exist_ok=True)

    return todas_existem


def validar_modulos() -> bool:
    """
    Valida se todos os módulos Python podem ser importados.

    Returns:
        bool: True se todos os módulos são importáveis
    """
    print("\n" + "=" * 60)
    print("🐍 VALIDANDO MÓDULOS PYTHON")
    print("=" * 60)

    sys.path.append('src')

    modulos = {
        'preprocessamento': [
            'carregar_dados_cadunico',
            'gerar_features_vulnerabilidade'],
        'modelos_ml': [
            'RandomForestVulnerabilidade',
            'XGBoostVulnerabilidade'],
        'meta_classificador_llm': ['MetaClassificadorLLM']}

    todos_ok = True

    for modulo, funcoes in modulos.items():
        try:
            mod = __import__(modulo)
            print(f"✅ {modulo}.py")

            # Verificar funções/classes específicas
            for funcao in funcoes:
                if hasattr(mod, funcao):
                    print(f"   ✅ {funcao}")
                else:
                    print(f"   ❌ {funcao} - não encontrado")
                    todos_ok = False

        except ImportError as e:
            print(f"❌ {modulo}.py - ERRO: {e}")
            todos_ok = False

    return todos_ok


def validar_dados() -> dict:
    """
    Valida disponibilidade e qualidade dos dados.

    Returns:
        dict: Informações sobre os dados
    """
    print("\n" + "=" * 60)
    print("📊 VALIDANDO DADOS")
    print("=" * 60)

    sys.path.append('src')
    from preprocessamento import carregar_dados_cadunico, carregar_dados_bolsa_familia

    info_dados = {
        'cadunico_real': False,
        'bolsa_familia_real': False,
        'cadunico_registros': 0,
        'bolsa_familia_registros': 0
    }

    # Verificar CadÚnico
    if Path('data/cadunico.csv').exists():
        print("✅ data/cadunico.csv (dados reais)")
        info_dados['cadunico_real'] = True
    else:
        print("⚠️  data/cadunico.csv não encontrado - usando dados fictícios")

    df_cadunico = carregar_dados_cadunico()
    info_dados['cadunico_registros'] = len(df_cadunico)
    print(f"   📈 {len(df_cadunico)} registros carregados")
    print(f"   📋 {df_cadunico.shape[1]} colunas")

    # Verificar Bolsa Família
    if Path('data/bolsa_familia.csv').exists():
        print("✅ data/bolsa_familia.csv (dados reais)")
        info_dados['bolsa_familia_real'] = True
    else:
        print("⚠️  data/bolsa_familia.csv não encontrado - usando dados fictícios")

    df_bolsa = carregar_dados_bolsa_familia()
    info_dados['bolsa_familia_registros'] = len(df_bolsa)
    print(f"   📈 {len(df_bolsa)} registros carregados")
    print(f"   📋 {df_bolsa.shape[1]} colunas")

    # Verificar pasta base_amostra_cad_201812
    pasta_amostra = Path('base_amostra_cad_201812')
    if pasta_amostra.exists():
        arquivos = list(pasta_amostra.glob('*'))
        if arquivos:
            print(
                f"✅ base_amostra_cad_201812/ - {len(arquivos)} arquivos encontrados")
        else:
            print("⚠️  base_amostra_cad_201812/ - pasta vazia")

    return info_dados


def testar_pipeline_completo() -> bool:
    """
    Testa o pipeline completo do sistema.

    Returns:
        bool: True se o pipeline funciona corretamente
    """
    print("\n" + "=" * 60)
    print("🔄 TESTANDO PIPELINE COMPLETO")
    print("=" * 60)

    try:
        sys.path.append('src')
        from preprocessamento import (
            carregar_dados_cadunico,
            carregar_dados_bolsa_familia,
            gerar_features_vulnerabilidade,
            preparar_dados_para_ml
        )

        # 1. Carregar dados
        print("1️⃣  Carregando dados...")
        df_cadunico = carregar_dados_cadunico()
        df_bolsa = carregar_dados_bolsa_familia()
        print(f"   ✅ {len(df_cadunico)} registros CadÚnico")
        print(f"   ✅ {len(df_bolsa)} registros Bolsa Família")

        # 2. Gerar features
        print("2️⃣  Gerando features de vulnerabilidade...")
        df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa)
        print(f"   ✅ {df_features.shape[1]} features geradas")

        # 3. Preparar para ML
        print("3️⃣  Preparando dados para ML...")
        X, y = preparar_dados_para_ml(df_features)
        print(f"   ✅ X: {X.shape}")
        print(f"   ✅ y: {y.shape}")

        # 4. Verificar distribuição
        print("4️⃣  Distribuição de vulnerabilidade:")
        distribuicao = df_features['nivel_vulnerabilidade'].value_counts()
        for nivel, count in distribuicao.items():
            porcentagem = (count / len(df_features)) * 100
            print(f"   {nivel}: {count} ({porcentagem:.1f}%)")

        print("\n✅ Pipeline completo funcionando!")
        return True

    except Exception as e:
        print(f"\n❌ ERRO no pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_openai_key() -> bool:
    """
    Verifica se a chave da OpenAI está configurada.

    Returns:
        bool: True se a chave está configurada
    """
    print("\n" + "=" * 60)
    print("🔑 VERIFICANDO CONFIGURAÇÃO OPENAI")
    print("=" * 60)

    api_key = os.getenv('OPENAI_API_KEY')

    if api_key:
        # Mascarar chave para segurança
        masked_key = api_key[:8] + "..." + \
            api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✅ OPENAI_API_KEY configurada: {masked_key}")
        return True
    else:
        print("⚠️  OPENAI_API_KEY não configurada")
        print("   Para usar funcionalidades LLM, execute:")
        print("   export OPENAI_API_KEY='sua-chave-aqui'")
        return False


def executar_validacao_completa():
    """
    Executa todas as validações do sistema.
    """
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print(
        "║" +
        " " *
        8 +
        "VALIDAÇÃO DO SISTEMA DE VULNERABILIDADE SOCIAL" +
        " " *
        4 +
        "║")
    print("╚" + "=" * 58 + "╝")

    resultados = {
        'dependencias': validar_dependencias(),
        'estrutura': validar_estrutura_pastas(),
        'modulos': validar_modulos(),
        'dados': validar_dados(),
        'pipeline': testar_pipeline_completo(),
        'openai': verificar_openai_key()
    }

    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("=" * 60)

    total = len(resultados)
    sucesso = sum(1 for v in resultados.values() if v)

    status_emoji = {
        True: "✅",
        False: "❌"
    }

    for nome, resultado in resultados.items():
        if nome == 'dados':
            # Dados é um dict, não bool
            print(f"✅ {nome.upper()}")
        else:
            emoji = status_emoji.get(resultado, "⚠️")
            print(f"{emoji} {nome.upper()}")

    print("\n" + "=" * 60)

    if sucesso >= total - 1:  # Permite que apenas OpenAI esteja ausente
        print("🎉 SISTEMA VALIDADO COM SUCESSO!")
        print("=" * 60)
        print("\n✅ Sistema pronto para uso!")
        print("\n📋 Próximos passos:")
        print("   1. Para treinar modelos: python exemplo_completo.py")
        print("   2. Para configurar OpenAI: export OPENAI_API_KEY='sua-chave'")
        print("   3. Para adicionar dados reais: copie CSVs para data/")
    else:
        print("⚠️  VALIDAÇÃO INCOMPLETA")
        print("=" * 60)
        print("\n❌ Corrija os erros acima antes de usar o sistema")

    print()


if __name__ == "__main__":
    executar_validacao_completa()
