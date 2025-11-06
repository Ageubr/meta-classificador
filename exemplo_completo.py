#!/usr/bin/env python3
"""
Exemplo completo de uso do Sistema de Análise de Vulnerabilidade Social.

Este script demonstra como usar todo o pipeline do sistema:
1. Preprocessamento de dados
2. Treinamento de modelos ML
3. Análise com meta-classificador LLM
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path para importar módulos
sys.path.append('src')

try:
    from preprocessamento import (
        carregar_dados_cadunico, 
        carregar_dados_bolsa_familia,
        gerar_features_vulnerabilidade,
        preparar_dados_para_ml,
        tratar_dados_faltantes
    )
    
    from modelos_ml import (
        treinar_e_salvar_modelos,
        comparar_modelos,
        RandomForestVulnerabilidade,
        XGBoostVulnerabilidade
    )
    
    from meta_classificador_llm import MetaClassificadorLLM
    
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que está executando este script do diretório raiz do projeto")
    sys.exit(1)


def main():
    """
    Execução principal do exemplo.
    """
    print("=" * 60)
    print("🏠 SISTEMA DE ANÁLISE DE VULNERABILIDADE SOCIAL")
    print("=" * 60)
    
    # Etapa 1: Carregar e preprocessar dados
    print("\n📊 ETAPA 1: Carregando e preprocessando dados...")
    
    df_cadunico = carregar_dados_cadunico()
    df_bolsa_familia = carregar_dados_bolsa_familia()
    
    # Tratar dados faltantes
    df_cadunico = tratar_dados_faltantes(df_cadunico, estrategia='mediana')
    df_bolsa_familia = tratar_dados_faltantes(df_bolsa_familia, estrategia='mediana')
    
    # Gerar features de vulnerabilidade
    df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa_familia)
    
    print(f"✅ Dados carregados e processados:")
    print(f"   - CadÚnico: {len(df_cadunico)} registros")
    print(f"   - Bolsa Família: {len(df_bolsa_familia)} registros") 
    print(f"   - Features geradas: {df_features.shape[1]} colunas")
    
    # Preparar dados para ML
    X, y = preparar_dados_para_ml(df_features)
    
    print(f"   - Dados para ML: {X.shape[0]} amostras, {X.shape[1]} features")
    print(f"   - Distribuição de vulnerabilidade:")
    for nivel, count in df_features['nivel_vulnerabilidade'].value_counts().items():
        print(f"     {nivel}: {count} pessoas")
    
    # Etapa 2: Treinar modelos ML
    print("\n🤖 ETAPA 2: Treinando modelos de Machine Learning...")
    
    # Treinar e salvar todos os modelos
    metricas = treinar_e_salvar_modelos(X, y)
    
    print(f"✅ Modelos treinados com sucesso:")
    print(f"   - Random Forest - Acurácia: {metricas['random_forest']['acuracia_teste']:.4f}")
    print(f"   - XGBoost - Acurácia: {metricas['xgboost']['acuracia_teste']:.4f}")
    
    # Etapa 3: Demonstrar meta-classificador
    print("\n🧠 ETAPA 3: Demonstrando meta-classificador com LLM...")
    
    # Inicializar meta-classificador
    meta_classificador = MetaClassificadorLLM()
    
    # Carregar modelos treinados
    meta_classificador.carregar_modelos_ml()
    
    # Selecionar alguns casos interessantes para análise
    casos_exemplo = [
        df_features.iloc[0],   # Primeiro caso
        df_features.iloc[50],  # Caso do meio
        df_features.iloc[-1],  # Último caso
    ]
    
    print(f"📋 Analisando {len(casos_exemplo)} casos exemplo...")
    
    for i, pessoa in enumerate(casos_exemplo):
        print(f"\n--- CASO {i+1} ---")
        print(f"Idade: {pessoa['idade']} | Renda per capita: R$ {pessoa['renda_per_capita']:.2f}")
        print(f"Escolaridade: {pessoa['escolaridade']} | Família: {pessoa['qtd_pessoas_familia']} pessoas")
        
        # Fazer análise completa
        resultado = meta_classificador.classificar_vulnerabilidade(pessoa)
        
        # Mostrar predições dos modelos ML
        print("\n🤖 Predições dos Modelos ML:")
        for modelo, pred in resultado['predicoes_ml'].items():
            nivel_pred = ['Baixa', 'Média', 'Alta', 'Muito Alta'][pred['classes'][0]]
            confianca = pred['confianca_maxima'][0] * 100
            print(f"   {modelo}: {nivel_pred} (confiança: {confianca:.1f}%)")
        
        # Mostrar análise do LLM (se disponível)
        if resultado['analise_llm']:
            print("\n🧠 Análise do LLM:")
            print(resultado['analise_llm'][:300] + "..." if len(resultado['analise_llm']) > 300 else resultado['analise_llm'])
        else:
            print("\n⚠️  Análise LLM não disponível (configure OPENAI_API_KEY)")
        
        print("-" * 40)
    
    # Etapa 4: Análise em lote (demonstração)
    print("\n📊 ETAPA 4: Demonstração de análise em lote...")
    
    # Analisar um subconjunto menor para demonstração
    amostra = df_features.head(5)
    
    print(f"Processando lote de {len(amostra)} pessoas...")
    
    # Para demonstração, vamos simular análise em lote sem chamar LLM
    # (para evitar custos desnecessários)
    resultados_lote = []
    
    for idx, pessoa in amostra.iterrows():
        # Fazer apenas predições ML
        X_pessoa = df_features.loc[[idx], X.columns]
        predicoes_ml = meta_classificador.predizer_modelos_ml(X_pessoa)
        
        resultado_simulado = {
            'dados_pessoa': pessoa.to_dict(),
            'predicoes_ml': predicoes_ml,
            'analise_llm': None,  # Não executar LLM para demonstração
            'timestamp': str(pd.Timestamp.now())
        }
        
        resultados_lote.append(resultado_simulado)
    
    # Gerar relatório consolidado
    relatorio = meta_classificador.gerar_relatorio_consolidado(resultados_lote)
    
    print(f"✅ Análise em lote concluída:")
    print(f"   - Total analisado: {relatorio.get('total_analisados', 0)} pessoas")
    print(f"   - Distribuição Random Forest: {relatorio.get('distribuicao_vulnerabilidade', {}).get('random_forest', {})}")
    print(f"   - Distribuição XGBoost: {relatorio.get('distribuicao_vulnerabilidade', {}).get('xgboost', {})}")
    
    # Informações finais
    print("\n" + "=" * 60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📁 Arquivos gerados:")
    print("   - outputs/modelos/: Modelos ML treinados")
    print("   - outputs/modelos/*_features_importance.png: Gráficos de importância")
    print("   - outputs/modelos/metricas_modelos.json: Métricas detalhadas")
    
    print("\n🚀 Próximos passos:")
    print("   1. Configure OPENAI_API_KEY para usar funcionalidades LLM")
    print("   2. Substitua dados fictícios por dados reais do CadÚnico")
    print("   3. Ajuste hiperparâmetros dos modelos conforme necessário")
    print("   4. Implemente interface web para uso em produção")
    
    print("\n📚 Para mais informações, consulte o README.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("Verifique os logs acima para mais detalhes")
        sys.exit(1)