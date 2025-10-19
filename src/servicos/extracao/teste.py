from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from src.models.noticia import Noticia
import sys

url = 'https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca'

# extração rss
response = requests.get(url)
xml_content = response.text

# Use o parser 'xml' em vez de 'html.parser' para processar XML
soup = BeautifulSoup(xml_content, 'lxml-xml')

print(type(soup))


def abrir_conexao():
    url = 'https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca'
    respose = requests.get(url)
    conteudo_xml = respose.content

    soup = BeautifulSoup(conteudo_xml, 'xml')
    print(type(soup))
    return soup


soup = abrir_conexao()


def extrair_dados_g1():
    pass


def limpar_descricao(descricao_html):
    print(type(descricao_html))
    # Faz um soup para manipular a descrição em HTML
    soup_desc = BeautifulSoup(descricao_html, 'html.parser')

    # Remove a tag <img>
    for img in soup_desc.find_all('img'):
        img.decompose()

    texto_limpo = soup_desc.get_text(separator=' ').strip()

    # Remove frases específicas usando regex (ignore case)
    padroes_a_remover = [
        r'vídeos?.*?(?=\n|$)',
        r'veja\s+mais\s+not[ií]cias.*?(?=\n|$)',
        r'leia\s+mais.*?(?=\n|$)',
        r'receba\s+no\s+whatsapp\s+as\s+not[ií]cias.*?(?=\n|$)',
        r'siga\s+o\s+canal\s+g1\s+ribeir[aã]o\s+e\s+franca\s+no\s+whatsapp.*?(?=\n|$)'

    ]

    for padrao in padroes_a_remover:
        texto_limpo = re.sub(padrao, '', texto_limpo, flags=re.IGNORECASE)

    # Remove espaços extras e quebras de linha
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()

    return texto_limpo


def tamanho_total_objetos(lista):
    tamanho = sys.getsizeof(lista)
    for obj in lista:
        tamanho += sys.getsizeof(obj)
    return tamanho / (1024 * 1024)



def obter_dados_noticia(soup):
    formato_entrada = "%a, %d %b %Y %H:%M:%S %z"
    lista_noticias = []
    for noticia in soup.find_all('item'):
        print(noticia.title.text)
        print(noticia.guid.text)
        descricao_html = noticia.description.text

        descricao_limpa = limpar_descricao(descricao_html)
        print(descricao_limpa)

        media_content_tag = noticia.find('media:content')
        media_content = media_content_tag['url'] if media_content_tag else None
        print(media_content)
        data = noticia.pubDate.text
        data = datetime.strptime(data, formato_entrada)
        data = data.strftime("%d-%m-%Y %H:%M:%S")

        data = datetime.strptime(data, "%d-%m-%Y %H:%M:%S")
        print(data, type(data))

        noticia = Noticia(
            titulo_noticia=noticia.title.text,
            url=noticia.guid.text,
            descricao_noticia=descricao_limpa,
            url_imagem=media_content,
            data_publicacao=data,

        )
        lista_noticias.append(noticia)
        print(type(noticia))
        print(noticia)
        print('=' * 100)
    print('Tamanho da lista')
    print(f'Tamanho da lista em MB (estrutura + objetos): {tamanho_total_objetos(lista_noticias):.6f}')


obter_dados_noticia(soup=soup)
