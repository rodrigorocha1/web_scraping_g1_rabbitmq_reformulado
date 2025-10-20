import sys
from typing import List, Dict

import pika
from bs4 import BeautifulSoup
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties

from src.conf_rabbitmq.configuacao_dlx import ConfiguracaoDLX
from src.conexao.conexao_redis import ConexaoRedis
from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco
from src.scripts_banco.script_mongo_db import ScriptMongoDB
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1
from src.servicos.manipulador.arquivo_docx import ArquivoDOCX

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia

from src.config.config import Config


class NoticiaTrabalhador:

    def __init__(
            self,
            nome_fila: str,
            servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
            consuta: IScriptBanco
    ):
        self.__credenciais = pika.PlainCredentials(Config.USR_RABBITMQ, Config.PWD_RABBITMQ)
        self.__parametros_conexao = pika.ConnectionParameters(
            host=Config.URL_RABBITMQ,
            port=Config.PORTA_RABBITMQ,
            virtual_host=Config.VIRTUAL_HOST_RABBITMQ,
            credentials=self.__credenciais
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__servico_web_scraping = servico_web_scraping
        self.__nome_fila = nome_fila
        self.__conexao_redis = ConexaoRedis()
        self.__exchange_dlx = 'dead_letter_exchange'
        self.__dlq_queue = f'{nome_fila}_dead_letter'
        self.__consulta = consuta
        self.__lote: List[Dict] = []
        self.__tamanho_lote = 60
        self.__dlx = ConfiguracaoDLX(self.__exchange_dlx)

    def configurar_fila(self):
        canal = self.__conexao.channel()
        self.__dlx.criar_fila_dlx(nome_fila=self.__nome_fila, canal=canal)
        return canal

    def processar_noticia(self, url: str, set_name: str, method: Basic.Deliver):
        try:
            self.__servico_web_scraping.url = url
            dados = self.__servico_web_scraping.abrir_conexao()
            if dados:
                noticia = self.__servico_web_scraping.obter_dados(dados=dados)
                if len(noticia.texto) > 0 or noticia.texto is not None:
                    print(noticia)
                    print('*' * 100)

            return True
        except:
            return False

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        url = body.decode()
        print(f'Dentro de {__name__} {__file__} -> url {url}')
        self.__servico_web_scraping.url = url
        noticia_processada = self.processar_noticia(url=url, set_name='a', method=method)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        # set_name = f'g1:{"_".join(method.routing_key.split("_")[2:])}:urls'
        # if not self.__conexao_redis.e_membro(set_name=set_name, valor=url):
        #     self.__servico_web_scraping.url = url
        #
        #     if self.processar_noticia(url=url, set_name=set_name, method=method):
        #         print(f'Url inserida no Redis {url}')
        #     else:
        #         ch.basic_publish(
        #             exchange=self.__exchange_dlx,
        #             routing_key=self.__dlq_queue,
        #             body=url,
        #             properties=pika.BasicProperties(delivery_mode=2)
        #         )
        #
        #     ch.basic_ack(delivery_tag=method.delivery_tag)
        # else:
        #     print(f'url já foi adicionada {url}')

    def rodar(self):
        canal = self.configurar_fila()
        try:
            canal.basic_consume(queue=self.__nome_fila, on_message_callback=self.callback)
            canal.start_consuming()
        except KeyboardInterrupt:
            canal.stop_consuming()
            self.__conexao.close()


if __name__ == '__main__':
    nome_fila = sys.argv[1]
    servico_web_scraping = WebScrapingG1(url=None, parse="html.parser")
    arquivo = ArquivoDOCX()
    notica_worker = NoticiaTrabalhador(
        nome_fila=nome_fila,
        servico_web_scraping=servico_web_scraping,
        consuta=ScriptMongoDB()
    )
    notica_worker.rodar()
