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

# OpenAI
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning(
        "OpenAI não está instalado. Funcionalidades de LLM não estarão disponíveis.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaClassificadorLLM:
    """
    Meta-classificador que combina modelos ML tradicionais com LLM para
    análise mais interpretável de vulnerabilidade social.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            modelo_llm: str = "gpt-3.5-turbo"):
        """
        Inicializa o meta-classificador.

        Args:
            api_key (str, optional): Chave da API OpenAI. Se None, tentará obter de variável de ambiente.
            modelo_llm (str): Modelo do LLM a ser usado
        """
        self.modelo_llm = modelo_llm
        self.client = None
        self.modelos_ml = {}
        self.historico_predicoes = []

        # Configurar cliente OpenAI
        if OPENAI_AVAILABLE:
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                logger.info("Cliente OpenAI configurado com sucesso")
            else:
                logger.warning(
                    "Chave da API OpenAI não encontrada. Defina OPENAI_API_KEY como variável de ambiente.")

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
                self.modelos_ml['random_forest'] = joblib.load(rf_path)
                logger.info("Modelo Random Forest carregado")

            # Carregar XGBoost
            xgb_path = f"{pasta_modelos}/xgboost_vulnerabilidade.pkl"
            if Path(xgb_path).exists():
                self.modelos_ml['xgboost'] = joblib.load(xgb_path)
                logger.info("Modelo XGBoost carregado")

        except Exception as e:
            logger.error(f"Erro ao carregar modelos ML: {e}")

    def predizer_modelos_ml(self, X: pd.DataFrame) -> Dict[str, Any]:
        """
        Faz predições usando modelos ML carregados.

        Args:
            X (pd.DataFrame): Features de entrada

        Returns:
            Dict[str, Any]: Predições e probabilidades dos modelos
        """
        predicoes = {}

        for nome_modelo, modelo_data in self.modelos_ml.items():
            try:
                modelo = modelo_data['modelo']
                scaler = modelo_data['scaler']

                # Escalar dados
                X_scaled = scaler.transform(X)

                # Fazer predições
                pred_classes = modelo.predict(X_scaled)
                pred_proba = modelo.predict_proba(X_scaled)

                predicoes[nome_modelo] = {
                    'classes': pred_classes.tolist(),
                    'probabilidades': pred_proba.tolist(),
                    'confianca_maxima': pred_proba.max(axis=1).tolist()
                }

            except Exception as e:
                logger.error(f"Erro ao fazer predição com {nome_modelo}: {e}")

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
        if not self.client:
            logger.error("Cliente OpenAI não configurado")
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.modelo_llm,
                messages=[
                    {"role": "system", "content": "Você é um especialista em vulnerabilidade social e políticas públicas brasileiras."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erro ao chamar OpenAI API: {e}")
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
    Exemplo simples de uso do meta-classificador (sem OpenAI).
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

    print("\nNOTA: Para usar o LLM completo, configure a variável de ambiente OPENAI_API_KEY")


if __name__ == "__main__":
    exemplo_uso_simples()
