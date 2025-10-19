import time
from typing import Dict, Generator, Any

import pika
from bs4 import BeautifulSoup

from conf_rabbitmq.configuacao_dlx import ConfiguracaoDLX
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingbs4g1rss import WebScrapingBs4G1Rss

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Generator[Dict[str, Any], None, None]
from config.config import Config


class Produtor:
    def __init__(self, servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador]):
        self.__credenciais = pika.PlainCredentials(Config.USR_RABBITMQ, Config.USR_RABBITMQ)
        self.__parametros_conexao = pika.ConnectionParameters(
            host=Config.URL_RABBITMQ,
            port=Config.PORTA_RABBITMQ,
            virtual_host='/',
            credentials=self.__credenciais
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__servico_web_scraping = servico_web_scraping
        self.__exchange_dlx = ConfiguracaoDLX()

    def rodar(self, urls_rss: Dict[str, str]):
        canal = self.__conexao.channel()
        while True:
            try:
                for nome_fila, url_rss in urls_rss.items():
                    self.__exchange_dlx.criar_fila_dlx(nome_fila=nome_fila, canal=canal)
                    self.__servico_web_scraping.url = url_rss
                    dados = self.__servico_web_scraping.abrir_conexao()
                    if dados:
                        for dados_g1 in self.__servico_web_scraping.obter_dados(dados):
                            url_g1 = dados_g1.get('url_rss')

                            if url_g1:
                                canal.basic_publish(
                                    exchange='',
                                    routing_key=nome_fila,
                                    body=url_g1,
                                    properties=pika.BasicProperties(delivery_mode=2)
                                )
            except KeyboardInterrupt:
                self.__conexao.close()
            time.sleep(10)


if __name__ == '__main__':
    urls_rss = {
        'fila_g1_ribeirao_preto': 'https://g1.globo.com/rss/g1/sp/ribeirao-preto-franca',
        'fila_g1_tecnologia': 'https://g1.globo.com/rss/g1/tecnologia/',
        'fila_g1_para': 'https://g1.globo.com/rss/g1/pa/para/'
    }
    rss_servico = WebScrapingBs4G1Rss(url=None)
    produtor = Produtor(
        servico_web_scraping=rss_servico
    )

    produtor.rodar(urls_rss=urls_rss)
