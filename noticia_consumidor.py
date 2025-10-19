from typing import Generator, Dict, Any

import pika
import sys
import time
from bs4 import BeautifulSoup
from pika.spec import BasicProperties
from pika.spec import Basic
from pika.adapters.blocking_connection import BlockingChannel

from src.conexao.conexao_redis import ConexaoRedis
from src.models.noticia import Noticia
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1
from src.servicos.manipulador.arquivo import Arquivo
from src.servicos.manipulador.arquivo_docx import ArquivoDOCX

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia


class NoticiaTrabalhador:

    def __init__(self, nome_fila: str, servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
                 arquivo: Arquivo):
        self.__credenciais = pika.PlainCredentials('rodrigo', '123456')
        self.__parametros_conexao = pika.ConnectionParameters(
            host='172.30.0.10',
            port=5672,
            virtual_host='/',
            credentials=self.__credenciais
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__servico_web_scraping = servico_web_scraping
        self.__arquivo = arquivo
        self.__nome_fila = nome_fila
        self.__conexao_redis = ConexaoRedis()
        self.__exchange_dlx = 'dead_letter_exchange'
        self.__dlq_queue = f'{nome_fila}_dead_letter'

    def configurar_fila(self):
        canal = self.__conexao.channel()
        canal.exchange_declare(exchange=self.__exchange_dlx, exchange_type='direct', durable=True)

        canal.queue_declare(queue=self.__exchange_dlx, durable=True)
        canal.queue_bind(exchange=self.__exchange_dlx, queue=self.__dlq_queue, routing_key=self.__dlq_queue)
        args = {
            "x-dead-letter-exchange": self.__exchange_dlx,
            "x-dead-letter-routing-key": self.__dlq_queue
        }

        canal.queue_declare(queue=self.__nome_fila, durable=True, arguments=args)
        return canal

    def processar_noticia(self, url: str, set_name: str, method: Basic.Deliver):
        try:
            if not self.__conexao_redis.e_membro(set_name=set_name, valor=url):
                self.__servico_web_scraping.url = url
                dados = self.__servico_web_scraping.abrir_conexao()
                if dados:
                    noticia = self.__servico_web_scraping.obter_dados(dados=dados)
                    if len(noticia.texto) > 0 or noticia.texto is not None:
                        self.__arquivo.noticia = noticia
                        nome_arquivo = ''.join(
                            url.split('.')[-2].split('/')[-1].replace('-', '_') + '.docx'
                        )
                        self.__arquivo.nome_arquivo = nome_arquivo
                        self.__arquivo.diretorio = method.routing_key
                        self.__arquivo.gerar_documento()
                        self.__arquivo()
                        self.__conexao_redis.adicionar_set(set_name=set_name, valor=url)

                return True

            return False
        except:
            return False

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        url = body.decode()
        set_name = f'g1:{"_".join(method.routing_key.split("_")[2:])}:urls'
        if not self.__conexao_redis.e_membro(set_name=set_name, valor=url):
            self.__servico_web_scraping.url = url

            if self.processar_noticia(url=url, set_name=set_name, method=method):
                print(f'Url inserida no Redis {url}')
            else:
                ch.basic_publish(
                    exchange=self.__exchange_dlx,
                    routing_key=self.__dlq_queue,
                    body=url,
                    properties=pika.BasicProperties(delivery_mode=2)
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f'url já foi adicionada {url}')


    def rodar(self):
        canal = self.configurar_fila()
        try:
            canal.basic_consume(queue=self.__nome_fila, on_message_callback=self.callback)
            canal.start_consuming()
        except KeyboardInterrupt:
            canal.stop_consuming()


if __name__ == '__main__':
    nome_fila = sys.argv[1]
    servico_web_scraping = WebScrapingG1(url=None, parse="html.parser")
    arquivo = ArquivoDOCX()
    notica_worker = NoticiaTrabalhador(
        nome_fila=nome_fila,
        servico_web_scraping=servico_web_scraping,
        arquivo=arquivo
    )
    notica_worker.rodar()
