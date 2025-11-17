"""
Módulo de meta-classificador com LLM para análise de vulnerabilidade social.

Este módulo integra modelos de ML tradicionais com LLMs para fornecer
classificações mais interpretáveis e explicações detalhadas sobre
vulnerabilidade social.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv()

# Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning(
        "Google Generative AI não está instalado. Funcionalidades de LLM não estarão disponíveis.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaClassificadorLLM:
    """
    Meta-classificador que combina modelos ML tradicionais com LLM para
    análise mais interpretável de vulnerabilidade social.
    Usa Google Gemini API (gratuita).
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            modelo_llm: str = "gemini-2.0-flash"):
        """
        Inicializa o meta-classificador.

        Args:
            api_key (str, optional): Chave da API Gemini. Se None, tentará obter de variável de ambiente.
            modelo_llm (str): Modelo do LLM a ser usado (gemini-1.5-flash, gemini-1.5-pro, gemini-pro)
        """
        self.modelo_llm = modelo_llm
        self.model = None
        self.modelos_ml = {}
        self.historico_predicoes = []

        # Configurar cliente Gemini
        if GEMINI_AVAILABLE:
            api_key = api_key or os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(modelo_llm)
                logger.info(f"Google Gemini configurado com sucesso (modelo: {modelo_llm})")
            else:
                logger.warning(
                    "Chave da API Gemini não encontrada. Defina GEMINI_API_KEY como variável de ambiente.")

    def carregar_modelos_ml(self, pasta_modelos: str = "outputs/modelos"):
        """
        Carrega modelos ML pré-treinados.

        Args:
            pasta_modelos (str): Pasta contendo os modelos salvos
        """
        try:
            import joblib

            # Carregar Random Forest
            rf_path = f"{pasta_modelos}/random_forest_vulnerabilidade.pkl"
            if Path(rf_path).exists():
                modelo_data = joblib.load(rf_path)
                # Extrair apenas o modelo e scaler do dict carregado
                self.modelos_ml['random_forest'] = {
                    'modelo': modelo_data['modelo'],
                    'scaler': modelo_data['scaler']
                }
                logger.info("Modelo Random Forest carregado")

            # Carregar XGBoost
            xgb_path = f"{pasta_modelos}/xgboost_vulnerabilidade.pkl"
            if Path(xgb_path).exists():
                modelo_data = joblib.load(xgb_path)
                # Extrair apenas o modelo e scaler do dict carregado
                self.modelos_ml['xgboost'] = {
                    'modelo': modelo_data['modelo'],
                    'scaler': modelo_data['scaler']
                }
                logger.info("Modelo XGBoost carregado")

        except Exception as e:
            logger.error(f"Erro ao carregar modelos ML: {e}")

    def predizer_modelos_ml(self, X: pd.DataFrame) -> Dict[str, Dict]:
        """
        Faz predições com os modelos ML carregados.
        
        Args:
            X: DataFrame com features
            
        Returns:
            Dicionário com predições de cada modelo
        """
        if not self.modelos_ml:
            raise ValueError("Modelos ML não foram carregados. Execute carregar_modelos_ml() primeiro.")
        
        # Features esperadas pelos modelos (mesmo do treinamento)
        features_esperadas = [
            'idade', 'escolaridade', 'renda_per_capita', 'qtd_pessoas_familia',
            'possui_deficiencia', 'situacao_trabalho', 'tipo_moradia',
            'acesso_agua', 'acesso_esgoto', 'vulnerabilidade_idade',
            'infraestrutura_adequada', 'escolaridade_baixa', 
            'situacao_trabalho_precaria', 'superlotacao', 'recebe_bolsa_familia'
        ]
        
        # Selecionar apenas features necessárias
        X_pred = X[features_esperadas].copy()
        
        predicoes = {}
        
        for nome_modelo, modelo_dict in self.modelos_ml.items():
            try:
                # Extrair modelo e scaler do dicionário
                modelo = modelo_dict['modelo']
                scaler = modelo_dict['scaler']
                
                # Escalar features
                X_scaled = scaler.transform(X_pred)
                
                # Fazer predição
                y_pred = modelo.predict(X_scaled)
                y_proba = modelo.predict_proba(X_scaled)
                
                # Armazenar resultados
                predicoes[nome_modelo] = {
                    'classes': y_pred,
                    'probabilidades': y_proba,
                    'confianca_maxima': y_proba.max(axis=1)
                }
                
            except Exception as e:
                logger.error(f"Erro ao fazer predição com {nome_modelo}: {e}")
                continue
        
        return predicoes

    def gerar_prompt_vulnerabilidade(
            self, dados_pessoa: Dict[str, Any], predicoes_ml: Dict[str, Any]) -> str:
        """
        Gera prompt para o LLM analisar vulnerabilidade social.

        Args:
            dados_pessoa (Dict): Dados da pessoa a ser analisada
            predicoes_ml (Dict): Predições dos modelos ML

        Returns:
            str: Prompt formatado para o LLM
        """

        # Mapear níveis de vulnerabilidade
        niveis_vulnerabilidade = {
            0: 'Baixa',
            1: 'Média',
            2: 'Alta',
            3: 'Muito Alta'}

        prompt = f"""
Você é um especialista em análise de vulnerabilidade social e políticas públicas.
Analise o perfil socioeconômico a seguir e forneça uma avaliação detalhada da vulnerabilidade social.

DADOS DA PESSOA:
- Idade: {dados_pessoa.get('idade', 'N/A')} anos
- Sexo: {dados_pessoa.get('sexo', 'N/A')}
- Escolaridade: Nível {dados_pessoa.get('escolaridade', 'N/A')} (0=analfabeto, 5=superior)
- Renda familiar: R$ {dados_pessoa.get('renda_familiar', 'N/A'):.2f}
- Pessoas na família: {dados_pessoa.get('qtd_pessoas_familia', 'N/A')}
- Renda per capita: R$ {dados_pessoa.get('renda_per_capita', 'N/A'):.2f}
- Possui deficiência: {'Sim' if dados_pessoa.get('possui_deficiencia', 0) else 'Não'}
- Situação de trabalho: {dados_pessoa.get('situacao_trabalho', 'N/A')} (0=desempregado, 1=informal, 2=formal)
- Tipo de moradia: {dados_pessoa.get('tipo_moradia', 'N/A')} (1=própria, 2=alugada, 3=cedida, 4=ocupação)
- Acesso à água: {'Sim' if dados_pessoa.get('acesso_agua', 0) else 'Não'}
- Acesso ao esgoto: {'Sim' if dados_pessoa.get('acesso_esgoto', 0) else 'Não'}
- Recebe Bolsa Família: {'Sim' if dados_pessoa.get('recebe_bolsa_familia', 0) else 'Não'}

PREDIÇÕES DOS MODELOS DE MACHINE LEARNING:
"""

        for nome_modelo, pred in predicoes_ml.items():
            if pred['classes']:
                nivel_pred = niveis_vulnerabilidade.get(
                    pred['classes'][0], 'Desconhecido')
                confianca = pred['confianca_maxima'][0] * \
                    100 if pred['confianca_maxima'] else 0
                prompt += f"- {nome_modelo}: {nivel_pred} (confiança: {
                    confianca:.1f}%)\n"

        prompt += """
Por favor, forneça uma análise estruturada contendo:

1. CLASSIFICAÇÃO FINAL DE VULNERABILIDADE:
   - Nível de vulnerabilidade (Baixa/Média/Alta/Muito Alta)
   - Justificativa para a classificação

2. FATORES DE RISCO IDENTIFICADOS:
   - Liste os principais fatores que contribuem para a vulnerabilidade
   - Priorize os fatores mais críticos

3. FATORES PROTETIVOS:
   - Identifique aspectos que reduzem a vulnerabilidade
   - Recursos e apoios disponíveis

4. RECOMENDAÇÕES DE POLÍTICAS PÚBLICAS:
   - Programas sociais mais adequados
   - Intervenções prioritárias
   - Ações de médio e longo prazo

5. MONITORAMENTO:
   - Indicadores para acompanhar evolução
   - Periodicidade de reavaliação sugerida

Seja específico, prático e considere o contexto socioeconômico brasileiro.
"""

        return prompt

    def analisar_com_llm(self, prompt: str) -> Optional[str]:
        """
        Envia prompt para o LLM e retorna a análise.

        Args:
            prompt (str): Prompt para o LLM

        Returns:
            Optional[str]: Resposta do LLM ou None se erro
        """
        if not self.model:
            logger.error("Google Gemini não configurado")
            return None

        try:
            # Adicionar contexto de sistema ao prompt
            prompt_completo = (
                "Você é um especialista em vulnerabilidade social e políticas públicas brasileiras.\n\n"
                + prompt
            )
            
            # Configurar geração
            generation_config = genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1500,
            )
            
            # Gerar resposta
            response = self.model.generate_content(
                prompt_completo,
                generation_config=generation_config
            )

            return response.text

        except Exception as e:
            logger.error(f"Erro ao chamar Google Gemini API: {e}")
            return None

    def classificar_vulnerabilidade(
            self, dados_pessoa: pd.Series) -> Dict[str, Any]:
        """
        Classifica vulnerabilidade combinando ML e LLM.

        Args:
            dados_pessoa (pd.Series): Dados da pessoa

        Returns:
            Dict[str, Any]: Análise completa de vulnerabilidade
        """
        # Converter para DataFrame para compatibilidade com modelos
        X = pd.DataFrame([dados_pessoa])

        # Obter predições dos modelos ML
        predicoes_ml = self.predizer_modelos_ml(X)

        # Preparar dados para o LLM
        dados_dict = dados_pessoa.to_dict()

        # Gerar análise com LLM
        prompt = self.gerar_prompt_vulnerabilidade(dados_dict, predicoes_ml)
        analise_llm = self.analisar_com_llm(prompt)

            # Consolidar resultado
        resultado = {
            'dados_pessoa': dados_dict,
            'predicoes_ml': predicoes_ml,
            'analise_llm': analise_llm,
            'prompt_usado': prompt,
            'modelo_usado': self.modelo_llm,
            'timestamp': pd.Timestamp.now().isoformat()
        }

        # Salvar no histórico
        self.historico_predicoes.append(resultado)

        return resultado

    def analisar_lote(self, df: pd.DataFrame,
                      salvar_resultados: bool = True) -> List[Dict[str, Any]]:
        """
        Analisa um lote de pessoas.

        Args:
            df (pd.DataFrame): DataFrame com dados das pessoas
            salvar_resultados (bool): Se deve salvar resultados em arquivo

        Returns:
            List[Dict[str, Any]]: Lista com análises de cada pessoa
        """
        logger.info(f"Iniciando análise de lote com {len(df)} registros")

        resultados = []

        for idx, row in df.iterrows():
            try:
                resultado = self.classificar_vulnerabilidade(row)
                resultados.append(resultado)

                if (idx + 1) % 10 == 0:
                    logger.info(f"Processados {idx + 1}/{len(df)} registros")

            except Exception as e:
                logger.error(f"Erro ao processar registro {idx}: {e}")
                continue

        # Salvar resultados se solicitado
        if salvar_resultados:
            self.salvar_resultados_lote(resultados)

        logger.info(
            f"Análise de lote concluída: {
                len(resultados)} registros processados")
        return resultados

    def salvar_resultados_lote(
            self, resultados: List[Dict[str, Any]], caminho: str = None):
        """
        Salva resultados de análise em lote.

        Args:
            resultados (List[Dict]): Lista de resultados
            caminho (str, optional): Caminho para salvar. Se None, usa timestamp.
        """
        if not caminho:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            caminho = f"outputs/analise_vulnerabilidade_{timestamp}.json"

        # Criar pasta se não existir
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)

        # Salvar resultados
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Resultados salvos em {caminho}")

    def gerar_relatorio_consolidado(
            self, resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera relatório consolidado das análises.

        Args:
            resultados (List[Dict]): Lista de resultados das análises

        Returns:
            Dict[str, Any]: Relatório consolidado
        """
        if not resultados:
            return {}

        # Extrair predições ML para estatísticas
        predicoes_rf = []
        predicoes_xgb = []

        for resultado in resultados:
            pred_ml = resultado.get('predicoes_ml', {})

            if 'random_forest' in pred_ml:
                predicoes_rf.extend(
                    pred_ml['random_forest'].get(
                        'classes', []))

            if 'xgboost' in pred_ml:
                predicoes_xgb.extend(pred_ml['xgboost'].get('classes', []))

        # Mapeamento de níveis
        niveis = {0: 'Baixa', 1: 'Média', 2: 'Alta', 3: 'Muito Alta'}

        relatorio = {
            'total_analisados': len(resultados),
            'distribuicao_vulnerabilidade': {
                'random_forest': {
                    niveis[i]: predicoes_rf.count(i) for i in range(4) if i in predicoes_rf} if predicoes_rf else {},
                'xgboost': {
                    niveis[i]: predicoes_xgb.count(i) for i in range(4) if i in predicoes_xgb} if predicoes_xgb else {}},
            'analises_llm_realizadas': sum(
                1 for r in resultados if r.get('analise_llm')),
            'timestamp_relatorio': pd.Timestamp.now().isoformat()}

        return relatorio


def exemplo_uso_simples():
    """
    Exemplo simples de uso do meta-classificador (sem API key).
    """
    print("=== Exemplo de Uso do Meta-Classificador (Modo Simulação) ===")

    # Simular dados de uma pessoa
    dados_exemplo = pd.Series({
        'idade': 35,
        'sexo': 'F',
        'escolaridade': 1,  # Ensino fundamental incompleto
        'renda_familiar': 400.00,
        'qtd_pessoas_familia': 4,
        'renda_per_capita': 100.00,
        'possui_deficiencia': 0,
        'situacao_trabalho': 1,  # Trabalho informal
        'tipo_moradia': 3,  # Cedida
        'acesso_agua': 1,
        'acesso_esgoto': 0,
        'recebe_bolsa_familia': 1
    })

    # Inicializar meta-classificador (sem API key para demo)
    meta_classificador = MetaClassificadorLLM()

    # Simular predições ML (já que não temos modelos treinados)
    predicoes_simuladas = {
        'random_forest': {
            'classes': [2],  # Alta vulnerabilidade
            'probabilidades': [[0.1, 0.2, 0.6, 0.1]],
            'confianca_maxima': [0.6]
        },
        'xgboost': {
            'classes': [3],  # Muito alta vulnerabilidade
            'probabilidades': [[0.05, 0.15, 0.3, 0.5]],
            'confianca_maxima': [0.5]
        }
    }

    # Gerar prompt para o LLM
    prompt = meta_classificador.gerar_prompt_vulnerabilidade(
        dados_exemplo.to_dict(),
        predicoes_simuladas
    )

    print("Prompt gerado para o LLM:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)

    print("\nNOTA: Para usar o LLM completo, configure a variável de ambiente GEMINI_API_KEY")
    print("Obtenha gratuitamente em: https://makersuite.google.com/app/apikey")


if __name__ == "__main__":
    exemplo_uso_simples()
