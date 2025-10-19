from typing import Optional
from src.models.noticia import Noticia
from bs4 import BeautifulSoup
import hashlib

from src.servicos.extracao.webscrapingbasebs4 import WebScrapingBs4base
from datetime import datetime



class WebScrapingG1(WebScrapingBs4base[Noticia]):

    def __init__(self, url: Optional[str], parse: str):
        super().__init__(url, parse)
        self.__parser_html = 'html.parser'

    def obter_dados(self, dados: BeautifulSoup) -> Noticia:
        """
        Método para obter a noticia
        :param dados: dados do bs4
        :type dados: Union[bs4.BeautifulSoup, str]
        :return: A noticia ou nada
        :rtype: Union[None, models.noticia.Noticia]
        """

        titulo_elem = dados.find('h1', class_='content-head__title')

        titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""

        sub_titulo_elem = dados.find('h2', class_='content-head__subtitle')
        sub_titulo = sub_titulo_elem.get_text(strip=True) if sub_titulo_elem else ""

        data_publi = dados.find('p', class_='content-publication-data__from')
        data_publicacao = None
        if data_publi:
            try:
                data_str = data_publi.text.strip()
                data_publicacao = datetime.strptime(data_str, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                data_publicacao = datetime.now()  # fallback

        texto_noticia_elem = dados.select('p.content-text__container')

        texto_noticia_tratado = self._tratamento.limpar_descricao(
            textos=texto_noticia_elem
        )

        autor_elem = dados.find('p', class_='content-publication-data__from')
        autor = autor_elem.get_text(strip=True) if autor_elem else ''

        noticia = Noticia(
            id_noticia=hashlib.md5(self.url.encode('utf-8')).hexdigest(),
            titulo=titulo,
            subtitulo=sub_titulo,
            autor=autor,
            data_hora=data_publicacao,
            texto=texto_noticia_tratado

        )

        return noticia


if __name__ == '__main__':
    from src.servicos.extracao.iwebscrapingbase import IWebScapingBase

    if issubclass(WebScrapingG1, IWebScapingBase):
        print('sim')
    else:
        print('Não')
