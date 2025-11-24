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


@app.get("/data-viewer.html", tags=["Root"])
async def data_viewer():
    """Serve a página de visualização de dados."""
    viewer_file = Path(__file__).parent.parent / "frontend" / "data-viewer.html"
    if viewer_file.exists():
        return FileResponse(viewer_file)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Página de visualização não encontrada"
        )


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


# ============================================================================
# ENDPOINTS PARA PROCESSAMENTO DE DADOS EM LOTE (CSVs da pasta data/)
# ============================================================================

@app.get("/data/files", tags=["Data Processing"])
async def listar_arquivos_csv():
    """
    Lista todos os arquivos CSV disponíveis na pasta data/.
    Retorna informações sobre cada arquivo incluindo tamanho e número de linhas.
    """
    try:
        data_path = Path("data")
        if not data_path.exists():
            return {"arquivos": [], "total": 0}
        
        arquivos = []
        for file_path in data_path.rglob("*.csv"):
            try:
                # Obter informações do arquivo
                size_mb = file_path.stat().st_size / (1024 * 1024)
                
                # Ler primeiras linhas para contar
                df_sample = pd.read_csv(file_path, nrows=1)
                total_lines = sum(1 for _ in open(file_path, encoding='utf-8', errors='ignore')) - 1
                
                arquivos.append({
                    "nome": file_path.name,
                    "caminho_relativo": str(file_path.relative_to(data_path)),
                    "tamanho_mb": round(size_mb, 2),
                    "linhas": total_lines,
                    "colunas": len(df_sample.columns)
                })
            except Exception as e:
                logger.warning(f"Erro ao processar arquivo {file_path}: {e}")
                continue
        
        return {
            "arquivos": sorted(arquivos, key=lambda x: x["linhas"], reverse=True),
            "total": len(arquivos),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar arquivos: {str(e)}"
        )


@app.get("/data/process/", tags=["Data Processing"])
async def processar_csv(filepath: str, max_rows: Optional[int] = None):
    """
    Processa um arquivo CSV da pasta data/ e retorna análise completa.
    Aplica os modelos ML em todos os registros e gera estatísticas.
    
    Args:
        filepath: Caminho relativo do arquivo (ex: base_amostra_cad_201812/base_amostra_familia_201812.csv)
        max_rows: Limitar número de linhas processadas (opcional)
    """
    if rf_model is None or xgb_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados"
        )
    
    try:
        # Construir caminho completo
        data_path = Path("data")
        file_path = data_path / filepath
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo {filepath} não encontrado em data/"
            )
        
        # Carregar dados
        logger.info(f"Carregando arquivo: {file_path}")
        if max_rows:
            df = pd.read_csv(file_path, nrows=max_rows, encoding='utf-8')
        else:
            df = pd.read_csv(file_path, encoding='utf-8')
        
        logger.info(f"Dados carregados: {len(df)} registros")
        
        # Gerar features de vulnerabilidade ANTES de preparar para ML
        from preprocessamento import gerar_features_vulnerabilidade
        df = gerar_features_vulnerabilidade(df)
        
        # Preparar dados para ML
        X, _ = preparar_dados_para_ml(df)
        
        # Fazer predições
        logger.info("Fazendo predições...")
        predicoes_rf = rf_model.predict(X)
        predicoes_xgb = xgb_model.predict(X)
        
        # Adicionar predições ao DataFrame
        df['predicao_rf'] = predicoes_rf
        df['predicao_xgb'] = predicoes_xgb
        
        # Calcular estatísticas gerais
        stats = {
            "total_registros": len(df),
            "distribuicao_rf": df['predicao_rf'].value_counts().to_dict(),
            "distribuicao_xgb": df['predicao_xgb'].value_counts().to_dict(),
            "estatisticas_gerais": {
                "idade_media": float(df['idade'].mean()) if 'idade' in df.columns else None,
                "renda_per_capita_media": float(df['renda_per_capita'].mean()) if 'renda_per_capita' in df.columns else None,
                "tamanho_familia_medio": float(df['qtd_pessoas_familia'].mean()) if 'qtd_pessoas_familia' in df.columns else None,
                "recebem_bolsa_familia": int(df['recebe_bolsa_familia'].sum()) if 'recebe_bolsa_familia' in df.columns else None,
                "percentual_bolsa_familia": float(df['recebe_bolsa_familia'].mean() * 100) if 'recebe_bolsa_familia' in df.columns else None
            }
        }
        
        return {
            "arquivo": filepath,
            "processado_em": datetime.now().isoformat(),
            "estatisticas": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@app.get("/data/analyze-municipality", tags=["Data Processing"])
async def analisar_por_municipio(filepath: str, max_rows: Optional[int] = None):
    """
    Analisa dados agregados por município com classificação ML e análise LLM.
    Retorna estatísticas detalhadas por município e análise interpretativa da IA.
    
    Args:
        filepath: Caminho relativo do arquivo CSV para analisar
        max_rows: Limitar número de linhas (opcional)
    """
    if rf_model is None or xgb_model is None or meta_classificador is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados"
        )
    
    try:
        # Construir caminho completo
        data_path = Path("data")
        file_path = data_path / filepath
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo {filepath} não encontrado em data/"
            )
        
        logger.info(f"Carregando arquivo: {file_path}")
        if max_rows:
            df = pd.read_csv(file_path, nrows=max_rows, encoding='utf-8')
        else:
            df = pd.read_csv(file_path, encoding='utf-8')
        
        # Verificar se tem coluna de município
        if 'cod_municipio' not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo não contém coluna 'cod_municipio'"
            )
        
        # Gerar features de vulnerabilidade ANTES de preparar para ML
        from preprocessamento import gerar_features_vulnerabilidade
        df = gerar_features_vulnerabilidade(df)
        
        # Preparar dados e fazer predições
        X, _ = preparar_dados_para_ml(df)
        
        # Fazer predições (retornam números: 0=Baixa, 1=Média, 2=Alta, 3=Muito Alta)
        pred_rf_numeric = rf_model.predict(X)
        pred_xgb_numeric = xgb_model.predict(X)
        
        # Mapear números para strings
        vulnerabilidade_map = {0: 'Baixa', 1: 'Média', 2: 'Alta', 3: 'Muito Alta'}
        df['predicao_rf'] = pd.Series(pred_rf_numeric).map(vulnerabilidade_map).values
        df['predicao_xgb'] = pd.Series(pred_xgb_numeric).map(vulnerabilidade_map).values
        
        # Agregar por município
        municipios = []
        
        for cod_mun, grupo in df.groupby('cod_municipio'):
            mun_stats = {
                "codigo_municipio": int(cod_mun),
                "nome_municipio": f"Município {cod_mun}",
                "total_familias": len(grupo),
                "vulnerabilidade": {
                    "Baixa": int((grupo['predicao_rf'] == 'Baixa').sum()),
                    "Média": int((grupo['predicao_rf'] == 'Média').sum()),
                    "Alta": int((grupo['predicao_rf'] == 'Alta').sum()),
                    "Muito Alta": int((grupo['predicao_rf'] == 'Muito Alta').sum())
                },
                "indicadores": {
                    "idade_media": float(grupo['idade'].mean()),
                    "renda_per_capita_media": float(grupo['renda_per_capita'].mean()),
                    "tamanho_familia_medio": float(grupo['qtd_pessoas_familia'].mean()),
                    "percentual_bolsa_familia": float(grupo['recebe_bolsa_familia'].mean() * 100),
                    "total_bolsa_familia": int(grupo['recebe_bolsa_familia'].sum())
                }
            }
            
            # Calcular percentuais
            mun_stats["vulnerabilidade_percentual"] = {
                k: round(v / len(grupo) * 100, 1) 
                for k, v in mun_stats["vulnerabilidade"].items()
            }
            
            municipios.append(mun_stats)
        
        # Ordenar por total de famílias
        municipios.sort(key=lambda x: x['total_familias'], reverse=True)
        
        # Gerar análise LLM dos dados agregados
        logger.info("Gerando análise LLM dos dados municipais...")
        analise_llm = await gerar_analise_llm_municipios(municipios, len(df))
        
        return {
            "arquivo": filepath,
            "total_registros": len(df),
            "total_municipios": len(municipios),
            "municipios": municipios,
            "analise_llm": analise_llm,
            "processado_em": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao analisar por município: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao analisar dados: {str(e)}"
        )


@app.get("/data/analyze-governo", tags=["Data Processing"])
async def analisar_arquivo_governo(filepath: str, max_rows: Optional[int] = 20000):
    """
    Analisa arquivos do governo (CadÚnico) DIRETAMENTE sem conversão.
    Detecta automaticamente o formato, mapeia colunas e processa.
    
    Args:
        filepath: Caminho relativo do arquivo (ex: base_amostra_cad_201812/base_amostra_familia_201812.csv)
        max_rows: Limite de linhas (padrão 20000 - ideal para análise representativa)
    """
    if rf_model is None or xgb_model is None or meta_classificador is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelos não estão carregados"
        )
    
    try:
        from mapeador_governo import carregar_e_mapear_arquivo
        
        # Construir caminho
        data_path = Path("data")
        file_path = data_path / filepath
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo {filepath} não encontrado"
            )
        
        # Carregar e mapear automaticamente
        logger.info(f"Processando arquivo do governo: {file_path}")
        df_mapped, info = carregar_e_mapear_arquivo(file_path, max_rows=max_rows)
        
        logger.info(f"Arquivo mapeado: {len(df_mapped)} registros, tipo: {info['tipo']}")
        
        # Adicionar valores padrão para colunas obrigatórias faltantes
        colunas_obrigatorias = {
            'idade': 35,
            'sexo': 'M',
            'escolaridade': 1,
            'qtd_pessoas_familia': 4,
            'renda_per_capita': 0,
            'situacao_trabalho': 0,
            'acesso_agua': 0,
            'acesso_esgoto': 0,
            'recebe_bolsa_familia': 0,
            'possui_deficiencia': 0,  # Não possui deficiência por padrão
            'tipo_moradia': 1,  # Moradia tipo 1 (alvenaria) por padrão
        }
        
        for col, valor_padrao in colunas_obrigatorias.items():
            if col not in df_mapped.columns:
                df_mapped[col] = valor_padrao
                logger.info(f"Adicionada coluna '{col}' com valor padrão: {valor_padrao}")
        
        # Se não tem cod_municipio, usar um valor padrão
        if 'cod_municipio' not in df_mapped.columns:
            df_mapped['cod_municipio'] = 999999
            logger.warning("Coluna 'cod_municipio' não encontrada, usando valor padrão")
        
        # Gerar features de vulnerabilidade
        from preprocessamento import gerar_features_vulnerabilidade
        df_mapped = gerar_features_vulnerabilidade(df_mapped)
        
        # Preparar dados e fazer predições
        X, _ = preparar_dados_para_ml(df_mapped)
        
        # Fazer predições (retornam números: 0=Baixa, 1=Média, 2=Alta, 3=Muito Alta)
        pred_rf_numeric = rf_model.predict(X)
        pred_xgb_numeric = xgb_model.predict(X)
        
        # Mapear números para strings
        vulnerabilidade_map = {0: 'Baixa', 1: 'Média', 2: 'Alta', 3: 'Muito Alta'}
        df_mapped['predicao_rf'] = pd.Series(pred_rf_numeric).map(vulnerabilidade_map).values
        df_mapped['predicao_xgb'] = pd.Series(pred_xgb_numeric).map(vulnerabilidade_map).values
        
        # Agregar por município
        municipios = []
        
        for cod_mun, grupo in df_mapped.groupby('cod_municipio'):
            mun_stats = {
                "codigo_municipio": int(cod_mun),
                "nome_municipio": f"Município {cod_mun}",
                "total_familias": len(grupo),
                "vulnerabilidade": {
                    "Baixa": int((grupo['predicao_rf'] == 'Baixa').sum()),
                    "Média": int((grupo['predicao_rf'] == 'Média').sum()),
                    "Alta": int((grupo['predicao_rf'] == 'Alta').sum()),
                    "Muito Alta": int((grupo['predicao_rf'] == 'Muito Alta').sum())
                },
                "indicadores": {
                    "idade_media": float(grupo['idade'].mean()),
                    "renda_per_capita_media": float(grupo['renda_per_capita'].mean()),
                    "tamanho_familia_medio": float(grupo['qtd_pessoas_familia'].mean()),
                    "percentual_bolsa_familia": float(grupo['recebe_bolsa_familia'].mean() * 100),
                    "total_bolsa_familia": int(grupo['recebe_bolsa_familia'].sum())
                }
            }
            
            # Calcular percentuais
            mun_stats["vulnerabilidade_percentual"] = {
                k: round(v / len(grupo) * 100, 1) 
                for k, v in mun_stats["vulnerabilidade"].items()
            }
            
            municipios.append(mun_stats)
        
        # Ordenar por total de famílias
        municipios.sort(key=lambda x: x['total_familias'], reverse=True)
        
        # Gerar análise com LLM
        analise_llm = await gerar_analise_llm_municipios(municipios, len(df_mapped))
        
        return {
            "arquivo_original": filepath,
            "tipo_detectado": info['tipo'],
            "formato_detectado": {
                "separador": info['separador'],
                "encoding": info['encoding']
            },
            "colunas_originais": len(info['colunas']),
            "total_registros": len(df_mapped),
            "total_municipios": len(municipios),
            "municipios": municipios,
            "analise_ia": analise_llm,
            "processado_em": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar arquivo do governo: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )


async def gerar_analise_llm_municipios(municipios: List[Dict], total_registros: int) -> str:
    """
    Gera análise interpretativa dos dados municipais usando LLM.
    """
    try:
        # Pegar top 5 municípios
        top_municipios = municipios[:5]
        
        # Criar prompt para análise
        prompt = f"""
Você é um especialista em análise de políticas públicas e vulnerabilidade social.
Analise os dados agregados de {len(municipios)} municípios brasileiros, totalizando {total_registros} famílias cadastradas no CadÚnico.

DADOS DOS TOP 5 MUNICÍPIOS (por número de famílias):

"""
        
        for i, mun in enumerate(top_municipios, 1):
            prompt += f"""
{i}. Município {mun['codigo_municipio']}:
   - Total de famílias: {mun['total_familias']}
   - Distribuição de vulnerabilidade:
     * Muito Alta: {mun['vulnerabilidade_percentual']['Muito Alta']}%
     * Alta: {mun['vulnerabilidade_percentual']['Alta']}%
     * Média: {mun['vulnerabilidade_percentual']['Média']}%
     * Baixa: {mun['vulnerabilidade_percentual']['Baixa']}%
   - Indicadores socioeconômicos:
     * Renda per capita média: R$ {mun['indicadores']['renda_per_capita_media']:.2f}
     * Idade média: {mun['indicadores']['idade_media']:.1f} anos
     * Tamanho médio da família: {mun['indicadores']['tamanho_familia_medio']:.1f} pessoas
     * Recebem Bolsa Família: {mun['indicadores']['percentual_bolsa_familia']:.1f}%

"""
        
        prompt += """
Por favor, forneça uma análise abrangente contemplando:

1. **Panorama Geral**: Avaliação do nível de vulnerabilidade social observado nos municípios
2. **Municípios Críticos**: Identificação dos municípios que requerem atenção prioritária
3. **Indicadores Socioeconômicos**: Análise dos padrões de renda, composição familiar e cobertura do Bolsa Família
4. **Recomendações**: Sugestões de políticas públicas e ações específicas para cada perfil de município
5. **Próximos Passos**: Orientações para gestores públicos sobre priorização de recursos

Seja específico, use os dados fornecidos e forneça insights práticos para tomada de decisão.
"""
        
        # Chamar LLM
        if meta_classificador and meta_classificador.model:
            response = meta_classificador.model.generate_content(prompt)
            return response.text
        else:
            return "Análise LLM não disponível (API key não configurada)"
    
    except Exception as e:
        logger.error(f"Erro ao gerar análise LLM: {e}")
        return f"Erro ao gerar análise: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
