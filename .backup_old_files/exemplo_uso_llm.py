"""
Exemplo de uso do Meta-Classificador LLM com OpenAI.

Este script demonstra como usar o sistema completo:
1. Carregar modelos ML treinados
2. Fazer predições com ML
3. Gerar análise detalhada com LLM (OpenAI)
"""

import sys
sys.path.append('src')

from preprocessamento import carregar_dados_cadunico, gerar_features_vulnerabilidade
from meta_classificador_llm import MetaClassificadorLLM
import pandas as pd


def exemplo_sem_openai():
    """
    Exemplo de uso SEM OpenAI (apenas ML).
    Sistema funciona normalmente, mas sem análise detalhada.
    """
    print("="*70)
    print("📊 EXEMPLO 1: USO SEM OPENAI (Apenas ML)")
    print("="*70)
    
    # Carregar dados
    print("\n1️⃣ Carregando dados processados...")
    df_cadunico = carregar_dados_cadunico()
    
    # Pegar uma família de exemplo
    familia_exemplo = df_cadunico.iloc[0]
    
    print(f"\n2️⃣ Família de exemplo:")
    print(f"   - Idade: {familia_exemplo['idade']} anos")
    print(f"   - Renda familiar: R$ {familia_exemplo['renda_familiar']:.2f}")
    print(f"   - Pessoas na família: {familia_exemplo['qtd_pessoas_familia']}")
    print(f"   - Renda per capita: R$ {familia_exemplo['renda_per_capita']:.2f}")
    print(f"   - Nível de vulnerabilidade: {familia_exemplo['nivel_vulnerabilidade']}")
    
    # Inicializar meta-classificador (sem API key)
    print("\n3️⃣ Inicializando meta-classificador...")
    meta = MetaClassificadorLLM()
    meta.carregar_modelos_ml()
    
    # Preparar dados para predição
    X = pd.DataFrame([familia_exemplo])
    
    # Fazer predições com ML
    print("\n4️⃣ Fazendo predições com modelos ML...")
    predicoes = meta.predizer_modelos_ml(X)
    
    print("\n📊 RESULTADOS (Apenas ML):")
    for modelo, pred in predicoes.items():
        nivel_map = {0: 'Baixa', 1: 'Média', 2: 'Alta', 3: 'Muito Alta'}
        nivel = nivel_map.get(pred['classes'][0], 'Desconhecido')
        confianca = pred['confianca_maxima'][0] * 100
        print(f"   {modelo}:")
        print(f"      └─ Vulnerabilidade: {nivel} (confiança: {confianca:.1f}%)")
    
    print("\n⚠️  Sem OpenAI: Apenas classificação numérica disponível")
    print("    Para análise detalhada, configure OPENAI_API_KEY")
    print("="*70)


def exemplo_com_openai():
    """
    Exemplo de uso COM OpenAI (ML + LLM).
    Sistema gera análise detalhada e recomendações.
    
    NOTA: Requer OPENAI_API_KEY configurada.
    """
    print("\n\n")
    print("="*70)
    print("🤖 EXEMPLO 2: USO COM OPENAI (ML + LLM)")
    print("="*70)
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY não configurada!")
        print("\nPara usar este exemplo:")
        print("   1. Crie conta em: https://platform.openai.com")
        print("   2. Gere API key em: https://platform.openai.com/api-keys")
        print("   3. Configure: export OPENAI_API_KEY='sua-chave'")
        print("   4. Execute novamente este script")
        print("\n💡 DICA: O sistema funciona perfeitamente SEM OpenAI!")
        print("   OpenAI é OPCIONAL para análises detalhadas.")
        return
    
    # Carregar dados
    print("\n1️⃣ Carregando dados processados...")
    df_cadunico = carregar_dados_cadunico()
    
    # Pegar uma família de alta vulnerabilidade
    familia_critica = df_cadunico[df_cadunico['nivel_vulnerabilidade'] == 'Muito Alta'].iloc[0]
    
    print(f"\n2️⃣ Família de exemplo (VULNERABILIDADE MUITO ALTA):")
    print(f"   - Idade: {familia_critica['idade']} anos")
    print(f"   - Renda familiar: R$ {familia_critica['renda_familiar']:.2f}")
    print(f"   - Pessoas: {familia_critica['qtd_pessoas_familia']}")
    print(f"   - Renda per capita: R$ {familia_critica['renda_per_capita']:.2f}")
    print(f"   - Acesso água: {'Sim' if familia_critica['acesso_agua'] else 'Não'}")
    print(f"   - Acesso esgoto: {'Sim' if familia_critica['acesso_esgoto'] else 'Não'}")
    print(f"   - Bolsa Família: {'Sim' if familia_critica['recebe_bolsa_familia'] else 'Não'}")
    
    # Inicializar meta-classificador COM OpenAI
    print("\n3️⃣ Inicializando meta-classificador com OpenAI...")
    meta = MetaClassificadorLLM(api_key=api_key)
    meta.carregar_modelos_ml()
    
    # Fazer análise completa
    print("\n4️⃣ Gerando análise completa (ML + LLM)...")
    print("   ⏳ Aguarde... consultando OpenAI GPT...")
    
    resultado = meta.classificar_vulnerabilidade(familia_critica)
    
    # Exibir resultados
    print("\n" + "="*70)
    print("📊 ANÁLISE COMPLETA COM LLM")
    print("="*70)
    
    print("\n🤖 Predições dos Modelos ML:")
    for modelo, pred in resultado['predicoes_ml'].items():
        nivel_map = {0: 'Baixa', 1: 'Média', 2: 'Alta', 3: 'Muito Alta'}
        nivel = nivel_map.get(pred['classes'][0], 'Desconhecido')
        confianca = pred['confianca_maxima'][0] * 100
        print(f"   {modelo}: {nivel} ({confianca:.1f}%)")
    
    print("\n📝 ANÁLISE DETALHADA DO LLM (OpenAI GPT):")
    print("-"*70)
    print(resultado['analise_llm'])
    print("-"*70)
    
    print("\n✅ Análise completa salva no histórico!")
    print(f"   Total de análises realizadas: {len(meta.historico_predicoes)}")
    
    print("\n💡 BENEFÍCIOS DO LLM:")
    print("   ✓ Explicação em linguagem natural")
    print("   ✓ Identificação de fatores de risco")
    print("   ✓ Recomendações personalizadas")
    print("   ✓ Plano de monitoramento")
    print("   ✓ Contexto de políticas públicas brasileiras")
    
    print("="*70)


def exemplo_lote_hibrido():
    """
    Exemplo de estratégia HÍBRIDA (recomendada).
    ML para todos, LLM apenas para casos críticos.
    """
    print("\n\n")
    print("="*70)
    print("⚡ EXEMPLO 3: ESTRATÉGIA HÍBRIDA (Recomendada)")
    print("="*70)
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Carregar dados
    print("\n1️⃣ Carregando amostra de dados...")
    df_cadunico = carregar_dados_cadunico()
    
    # Inicializar meta-classificador
    meta = MetaClassificadorLLM(api_key=api_key if api_key else None)
    meta.carregar_modelos_ml()
    
    print(f"\n2️⃣ Processando {len(df_cadunico)} famílias...")
    print("   📊 Estratégia:")
    print("      └─ ML rápido para TODOS")
    print("      └─ LLM detalhado apenas para CASOS CRÍTICOS")
    
    # Fazer predições ML em lote
    X = df_cadunico.drop(columns=['nivel_vulnerabilidade', 'score_vulnerabilidade'], errors='ignore')
    predicoes_lote = meta.predizer_modelos_ml(X)
    
    # Identificar casos críticos (vulnerabilidade muito alta)
    casos_criticos = df_cadunico[df_cadunico['nivel_vulnerabilidade'] == 'Muito Alta']
    
    print(f"\n3️⃣ Resultados da triagem ML:")
    print(f"   - Total analisado: {len(df_cadunico)} famílias")
    print(f"   - Casos críticos identificados: {len(casos_criticos)} ({len(casos_criticos)/len(df_cadunico)*100:.1f}%)")
    print(f"   - Distribuição:")
    print(df_cadunico['nivel_vulnerabilidade'].value_counts().to_string(header=False))
    
    if api_key and len(casos_criticos) > 0:
        print(f"\n4️⃣ Gerando análises LLM para {min(3, len(casos_criticos))} casos críticos...")
        
        analises_detalhadas = []
        for idx, (_, familia) in enumerate(casos_criticos.head(3).iterrows()):
            print(f"   ⏳ Analisando caso {idx+1}/3...")
            resultado = meta.classificar_vulnerabilidade(familia)
            analises_detalhadas.append(resultado)
        
        print(f"\n✅ {len(analises_detalhadas)} análises detalhadas geradas!")
        
        # Calcular custos
        custo_por_analise = 0.002  # GPT-3.5-turbo
        custo_total_criticos = len(casos_criticos) * custo_por_analise
        custo_total_todos = len(df_cadunico) * custo_por_analise
        economia = custo_total_todos - custo_total_criticos
        
        print(f"\n💰 ANÁLISE DE CUSTOS:")
        print(f"   Estratégia 1 (LLM para TODOS):")
        print(f"      └─ {len(df_cadunico)} análises × ${custo_por_analise} = ${custo_total_todos:.2f}")
        print(f"\n   Estratégia 2 (HÍBRIDA - apenas críticos):")
        print(f"      └─ {len(casos_criticos)} análises × ${custo_por_analise} = ${custo_total_criticos:.2f}")
        print(f"\n   💡 ECONOMIA: ${economia:.2f} ({(economia/custo_total_todos)*100:.1f}%)")
        
    else:
        print(f"\n⚠️  OpenAI não configurada - análises LLM não disponíveis")
        print("   Configure OPENAI_API_KEY para análises detalhadas")
    
    print("\n📊 RESUMO DA ESTRATÉGIA HÍBRIDA:")
    print("   ✅ ML processa TODOS rapidamente (99.15% acurácia)")
    print("   ✅ LLM analisa apenas CASOS CRÍTICOS (54.9%)")
    print("   ✅ Reduz custos em ~45%")
    print("   ✅ Mantém qualidade alta onde mais importa")
    
    print("="*70)


if __name__ == "__main__":
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*10 + "EXEMPLOS DE USO DO META-CLASSIFICADOR LLM" + " "*16 + "║")
    print("╚" + "="*68 + "╝")
    
    # Executar exemplos
    exemplo_sem_openai()
    exemplo_com_openai()
    exemplo_lote_hibrido()
    
    print("\n\n" + "="*70)
    print("✅ EXEMPLOS CONCLUÍDOS!")
    print("="*70)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Configure OpenAI: export OPENAI_API_KEY='sua-chave'")
    print("   2. Execute novamente para ver análises LLM")
    print("   3. Use estratégia híbrida em produção")
    print("\n📚 Mais info:")
    print("   - README.md")
    print("   - ANALISE_COMPLETA.md")
    print("   - src/meta_classificador_llm.py")
    print("="*70 + "\n")
