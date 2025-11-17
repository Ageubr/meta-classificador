"""
Script para adaptar dados reais do CadÚnico e Bolsa Família
para o formato esperado pelo sistema de vulnerabilidade social.

Este script:
1. Carrega dados reais do CadÚnico (Família e Pessoa) e Bolsa Família
2. Faz JOIN entre as tabelas
3. Aplica transformações e mapeamentos
4. Gera features de vulnerabilidade
5. Prepara dados para treinamento de ML
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Optional
import gc

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdaptadorDadosReais:
    """Classe para adaptar dados reais do CadÚnico para o sistema."""
    
    def __init__(self, pasta_base: str = "data"):
        self.pasta_base = Path(pasta_base)
        
        # Caminhos dos arquivos
        self.path_bf = self.pasta_base / "bolsa_familia.csv" / "202101_BolsaFamilia_Pagamentos.csv"
        self.path_fam = self.pasta_base / "base_amostra_cad_201812" / "base_amostra_familia_201812.csv"
        self.path_pes = self.pasta_base / "base_amostra_cad_201812" / "base_amostra_pessoa_201812.csv"
        
    def carregar_bolsa_familia(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """Carrega dados do Bolsa Família."""
        logger.info(f"Carregando Bolsa Família{f' ({nrows} registros)' if nrows else ''}...")
        
        df = pd.read_csv(
            self.path_bf,
            sep=';',
            encoding='latin-1',
            nrows=nrows
        )
        
        # Converter valor para float
        df['valor_beneficio'] = df['VALOR PARCELA'].str.replace(',', '.').astype(float)
        
        # Renomear colunas
        df = df.rename(columns={
            'NIS FAVORECIDO': 'nis',
            'NOME MUNICÍPIO': 'municipio',
            'UF': 'uf'
        })
        
        # Selecionar colunas relevantes
        df = df[['nis', 'valor_beneficio', 'municipio', 'uf']]
        
        logger.info(f"Bolsa Família carregado: {len(df):,} registros")
        return df
    
    def carregar_cadunico_familia(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """Carrega dados do CadÚnico - Família."""
        logger.info(f"Carregando CadÚnico Família{f' ({nrows} registros)' if nrows else ''}...")
        
        df = pd.read_csv(
            self.path_fam,
            sep=';',
            encoding='latin-1',
            nrows=nrows
        )
        
        logger.info(f"CadÚnico Família carregado: {len(df):,} registros")
        return df
    
    def carregar_cadunico_pessoa(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """Carrega dados do CadÚnico - Pessoa."""
        logger.info(f"Carregando CadÚnico Pessoa{f' ({nrows} registros)' if nrows else ''}...")
        
        df = pd.read_csv(
            self.path_pes,
            sep=';',
            encoding='latin-1',
            nrows=nrows
        )
        
        logger.info(f"CadÚnico Pessoa carregado: {len(df):,} registros")
        return df
    
    def transformar_sexo(self, cod_sexo: pd.Series) -> pd.Series:
        """Transforma código de sexo para M/F."""
        return cod_sexo.map({1: 'M', 2: 'F'})
    
    def transformar_agua(self, cod_agua: pd.Series) -> pd.Series:
        """Transforma código de acesso à água para 0/1."""
        # 1 = Rede geral (adequado)
        return (cod_agua == 1).astype(int)
    
    def transformar_esgoto(self, cod_esgoto: pd.Series) -> pd.Series:
        """Transforma código de esgoto para 0/1."""
        # 1 = Rede coletora (adequado)
        return (cod_esgoto == 1).astype(int)
    
    def transformar_deficiencia(self, cod_deficiencia: pd.Series) -> pd.Series:
        """Transforma código de deficiência para 0/1."""
        # 1 = Não tem deficiência
        return (cod_deficiencia != 1).astype(int)
    
    def transformar_trabalho(self, cod_trabalho: pd.Series) -> pd.Series:
        """Transforma código de trabalho para 0/1/2."""
        # 1 = Trabalhou (considerar informal)
        # 2 = Não trabalhou (desempregado)
        return cod_trabalho.map({1: 1, 2: 0}).fillna(0).astype(int)
    
    def transformar_escolaridade(self, cod_curso: pd.Series) -> pd.Series:
        """Transforma código de escolaridade para escala 0-5."""
        mapa = {
            1: 0,   # Creche
            2: 0,   # Pré-escola
            3: 1,   # EF anos iniciais
            4: 2,   # EF anos finais
            5: 3,   # Ensino Médio
            6: 5,   # Superior
            7: 2,   # EJA
            8: 3,   # EJA Médio
        }
        return cod_curso.map(mapa).fillna(0).astype(int)
    
    def agregar_pessoa_para_familia(self, df_pessoa: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega dados de pessoas para nível de família.
        Seleciona o responsável familiar (cod_parentesco_rf_pessoa == 1).
        """
        logger.info("Agregando dados de pessoas para nível de família...")
        
        # Filtrar apenas responsáveis familiares
        df_responsavel = df_pessoa[df_pessoa['cod_parentesco_rf_pessoa'] == 1].copy()
        
        # Transformar campos do responsável
        df_responsavel['sexo'] = self.transformar_sexo(df_responsavel['cod_sexo_pessoa'])
        df_responsavel['possui_deficiencia'] = self.transformar_deficiencia(df_responsavel['cod_deficiencia_memb'])
        df_responsavel['situacao_trabalho'] = self.transformar_trabalho(df_responsavel['cod_trabalhou_memb'])
        df_responsavel['escolaridade'] = self.transformar_escolaridade(df_responsavel['cod_curso_frequenta_memb'])
        
        # Renomear idade
        df_responsavel = df_responsavel.rename(columns={'idade': 'idade'})
        
        # Selecionar colunas relevantes
        colunas_relevantes = [
            'id_familia',
            'idade',
            'sexo',
            'escolaridade',
            'possui_deficiencia',
            'situacao_trabalho'
        ]
        
        df_responsavel = df_responsavel[colunas_relevantes]
        
        logger.info(f"Dados agregados: {len(df_responsavel):,} responsáveis")
        return df_responsavel
    
    def juntar_dados(
        self,
        df_familia: pd.DataFrame,
        df_pessoa: pd.DataFrame,
        df_bf: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Junta dados de família, pessoa e bolsa família."""
        logger.info("Juntando dados...")
        
        # Agregar dados de pessoa (responsável) para família
        df_responsavel = self.agregar_pessoa_para_familia(df_pessoa)
        
        # JOIN família com responsável
        df_completo = df_familia.merge(
            df_responsavel,
            on='id_familia',
            how='inner'
        )
        
        logger.info(f"Após JOIN família-responsável: {len(df_completo):,} registros")
        
        # Transformar campos da família
        df_completo['acesso_agua'] = self.transformar_agua(df_completo['cod_abaste_agua_domic_fam'])
        df_completo['acesso_esgoto'] = self.transformar_esgoto(df_completo['cod_escoa_sanitario_domic_fam'])
        df_completo['tipo_moradia'] = df_completo['cod_especie_domic_fam'].fillna(1).astype(int)
        df_completo['recebe_bolsa_familia'] = df_completo['marc_pbf']
        
        # Renomear colunas
        df_completo = df_completo.rename(columns={
            'vlr_renda_media_fam': 'renda_familiar',
            'qtde_pessoas': 'qtd_pessoas_familia',
            'cd_ibge': 'cod_municipio'
        })
        
        # Selecionar colunas finais (compatíveis com o sistema)
        colunas_finais = [
            'id_familia',
            'idade',
            'sexo',
            'escolaridade',
            'renda_familiar',
            'qtd_pessoas_familia',
            'possui_deficiencia',
            'situacao_trabalho',
            'tipo_moradia',
            'acesso_agua',
            'acesso_esgoto',
            'recebe_bolsa_familia',
            'cod_municipio'
        ]
        
        # Verificar quais colunas existem
        colunas_existentes = [col for col in colunas_finais if col in df_completo.columns]
        df_completo = df_completo[colunas_existentes]
        
        # Tratar valores faltantes
        df_completo['renda_familiar'] = df_completo['renda_familiar'].fillna(0)
        df_completo['idade'] = df_completo['idade'].fillna(0).astype(int)
        df_completo['qtd_pessoas_familia'] = df_completo['qtd_pessoas_familia'].fillna(1).astype(int)
        
        logger.info(f"Dados finais: {len(df_completo):,} registros, {len(df_completo.columns)} colunas")
        return df_completo
    
    def gerar_features_vulnerabilidade(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera features de vulnerabilidade (compatível com sistema existente)."""
        logger.info("Gerando features de vulnerabilidade...")
        
        df_features = df.copy()
        
        # Feature de renda per capita
        df_features['renda_per_capita'] = df_features['renda_familiar'] / df_features['qtd_pessoas_familia']
        
        # Feature de vulnerabilidade por idade
        df_features['vulnerabilidade_idade'] = (
            (df_features['idade'] < 18) | (df_features['idade'] > 65)
        ).astype(int)
        
        # Feature de infraestrutura adequada
        df_features['infraestrutura_adequada'] = (
            df_features['acesso_agua'] & df_features['acesso_esgoto']
        ).astype(int)
        
        # Feature de escolaridade baixa
        df_features['escolaridade_baixa'] = (
            df_features['escolaridade'] <= 2
        ).astype(int)
        
        # Feature de situação de trabalho precária
        df_features['situacao_trabalho_precaria'] = (
            df_features['situacao_trabalho'] <= 1
        ).astype(int)
        
        # Feature de superlotação
        df_features['superlotacao'] = (
            df_features['qtd_pessoas_familia'] > 5
        ).astype(int)
        
        # Score de vulnerabilidade (soma ponderada)
        pesos = {
            'renda_per_capita': -0.3,
            'vulnerabilidade_idade': 0.2,
            'infraestrutura_adequada': -0.15,
            'escolaridade_baixa': 0.15,
            'situacao_trabalho_precaria': 0.2,
            'superlotacao': 0.1,
            'possui_deficiencia': 0.1
        }
        
        # Normalizar renda per capita
        df_features['renda_per_capita_norm'] = (
            df_features['renda_per_capita'] - df_features['renda_per_capita'].mean()
        ) / df_features['renda_per_capita'].std()
        
        score_vulnerabilidade = 0
        for feature, peso in pesos.items():
            if feature == 'renda_per_capita':
                score_vulnerabilidade += peso * df_features['renda_per_capita_norm']
            else:
                score_vulnerabilidade += peso * df_features[feature]
        
        df_features['score_vulnerabilidade'] = score_vulnerabilidade
        
        # Classificação categórica
        df_features['nivel_vulnerabilidade'] = pd.cut(
            df_features['score_vulnerabilidade'],
            bins=[-np.inf, -0.5, 0, 0.5, np.inf],
            labels=['Baixa', 'Média', 'Alta', 'Muito Alta']
        )
        
        logger.info(f"Features geradas: {len(df_features.columns)} colunas")
        return df_features
    
    def processar_amostra(
        self,
        n_registros: int = 100000,
        salvar: bool = True
    ) -> pd.DataFrame:
        """
        Processa uma amostra dos dados completos.
        
        Args:
            n_registros: Número de registros a processar
            salvar: Se deve salvar o resultado em CSV
        
        Returns:
            DataFrame processado
        """
        logger.info(f"Processando amostra de {n_registros:,} registros...")
        
        # Carregar dados
        df_fam = self.carregar_cadunico_familia(nrows=n_registros)
        df_pes = self.carregar_cadunico_pessoa(nrows=n_registros * 3)  # Mais pessoas que famílias
        
        # Juntar dados
        df_completo = self.juntar_dados(df_fam, df_pes)
        
        # Gerar features
        df_final = self.gerar_features_vulnerabilidade(df_completo)
        
        # Salvar se solicitado
        if salvar:
            output_path = self.pasta_base / f"cadunico_processado_{n_registros}.csv"
            df_final.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Dados salvos em: {output_path}")
        
        # Estatísticas
        logger.info("\n" + "="*70)
        logger.info("📊 ESTATÍSTICAS DOS DADOS PROCESSADOS")
        logger.info("="*70)
        logger.info(f"Total de registros: {len(df_final):,}")
        logger.info(f"Distribuição de vulnerabilidade:")
        print(df_final['nivel_vulnerabilidade'].value_counts())
        logger.info(f"\nRenda per capita - média: R$ {df_final['renda_per_capita'].mean():.2f}")
        logger.info(f"Pessoas por família - média: {df_final['qtd_pessoas_familia'].mean():.2f}")
        logger.info(f"Recebem Bolsa Família: {df_final['recebe_bolsa_familia'].sum():,} ({df_final['recebe_bolsa_familia'].mean()*100:.1f}%)")
        logger.info("="*70 + "\n")
        
        return df_final
    
    def processar_completo_chunks(
        self,
        chunk_size: int = 100000,
        output_path: str = "data/cadunico_processado_completo.csv"
    ):
        """
        Processa dados completos em chunks para evitar estouro de memória.
        
        Args:
            chunk_size: Tamanho de cada chunk
            output_path: Caminho para salvar resultado
        """
        logger.info(f"Processando dados completos em chunks de {chunk_size:,}...")
        
        first_chunk = True
        total_processado = 0
        
        # Processar família em chunks
        for chunk_fam in pd.read_csv(
            self.path_fam,
            sep=';',
            encoding='latin-1',
            chunksize=chunk_size
        ):
            # Carregar pessoas correspondentes (aproximado)
            df_pes = self.carregar_cadunico_pessoa(nrows=chunk_size * 3)
            
            # Processar chunk
            df_chunk = self.juntar_dados(chunk_fam, df_pes)
            df_chunk = self.gerar_features_vulnerabilidade(df_chunk)
            
            # Salvar chunk
            mode = 'w' if first_chunk else 'a'
            header = first_chunk
            df_chunk.to_csv(output_path, mode=mode, header=header, index=False, encoding='utf-8')
            
            total_processado += len(df_chunk)
            logger.info(f"Processados {total_processado:,} registros...")
            
            first_chunk = False
            
            # Liberar memória
            del df_chunk, df_pes, chunk_fam
            gc.collect()
        
        logger.info(f"✅ Processamento completo: {total_processado:,} registros salvos em {output_path}")


def exemplo_uso():
    """Exemplo de uso do adaptador."""
    print("="*70)
    print("🔄 ADAPTADOR DE DADOS REAIS DO CADUNICO")
    print("="*70)
    
    # Criar adaptador
    adaptador = AdaptadorDadosReais()
    
    # Processar amostra de 100k registros
    df_amostra = adaptador.processar_amostra(n_registros=100000, salvar=True)
    
    print("\n✅ Processamento concluído!")
    print(f"Amostra gerada com {len(df_amostra):,} registros")
    print("\nPrimeiras linhas:")
    print(df_amostra.head())
    
    print("\nColunas disponíveis:")
    print(df_amostra.columns.tolist())


if __name__ == "__main__":
    exemplo_uso()
