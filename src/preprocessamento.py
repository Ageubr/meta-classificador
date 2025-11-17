"""
Módulo de preprocessamento de dados para análise de vulnerabilidade social.

Este módulo contém funções para carregar, limpar e preparar dados do
CadÚnico e Bolsa Família para análise de vulnerabilidade social.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def carregar_dados_cadunico(
        caminho_arquivo: str = "data/cadunico.csv") -> pd.DataFrame:
    """
    Carrega dados do CadÚnico a partir de arquivo CSV.

    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV do CadÚnico

    Returns:
        pd.DataFrame: DataFrame com dados do CadÚnico
    """
    try:
        # Verificar se existe o arquivo processado primeiro
        caminho_processado = "data/cadunico_processado_100000.csv"
        if Path(caminho_processado).exists():
            logger.info("Carregando dados reais processados...")
            df = pd.read_csv(caminho_processado, encoding='utf-8')
            logger.info(
                f"Dados do CadÚnico carregados: {
                    df.shape[0]} registros, {
                    df.shape[1]} colunas")
            return df
        
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        logger.info(
            f"Dados do CadÚnico carregados: {
                df.shape[0]} registros, {
                df.shape[1]} colunas")
        return df
    except (FileNotFoundError, IsADirectoryError):
        logger.warning(
            f"Arquivo {caminho_arquivo} não encontrado. Gerando dados fictícios...")
        return gerar_dados_ficticios_cadunico()
    except Exception as e:
        logger.error(f"Erro ao carregar dados do CadÚnico: {e}")
        logger.warning("Gerando dados fictícios...")
        return gerar_dados_ficticios_cadunico()


def carregar_dados_bolsa_familia(
        caminho_arquivo: str = "data/bolsa_familia.csv") -> pd.DataFrame:
    """
    Carrega dados do Bolsa Família a partir de arquivo CSV.

    Args:
        caminho_arquivo (str): Caminho para o arquivo CSV do Bolsa Família

    Returns:
        pd.DataFrame: DataFrame com dados do Bolsa Família
    """
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        logger.info(
            f"Dados do Bolsa Família carregados: {
                df.shape[0]} registros, {
                df.shape[1]} colunas")
        return df
    except (FileNotFoundError, IsADirectoryError):
        logger.warning(
            f"Arquivo {caminho_arquivo} não encontrado. Gerando dados fictícios...")
        return gerar_dados_ficticios_bolsa_familia()
    except Exception as e:
        logger.error(f"Erro ao carregar dados do Bolsa Família: {e}")
        logger.warning("Gerando dados fictícios...")
        return gerar_dados_ficticios_bolsa_familia()


def gerar_dados_ficticios_cadunico(n_registros: int = 1000) -> pd.DataFrame:
    """
    Gera dados fictícios do CadÚnico para testes.

    Args:
        n_registros (int): Número de registros a gerar

    Returns:
        pd.DataFrame: DataFrame com dados fictícios do CadÚnico
    """
    np.random.seed(42)

    data = {
        'nis': [f"{np.random.randint(10000000000, 99999999999)}" for _ in range(n_registros)],
        'nome': [f"Pessoa_{i}" for i in range(n_registros)],
        'idade': np.random.randint(0, 80, n_registros),
        'sexo': np.random.choice(['M', 'F'], n_registros),
        # 0=analfabeto, 5=superior
        'escolaridade': np.random.choice([0, 1, 2, 3, 4, 5], n_registros),
        'renda_familiar': np.random.exponential(500, n_registros),
        'qtd_pessoas_familia': np.random.randint(1, 8, n_registros),
        'possui_deficiencia': np.random.choice([0, 1], n_registros, p=[0.85, 0.15]),
        # 0=desempregado, 1=informal, 2=formal
        'situacao_trabalho': np.random.choice([0, 1, 2], n_registros),
        # 1=própria, 2=alugada, 3=cedida, 4=ocupação
        'tipo_moradia': np.random.choice([1, 2, 3, 4], n_registros),
        'acesso_agua': np.random.choice([0, 1], n_registros, p=[0.2, 0.8]),
        'acesso_esgoto': np.random.choice([0, 1], n_registros, p=[0.3, 0.7]),
        'municipio': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Recife'], n_registros)
    }

    return pd.DataFrame(data)


def gerar_dados_ficticios_bolsa_familia(
        n_registros: int = 800) -> pd.DataFrame:
    """
    Gera dados fictícios do Bolsa Família para testes.

    Args:
        n_registros (int): Número de registros a gerar

    Returns:
        pd.DataFrame: DataFrame com dados fictícios do Bolsa Família
    """
    np.random.seed(43)

    # Simular que nem todos do CadÚnico recebem Bolsa Família
    nis_cadunico = [
        f"{np.random.randint(10000000000, 99999999999)}" for _ in range(1000)]
    nis_beneficiarios = np.random.choice(
        nis_cadunico, n_registros, replace=False)

    data = {
        'nis': nis_beneficiarios,
        'valor_beneficio': np.random.uniform(89, 400, n_registros),
        'data_inicio_beneficio': pd.date_range('2020-01-01', '2023-12-31', periods=n_registros),
        'status_beneficio': np.random.choice(['ativo', 'cancelado', 'suspenso'], n_registros, p=[0.8, 0.15, 0.05]),
        'modalidade': np.random.choice(['básico', 'variável', 'jovem'], n_registros),
        'municipio': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 'Recife'], n_registros)
    }

    return pd.DataFrame(data)


def tratar_dados_faltantes(
        df: pd.DataFrame,
        estrategia: str = 'mediana') -> pd.DataFrame:
    """
    Trata dados faltantes no DataFrame.

    Args:
        df (pd.DataFrame): DataFrame com dados a serem tratados
        estrategia (str): Estratégia para tratar dados faltantes ('mediana', 'media', 'moda', 'remover')

    Returns:
        pd.DataFrame: DataFrame com dados faltantes tratados
    """
    df_tratado = df.copy()

    if estrategia == 'mediana':
        for col in df_tratado.select_dtypes(include=[np.number]).columns:
            df_tratado[col].fillna(df_tratado[col].median(), inplace=True)
    elif estrategia == 'media':
        for col in df_tratado.select_dtypes(include=[np.number]).columns:
            df_tratado[col].fillna(df_tratado[col].mean(), inplace=True)
    elif estrategia == 'moda':
        for col in df_tratado.columns:
            df_tratado[col].fillna(
                df_tratado[col].mode().iloc[0] if not df_tratado[col].mode().empty else 0,
                inplace=True)
    elif estrategia == 'remover':
        df_tratado = df_tratado.dropna()

    logger.info(f"Dados faltantes tratados usando estratégia '{estrategia}'")
    return df_tratado


def gerar_features_vulnerabilidade(
        df_cadunico: pd.DataFrame,
        df_bolsa_familia: pd.DataFrame = None) -> pd.DataFrame:
    """
    Gera features para análise de vulnerabilidade social.

    Args:
        df_cadunico (pd.DataFrame): DataFrame do CadÚnico
        df_bolsa_familia (pd.DataFrame): DataFrame do Bolsa Família (opcional)

    Returns:
        pd.DataFrame: DataFrame com features de vulnerabilidade
    """
    df_features = df_cadunico.copy()
    
    # Verificar se já possui as features calculadas (dados já processados)
    if 'nivel_vulnerabilidade' in df_features.columns:
        logger.info("Dados já possuem features de vulnerabilidade calculadas")
        return df_features

    # Feature de renda per capita
    if 'renda_per_capita' not in df_features.columns:
        df_features['renda_per_capita'] = df_features['renda_familiar'] / \
            df_features['qtd_pessoas_familia']

    # Feature de vulnerabilidade por idade (crianças e idosos são mais
    # vulneráveis)
    if 'vulnerabilidade_idade' not in df_features.columns:
        df_features['vulnerabilidade_idade'] = (
            (df_features['idade'] < 18) | (
                df_features['idade'] > 65)).astype(int)

    # Feature de infraestrutura (combinação de acesso à água e esgoto)
    if 'infraestrutura_adequada' not in df_features.columns:
        df_features['infraestrutura_adequada'] = (
            df_features['acesso_agua'] & df_features['acesso_esgoto']).astype(int)

    # Feature de escolaridade baixa
    if 'escolaridade_baixa' not in df_features.columns:
        df_features['escolaridade_baixa'] = (
            df_features['escolaridade'] <= 2).astype(int)

    # Feature de desemprego/informalidade
    if 'situacao_trabalho_precaria' not in df_features.columns:
        df_features['situacao_trabalho_precaria'] = (
            df_features['situacao_trabalho'] <= 1).astype(int)

    # Feature de superlotação (muitas pessoas por família)
    if 'superlotacao' not in df_features.columns:
        df_features['superlotacao'] = (
            df_features['qtd_pessoas_familia'] > 5).astype(int)

    # Se temos dados do Bolsa Família, adicionar feature de recebimento
    if df_bolsa_familia is not None and 'recebe_bolsa_familia' not in df_features.columns:
        beneficiarios_ativos = df_bolsa_familia[df_bolsa_familia['status_beneficio'] == 'ativo']['nis'].unique(
        )
        df_features['recebe_bolsa_familia'] = df_features['nis'].isin(
            beneficiarios_ativos).astype(int)
    elif 'recebe_bolsa_familia' not in df_features.columns:
        df_features['recebe_bolsa_familia'] = 0

    # Score de vulnerabilidade (soma ponderada de fatores)
    if 'score_vulnerabilidade' not in df_features.columns:
        pesos = {
            'renda_per_capita': -0.3,  # Renda maior reduz vulnerabilidade
            'vulnerabilidade_idade': 0.2,
            'infraestrutura_adequada': -0.15,  # Infraestrutura adequada reduz vulnerabilidade
            'escolaridade_baixa': 0.15,
            'situacao_trabalho_precaria': 0.2,
            'superlotacao': 0.1,
            'possui_deficiencia': 0.1
        }

        # Normalizar renda per capita
        df_features['renda_per_capita_norm'] = (
            df_features['renda_per_capita'] - df_features['renda_per_capita'].mean()) / df_features['renda_per_capita'].std()

        score_vulnerabilidade = 0
        for feature, peso in pesos.items():
            if feature == 'renda_per_capita':
                score_vulnerabilidade += peso * \
                    df_features['renda_per_capita_norm']
            else:
                score_vulnerabilidade += peso * df_features[feature]

        df_features['score_vulnerabilidade'] = score_vulnerabilidade

    # Classificação categórica de vulnerabilidade
    if 'nivel_vulnerabilidade' not in df_features.columns:
        df_features['nivel_vulnerabilidade'] = pd.cut(
            df_features['score_vulnerabilidade'],
            bins=[-np.inf, -0.5, 0, 0.5, np.inf],
            labels=['Baixa', 'Média', 'Alta', 'Muito Alta']
        )

    logger.info(
        f"Features de vulnerabilidade geradas para {
            len(df_features)} registros")
    return df_features


def consolidar_dados(df_cadunico: pd.DataFrame,
                     df_bolsa_familia: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida dados do CadÚnico e Bolsa Família em um único DataFrame.

    Args:
        df_cadunico (pd.DataFrame): DataFrame do CadÚnico
        df_bolsa_familia (pd.DataFrame): DataFrame do Bolsa Família

    Returns:
        pd.DataFrame: DataFrame consolidado
    """
    # Fazer join pelos NIS
    df_consolidado = df_cadunico.merge(
        df_bolsa_familia[['nis', 'valor_beneficio', 'status_beneficio', 'modalidade']],
        on='nis',
        how='left'
    )

    # Preencher valores ausentes para quem não recebe Bolsa Família
    df_consolidado['valor_beneficio'].fillna(0, inplace=True)
    df_consolidado['status_beneficio'].fillna('não_beneficiário', inplace=True)
    df_consolidado['modalidade'].fillna('não_beneficiário', inplace=True)

    logger.info(f"Dados consolidados: {len(df_consolidado)} registros")
    return df_consolidado


def preparar_dados_para_ml(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepara dados para machine learning.

    Args:
        df (pd.DataFrame): DataFrame com features

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Features (X) e target (y)
    """
    # Selecionar features numéricas para ML
    features_numericas = [
        'idade', 'escolaridade', 'renda_per_capita', 'qtd_pessoas_familia',
        'possui_deficiencia', 'situacao_trabalho', 'tipo_moradia',
        'acesso_agua', 'acesso_esgoto', 'vulnerabilidade_idade',
        'infraestrutura_adequada', 'escolaridade_baixa',
        'situacao_trabalho_precaria', 'superlotacao'
    ]

    # Adicionar feature de Bolsa Família se existir
    if 'recebe_bolsa_familia' in df.columns:
        features_numericas.append('recebe_bolsa_familia')

    X = df[features_numericas].copy()

    # Target: nível de vulnerabilidade (convertido para numérico)
    target_mapping = {'Baixa': 0, 'Média': 1, 'Alta': 2, 'Muito Alta': 3}
    y = df['nivel_vulnerabilidade'].map(target_mapping)

    logger.info(
        f"Dados preparados para ML: {
            X.shape[0]} amostras, {
            X.shape[1]} features")
    return X, y


if __name__ == "__main__":
    # Exemplo de uso
    print("=== Exemplo de Uso do Módulo de Preprocessamento ===")

    # Carregar dados (irá gerar dados fictícios se os arquivos não existirem)
    df_cadunico = carregar_dados_cadunico()
    df_bolsa_familia = carregar_dados_bolsa_familia()

    # Tratar dados faltantes
    df_cadunico = tratar_dados_faltantes(df_cadunico)
    df_bolsa_familia = tratar_dados_faltantes(df_bolsa_familia)

    # Consolidar dados
    df_consolidado = consolidar_dados(df_cadunico, df_bolsa_familia)

    # Gerar features de vulnerabilidade
    df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa_familia)

    # Preparar dados para ML
    X, y = preparar_dados_para_ml(df_features)

    print(f"\nResumo dos dados:")
    print(f"- CadÚnico: {len(df_cadunico)} registros")
    print(f"- Bolsa Família: {len(df_bolsa_familia)} registros")
    print(f"- Features para ML: {X.shape}")
    print(f"- Distribuição de vulnerabilidade:")
    print(df_features['nivel_vulnerabilidade'].value_counts())
