"""
Módulo de modelos de Machine Learning para análise de vulnerabilidade social.

Este módulo contém implementações de Random Forest e XGBoost para classificar
níveis de vulnerabilidade social baseado em dados do CadÚnico e Bolsa Família.
"""

import pandas as pd
import numpy as np
import pickle
import joblib
from typing import Tuple, Dict, Any, Optional
import logging
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Visualização
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar matplotlib para não mostrar plots em modo headless
plt.switch_backend('Agg')


class ModeloVulnerabilidade:
    """
    Classe base para modelos de classificação de vulnerabilidade social.
    """

    def __init__(self, nome_modelo: str):
        self.nome_modelo = nome_modelo
        self.modelo = None
        self.scaler = StandardScaler()
        self.features_names = None
        self.historico_treino = {}

    def treinar(self, X: pd.DataFrame, y: pd.Series, validacao_cruzada: bool = True) -> Dict[str, Any]:
        """
        Treina o modelo com os dados fornecidos.

        Args:
            X (pd.DataFrame): Features de entrada
            y (pd.Series): Target (níveis de vulnerabilidade)
            validacao_cruzada (bool): Se deve fazer validação cruzada

        Returns:
            Dict[str, Any]: Métricas de performance do modelo
        """
        raise NotImplementedError("Subclasses devem implementar este método")

    def predizer(self, X: pd.DataFrame) -> np.ndarray:
        """
        Faz predições com o modelo treinado.

        Args:
            X (pd.DataFrame): Features de entrada

        Returns:
            np.ndarray: Predições do modelo
        """
        if self.modelo is None:
            raise ValueError("Modelo não foi treinado ainda")

        X_scaled = self.scaler.transform(X)
        return self.modelo.predict(X_scaled)

    def predizer_probabilidade(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retorna probabilidades das predições.

        Args:
            X (pd.DataFrame): Features de entrada

        Returns:
            np.ndarray: Probabilidades das classes
        """
        if self.modelo is None:
            raise ValueError("Modelo não foi treinado ainda")

        X_scaled = self.scaler.transform(X)
        return self.modelo.predict_proba(X_scaled)

    def salvar_modelo(self, caminho: str):
        """
        Salva o modelo treinado em disco.

        Args:
            caminho (str): Caminho para salvar o modelo
        """
        modelo_data = {
            'modelo': self.modelo,
            'scaler': self.scaler,
            'features_names': self.features_names,
            'historico_treino': self.historico_treino,
            'nome_modelo': self.nome_modelo
        }

        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(modelo_data, caminho)
        logger.info(f"Modelo {self.nome_modelo} salvo em {caminho}")

    def carregar_modelo(self, caminho: str):
        """
        Carrega modelo salvo do disco.

        Args:
            caminho (str): Caminho do modelo salvo
        """
        modelo_data = joblib.load(caminho)
        self.modelo = modelo_data['modelo']
        self.scaler = modelo_data['scaler']
        self.features_names = modelo_data['features_names']
        self.historico_treino = modelo_data['historico_treino']
        self.nome_modelo = modelo_data['nome_modelo']
        logger.info(f"Modelo {self.nome_modelo} carregado de {caminho}")


class RandomForestVulnerabilidade(ModeloVulnerabilidade):
    """
    Implementação de Random Forest para classificação de vulnerabilidade.
    """

    def __init__(self, n_estimators: int = 100, max_depth: Optional[int] = None, random_state: int = 42):
        super().__init__("Random Forest")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

    def treinar(self, X: pd.DataFrame, y: pd.Series, validacao_cruzada: bool = True) -> Dict[str, Any]:
        """
        Treina o modelo Random Forest.
        """
        logger.info(f"Iniciando treinamento do {self.nome_modelo}")

        # Salvar nomes das features
        self.features_names = X.columns.tolist()

        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )

        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Treinar modelo
        self.modelo = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )

        self.modelo.fit(X_train_scaled, y_train)

        # Avaliar modelo
        y_pred_train = self.modelo.predict(X_train_scaled)
        y_pred_test = self.modelo.predict(X_test_scaled)

        metricas = {
            'acuracia_treino': accuracy_score(y_train, y_pred_train),
            'acuracia_teste': accuracy_score(y_test, y_pred_test),
            'relatorio_classificacao': classification_report(y_test, y_pred_test, output_dict=True),
            'matriz_confusao': confusion_matrix(y_test, y_pred_test).tolist(),
            'importancia_features': dict(zip(self.features_names, self.modelo.feature_importances_))
        }

        # Validação cruzada
        if validacao_cruzada:
            cv_scores = cross_val_score(self.modelo, X_train_scaled, y_train, cv=5)
            metricas['validacao_cruzada'] = {
                'scores': cv_scores.tolist(),
                'media': cv_scores.mean(),
                'desvio_padrao': cv_scores.std()
            }

        self.historico_treino = metricas

        logger.info(f"Treinamento concluído - Acurácia teste: {metricas['acuracia_teste']:.4f}")
        return metricas

    def otimizar_hiperparametros(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Otimiza hiperparâmetros usando Grid Search.
        """
        logger.info("Iniciando otimização de hiperparâmetros")

        # Preparar dados
        X_scaled = self.scaler.fit_transform(X)

        # Definir grid de parâmetros
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }

        # Grid Search
        rf = RandomForestClassifier(random_state=self.random_state, n_jobs=-1)
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )

        grid_search.fit(X_scaled, y)

        # Atualizar modelo com melhores parâmetros
        self.modelo = grid_search.best_estimator_

        resultados = {
            'melhores_parametros': grid_search.best_params_,
            'melhor_score': grid_search.best_score_,
            'resultados_grid': grid_search.cv_results_
        }

        logger.info(f"Otimização concluída - Melhor score: {resultados['melhor_score']:.4f}")
        return resultados


class XGBoostVulnerabilidade(ModeloVulnerabilidade):
    """
    Implementação de XGBoost para classificação de vulnerabilidade.
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = 6, learning_rate: float = 0.1, random_state: int = 42):
        super().__init__("XGBoost")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state

    def treinar(self, X: pd.DataFrame, y: pd.Series, validacao_cruzada: bool = True) -> Dict[str, Any]:
        """
        Treina o modelo XGBoost.
        """
        logger.info(f"Iniciando treinamento do {self.nome_modelo}")

        # Salvar nomes das features
        self.features_names = X.columns.tolist()

        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state, stratify=y
        )

        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Treinar modelo
        self.modelo = xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            eval_metric='mlogloss',
            n_jobs=-1
        )

        # Treinar com early stopping (apenas quando temos eval_set)
        self.modelo.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )

        # Avaliar modelo
        y_pred_train = self.modelo.predict(X_train_scaled)
        y_pred_test = self.modelo.predict(X_test_scaled)

        metricas = {
            'acuracia_treino': accuracy_score(y_train, y_pred_train),
            'acuracia_teste': accuracy_score(y_test, y_pred_test),
            'relatorio_classificacao': classification_report(y_test, y_pred_test, output_dict=True),
            'matriz_confusao': confusion_matrix(y_test, y_pred_test).tolist(),
            'importancia_features': dict(zip(self.features_names, self.modelo.feature_importances_))
        }

        # Validação cruzada
        if validacao_cruzada:
            cv_scores = cross_val_score(self.modelo, X_train_scaled, y_train, cv=5)
            metricas['validacao_cruzada'] = {
                'scores': cv_scores.tolist(),
                'media': cv_scores.mean(),
                'desvio_padrao': cv_scores.std()
            }

        self.historico_treino = metricas

        logger.info(f"Treinamento concluído - Acurácia teste: {metricas['acuracia_teste']:.4f}")
        return metricas


def comparar_modelos(X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """
    Compara performance de diferentes modelos.

    Args:
        X (pd.DataFrame): Features
        y (pd.Series): Target

    Returns:
        Dict[str, Any]: Comparação dos modelos
    """
    logger.info("Comparando modelos Random Forest e XGBoost")

    # Inicializar modelos
    rf_model = RandomForestVulnerabilidade()
    xgb_model = XGBoostVulnerabilidade()

    # Treinar modelos
    rf_metricas = rf_model.treinar(X, y)
    xgb_metricas = xgb_model.treinar(X, y)

    # Comparar resultados
    comparacao = {
        'Random Forest': {
            'acuracia_teste': rf_metricas['acuracia_teste'],
            'cv_media': rf_metricas['validacao_cruzada']['media'],
            'cv_std': rf_metricas['validacao_cruzada']['desvio_padrao']
        },
        'XGBoost': {
            'acuracia_teste': xgb_metricas['acuracia_teste'],
            'cv_media': xgb_metricas['validacao_cruzada']['media'],
            'cv_std': xgb_metricas['validacao_cruzada']['desvio_padrao']
        }
    }

    # Determinar melhor modelo
    melhor_modelo = 'Random Forest' if rf_metricas['acuracia_teste'] > xgb_metricas['acuracia_teste'] else 'XGBoost'

    resultado = {
        'comparacao': comparacao,
        'melhor_modelo': melhor_modelo,
        'modelos_treinados': {
            'random_forest': rf_model,
            'xgboost': xgb_model
        }
    }

    logger.info(f"Melhor modelo: {melhor_modelo}")
    return resultado


def gerar_relatorio_features(modelo: ModeloVulnerabilidade, caminho_saida: str = "outputs/importancia_features.png"):
    """
    Gera relatório visual da importância das features.

    Args:
        modelo (ModeloVulnerabilidade): Modelo treinado
        caminho_saida (str): Caminho para salvar o gráfico
    """
    if modelo.modelo is None:
        raise ValueError("Modelo não foi treinado ainda")

    # Obter importância das features
    importancias = modelo.historico_treino['importancia_features']

    # Ordenar por importância
    features_ordenadas = sorted(importancias.items(), key=lambda x: x[1], reverse=True)

    # Criar gráfico
    plt.figure(figsize=(12, 8))
    features, valores = zip(*features_ordenadas)

    plt.barh(range(len(features)), valores)
    plt.yticks(range(len(features)), features)
    plt.xlabel('Importância')
    plt.title(f'Importância das Features - {modelo.nome_modelo}')
    plt.tight_layout()

    # Salvar gráfico
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Relatório de features salvo em {caminho_saida}")


def treinar_e_salvar_modelos(X: pd.DataFrame, y: pd.Series, pasta_modelos: str = "outputs/modelos"):
    """
    Treina e salva todos os modelos.

    Args:
        X (pd.DataFrame): Features
        y (pd.Series): Target
        pasta_modelos (str): Pasta para salvar os modelos
    """
    logger.info("Iniciando treinamento e salvamento de todos os modelos")

    # Criar pasta se não existir
    Path(pasta_modelos).mkdir(parents=True, exist_ok=True)

    # Treinar Random Forest
    rf_model = RandomForestVulnerabilidade()
    rf_metricas = rf_model.treinar(X, y)
    rf_model.salvar_modelo(f"{pasta_modelos}/random_forest_vulnerabilidade.pkl")

    # Treinar XGBoost
    xgb_model = XGBoostVulnerabilidade()
    xgb_metricas = xgb_model.treinar(X, y)
    xgb_model.salvar_modelo(f"{pasta_modelos}/xgboost_vulnerabilidade.pkl")

    # Gerar relatórios de features
    gerar_relatorio_features(rf_model, f"{pasta_modelos}/rf_features_importance.png")
    gerar_relatorio_features(xgb_model, f"{pasta_modelos}/xgb_features_importance.png")

    # Salvar métricas
    metricas_resumo = {
        'random_forest': rf_metricas,
        'xgboost': xgb_metricas,
        'data_treinamento': pd.Timestamp.now().isoformat()
    }

    with open(f"{pasta_modelos}/metricas_modelos.json", 'w') as f:
        import json
        json.dump(metricas_resumo, f, indent=2, default=str)

    logger.info("Todos os modelos foram treinados e salvos com sucesso")
    return metricas_resumo


if __name__ == "__main__":
    # Exemplo de uso
    print("=== Exemplo de Uso dos Modelos de ML ===")

    # Importar dados (assumindo que preprocessamento.py está no mesmo diretório)
    import sys
    sys.path.append('.')

    try:
        from preprocessamento import carregar_dados_cadunico, carregar_dados_bolsa_familia, gerar_features_vulnerabilidade, preparar_dados_para_ml

        # Carregar e preparar dados
        df_cadunico = carregar_dados_cadunico()
        df_bolsa_familia = carregar_dados_bolsa_familia()
        df_features = gerar_features_vulnerabilidade(df_cadunico, df_bolsa_familia)
        X, y = preparar_dados_para_ml(df_features)

        # Treinar e salvar modelos
        metricas = treinar_e_salvar_modelos(X, y)

        print("\nResumo do treinamento:")
        print(f"Random Forest - Acurácia: {metricas['random_forest']['acuracia_teste']:.4f}")
        print(f"XGBoost - Acurácia: {metricas['xgboost']['acuracia_teste']:.4f}")

        # Comparar modelos
        comparacao = comparar_modelos(X, y)
        print(f"\nMelhor modelo: {comparacao['melhor_modelo']}")

    except ImportError:
        print("Erro: Não foi possível importar o módulo preprocessamento.py")
        print("Execute este script a partir do diretório raiz do projeto")
