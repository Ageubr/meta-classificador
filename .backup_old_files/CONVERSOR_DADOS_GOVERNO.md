# 🔄 Conversor de Dados do Governo

## 📋 Visão Geral

Este conversor permite usar **arquivos originais do governo** (CadÚnico) diretamente no sistema, sem precisar criar arquivos manualmente.

Os arquivos originais disponibilizados pelo governo usam formato diferente (separador `;`, codificação `latin-1`), e este script converte automaticamente para o formato que o sistema precisa.

## 🎯 Arquivos Suportados

✅ **base_amostra_familia_201812.csv** (4.8M registros)
- Dados das famílias cadastradas
- Renda, infraestrutura, Bolsa Família

✅ **base_amostra_pessoa_201812.csv** (12.8M registros)  
- Dados das pessoas da família
- Idade, sexo, escolaridade, trabalho

## 🚀 Como Usar

### Opção 1: Conversão Rápida (Recomendado)

Converte **5.000 registros** (rápido para testar):

```bash
python src/conversor_dados_governo.py --max-linhas 5000
```

### Opção 2: Conversão Média

Converte **50.000 registros** (~2-3 minutos):

```bash
python src/conversor_dados_governo.py --max-linhas 50000
```

### Opção 3: Conversão Completa

Converte **TODOS** os registros (~30-40 minutos):

```bash
python src/conversor_dados_governo.py --max-linhas 0
```

### Opção 4: Personalizada

```bash
python src/conversor_dados_governo.py \
  --familias data/base_amostra_cad_201812/base_amostra_familia_201812.csv \
  --pessoas data/base_amostra_cad_201812/base_amostra_pessoa_201812.csv \
  --saida data/meu_arquivo_convertido.csv \
  --max-linhas 10000
```

## 📊 O que o Conversor Faz

### 1. **Lê arquivos originais do governo**
- Detecta automaticamente separador `;`
- Usa codificação `latin-1`
- Processa milhões de linhas

### 2. **Extrai e converte dados**

**Do arquivo de FAMÍLIAS:**
- ✅ `cd_ibge` → `cod_municipio`
- ✅ `vlr_renda_media_fam` → `renda_familiar`
- ✅ `qtde_pessoas` → `qtd_pessoas_familia`
- ✅ `marc_pbf` → `recebe_bolsa_familia`
- ✅ `cod_agua_canalizada_fam` → `acesso_agua`
- ✅ `cod_escoa_sanitario_domic_fam` → `acesso_esgoto`
- ✅ `cod_especie_domic_fam` → `tipo_moradia`

**Do arquivo de PESSOAS:**
- ✅ `idade` → `idade` (do responsável)
- ✅ `cod_sexo_pessoa` → `sexo`
- ✅ `cod_curso_frequentou_pessoa_memb` → `escolaridade`
- ✅ `cod_trabalhou_memb` → `situacao_trabalho`
- ✅ `cod_deficiencia_memb` → `possui_deficiencia`

### 3. **Calcula campos adicionais**
- ✅ `renda_per_capita` = renda_familiar / qtd_pessoas_familia

### 4. **Mescla famílias com pessoas**
- Identifica o responsável familiar
- Adiciona dados pessoais ao registro da família
- Remove registros inválidos

### 5. **Salva no formato do sistema**
- Arquivo CSV com vírgula
- Codificação UTF-8
- Pronto para análise!

## 📈 Resultado

Após a conversão, você terá um arquivo como:

```csv
cod_municipio,id_familia,idade,sexo,escolaridade,renda_familiar,qtd_pessoas_familia,renda_per_capita,possui_deficiencia,situacao_trabalho,tipo_moradia,acesso_agua,acesso_esgoto,recebe_bolsa_familia
3205002,1,35,F,1,244,5,48.8,0,0,1,1,1,0
3205101,3,35,F,1,60,5,12.0,0,0,1,1,1,1
...
```

## 🎯 Usar no Sistema

Depois de converter:

1. **Acesse**: `http://localhost:8000/data-viewer.html`
2. **Você verá**: `cadunico_convertido.csv` na lista
3. **Clique** no arquivo
4. **Veja** a análise completa por município com IA!

## 📊 Exemplo de Saída

```
======================================================================
CONVERSÃO DE DADOS DO GOVERNO PARA O SISTEMA
======================================================================

[1/4] Lendo dados de famílias...
✓ 5000 famílias lidas

[2/4] Lendo dados de pessoas...
✓ 15000 pessoas lidas

[3/4] Processando dados de famílias...

[4/4] Mesclando dados de pessoas (responsável familiar)...
✓ Conversão concluída: 5000 registros finais
✓ Arquivo salvo em: data/cadunico_convertido.csv

======================================================================
ESTATÍSTICAS DO ARQUIVO CONVERTIDO
======================================================================
Total de registros: 5,000
Total de municípios: 83
Renda per capita média: R$ 156.61
Recebem Bolsa Família: 2,619 (52.4%)
======================================================================

✅ Conversão concluída com sucesso!
```

## ⚡ Performance

| Registros | Tempo Estimado | Tamanho Arquivo |
|-----------|---------------|-----------------|
| 5.000     | ~10 segundos  | ~250 KB        |
| 50.000    | ~2 minutos    | ~2.5 MB        |
| 500.000   | ~20 minutos   | ~25 MB         |
| 4.8M      | ~2 horas      | ~240 MB        |

## 🔧 Parâmetros

### `--familias`
Caminho do arquivo de famílias do governo
- Padrão: `data/base_amostra_cad_201812/base_amostra_familia_201812.csv`

### `--pessoas`
Caminho do arquivo de pessoas do governo
- Padrão: `data/base_amostra_cad_201812/base_amostra_pessoa_201812.csv`

### `--saida`
Onde salvar o arquivo convertido
- Padrão: `data/cadunico_convertido.csv`

### `--max-linhas`
Número máximo de famílias para processar
- Padrão: `10000`
- Use `0` para processar TODAS

## 💡 Dicas

### ✅ Para Testes Rápidos
```bash
python src/conversor_dados_governo.py --max-linhas 1000
```
Converte 1000 famílias em ~5 segundos

### ✅ Para Análise Completa
```bash
python src/conversor_dados_governo.py --max-linhas 100000
```
Converte 100.000 famílias em ~10 minutos

### ✅ Para Dados Regionais
Primeiro filtre o CSV original por estado/região, depois converta

## 🚨 Solução de Problemas

### Erro: "Arquivo não encontrado"
```bash
# Verifique se os arquivos existem
ls -lh data/base_amostra_cad_201812/
```

### Erro: "Memory error"
Use `--max-linhas` menor:
```bash
python src/conversor_dados_governo.py --max-linhas 10000
```

### Arquivo muito lento para processar
- Comece com poucos registros (5000)
- Aumente gradualmente conforme necessidade
- Sistema funciona bem até 100.000 registros

## 📚 Estrutura dos Dados Originais

### Arquivo de Famílias
- **cd_ibge**: Código IBGE do município
- **vlr_renda_media_fam**: Renda média da família
- **qtde_pessoas**: Quantidade de pessoas
- **marc_pbf**: Marcador Bolsa Família (0/1)
- **cod_agua_canalizada_fam**: Água canalizada (1=sim)
- **cod_escoa_sanitario_domic_fam**: Esgoto (1=sim)

### Arquivo de Pessoas
- **id_familia**: ID da família (chave para mesclar)
- **idade**: Idade da pessoa
- **cod_sexo_pessoa**: 1=M, 2=F
- **cod_parentesco_rf_pessoa**: 1=Responsável Familiar
- **cod_curso_frequentou_pessoa_memb**: Nível de escolaridade
- **cod_trabalhou_memb**: Trabalhou (0=não, 1=sim)
- **cod_deficiencia_memb**: Possui deficiência

## 🎉 Pronto!

Agora você pode usar os **dados reais do governo** diretamente no sistema, sem precisar criar arquivos manualmente!

**Próximo passo**: Abra `http://localhost:8000/data-viewer.html` e analise! 🚀
