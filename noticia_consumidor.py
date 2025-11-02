import sys
from datetime import datetime

import pika
from bs4 import BeautifulSoup
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties

from enuns.enum_status import EnumStatus
from src.conexao.conexao_redis import OperacaoRedis
from src.conexao.ioperacao import IOperacao
from src.conexao.operacoes_bancomongodb import OperacoesBancoMongoDB
from src.conf_rabbitmq.conexao_rabbitmq import ConexaoRabbitMq
from src.conf_rabbitmq.configuacao_dlx import ConfiguracaoDLX
from src.models.noticia import Noticia
from src.processo_etl.processo_etl import ProcessoEtl
from src.scripts_banco.iscript_banco import IScriptBanco
from src.scripts_banco.script_mongo_db import ScriptMongoDB
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia


class NoticiaTrabalhador:

    def __init__(
            self,
            nome_fila: str,
            servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
            script_banco: IScriptBanco,
            conexao_banco: IOperacao,
            conexao_log: IOperacao
    ):

        self.__conexao = ConexaoRabbitMq()
        self.__servico_web_scraping = servico_web_scraping
        self.__nome_fila = nome_fila
        self.__conexao_log = conexao_log
        self.__exchange_dlx = 'dead_letter_exchange'
        self.__dlq_queue = f'{nome_fila}_dead_letter'

        self.__processo_etl = ProcessoEtl(
            servico_web_scraping=servico_web_scraping,
            conexao_banco=conexao_banco,
            script_banco=script_banco,
            conexao_log=self.__conexao_log
        )

        self.__dlx = ConfiguracaoDLX(self.__exchange_dlx)
        self.__chave_links_processados = f'links:processados:{self.__nome_fila.replace("fila_g1_", "")}'

    def configurar_fila(self):
        canal = self.__conexao.channel()
        self.__dlx.criar_fila_dlx(nome_fila=self.__nome_fila, canal=canal)
        return canal

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        url = body.decode()
        if not self.__conexao_log.consultar_url_processada(chave=self.__chave_links_processados, link=url):
            self.__servico_web_scraping.url = url
            if self.__processo_etl.processar_noticia(url=url, nome_fila=self.__nome_fila,
                                                     chave_links_processados=self.__chave_links_processados)[0]:
                self.__processo_etl.enviar_noticia(url=url, nome_fila=nome_fila)
            else:
                ch.basic_publish(
                    exchange=self.__exchange_dlx,
                    routing_key=self.__dlq_queue,
                    body=url,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                chave = f'log:g1:erro_dlx:{nome_fila}'
                data_agora = datetime.now()
                data_formatada = data_agora.strftime("%d-%m-%Y %H:%M:%S")
                dados = {
                    'url': url,
                    'status': EnumStatus.EM_PROCESSO.ERRO_ENVIADO_FILA_DLX,
                    'data_envio': data_formatada

                }
                self.__conexao_log.gravar_registro(chave=chave, dados=dados)

            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f'url enviada: {url}')

    def rodar(self):
        canal = self.configurar_fila()
        try:
            canal.basic_consume(queue=self.__nome_fila, on_message_callback=self.callback)
            canal.start_consuming()
        except Exception as e:
            canal.stop_consuming()
            self.__conexao.close()


if __name__ == '__main__':
    nome_fila = sys.argv[1]
    servico_web_scraping = WebScrapingG1(url=None, parse="html.parser")

    notica_worker = NoticiaTrabalhador(
        nome_fila=nome_fila,
        servico_web_scraping=servico_web_scraping,
        script_banco=ScriptMongoDB(),
        conexao_banco=OperacoesBancoMongoDB(),
        conexao_log=OperacaoRedis()
    )
    notica_worker.rodar()
