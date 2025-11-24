#!/usr/bin/env python3
"""
Conversor de Dados do Governo (CadÚnico) para formato do Sistema

Este script converte os arquivos originais disponibilizados pelo governo
(formato com separador ';') para o formato esperado pelo sistema de
análise de vulnerabilidade social.

Arquivos suportados:
- base_amostra_familia_201812.csv
- base_amostra_pessoa_201812.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def converter_arquivo_familias(
    arquivo_entrada: str,
    arquivo_saida: str,
    max_linhas: int = None
) -> pd.DataFrame:
    """
    Converte arquivo de famílias do CadÚnico para formato do sistema.
    
    Args:
        arquivo_entrada: Caminho do arquivo original
        arquivo_saida: Caminho do arquivo convertido
        max_linhas: Número máximo de linhas para processar (None = todas)
    
    Returns:
        DataFrame processado
    """
    logger.info(f"Lendo arquivo original: {arquivo_entrada}")
    
    # Ler arquivo com separador ';'
    df_original = pd.read_csv(
        arquivo_entrada,
        sep=';',
        encoding='latin-1',
        nrows=max_linhas,
        low_memory=False
    )
    
    logger.info(f"Arquivo lido: {len(df_original)} registros")
    
    # Criar DataFrame no formato esperado
    df_novo = pd.DataFrame()
    
    # Código do município (IBGE)
    df_novo['cod_municipio'] = df_original['cd_ibge'].astype(str).str.replace('"', '')
    
    # ID da família
    df_novo['id_familia'] = df_original['id_familia'].astype(str).str.replace('"', '')
    
    # Renda familiar
    df_novo['renda_familiar'] = pd.to_numeric(
        df_original['vlr_renda_media_fam'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(0)
    
    # Quantidade de pessoas na família
    df_novo['qtd_pessoas_familia'] = pd.to_numeric(
        df_original['qtde_pessoas'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(1)
    
    # Renda per capita
    df_novo['renda_per_capita'] = df_novo['renda_familiar'] / df_novo['qtd_pessoas_familia']
    df_novo['renda_per_capita'] = df_novo['renda_per_capita'].fillna(0)
    
    # Tipo de moradia (1=própria, 2=alugada, 3=cedida, 4=outra)
    df_novo['tipo_moradia'] = pd.to_numeric(
        df_original['cod_especie_domic_fam'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(1)
    
    # Acesso a água (1=sim, 0=não)
    df_novo['acesso_agua'] = pd.to_numeric(
        df_original['cod_agua_canalizada_fam'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(0)
    df_novo['acesso_agua'] = (df_novo['acesso_agua'] == 1).astype(int)
    
    # Acesso a esgoto (1=sim, 0=não)
    df_novo['acesso_esgoto'] = pd.to_numeric(
        df_original['cod_escoa_sanitario_domic_fam'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(0)
    df_novo['acesso_esgoto'] = (df_novo['acesso_esgoto'] == 1).astype(int)
    
    # Recebe Bolsa Família (marc_pbf: 0=não, 1=sim)
    df_novo['recebe_bolsa_familia'] = pd.to_numeric(
        df_original['marc_pbf'].astype(str).str.replace('"', ''),
        errors='coerce'
    ).fillna(0).astype(int)
    
    # Campos padrão para compatibilidade (serão preenchidos com dados de pessoa)
    df_novo['idade'] = 35  # Será atualizado depois
    df_novo['sexo'] = 'F'  # Será atualizado depois
    df_novo['escolaridade'] = 1  # Será atualizado depois
    df_novo['situacao_trabalho'] = 0  # Será atualizado depois
    df_novo['possui_deficiencia'] = 0  # Será atualizado depois
    
    logger.info(f"Conversão concluída: {len(df_novo)} registros")
    
    # Salvar arquivo
    df_novo.to_csv(arquivo_saida, index=False, encoding='utf-8')
    logger.info(f"Arquivo salvo em: {arquivo_saida}")
    
    return df_novo


def converter_e_mesclar_familias_pessoas(
    arquivo_familias: str,
    arquivo_pessoas: str,
    arquivo_saida: str,
    max_linhas: int = None
) -> pd.DataFrame:
    """
    Converte e mescla dados de famílias e pessoas do CadÚnico.
    
    Args:
        arquivo_familias: Caminho do arquivo de famílias
        arquivo_pessoas: Caminho do arquivo de pessoas
        arquivo_saida: Caminho do arquivo final
        max_linhas: Número máximo de linhas para processar
    
    Returns:
        DataFrame processado e mesclado
    """
    logger.info("=" * 70)
    logger.info("CONVERSÃO DE DADOS DO GOVERNO PARA O SISTEMA")
    logger.info("=" * 70)
    
    # 1. Ler arquivo de famílias
    logger.info("\n[1/4] Lendo dados de famílias...")
    df_familias = pd.read_csv(
        arquivo_familias,
        sep=';',
        encoding='latin-1',
        nrows=max_linhas,
        low_memory=False
    )
    logger.info(f"✓ {len(df_familias)} famílias lidas")
    
    # 2. Ler arquivo de pessoas
    logger.info("\n[2/4] Lendo dados de pessoas...")
    df_pessoas = pd.read_csv(
        arquivo_pessoas,
        sep=';',
        encoding='latin-1',
        nrows=max_linhas * 3 if max_linhas else None,  # 3 pessoas por família em média
        low_memory=False
    )
    logger.info(f"✓ {len(df_pessoas)} pessoas lidas")
    
    # 3. Processar famílias
    logger.info("\n[3/4] Processando dados de famílias...")
    df_final = pd.DataFrame()
    
    # Limpar aspas
    for col in df_familias.columns:
        if df_familias[col].dtype == object:
            df_familias[col] = df_familias[col].astype(str).str.replace('"', '')
    
    for col in df_pessoas.columns:
        if df_pessoas[col].dtype == object:
            df_pessoas[col] = df_pessoas[col].astype(str).str.replace('"', '')
    
    # Dados da família
    df_final['cod_municipio'] = pd.to_numeric(df_familias['cd_ibge'], errors='coerce')
    df_final['id_familia'] = df_familias['id_familia']
    df_final['renda_familiar'] = pd.to_numeric(df_familias['vlr_renda_media_fam'], errors='coerce').fillna(0)
    df_final['qtd_pessoas_familia'] = pd.to_numeric(df_familias['qtde_pessoas'], errors='coerce').fillna(1)
    df_final['renda_per_capita'] = df_final['renda_familiar'] / df_final['qtd_pessoas_familia']
    
    # Infraestrutura
    df_final['tipo_moradia'] = pd.to_numeric(df_familias['cod_especie_domic_fam'], errors='coerce').fillna(1)
    df_final['acesso_agua'] = (pd.to_numeric(df_familias['cod_agua_canalizada_fam'], errors='coerce') == 1).astype(int)
    df_final['acesso_esgoto'] = (pd.to_numeric(df_familias['cod_escoa_sanitario_domic_fam'], errors='coerce') == 1).astype(int)
    df_final['recebe_bolsa_familia'] = pd.to_numeric(df_familias['marc_pbf'], errors='coerce').fillna(0).astype(int)
    
    # 4. Adicionar dados do responsável familiar (primeira pessoa de cada família)
    logger.info("\n[4/4] Mesclando dados de pessoas (responsável familiar)...")
    
    # Filtrar apenas responsáveis (cod_parentesco_rf_pessoa == 1)
    df_responsaveis = df_pessoas[df_pessoas['cod_parentesco_rf_pessoa'] == '1'].copy()
    
    # Mesclar
    df_responsaveis['id_familia_merge'] = df_responsaveis['id_familia']
    df_final['id_familia_merge'] = df_final['id_familia']
    
    df_merged = df_final.merge(
        df_responsaveis[['id_familia_merge', 'idade', 'cod_sexo_pessoa', 
                         'cod_curso_frequentou_pessoa_memb', 'cod_trabalhou_memb', 
                         'cod_deficiencia_memb']],
        on='id_familia_merge',
        how='left'
    )
    
    # Processar campos de pessoas
    df_merged['idade'] = pd.to_numeric(df_merged['idade'], errors='coerce').fillna(35)
    df_merged['sexo'] = df_merged['cod_sexo_pessoa'].map({'1': 'M', '2': 'F'}).fillna('F')
    df_merged['escolaridade'] = pd.to_numeric(df_merged['cod_curso_frequentou_pessoa_memb'], errors='coerce').fillna(1)
    df_merged['situacao_trabalho'] = pd.to_numeric(df_merged['cod_trabalhou_memb'], errors='coerce').fillna(0)
    df_merged['possui_deficiencia'] = (pd.to_numeric(df_merged['cod_deficiencia_memb'], errors='coerce') > 0).astype(int)
    
    # Selecionar colunas finais
    colunas_finais = [
        'cod_municipio', 'id_familia', 'idade', 'sexo', 'escolaridade',
        'renda_familiar', 'qtd_pessoas_familia', 'renda_per_capita',
        'possui_deficiencia', 'situacao_trabalho', 'tipo_moradia',
        'acesso_agua', 'acesso_esgoto', 'recebe_bolsa_familia'
    ]
    
    df_resultado = df_merged[colunas_finais].copy()
    
    # Limpar valores inválidos
    df_resultado = df_resultado.dropna(subset=['cod_municipio', 'renda_per_capita'])
    df_resultado = df_resultado[df_resultado['cod_municipio'] > 0]
    
    logger.info(f"✓ Conversão concluída: {len(df_resultado)} registros finais")
    
    # Salvar
    df_resultado.to_csv(arquivo_saida, index=False, encoding='utf-8')
    logger.info(f"✓ Arquivo salvo em: {arquivo_saida}")
    
    # Estatísticas
    logger.info("\n" + "=" * 70)
    logger.info("ESTATÍSTICAS DO ARQUIVO CONVERTIDO")
    logger.info("=" * 70)
    logger.info(f"Total de registros: {len(df_resultado):,}")
    logger.info(f"Total de municípios: {df_resultado['cod_municipio'].nunique():,}")
    logger.info(f"Renda per capita média: R$ {df_resultado['renda_per_capita'].mean():.2f}")
    logger.info(f"Recebem Bolsa Família: {df_resultado['recebe_bolsa_familia'].sum():,} ({df_resultado['recebe_bolsa_familia'].mean()*100:.1f}%)")
    logger.info("=" * 70)
    
    return df_resultado


def main():
    """Função principal para converter arquivos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Conversor de dados do governo para o sistema')
    parser.add_argument('--familias', default='data/base_amostra_cad_201812/base_amostra_familia_201812.csv',
                       help='Arquivo de famílias')
    parser.add_argument('--pessoas', default='data/base_amostra_cad_201812/base_amostra_pessoa_201812.csv',
                       help='Arquivo de pessoas')
    parser.add_argument('--saida', default='data/cadunico_convertido.csv',
                       help='Arquivo de saída')
    parser.add_argument('--max-linhas', type=int, default=10000,
                       help='Máximo de linhas para processar (None = todas)')
    
    args = parser.parse_args()
    
    # Converter
    df = converter_e_mesclar_familias_pessoas(
        args.familias,
        args.pessoas,
        args.saida,
        args.max_linhas
    )
    
    print("\n✅ Conversão concluída com sucesso!")
    print(f"📊 Arquivo disponível em: {args.saida}")
    print(f"📈 Total de registros: {len(df):,}")
    print("\n💡 Agora você pode usar este arquivo no sistema de visualização!")


if __name__ == '__main__':
    main()
