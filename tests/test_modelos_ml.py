"""
Testes unitários para o módulo de modelos de Machine Learning.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import tempfile
import os

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modelos_ml import (
    RandomForestVulnerabilidade,
    XGBoostVulnerabilidade,
    comparar_modelos
)
from preprocessamento import (
    gerar_dados_ficticios_cadunico,
    gerar_features_vulnerabilidade,
    preparar_dados_para_ml
)


@pytest.fixture
def dados_teste():
    """Fixture para gerar dados de teste."""
    df_cadunico = gerar_dados_ficticios_cadunico(200)
    df_features = gerar_features_vulnerabilidade(df_cadunico)
    X, y = preparar_dados_para_ml(df_features)
    return X, y


class TestRandomForestVulnerabilidade:
    """Testes para o modelo Random Forest."""

    def test_inicializacao(self):
        """Testa inicialização do modelo."""
        modelo = RandomForestVulnerabilidade()
        assert modelo.nome_modelo == "Random Forest"
        assert modelo.modelo is None

    def test_treinamento(self, dados_teste):
        """Testa treinamento do modelo."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        metricas = modelo.treinar(X, y, validacao_cruzada=False)

        assert 'acuracia_treino' in metricas
        assert 'acuracia_teste' in metricas
        assert metricas['acuracia_treino'] > 0
        assert metricas['acuracia_teste'] > 0

    def test_predicao(self, dados_teste):
        """Testa predição do modelo."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        predicoes = modelo.predizer(X.head(10))
        assert len(predicoes) == 10
        assert all(p in [0, 1, 2, 3] for p in predicoes)

    def test_predicao_probabilidade(self, dados_teste):
        """Testa predição de probabilidades."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        probs = modelo.predizer_probabilidade(X.head(10))
        assert probs.shape == (10, 4)  # 10 amostras, 4 classes
        # Soma das probabilidades = 1
        assert np.allclose(probs.sum(axis=1), 1.0)

    def test_salvar_carregar_modelo(self, dados_teste):
        """Testa salvamento e carregamento do modelo."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, 'modelo_teste.pkl')
            modelo.salvar_modelo(caminho)

            modelo_carregado = RandomForestVulnerabilidade()
            modelo_carregado.carregar_modelo(caminho)

            # Testar que predições são iguais
            pred_original = modelo.predizer(X.head(5))
            pred_carregado = modelo_carregado.predizer(X.head(5))
            assert np.array_equal(pred_original, pred_carregado)

    def test_importancia_features(self, dados_teste):
        """Testa importância das features."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        metricas = modelo.treinar(X, y, validacao_cruzada=False)

        assert 'importancia_features' in metricas
        assert len(metricas['importancia_features']) == X.shape[1]


class TestXGBoostVulnerabilidade:
    """Testes para o modelo XGBoost."""

    def test_inicializacao(self):
        """Testa inicialização do modelo."""
        modelo = XGBoostVulnerabilidade()
        assert modelo.nome_modelo == "XGBoost"
        assert modelo.modelo is None

    def test_treinamento(self, dados_teste):
        """Testa treinamento do modelo."""
        X, y = dados_teste
        modelo = XGBoostVulnerabilidade(n_estimators=10)
        metricas = modelo.treinar(X, y, validacao_cruzada=False)

        assert 'acuracia_treino' in metricas
        assert 'acuracia_teste' in metricas
        assert metricas['acuracia_treino'] > 0
        assert metricas['acuracia_teste'] > 0

    def test_predicao(self, dados_teste):
        """Testa predição do modelo."""
        X, y = dados_teste
        modelo = XGBoostVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        predicoes = modelo.predizer(X.head(10))
        assert len(predicoes) == 10
        assert all(p in [0, 1, 2, 3] for p in predicoes)

    def test_predicao_probabilidade(self, dados_teste):
        """Testa predição de probabilidades."""
        X, y = dados_teste
        modelo = XGBoostVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        probs = modelo.predizer_probabilidade(X.head(10))
        assert probs.shape == (10, 4)  # 10 amostras, 4 classes
        # Soma das probabilidades = 1
        assert np.allclose(probs.sum(axis=1), 1.0)

    def test_salvar_carregar_modelo(self, dados_teste):
        """Testa salvamento e carregamento do modelo."""
        X, y = dados_teste
        modelo = XGBoostVulnerabilidade(n_estimators=10)
        modelo.treinar(X, y, validacao_cruzada=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, 'modelo_teste.pkl')
            modelo.salvar_modelo(caminho)

            modelo_carregado = XGBoostVulnerabilidade()
            modelo_carregado.carregar_modelo(caminho)

            # Testar que predições são iguais
            pred_original = modelo.predizer(X.head(5))
            pred_carregado = modelo_carregado.predizer(X.head(5))
            assert np.array_equal(pred_original, pred_carregado)


class TestComparacaoModelos:
    """Testes para comparação entre modelos."""

    def test_comparar_modelos(self, dados_teste):
        """Testa comparação entre Random Forest e XGBoost."""
        X, y = dados_teste

        # Usar poucos estimadores para teste rápido
        resultado = comparar_modelos(X, y)

        assert 'comparacao' in resultado
        assert 'melhor_modelo' in resultado
        assert 'modelos_treinados' in resultado

        assert 'Random Forest' in resultado['comparacao']
        assert 'XGBoost' in resultado['comparacao']

        assert resultado['melhor_modelo'] in ['Random Forest', 'XGBoost']


class TestMetricasModelos:
    """Testes para métricas dos modelos."""

    def test_metricas_completas(self, dados_teste):
        """Testa se todas as métricas são retornadas."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        metricas = modelo.treinar(X, y, validacao_cruzada=True)

        metricas_esperadas = [
            'acuracia_treino',
            'acuracia_teste',
            'relatorio_classificacao',
            'matriz_confusao',
            'importancia_features',
            'validacao_cruzada'
        ]

        for metrica in metricas_esperadas:
            assert metrica in metricas

    def test_validacao_cruzada(self, dados_teste):
        """Testa validação cruzada."""
        X, y = dados_teste
        modelo = RandomForestVulnerabilidade(n_estimators=10)
        metricas = modelo.treinar(X, y, validacao_cruzada=True)

        assert 'validacao_cruzada' in metricas
        assert 'scores' in metricas['validacao_cruzada']
        assert 'media' in metricas['validacao_cruzada']
        assert 'desvio_padrao' in metricas['validacao_cruzada']

        # Deve ter 5 scores (cv=5)
        assert len(metricas['validacao_cruzada']['scores']) == 5


class TestRobustez:
    """Testes de robustez dos modelos."""

    def test_modelo_com_poucos_dados(self):
        """Testa modelo com poucos dados."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        modelo = RandomForestVulnerabilidade(n_estimators=5)
        metricas = modelo.treinar(X, y, validacao_cruzada=False)

        assert metricas['acuracia_treino'] > 0

    def test_predicao_sem_treinamento(self):
        """Testa que predição sem treinamento gera erro."""
        df_cadunico = gerar_dados_ficticios_cadunico(50)
        df_features = gerar_features_vulnerabilidade(df_cadunico)
        X, y = preparar_dados_para_ml(df_features)

        modelo = RandomForestVulnerabilidade()

        with pytest.raises(ValueError):
            modelo.predizer(X)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
