import sys
from typing import List, Dict

import pika
from bs4 import BeautifulSoup
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties

from src.conexao.conexao_redis import OperacaoRedis
from src.conexao.ioperacao import IOperacao
from src.conexao.operacoes_bancomongodb import OperacoesBancoMongoDB
from src.conf_rabbitmq.configuacao_dlx import ConfiguracaoDLX
from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco
from src.scripts_banco.script_mongo_db import ScriptMongoDB
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia

from src.config.config import Config


class NoticiaTrabalhador:

    def __init__(
            self,
            nome_fila: str,
            servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
            script_banco: IScriptBanco,
            conexao_banco: IOperacao
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
        self.__conexao_redis = OperacaoRedis()
        self.__exchange_dlx = 'dead_letter_exchange'
        self.__dlq_queue = f'{nome_fila}_dead_letter'
        self.__scripts_banco = script_banco
        self.__conexao_banco = conexao_banco
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
                    id_site = self.__escolha_id_site()
                    consulta = self.__scripts_banco.realizar_insercao_lote(id_site=id_site, param=noticia)
                    self.__lote.append(consulta)
                    if len(self.__lote) >= self.__tamanho_lote:
                        self.__conexao_banco.gravar_registro(chave=id_site, dados=self.__lote)
                        self.__lote.clear()

            return True
        except:
            return False

    def __escolha_id_site(self) -> int:
        match self.__nome_fila:
            case 'fila_g1_ribeirao_preto':
                return 1
            case 'fila_g1_para':
                return 2
            case 'fila_g1_tecnologia':
                return 3
            case _:
                raise ValueError(f"Fila desconhecida: {self.__nome_fila}")

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        url = body.decode()

        self.__servico_web_scraping.url = url
        noticia_processada = self.processar_noticia(url=url, set_name='a', method=method)
        print(noticia_processada)
        ch.basic_ack(delivery_tag=method.delivery_tag)

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

    notica_worker = NoticiaTrabalhador(
        nome_fila=nome_fila,
        servico_web_scraping=servico_web_scraping,
        script_banco=ScriptMongoDB(),
        conexao_banco=OperacoesBancoMongoDB()
    )
    notica_worker.rodar()
