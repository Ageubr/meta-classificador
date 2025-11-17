#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST para o Sistema de Meta-Classificação de Vulnerabilidade Social
Fornece endpoints para predições e análises usando FastAPI
"""

# Imports padrão
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Imports terceiros
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import pandas as pd
import joblib

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Imports locais
from preprocessamento import gerar_features_vulnerabilidade, preparar_dados_para_ml
from meta_classificador_llm import MetaClassificadorLLM

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="API de Análise de Vulnerabilidade Social",
    description="API para classificação de vulnerabilidade social usando ML e LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis globais para modelos
rf_model = None
xgb_model = None
feature_names = None
meta_classificador = None


# Modelos Pydantic
class DadosFamilia(BaseModel):
    """Modelo Pydantic para dados de entrada de uma família."""
    idade_responsavel: int
    numero_membros: int
    criancas: int
    idosos: int
    renda_per_capita: float
    pessoas_trabalhando: int
    possui_agua_encanada: bool
    possui_esgoto: bool
    possui_coleta_lixo: bool
    possui_energia: bool
    material_parede: str  # "Alvenaria", "Madeira", "Taipa", "Outros"
    material_teto: str
    comodos: int
    possui_banheiro: bool
    tempo_residencia: int  # em meses
    recebe_bolsa_familia: bool
    valor_bolsa_familia: float
    nivel_escolaridade: str
    situacao_trabalho: str

    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "idade_responsavel": 35,
                "numero_membros": 4,
                "criancas": 2,
                "idosos": 0,
                "renda_per_capita": 200.0,
                "pessoas_trabalhando": 1,
                "possui_agua_encanada": True,
                "possui_esgoto": False,
                "possui_coleta_lixo": True,
                "possui_energia": True,
                "material_parede": "Alvenaria",
                "material_teto": "Telha",
                "comodos": 3,
                "possui_banheiro": True,
                "tempo_residencia": 24,
                "recebe_bolsa_familia": True,
                "valor_bolsa_familia": 150.0,
                "nivel_escolaridade": "Fundamental",
                "situacao_trabalho": "Autônomo"
            }
        }


class PredictionResponse(BaseModel):
    """Modelo de resposta para predições."""
    vulnerabilidade_rf: str
    vulnerabilidade_xgb: str
    probabilidade_rf: dict
    probabilidade_xgb: dict
    features_importantes: dict
    timestamp: str


# Eventos da aplicação
@app.on_event("startup")
async def startup_event():
    """Carrega os modelos treinados na inicialização da API."""
    global rf_model, xgb_model, feature_names, meta_classificador

    try:
        # Carregar modelos treinados
        modelos_dir = Path(__file__).parent.parent / "outputs" / "modelos"

        rf_path = modelos_dir / "random_forest_vulnerabilidade.pkl"
        xgb_path = modelos_dir / "xgboost_vulnerabilidade.pkl"

        if rf_path.exists():
            rf_data = joblib.load(rf_path)
            rf_model = rf_data['modelo']
            feature_names = rf_data.get('features', None)
            logger.info("Modelo Random Forest carregado com sucesso")
        else:
            logger.warning("Modelo RF não encontrado em %s", rf_path)

        if xgb_path.exists():
            xgb_data = joblib.load(xgb_path)
            xgb_model = xgb_data['modelo']
            if not feature_names:
                feature_names = xgb_data.get('features', None)
            logger.info("Modelo XGBoost carregado com sucesso")
        else:
            logger.warning("Modelo XGBoost não encontrado em %s", xgb_path)

        # Inicializar meta-classificador LLM
        meta_classificador = MetaClassificadorLLM()
        logger.info("Meta-classificador LLM inicializado")

        logger.info("API iniciada com sucesso!")

    except Exception as e:
        logger.error("Erro ao carregar modelos: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erro ao carregar modelos: {str(e)}"
        ) from e


# Montar arquivos estáticos (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Frontend montado em /static")


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Serve a interface web do sistema."""
    frontend_file = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    else:
        return {
            "mensagem": "API de Análise de Vulnerabilidade Social",
            "versao": "1.0.0",
            "documentacao": "/docs",
            "health": "/health",
            "interface": "Frontend não encontrado. Acesse /docs para API docs."
        }


@app.get("/api", tags=["Info"])
async def api_info():
    """Informações da API."""
    return {
        "mensagem": "API de Análise de Vulnerabilidade Social",
        "versao": "1.0.0",
        "documentacao": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica o status de saúde da API e dos modelos carregados."""
    try:
        models_status = {
            "random_forest": rf_model is not None,
            "xgboost": xgb_model is not None,
            "meta_classificador": meta_classificador is not None
        }

        return {
            "status": "healthy",
            "models": models_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("Erro no health check: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no health check: {str(e)}"
        ) from e


@app.get("/models", tags=["Models"])
async def listar_modelos():
    """Lista os modelos disponíveis e suas informações."""
    return {
        "modelos_disponiveis": {
            "random_forest": {
                "status": "carregado" if rf_model is not None else "não carregado",
                "tipo": "Classificador de Ensemble"
            },
            "xgboost": {
                "status": "carregado" if xgb_model is not None else "não carregado",
                "tipo": "Gradient Boosting"
            },
            "meta_classificador": {
                "status": "carregado" if meta_classificador is not None else "não carregado",
                "tipo": "Meta-Classificador com LLM"
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(dados: DadosFamilia):
    """
    Realiza predição de vulnerabilidade social para uma família.
    Retorna classificações de ambos os modelos (RF e XGBoost) com probabilidades.
    """
    if rf_model is None or xgb_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados. Execute o treinamento primeiro."
        )

    try:
        # Converter dados para DataFrame
        dados_dict = dados.dict()
        df = pd.DataFrame([dados_dict])
        
        # Mapear campos da API para campos esperados pelo preprocessamento
        df['idade'] = df['idade_responsavel']
        df['qtd_pessoas_familia'] = df['numero_membros']
        df['acesso_agua'] = df['possui_agua_encanada'].astype(int)
        df['acesso_esgoto'] = df['possui_esgoto'].astype(int)
        df['possui_deficiencia'] = 0  # Usar campo pessoa_deficiencia quando disponível
        df['tipo_moradia'] = df['material_parede'].map({
            'Alvenaria': 1,
            'Madeira': 2,
            'Taipa': 3,
            'Outros': 4
        }).fillna(1)
        df['escolaridade'] = df['nivel_escolaridade'].map({
            'Sem Instrução': 0,
            'Fundamental Incompleto': 1,
            'Fundamental Completo': 2,
            'Médio Incompleto': 3,
            'Médio Completo': 4,
            'Superior Incompleto': 5,
            'Superior Completo': 6
        }).fillna(1)
        df['situacao_trabalho'] = df['situacao_trabalho'].map({
            'Desempregado': 0,
            'Informal': 1,
            'Formal': 2,
            'Aposentado': 3
        }).fillna(0)

        # Gerar features de vulnerabilidade
        df = gerar_features_vulnerabilidade(df)

        # Preparar dados para ML
        X, _ = preparar_dados_para_ml(df)

        # Predições (modelos scikit-learn)
        pred_rf = rf_model.predict(X)[0]
        pred_xgb = xgb_model.predict(X)[0]

        # Probabilidades
        prob_rf = rf_model.predict_proba(X)[0]
        prob_xgb = xgb_model.predict_proba(X)[0]
        
        # Mapear números para classes
        classes = {0: "Baixa", 1: "Média", 2: "Alta"}
        pred_rf_label = classes[pred_rf]
        pred_xgb_label = classes[pred_xgb]

        # Features importantes (top 5)
        if hasattr(rf_model, 'feature_importances_') and feature_names:
            importances_rf = dict(zip(feature_names, rf_model.feature_importances_))
            importances_rf = dict(
                sorted(importances_rf.items(),
                       key=lambda x: x[1], reverse=True)[:5]
            )
        else:
            importances_rf = {}

        return PredictionResponse(
            vulnerabilidade_rf=pred_rf_label,
            vulnerabilidade_xgb=pred_xgb_label,
            probabilidade_rf={
                "Baixa": float(prob_rf[0]),
                "Média": float(prob_rf[1]),
                "Alta": float(prob_rf[2])
            },
            probabilidade_xgb={
                "Baixa": float(prob_xgb[0]),
                "Média": float(prob_xgb[1]),
                "Alta": float(prob_xgb[2])
            },
            features_importantes=importances_rf,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error("Erro ao processar predição: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar predição: {str(e)}"
        ) from e


@app.post("/analyze", tags=["Analysis"])
async def analyze_with_llm(dados: DadosFamilia):
    """
    Realiza análise completa usando meta-classificador LLM.
    Combina predições de ambos modelos com análise interpretável do LLM.
    """
    if rf_model is None or xgb_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados. Execute o treinamento primeiro."
        )

    try:
        # Converter dados para DataFrame
        dados_dict = dados.dict()
        df = pd.DataFrame([dados_dict])
        
        # Mapear campos da API para campos esperados pelo preprocessamento
        df['idade'] = df['idade_responsavel']
        df['qtd_pessoas_familia'] = df['numero_membros']
        df['acesso_agua'] = df['possui_agua_encanada'].astype(int)
        df['acesso_esgoto'] = df['possui_esgoto'].astype(int)
        df['possui_deficiencia'] = 0  # Usar campo pessoa_deficiencia quando disponível
        df['tipo_moradia'] = df['material_parede'].map({
            'Alvenaria': 1,
            'Madeira': 2,
            'Taipa': 3,
            'Outros': 4
        }).fillna(1)
        df['escolaridade'] = df['nivel_escolaridade'].map({
            'Sem Instrução': 0,
            'Fundamental Incompleto': 1,
            'Fundamental Completo': 2,
            'Médio Incompleto': 3,
            'Médio Completo': 4,
            'Superior Incompleto': 5,
            'Superior Completo': 6
        }).fillna(1)
        df['situacao_trabalho'] = df['situacao_trabalho'].map({
            'Desempregado': 0,
            'Informal': 1,
            'Formal': 2,
            'Aposentado': 3
        }).fillna(0)

        # Gerar features
        df = gerar_features_vulnerabilidade(df)

        # Preparar dados
        X, _ = preparar_dados_para_ml(df)

        # Predições dos modelos ML (são modelos scikit-learn diretos)
        pred_rf = rf_model.predict(X)[0]
        pred_xgb = xgb_model.predict(X)[0]
        prob_rf = rf_model.predict_proba(X)[0]
        prob_xgb = xgb_model.predict_proba(X)[0]
        
        # Mapear números para classes
        classes = {0: "Baixa", 1: "Média", 2: "Alta"}
        pred_rf_label = classes[pred_rf]
        pred_xgb_label = classes[pred_xgb]

        # Análise com LLM (se disponível)
        analise_llm = None
        if meta_classificador:
            # Criar prompt para análise
            prompt = f"""
Analise o seguinte caso de vulnerabilidade social:

**Dados da Família:**
- Idade do responsável: {dados_dict['idade_responsavel']} anos
- Membros da família: {dados_dict['numero_membros']}
- Crianças: {dados_dict['criancas']}
- Idosos: {dados_dict['idosos']}
- Renda per capita: R$ {dados_dict['renda_per_capita']:.2f}
- Pessoas trabalhando: {dados_dict['pessoas_trabalhando']}

**Infraestrutura:**
- Água encanada: {'Sim' if dados_dict['possui_agua_encanada'] else 'Não'}
- Esgoto: {'Sim' if dados_dict['possui_esgoto'] else 'Não'}
- Coleta de lixo: {'Sim' if dados_dict['possui_coleta_lixo'] else 'Não'}
- Energia elétrica: {'Sim' if dados_dict['possui_energia'] else 'Não'}
- Material da parede: {dados_dict['material_parede']}
- Material do teto: {dados_dict['material_teto']}
- Cômodos: {dados_dict['comodos']}
- Possui banheiro: {'Sim' if dados_dict['possui_banheiro'] else 'Não'}

**Situação Socioeconômica:**
- Tempo de residência: {dados_dict['tempo_residencia']} meses
- Recebe Bolsa Família: {'Sim' if dados_dict['recebe_bolsa_familia'] else 'Não'}
- Valor Bolsa Família: R$ {dados_dict['valor_bolsa_familia']:.2f}
- Escolaridade: {dados_dict['nivel_escolaridade']}
- Situação de trabalho: {dados_dict['situacao_trabalho']}

**Predições dos Modelos:**
- Random Forest: {pred_rf_label} (probabilidades: Baixa={prob_rf[0]:.2%}, Média={prob_rf[1]:.2%}, Alta={prob_rf[2]:.2%})
- XGBoost: {pred_xgb_label} (probabilidades: Baixa={prob_xgb[0]:.2%}, Média={prob_xgb[1]:.2%}, Alta={prob_xgb[2]:.2%})

Forneça uma análise detalhada identificando:
1. Principais fatores de vulnerabilidade
2. Pontos positivos da situação
3. Recomendações práticas
4. Classificação final de vulnerabilidade (Baixa/Média/Alta) e justificativa
"""
            analise_llm = meta_classificador.analisar_com_llm(prompt)

        return {
            "predicao_rf": pred_rf_label,
            "predicao_xgb": pred_xgb_label,
            "probabilidades_rf": {
                "Baixa": float(prob_rf[0]),
                "Média": float(prob_rf[1]),
                "Alta": float(prob_rf[2])
            },
            "probabilidades_xgb": {
                "Baixa": float(prob_xgb[0]),
                "Média": float(prob_xgb[1]),
                "Alta": float(prob_xgb[2])
            },
            "analise_llm": analise_llm,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error("Erro ao processar análise: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar análise: {str(e)}"
        ) from e


@app.post("/predict-batch", tags=["Predictions"])
async def predict_batch(dados_lista: List[DadosFamilia]):
    """
    Realiza predições em lote para múltiplas famílias.
    Útil para processar grandes volumes de dados.
    """
    if rf_model is None or xgb_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados. Execute o treinamento primeiro."
        )

    try:
        resultados = []

        for dados in dados_lista:
            # Converter para DataFrame
            dados_dict = dados.dict()
            df = pd.DataFrame([dados_dict])

            # Gerar features
            df = gerar_features_vulnerabilidade(df)

            # Preparar dados
            X, _ = preparar_dados_para_ml(df)

            # Predições
            pred_rf = rf_model.prever(X)[0]
            pred_xgb = xgb_model.prever(X)[0]

            resultados.append({
                "dados_entrada": dados_dict,
                "predicao_rf": pred_rf,
                "predicao_xgb": pred_xgb
            })

        return {
            "total_processado": len(resultados),
            "resultados": resultados,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error("Erro ao processar lote: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar lote: {str(e)}"
        ) from e


@app.get("/stats", tags=["Statistics"])
async def obter_estatisticas():
    """Retorna estatísticas dos modelos carregados."""
    if rf_model is None or xgb_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não disponíveis"
        )

    try:
        stats = {
            "random_forest": {
                "metricas": rf_model.metricas if hasattr(rf_model, 'metricas') else None
            },
            "xgboost": {
                "metricas": xgb_model.metricas if hasattr(xgb_model, 'metricas') else None
            },
            "timestamp": datetime.now().isoformat()
        }
        return stats

    except Exception as e:
        logger.error("Erro ao obter estatísticas: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
