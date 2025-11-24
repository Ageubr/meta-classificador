#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para mapear dados do governo (CadÚnico e Bolsa Família) 
para o formato esperado pelo sistema, SEM converter arquivos.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detectar_formato_arquivo(file_path: Path) -> Dict[str, any]:
    """
    Detecta automaticamente o formato do arquivo CSV.
    
    Returns:
        dict com 'separador', 'encoding', 'tipo' (cadunico_familia, cadunico_pessoa, bolsa_familia)
    """
    # Tentar diferentes encodings e separadores
    configs = [
        {'sep': ';', 'encoding': 'latin-1'},
        {'sep': ';', 'encoding': 'utf-8'},
        {'sep': '\t', 'encoding': 'latin-1'},
        {'sep': '\t', 'encoding': 'utf-8'},
        {'sep': ',', 'encoding': 'utf-8'},
        {'sep': ',', 'encoding': 'latin-1'},
    ]
    
    for config in configs:
        try:
            df_test = pd.read_csv(file_path, nrows=5, **config)
            
            # Identificar tipo pelo nome das colunas
            colunas = [col.lower() for col in df_test.columns]
            
            if 'cd_ibge' in colunas or 'cod_familiar_fam' in colunas:
                tipo = 'cadunico_familia'
            elif 'cod_familiar_pes' in colunas or 'nom_pessoa' in colunas:
                tipo = 'cadunico_pessoa'
            elif 'uf' in colunas and 'valor_parcela' in colunas:
                tipo = 'bolsa_familia'
            else:
                tipo = 'desconhecido'
            
            logger.info(f"Arquivo detectado como: {tipo} | sep={config['sep']} | encoding={config['encoding']}")
            
            return {
                'separador': config['sep'],
                'encoding': config['encoding'],
                'tipo': tipo,
                'colunas': df_test.columns.tolist()
            }
            
        except Exception as e:
            continue
    
    raise ValueError(f"Não foi possível detectar o formato do arquivo {file_path}")


def mapear_cadunico_familia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia colunas do arquivo de família do CadÚnico para o formato do sistema.
    Usa TODAS as colunas relevantes disponíveis no arquivo.
    """
    logger.info(f"Mapeando {len(df)} registros de famílias do CadÚnico")
    
    df_mapped = pd.DataFrame()
    
    # 1. IDENTIFICAÇÃO DO MUNICÍPIO
    df_mapped['cod_municipio'] = df['cd_ibge']
    
    # 2. RENDA E FAMÍLIA
    df_mapped['renda_familiar'] = df['vlr_renda_media_fam'].fillna(0)
    df_mapped['qtd_pessoas_familia'] = df['qtde_pessoas'].fillna(1).astype(int)
    df_mapped['renda_per_capita'] = (
        df_mapped['renda_familiar'] / df_mapped['qtd_pessoas_familia'].replace(0, 1)
    ).replace([np.inf, -np.inf], 0).fillna(0)
    
    # 3. BOLSA FAMÍLIA
    # marc_pbf: 1=sim, 0=não
    df_mapped['recebe_bolsa_familia'] = df['marc_pbf'].fillna(0).astype(int)
    
    # 4. INFRAESTRUTURA - ÁGUA
    # cod_abaste_agua_domic_fam: 1=Rede geral de distribuição
    df_mapped['acesso_agua'] = (df['cod_abaste_agua_domic_fam'] == 1).astype(int)
    
    # 5. INFRAESTRUTURA - ESGOTO
    # cod_escoa_sanitario_domic_fam: 1=Rede coletora de esgoto, 2=Fossa séptica
    df_mapped['acesso_esgoto'] = df['cod_escoa_sanitario_domic_fam'].isin([1, 2]).astype(int)
    
    # 6. TIPO DE MORADIA
    # cod_material_domic_fam: 1=Alvenaria com revestimento, 2=Alvenaria sem revestimento, 
    # 3=Madeira aparelhada, 4=Taipa revestida, 5=Taipa não revestida, 6=Madeira aproveitada, 
    # 7=Palha, 8=Outro material
    material_mapping = {
        1.0: 2,  # Alvenaria com revestimento = Tipo 2 (melhor)
        2.0: 1,  # Alvenaria sem revestimento = Tipo 1 (médio)
        3.0: 1,  # Madeira aparelhada = Tipo 1
        4.0: 1,  # Taipa revestida = Tipo 1
        5.0: 0,  # Taipa não revestida = Tipo 0 (precário)
        6.0: 0,  # Madeira aproveitada = Tipo 0
        7.0: 0,  # Palha = Tipo 0
        8.0: 0,  # Outro material = Tipo 0
    }
    df_mapped['tipo_moradia'] = df['cod_material_domic_fam'].map(material_mapping).fillna(1).astype(int)
    
    # 7. COMODOS E SUPERLOTAÇÃO
    qtd_comodos = df['qtd_comodos_domic_fam'].fillna(4)
    pessoas_por_comodo = df_mapped['qtd_pessoas_familia'] / qtd_comodos.replace(0, 1)
    # Considera superlotação se há mais de 2 pessoas por cômodo
    df_mapped['superlotacao'] = (pessoas_por_comodo > 2).astype(int)
    
    # 8. ENERGIA ELÉTRICA
    # cod_iluminacao_domic_fam: 1=Elétrica, 2=Óleo/querosene/gás, 3=Vela, 4=Outra forma, 5=Não possui
    df_mapped['acesso_energia'] = (df['cod_iluminacao_domic_fam'] == 1).astype(int)
    
    # 9. COLETA DE LIXO
    # cod_destino_lixo_domic_fam: 1=Coletado, 2=Queimado/enterrado, 3=Céu aberto, 4=Outro
    df_mapped['coleta_lixo'] = (df['cod_destino_lixo_domic_fam'] == 1).astype(int)
    
    # 10. VALORES PADRÃO para colunas que não existem no arquivo de família
    # Estas serão preenchidas com valores médios/padrão
    df_mapped['idade'] = 35  # Idade padrão do responsável
    df_mapped['sexo'] = 'F'  # Sexo padrão (maioria dos responsáveis é mulher)
    df_mapped['escolaridade'] = 2  # Escolaridade padrão (fundamental completo)
    df_mapped['situacao_trabalho'] = 0  # Trabalho padrão (desempregado/informal)
    df_mapped['possui_deficiencia'] = 0  # Sem deficiência por padrão
    
    logger.info(f"✅ Família mapeada: {len(df_mapped)} registros com {len(df_mapped.columns)} colunas")
    logger.info(f"📊 Colunas geradas: {df_mapped.columns.tolist()}")
    
    return df_mapped


def mapear_cadunico_pessoa(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia colunas do arquivo de pessoa do CadÚnico.
    Extrai dados do responsável familiar.
    """
    logger.info(f"Mapeando {len(df)} registros de pessoas do CadÚnico")
    
    # Filtrar apenas responsáveis (cod_parentesco_rf_pessoa == 1)
    if 'cod_parentesco_rf_pessoa' in df.columns:
        df_resp = df[df['cod_parentesco_rf_pessoa'] == 1].copy()
        logger.info(f"Encontrados {len(df_resp)} responsáveis familiares")
    else:
        df_resp = df.copy()
    
    mapeamento = {
        'cod_familiar_fam': 'cod_familia',
        'idade_pessoa': 'idade',
        'cod_sexo_pessoa': 'sexo',
        'cod_curso_frequenta_pessoa': 'escolaridade',
        'cod_trabalho_12_meses_pessoa': 'situacao_trabalho',
    }
    
    df_mapped = pd.DataFrame()
    
    for col_origem, col_destino in mapeamento.items():
        if col_origem in df_resp.columns:
            df_mapped[col_destino] = df_resp[col_origem]
    
    # Mapear sexo (1=M, 2=F)
    if 'sexo' in df_mapped.columns:
        df_mapped['sexo'] = df_mapped['sexo'].map({1: 'M', 2: 'F'}).fillna('M')
    
    # Mapear situação trabalho (1=trabalhou, 2=não trabalhou)
    if 'situacao_trabalho' in df_mapped.columns:
        df_mapped['situacao_trabalho'] = df_mapped['situacao_trabalho'].map({
            1: 2,  # Trabalhou = Formal (código 2)
            2: 0,  # Não trabalhou = Desempregado (código 0)
        }).fillna(0).astype(int)
    
    logger.info(f"Pessoas mapeadas: {len(df_mapped)} registros")
    return df_mapped


def mapear_bolsa_familia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia colunas do arquivo de pagamentos do Bolsa Família.
    """
    logger.info(f"Mapeando {len(df)} registros do Bolsa Família")
    
    mapeamento = {
        'VALOR PARCELA': 'valor_bolsa_familia',
    }
    
    df_mapped = pd.DataFrame()
    
    for col_origem, col_destino in mapeamento.items():
        if col_origem in df.columns:
            df_mapped[col_destino] = df[col_origem]
    
    # Adicionar flag de recebimento
    df_mapped['recebe_bolsa_familia'] = 1
    
    return df_mapped


def carregar_e_mapear_arquivo(
    file_path: Path,
    max_rows: Optional[int] = None
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Carrega e mapeia automaticamente um arquivo do governo.
    
    Args:
        file_path: Caminho do arquivo
        max_rows: Limite de linhas a carregar
        
    Returns:
        Tuple com (DataFrame mapeado, informações de detecção)
    """
    # Detectar formato
    info = detectar_formato_arquivo(file_path)
    
    # Carregar arquivo completo
    logger.info(f"Carregando arquivo {file_path.name}...")
    df = pd.read_csv(
        file_path,
        sep=info['separador'],
        encoding=info['encoding'],
        nrows=max_rows
    )
    
    logger.info(f"Arquivo carregado: {len(df)} registros, {len(df.columns)} colunas")
    
    # Mapear conforme tipo detectado
    if info['tipo'] == 'cadunico_familia':
        df_mapped = mapear_cadunico_familia(df)
    elif info['tipo'] == 'cadunico_pessoa':
        df_mapped = mapear_cadunico_pessoa(df)
    elif info['tipo'] == 'bolsa_familia':
        df_mapped = mapear_bolsa_familia(df)
    else:
        # Se não detectou, retorna o DataFrame original
        logger.warning(f"Tipo não reconhecido, retornando dados originais")
        df_mapped = df
    
    return df_mapped, info


def mesclar_familia_pessoa(
    df_familia: pd.DataFrame,
    df_pessoa: pd.DataFrame
) -> pd.DataFrame:
    """
    Mescla dados de família e pessoa usando cod_familia.
    """
    if 'cod_familia' not in df_pessoa.columns:
        logger.warning("Dados de pessoa não têm 'cod_familia', retornando apenas família")
        return df_familia
    
    # Fazer merge
    df_final = df_familia.merge(
        df_pessoa,
        left_on='cod_municipio',  # Aproximação se não tiver ID comum
        right_on='cod_familia',
        how='left',
        suffixes=('', '_pessoa')
    )
    
    logger.info(f"Mesclagem completa: {len(df_final)} registros")
    return df_final


if __name__ == "__main__":
    # Teste do mapeador
    import sys
    
    if len(sys.argv) > 1:
        arquivo = Path(sys.argv[1])
        df_mapped, info = carregar_e_mapear_arquivo(arquivo, max_rows=10)
        
        print(f"\n{'='*70}")
        print(f"INFORMAÇÕES DO ARQUIVO")
        print(f"{'='*70}")
        print(f"Tipo: {info['tipo']}")
        print(f"Separador: {repr(info['separador'])}")
        print(f"Encoding: {info['encoding']}")
        print(f"\nColunas originais: {len(info['colunas'])}")
        print(f"Colunas mapeadas: {len(df_mapped.columns)}")
        print(f"\n{'='*70}")
        print(f"DADOS MAPEADOS (primeiras linhas)")
        print(f"{'='*70}")
        print(df_mapped.head())
    else:
        print("Uso: python mapeador_governo.py <arquivo.csv>")
