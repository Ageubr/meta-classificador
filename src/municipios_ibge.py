"""
Módulo para mapear códigos IBGE para nomes de municípios.
Usa cache local e fallback para API do IBGE quando necessário.
"""

import json
from pathlib import Path
import requests
import logging

logger = logging.getLogger(__name__)

# Cache de municípios (top 100 mais populosos + ES)
MUNICIPIOS_CACHE = {
    # Espírito Santo
    3200102: "Afonso Cláudio",
    3200136: "Água Doce do Norte",
    3200169: "Águia Branca",
    3200201: "Alegre",
    3200300: "Alfredo Chaves",
    3200359: "Alto Rio Novo",
    3200409: "Anchieta",
    3200508: "Apiacá",
    3200607: "Aracruz",
    3200706: "Atílio Vivácqua",
    3200805: "Baixo Guandu",
    3200904: "Barra de São Francisco",
    3201001: "Boa Esperança",
    3201100: "Bom Jesus do Norte",
    3201159: "Brejetuba",
    3201209: "Cachoeiro de Itapemirim",
    3201308: "Cariacica",
    3201407: "Castelo",
    3201506: "Colatina",
    3201605: "Conceição da Barra",
    3201704: "Conceição do Castelo",
    3201803: "Divino de São Lourenço",
    3201902: "Domingos Martins",
    3202009: "Dores do Rio Preto",
    3202108: "Ecoporanga",
    3202207: "Fundão",
    3202256: "Governador Lindenberg",
    3202306: "Guaçuí",
    3202405: "Guarapari",
    3202454: "Ibatiba",
    3202504: "Ibiraçu",
    3202553: "Ibitirama",
    3202603: "Iconha",
    3202652: "Irupi",
    3202702: "Itaguaçu",
    3202801: "Itapemirim",
    3202900: "Itarana",
    3203007: "Iúna",
    3203056: "Jaguaré",
    3203106: "Jerônimo Monteiro",
    3203130: "João Neiva",
    3203163: "Laranja da Terra",
    3203205: "Linhares",
    3203304: "Mantenópolis",
    3203320: "Marataízes",
    3203346: "Marechal Floriano",
    3203353: "Marilândia",
    3203403: "Mimoso do Sul",
    3203502: "Montanha",
    3203601: "Mucurici",
    3203700: "Muniz Freire",
    3203809: "Muqui",
    3203908: "Nova Venécia",
    3204005: "Pancas",
    3204054: "Pedro Canário",
    3204104: "Pinheiros",
    3204203: "Piúma",
    3204252: "Ponto Belo",
    3204302: "Presidente Kennedy",
    3204351: "Rio Bananal",
    3204401: "Rio Novo do Sul",
    3204500: "Santa Leopoldina",
    3204559: "Santa Maria de Jetibá",
    3204609: "Santa Teresa",
    3204658: "São Domingos do Norte",
    3204708: "São Gabriel da Palha",
    3204807: "São José do Calçado",
    3204906: "São Mateus",
    3204955: "São Roque do Canaã",
    3205002: "Serra",
    3205010: "Sooretama",
    3205036: "Vargem Alta",
    3205069: "Venda Nova do Imigrante",
    3205101: "Viana",
    3205150: "Vila Pavão",
    3205176: "Vila Valério",
    3205200: "Vila Velha",
    3205309: "Vitória",
    
    # Capitais e grandes municípios
    1100205: "Porto Velho",
    1200401: "Rio Branco",
    1302603: "Manaus",
    1400100: "Boa Vista",
    1501402: "Belém",
    1600303: "Macapá",
    1721000: "Palmas",
    2111300: "São Luís",
    2211001: "Teresina",
    2304400: "Fortaleza",
    2408102: "Natal",
    2507507: "João Pessoa",
    2611606: "Recife",
    2704302: "Maceió",
    2800308: "Aracaju",
    2927408: "Salvador",
    3106200: "Belo Horizonte",
    3304557: "Rio de Janeiro",
    3509502: "Campinas",
    3518800: "Guarulhos",
    3550308: "São Paulo",
    4106902: "Curitiba",
    4205407: "Florianópolis",
    4314902: "Porto Alegre",
    5002704: "Campo Grande",
    5103403: "Cuiabá",
    5208707: "Goiânia",
    5300108: "Brasília",
    
    # Outros municípios ES frequentes
    3202355: "Guaçuí",
    3203130: "João Neiva",
    3204252: "Ponto Belo",
    3204609: "Santa Teresa",
    3204955: "São Roque do Canaã",
    3205010: "Sooretama",
    
    # Adicionar códigos específicos da amostra
    2304301: "Fortaleza",
    2403251: "Mossoró",
    2304400: "Fortaleza",
    2310308: "Juazeiro do Norte",
    2312908: "Sobral",
    2403301: "Natal",
    2408102: "Natal",
}


def buscar_nome_municipio_api(cod_ibge: int) -> str:
    """
    Busca nome do município via API do IBGE.
    
    Args:
        cod_ibge: Código IBGE do município (6 ou 7 dígitos)
        
    Returns:
        Nome do município ou código como string se não encontrar
    """
    try:
        # API do IBGE - localidades (timeout reduzido para 2s)
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{cod_ibge}"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            nome = data.get('nome', str(cod_ibge))
            uf = data.get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('sigla', '')
            
            if uf:
                return f"{nome}/{uf}"
            return nome
        else:
            logger.debug(f"API IBGE retornou status {response.status_code} para município {cod_ibge}")
            return f"Município {cod_ibge}"
            
    except Exception as e:
        logger.debug(f"Erro ao buscar município {cod_ibge} na API: {e}")
        return f"Município {cod_ibge}"


def obter_nome_municipio(cod_ibge: int) -> str:
    """
    Obtém o nome do município a partir do código IBGE.
    Primeiro tenta cache local, depois API do IBGE.
    
    Args:
        cod_ibge: Código IBGE do município
        
    Returns:
        Nome do município formatado
    """
    # Verificar cache local
    if cod_ibge in MUNICIPIOS_CACHE:
        nome = MUNICIPIOS_CACHE[cod_ibge]
        
        # Adicionar UF para municípios do ES (códigos 32xxxxx)
        if str(cod_ibge).startswith('32'):
            return f"{nome}/ES"
        return nome
    
    # Buscar na API do IBGE
    return buscar_nome_municipio_api(cod_ibge)


def obter_nomes_municipios_batch(codigos: list[int]) -> dict[int, str]:
    """
    Obtém nomes de múltiplos municípios de uma vez.
    
    Args:
        codigos: Lista de códigos IBGE
        
    Returns:
        Dicionário {codigo: nome}
    """
    resultado = {}
    
    for cod in codigos:
        resultado[cod] = obter_nome_municipio(cod)
    
    return resultado


if __name__ == "__main__":
    # Testes
    print("Testando mapeamento de municípios:")
    print()
    
    codigos_teste = [3205002, 3201308, 3205200, 3205309, 3106200, 3550308, 1234567]
    
    for cod in codigos_teste:
        nome = obter_nome_municipio(cod)
        print(f"  {cod} → {nome}")
