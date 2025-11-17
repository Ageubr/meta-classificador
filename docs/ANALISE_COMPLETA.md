# 📊 Análise Completa dos Dados - CadÚnico e Bolsa Família

**Data:** 13/11/2025  
**Status:** ✅ Dados descompactados e analisados

---

## 📁 RESUMO DOS ARQUIVOS

### Arquivos Originais Descompactados

| Arquivo | Registros | Tamanho | Status |
|---------|-----------|---------|--------|
| **Bolsa Família** (202101_BolsaFamilia_Pagamentos.csv) | 14.233.116 | 1,5 GB | ✅ |
| **CadÚnico Família** (base_amostra_familia_201812.csv) | 4.807.996 | 659 MB | ✅ |
| **CadÚnico Pessoa** (base_amostra_pessoa_201812.csv) | 12.852.599 | 1,4 GB | ✅ |
| **TOTAL** | **31.893.711** | **~3,5 GB** | ✅ |

---

## 🔍 ESTRUTURA DOS DADOS

### 1. Bolsa Família (14,2M registros)

**Colunas principais:**
- MÊS COMPETÊNCIA, MÊS REFERÊNCIA
- UF, CÓDIGO MUNICÍPIO SIAFI, NOME MUNICÍPIO
- **NIS FAVORECIDO** (chave de identificação)
- NOME FAVORECIDO, CPF FAVORECIDO
- **VALOR PARCELA** (R$ 41 a R$ 1.426, média R$ 266)

**Características:**
- Dados de janeiro/2021 (competência) referentes a agosto/2020
- 99.713 NIS únicos em amostra de 100k
- Cobertura nacional (todos os estados)

---

### 2. CadÚnico - Família (4,8M registros)

**31 colunas incluindo:**

#### Identificação
- **id_familia** (chave única)
- cd_ibge (código município)
- estrato, classf, peso.fam

#### Renda e Composição
- **vlr_renda_media_fam**: R$ 0 a R$ 2.862 (média R$ 274, mediana R$ 104)
- **qtde_pessoas**: 1 a 14 pessoas (média 2,87)
- **marc_pbf**: 51,4% recebem Bolsa Família

#### Infraestrutura da Moradia
- **Água**: 62,4% têm rede geral
- **Esgoto**: 30,2% têm rede coletora
- **Material**: parede, piso, teto
- **Cômodos**: média 4,2 cômodos, 1,8 dormitórios

#### Serviços
- Iluminação, coleta de lixo
- Acesso a serviços de saúde e assistência social

**Estatísticas-chave:**
- 48,6% sem Bolsa Família (vulneráveis não atendidos)
- 37,6% sem água encanada
- 69,8% sem esgoto adequado

---

### 3. CadÚnico - Pessoa (12,8M registros)

**35 colunas incluindo:**

#### Demográfico
- **id_familia** (chave para JOIN)
- **id_pessoa** (identificador único)
- **cod_sexo_pessoa**: 57% Feminino, 43% Masculino
- **idade**: 0 a 120 anos (média 26,8)
- **cod_parentesco_rf_pessoa**: 1=Responsável, 2=Cônjuge, 3=Filho, 4=Outro
- **cod_raca_cor_pessoa**: Branca/Preta/Amarela/Parda/Indígena

#### Educação
- **cod_sabe_ler_escrever_memb**: alfabetização
- **ind_frequenta_escola_memb**: frequência escolar
- **cod_curso_frequenta_memb**: nível de ensino

#### Trabalho e Renda
- **cod_trabalhou_memb**: situação de trabalho
- **val_remuner_emprego_memb**: remuneração
- **val_renda_bruta_12_meses_memb**: renda anual
- **val_renda_aposent_memb**: aposentadoria
- **val_renda_pensao_alimen_memb**: pensão

#### Deficiência
- **cod_deficiencia_memb**: tipo de deficiência (visual, auditiva, física, mental, múltipla)

**Perfil demográfico:**
- ~40% crianças/adolescentes (0-17 anos)
- ~35% responsáveis familiares
- Concentração em idades reprodutivas (20-40 anos)

---

## 🔗 RELACIONAMENTOS E LIMITAÇÕES

### Estrutura Relacional

```
CadÚnico Família (id_familia)
    ↓ 1:N
CadÚnico Pessoa (id_familia, id_pessoa)
    ↓ ??? (PROBLEMA)
Bolsa Família (NIS)
```

### ⚠️ PROBLEMAS IDENTIFICADOS:

1. **Falta de NIS no CadÚnico**
   - CadÚnico não tem campo NIS explícito
   - Bolsa Família usa NIS como chave
   - **Solução atual:** Usar `marc_pbf=1` para identificar beneficiários

2. **JOIN limitado**
   - De 100k famílias + 300k pessoas → apenas 2.355 registros completos (2,4%)
   - Causa: `id_familia` não corresponde entre amostras sequenciais
   - **Solução:** Processar todos os dados ou usar amostras proporcionais

3. **Dados desatualizados**
   - CadÚnico: dezembro/2018
   - Bolsa Família: janeiro/2021
   - Diferença de 2 anos pode afetar correspondência

---

## 📊 RESULTADOS DO PROCESSAMENTO (Amostra)

### Dados Processados: 2.355 registros

#### Distribuição de Vulnerabilidade:
| Nível | Quantidade | % |
|-------|-----------|---|
| **Muito Alta** | 1.294 | 54,9% |
| **Alta** | 830 | 35,2% |
| **Média** | 194 | 8,2% |
| **Baixa** | 37 | 1,6% |

**⚠️ ALERTA:** 90,1% das famílias em vulnerabilidade Alta/Muito Alta!

#### Indicadores Socioeconômicos:
- **Renda per capita média:** R$ 171,63
- **Pessoas por família:** 2,87 (média)
- **Bolsa Família:** 51,6% recebem
- **Infraestrutura adequada:** minoria tem água + esgoto

---

## 🎯 MAPEAMENTO IMPLEMENTADO

### Transformações Aplicadas:

```python
# CadÚnico → Sistema
{
    'id_familia': 'id_familia',
    'idade': 'idade',
    'cod_sexo_pessoa': 'sexo' (1→M, 2→F),
    'vlr_renda_media_fam': 'renda_familiar',
    'qtde_pessoas': 'qtd_pessoas_familia',
    'cod_deficiencia_memb': 'possui_deficiencia' (1→0, 2+→1),
    'cod_trabalhou_memb': 'situacao_trabalho' (1→1, 2→0),
    'cod_abaste_agua_domic_fam': 'acesso_agua' (1→1, resto→0),
    'cod_escoa_sanitario_domic_fam': 'acesso_esgoto' (1→1, resto→0),
    'marc_pbf': 'recebe_bolsa_familia',
    'cod_especie_domic_fam': 'tipo_moradia'
}
```

### Features Geradas:
1. **renda_per_capita** = renda_familiar / qtd_pessoas
2. **vulnerabilidade_idade** = idade < 18 ou > 65
3. **infraestrutura_adequada** = água E esgoto
4. **escolaridade_baixa** = escolaridade ≤ 2
5. **situacao_trabalho_precaria** = trabalho ≤ 1
6. **superlotacao** = pessoas > 5
7. **score_vulnerabilidade** = soma ponderada
8. **nivel_vulnerabilidade** = classificação (Baixa/Média/Alta/Muito Alta)

---

## 🚀 ARQUIVOS GERADOS

### 1. Documentação
- ✅ `MAPEAMENTO_DADOS.md` - Mapeamento completo de campos
- ✅ `ANALISE_COMPLETA.md` - Este documento

### 2. Scripts
- ✅ `src/adaptar_dados_reais.py` - Adaptador de dados

### 3. Dados Processados
- ✅ `data/cadunico_processado_100000.csv` - Amostra processada (2.355 registros)

---

## 📋 PRÓXIMOS PASSOS

### ✅ CONCLUÍDO:
1. Descompactação dos arquivos ZIP
2. Análise da estrutura dos dados
3. Mapeamento de campos
4. Criação do adaptador
5. Processamento de amostra

### 🔄 EM ANDAMENTO:
6. Ajuste do JOIN para aumentar aproveitamento dos dados

### ⬜ PENDENTE:
7. Processar amostra maior (500k-1M registros)
8. Treinar modelos ML com dados reais
9. Validar métricas de performance
10. Comparar com modelos treinados em dados fictícios
11. Ajustar hiperparâmetros
12. Processar dados completos (31M registros)
13. Implementar processamento em chunks/paralelo
14. Integrar com API FastAPI
15. Configurar OpenAI para análise LLM

---

## ⚡ RECOMENDAÇÕES TÉCNICAS

### Para Desenvolvimento Imediato:
1. **Aumentar amostra para 500k** com JOIN proporcional
2. **Treinar modelos** com dados reais processados
3. **Comparar performance** com dados fictícios

### Para Produção:
1. **Processar dados completos** em chunks de 500k
2. **Salvar em banco de dados** (PostgreSQL/SQLite)
3. **Criar índices** em id_familia, nis, cod_municipio
4. **Pipeline automatizado** para atualização mensal
5. **Monitoramento** de qualidade dos dados

### Para Escala:
1. **Apache Spark** para processamento distribuído
2. **Dask** para pandas em grande escala
3. **Parquet** em vez de CSV para melhor performance
4. **Cloud storage** (S3/Azure) para dados brutos

---

## 📞 INFORMAÇÕES ADICIONAIS

### Fonte dos Dados:
- **CadÚnico:** Base amostral dezembro/2018
- **Bolsa Família:** Pagamentos janeiro/2021
- **Origem:** Portais do governo federal

### Limitações Conhecidas:
- Diferença temporal entre bases (2 anos)
- Falta de NIS no CadÚnico
- JOIN limitado entre tabelas (2,4% aproveitamento)
- Dados amostrais (não universo completo)

### Contato:
- Sistema: Meta-Classificador de Vulnerabilidade Social
- Repositório: meta-classificador
- Última atualização: 13/11/2025

---

## 🎉 CONCLUSÃO

✅ **Sistema pronto para treinar modelos com dados reais!**

Os dados foram descompactados, analisados e processados com sucesso. O adaptador está funcional e pode processar tanto amostras quanto os dados completos. 

**Próximo passo recomendado:** Treinar modelos ML com a amostra processada e validar resultados.

---

**Documentação gerada automaticamente durante análise dos dados**
