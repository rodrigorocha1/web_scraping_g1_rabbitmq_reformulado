import time

import pika
from bs4 import BeautifulSoup
from src.servicos.extracao.webscrapingbs4g1rss import WebScrapingBs4G1Rss
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from typing import Dict, Generator, Any
from pika.adapters.blocking_connection import BlockingChannel

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Generator[Dict[str, Any], None, None]


class Produtor:
    def __init__(self, servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador]):
        self.__credenciais = pika.PlainCredentials('rodrigo', '123456')
        self.__parametros_conexao = pika.ConnectionParameters(
            host='172.30.0.10',
            port=5672,
            virtual_host='/',
            credentials=self.__credenciais
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__servico_web_scraping = servico_web_scraping
        self.__exchange_dlx = 'dead_letter_exchange'

    def criar_fila_com_dlx(self, nome_fila: str, canal: BlockingChannel):
        fila_dlq = f"{nome_fila}_dead_letter"
        canal.exchange_declare(exchange=self.__exchange_dlx, exchange_type='direct', durable=True)
        canal.queue_declare(queue=fila_dlq, durable=True, arguments={
            "x-message-ttl": 60000  # 60 segundos
        })
        canal.queue_bind(exchange=self.__exchange_dlx, queue=fila_dlq, routing_key=fila_dlq)
        args = {
            "x-dead-letter-exchange": self.__exchange_dlx,
            "x-dead-letter-routing-key": fila_dlq
        }
        canal.queue_declare(queue=nome_fila, durable=True, arguments=args)


    def rodar(self, urls_rss: Dict[str, str]):
        canal = self.__conexao.channel()
        while True:
            try:
                for nome_fila, url_rss in urls_rss.items():
                    self.criar_fila_com_dlx(nome_fila=nome_fila, canal=canal)
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

