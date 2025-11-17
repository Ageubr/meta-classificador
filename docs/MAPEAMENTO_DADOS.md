# 📊 Mapeamento de Dados - CadÚnico e Bolsa Família

## 📁 Estrutura dos Arquivos

### 1. **Bolsa Família** (14,2M registros - 1,5GB)
**Arquivo:** `202101_BolsaFamilia_Pagamentos.csv`

| Campo Original | Descrição | Tipo |
|----------------|-----------|------|
| MÊS COMPETÊNCIA | Mês de pagamento (YYYYMM) | int64 |
| MÊS REFERÊNCIA | Mês de referência (YYYYMM) | int64 |
| UF | Estado | string |
| CÓDIGO MUNICÍPIO SIAFI | Código do município | int64 |
| NOME MUNICÍPIO | Nome do município | string |
| CPF FAVORECIDO | CPF (mascarado) | string |
| **NIS FAVORECIDO** | NIS do beneficiário (CHAVE) | int64 |
| NOME FAVORECIDO | Nome do beneficiário | string |
| VALOR PARCELA | Valor do benefício (formato: "XXX,XX") | string |

**Valores típicos:**
- Valor médio: R$ 266,34
- Valor mínimo: R$ 41,00
- Valor máximo: R$ 1.426,00

---

### 2. **CadÚnico - Família** (4,8M registros - 659MB)
**Arquivo:** `base_amostra_familia_201812.csv`

#### Campos Principais (31 colunas)

| Campo | Descrição | Mapeamento para Sistema |
|-------|-----------|------------------------|
| **id_familia** | ID único da família (CHAVE) | Identificador |
| cd_ibge | Código IBGE do município | município |
| vlr_renda_media_fam | Renda média familiar | renda_familiar |
| qtde_pessoas | Quantidade de pessoas | qtd_pessoas_familia |
| marc_pbf | Marca se recebe Bolsa Família (0/1) | recebe_bolsa_familia |

#### Infraestrutura da Moradia

| Campo | Valores | Mapeamento |
|-------|---------|------------|
| cod_abaste_agua_domic_fam | 1=Rede geral, 2=Poço/nascente, 3=Cisterna, 4=Outro | acesso_agua |
| cod_escoa_sanitario_domic_fam | 1=Rede coletora, 2=Fossa séptica, 3=Fossa rudimentar, 4=Vala, 5=Céu aberto, 6=Outro | acesso_esgoto |
| cod_banheiro_domic_fam | 1=Sim, 2=Não | possui_banheiro |
| qtd_comodos_domic_fam | Quantidade de cômodos | comodos |
| qtd_comodos_dormitorio_fam | Quantidade de dormitórios | dormitorios |
| cod_material_domic_fam | Material da parede | material_parede |
| cod_material_piso_fam | Material do piso | material_piso |

#### Estatísticas (amostra 100k):
- **Renda média:** R$ 274,25 (mediana: R$ 104,00)
- **Pessoas por família:** média 2,85 (1 a 14)
- **Bolsa Família:** 51,4% recebem
- **Água encanada:** 62,4% têm acesso
- **Esgoto adequado:** 30,2% (rede coletora)

---

### 3. **CadÚnico - Pessoa** (12,8M registros - 1,4GB)
**Arquivo:** `base_amostra_pessoa_201812.csv`

#### Campos Principais (35 colunas)

| Campo | Descrição | Mapeamento para Sistema |
|-------|-----------|------------------------|
| **id_familia** | ID da família (CHAVE para JOIN) | Link com família |
| **id_pessoa** | ID único da pessoa | Identificador |
| cod_sexo_pessoa | 1=Masculino, 2=Feminino | sexo |
| idade | Idade em anos | idade |
| cod_parentesco_rf_pessoa | 1=Responsável, 2=Cônjuge, 3=Filho, 4=Outro | parentesco |
| cod_raca_cor_pessoa | 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena | raca_cor |

#### Educação

| Campo | Valores | Mapeamento |
|-------|---------|------------|
| cod_sabe_ler_escrever_memb | 1=Sim, 2=Não | alfabetizado |
| ind_frequenta_escola_memb | 1=Sim, 2=Não, 3=Nunca frequentou | frequenta_escola |
| cod_curso_frequenta_memb | Nível de ensino atual | escolaridade |

#### Trabalho e Renda

| Campo | Descrição | Mapeamento |
|-------|-----------|------------|
| cod_trabalhou_memb | Trabalhou na semana anterior (1=Sim, 2=Não) | situacao_trabalho |
| val_remuner_emprego_memb | Valor da remuneração | renda_trabalho |
| val_renda_bruta_12_meses_memb | Renda bruta últimos 12 meses | renda_anual |
| val_renda_aposent_memb | Renda de aposentadoria | renda_aposentadoria |
| val_renda_pensao_alimen_memb | Pensão alimentícia | renda_pensao |

#### Deficiência

| Campo | Valores | Mapeamento |
|-------|---------|------------|
| cod_deficiencia_memb | 1=Não tem, 2=Visual, 3=Auditiva, 4=Física, 5=Mental, 6=Múltipla | possui_deficiencia |

#### Estatísticas (amostra 100k):
- **Sexo:** 57% Feminino, 43% Masculino
- **Idade média:** 26,8 anos (0 a 120)
- **Crianças (0-17):** ~40% da amostra
- **Responsável familiar:** ~35% dos registros

---

## 🔗 Relacionamentos entre Tabelas

```
CadÚnico Família (id_familia) ←─┐
                                 │
                                 ├─ CadÚnico Pessoa (id_familia)
                                 │
Bolsa Família (NIS) ─────────────┘ (precisa criar relação via pessoa/responsável)
```

### Estratégia de JOIN:

1. **Família ↔ Pessoa**: JOIN direto por `id_familia`
2. **Pessoa ↔ Bolsa Família**: Precisa identificar NIS no CadÚnico
   - ⚠️ **PROBLEMA**: CadÚnico não tem campo NIS explícito
   - **SOLUÇÃO**: Usar combinação de dados demográficos ou considerar famílias com `marc_pbf=1`

---

## 📊 Mapeamento para o Sistema Atual

### De: **CadÚnico** → Para: **Sistema**

```python
{
    # Identificação
    'id_familia': 'id_familia',
    'id_pessoa': 'nis',  # Usar como substituto
    
    # Demográfico
    'idade': 'idade',
    'cod_sexo_pessoa': 'sexo',  # 1=M, 2=F
    
    # Educação
    'cod_curso_frequenta_memb': 'escolaridade',  # 0-5
    
    # Renda
    'vlr_renda_media_fam': 'renda_familiar',
    'qtde_pessoas': 'qtd_pessoas_familia',
    
    # Deficiência
    'cod_deficiencia_memb': 'possui_deficiencia',  # 1=Não, 2+=Sim
    
    # Trabalho
    'cod_trabalhou_memb': 'situacao_trabalho',  # 1=Sim, 2=Não
    
    # Moradia
    'cod_especie_domic_fam': 'tipo_moradia',
    'cod_abaste_agua_domic_fam': 'acesso_agua',  # 1=Sim, 2+=Não
    'cod_escoa_sanitario_domic_fam': 'acesso_esgoto',  # 1=Sim, resto=Não
    
    # Município
    'cd_ibge': 'municipio',
    
    # Bolsa Família
    'marc_pbf': 'recebe_bolsa_familia'
}
```

---

## ⚙️ Transformações Necessárias

### 1. **Sexo**
```python
# De: 1=Masculino, 2=Feminino
# Para: 'M', 'F'
sexo_map = {1: 'M', 2: 'F'}
```

### 2. **Acesso à Água**
```python
# De: 1=Rede, 2=Poço, 3=Cisterna, 4=Outro
# Para: 0/1 (adequado/inadequado)
agua_map = {1: 1, 2: 0, 3: 0, 4: 0}  # Apenas rede = adequado
```

### 3. **Acesso ao Esgoto**
```python
# De: 1=Rede, 2=Fossa séptica, 3=Fossa rudimentar, 4=Vala, 5=Céu aberto, 6=Outro
# Para: 0/1 (adequado/inadequado)
esgoto_map = {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Apenas rede = adequado
```

### 4. **Deficiência**
```python
# De: 1=Não, 2=Visual, 3=Auditiva, 4=Física, 5=Mental, 6=Múltipla
# Para: 0/1
deficiencia_map = lambda x: 0 if x == 1 else 1
```

### 5. **Situação de Trabalho**
```python
# De: 1=Trabalhou, 2=Não trabalhou
# Para: 0=Desempregado, 1=Informal, 2=Formal (simplificado)
# Usar: 1 → 1 (informal), 2 → 0 (desempregado)
trabalho_map = {1: 1, 2: 0}
```

### 6. **Escolaridade**
```python
# Mapear cod_curso_frequenta_memb para 0-5
# 1=Creche → 0
# 2=Pré-escola → 0
# 3=EF 1-4 → 1
# 4=EF 5-9 → 2
# 5=Médio → 3
# 6=Superior → 5
# 7=EJA → 2
```

---

## 💾 Volumes de Dados

| Dataset | Registros | Tamanho | Linhas/MB |
|---------|-----------|---------|-----------|
| **Bolsa Família** | 14.233.116 | 1,5 GB | ~9.500 |
| **CadÚnico Família** | 4.807.996 | 659 MB | ~7.300 |
| **CadÚnico Pessoa** | 12.852.599 | 1,4 GB | ~9.200 |

**Total:** ~32 milhões de registros, ~3,5 GB

---

## 🎯 Recomendações

### Para Desenvolvimento:
- ✅ Criar amostra de **100k registros** de cada arquivo
- ✅ Testar pipeline completo com amostra
- ✅ Validar mapeamentos e transformações

### Para Produção:
- ⚠️ Processar em **chunks de 100k-500k** registros
- ⚠️ Usar **Dask ou Pandas chunking** para evitar estouro de memória
- ⚠️ Criar índices no SQLite/PostgreSQL para consultas rápidas
- ⚠️ Considerar **Apache Spark** para processamento distribuído

### Prioridades:
1. **JOIN Família + Pessoa** para criar dataset completo
2. **Aplicar transformações** de mapeamento
3. **Criar features de vulnerabilidade** conforme sistema atual
4. **Treinar modelos** com dados reais
5. **Validar resultados** com especialistas

---

## 📝 Próximos Passos

1. ✅ Criar script de conversão/adaptação
2. ✅ Gerar amostra de desenvolvimento (100k)
3. ✅ Testar pipeline com dados reais
4. ⬜ Treinar modelos ML
5. ⬜ Avaliar performance e métricas
6. ⬜ Ajustar features conforme necessário

---

**Data da Análise:** 2025-11-13  
**Versão:** 1.0
