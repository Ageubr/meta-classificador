"""
Testes unitários para o módulo de preprocessamento.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from preprocessamento import (
    gerar_dados_ficticios_cadunico,
    gerar_dados_ficticios_bolsa_familia,
    tratar_dados_faltantes,
    gerar_features_vulnerabilidade,
    preparar_dados_para_ml
)


class TestGeracaoDadosFicticios:
    """Testes para geração de dados fictícios."""

    def test_gerar_dados_cadunico_quantidade(self):
        """Testa se gera quantidade correta de registros."""
        n_registros = 100
        df = gerar_dados_ficticios_cadunico(n_registros)
        assert len(df) == n_registros

    def test_gerar_dados_cadunico_colunas(self):
        """Testa se possui todas as colunas necessárias."""
        df = gerar_dados_ficticios_cadunico(10)
        colunas_esperadas = [
            'nis', 'nome', 'idade', 'sexo', 'escolaridade',
            'renda_familiar', 'qtd_pessoas_familia', 'possui_deficiencia',
            'situacao_trabalho', 'tipo_moradia', 'acesso_agua',
            'acesso_esgoto', 'municipio'
        ]
        for coluna in colunas_esperadas:
            assert coluna in df.columns

    def test_gerar_dados_cadunico_tipos(self):
        """Testa tipos de dados das colunas."""
        df = gerar_dados_ficticios_cadunico(10)
        assert df['idade'].dtype in [np.int64, np.int32]
        assert df['renda_familiar'].dtype in [np.float64, np.float32]
        assert df['sexo'].dtype == object

    def test_gerar_dados_bolsa_familia_quantidade(self):
        """Testa se gera quantidade correta de registros."""
        n_registros = 50
        df = gerar_dados_ficticios_bolsa_familia(n_registros)
        assert len(df) == n_registros

    def test_gerar_dados_bolsa_familia_colunas(self):
        """Testa se possui todas as colunas necessárias."""
        df = gerar_dados_ficticios_bolsa_familia(10)
        colunas_esperadas = [
            'nis', 'valor_beneficio', 'data_inicio_beneficio',
            'status_beneficio', 'modalidade', 'municipio'
        ]
        for coluna in colunas_esperadas:
            assert coluna in df.columns


class TestTratamentoDadosFaltantes:
    """Testes para tratamento de dados faltantes."""

    def test_tratamento_mediana(self):
        """Testa tratamento com mediana."""
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': [10, np.nan, 30, 40, 50]
        })
        df_tratado = tratar_dados_faltantes(df, estrategia='mediana')
        assert df_tratado['col1'].isna().sum() == 0
        assert df_tratado['col2'].isna().sum() == 0

    def test_tratamento_media(self):
        """Testa tratamento com média."""
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': [10, np.nan, 30, 40, 50]
        })
        df_tratado = tratar_dados_faltantes(df, estrategia='media')
        assert df_tratado['col1'].isna().sum() == 0
        assert df_tratado['col2'].isna().sum() == 0

    def test_tratamento_remover(self):
        """Testa remoção de linhas com dados faltantes."""
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': [10, 20, 30, 40, 50]
        })
        df_tratado = tratar_dados_faltantes(df, estrategia='remover')
        assert len(df_tratado) == 4  # Remove 1 linha


class TestGeracaoFeatures:
    """Testes para geração de features de vulnerabilidade."""

    def test_gerar_features_basicas(self):
        """Testa geração de features básicas."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)

        # Verificar novas features criadas
        features_esperadas = [
            'renda_per_capita',
            'vulnerabilidade_idade',
            'infraestrutura_adequada',
            'escolaridade_baixa',
            'situacao_trabalho_precaria',
            'superlotacao',
            'score_vulnerabilidade',
            'nivel_vulnerabilidade'
        ]

        for feature in features_esperadas:
            assert feature in df_features.columns

    def test_gerar_features_com_bolsa_familia(self):
        """Testa geração de features incluindo Bolsa Família."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_bolsa = gerar_dados_ficticios_bolsa_familia(30)
        df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa)

        assert 'recebe_bolsa_familia' in df_features.columns

    def test_renda_per_capita_calculo(self):
        """Testa cálculo correto da renda per capita."""
        df_cadunico = pd.DataFrame({
            'nis': ['123'],
            'nome': ['Teste'],
            'idade': [30],
            'sexo': ['M'],
            'escolaridade': [2],
            'renda_familiar': [1000],
            'qtd_pessoas_familia': [4],
            'possui_deficiencia': [0],
            'situacao_trabalho': [1],
            'tipo_moradia': [1],
            'acesso_agua': [1],
            'acesso_esgoto': [1],
            'municipio': ['São Paulo']
        })

        df_features = gerar_features_vulnerabilidade(df_cadunico)
        assert df_features['renda_per_capita'].iloc[0] == 250  # 1000/4

    def test_nivel_vulnerabilidade_categorias(self):
        """Testa se níveis de vulnerabilidade estão corretos."""
        df_cadunico = gerar_dados_ficticios_cadunico(100)
        df_features = gerar_features_vulnerabilidade(df_cadunico)

        niveis_validos = ['Baixa', 'Média', 'Alta', 'Muito Alta']
        assert df_features['nivel_vulnerabilidade'].isin(niveis_validos).all()


class TestPreparacaoDadosML:
    """Testes para preparação de dados para ML."""

    def test_preparar_dados_dimensoes(self):
        """Testa dimensões dos dados preparados."""
        df_cadunico = gerar_dados_ficticios_cadunico(100)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        assert X.shape[0] == 100  # Número de amostras
        assert y.shape[0] == 100
        assert X.shape[1] > 0  # Número de features

    def test_preparar_dados_tipos(self):
        """Testa tipos de dados retornados."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)

    def test_target_valores_validos(self):
        """Testa se target possui apenas valores válidos."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        valores_validos = [0, 1, 2, 3]  # Baixa, Média, Alta, Muito Alta
        assert y.isin(valores_validos).all()

    def test_sem_dados_faltantes_X(self):
        """Testa se X não possui dados faltantes."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        assert X.isna().sum().sum() == 0

    def test_sem_dados_faltantes_y(self):
        """Testa se y não possui dados faltantes."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        assert y.isna().sum() == 0


class TestValidacaoDados:
    """Testes para validação de dados."""

    def test_idade_valida(self):
        """Testa se idades geradas são válidas."""
        df = gerar_dados_ficticios_cadunico(100)
        assert (df['idade'] >= 0).all()
        assert (df['idade'] <= 120).all()

    def test_renda_valida(self):
        """Testa se rendas geradas são válidas."""
        df = gerar_dados_ficticios_cadunico(100)
        assert (df['renda_familiar'] >= 0).all()

    def test_qtd_pessoas_familia_valida(self):
        """Testa se quantidade de pessoas é válida."""
        df = gerar_dados_ficticios_cadunico(100)
        assert (df['qtd_pessoas_familia'] >= 1).all()
        assert (df['qtd_pessoas_familia'] <= 20).all()

    def test_sexo_valido(self):
        """Testa se sexo possui apenas valores válidos."""
        df = gerar_dados_ficticios_cadunico(100)
        assert df['sexo'].isin(['M', 'F']).all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
