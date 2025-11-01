import sys

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
from src.processo_etl.processo_etl import ProcessoEtl
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
            conexao_banco: IOperacao,
            conexao_log: IOperacao
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
        self.__conexao_log = conexao_log
        self.__exchange_dlx = 'dead_letter_exchange'
        self.__dlq_queue = f'{nome_fila}_dead_letter'
        self.__scripts_banco = script_banco
        self.__conexao_banco = conexao_banco
        self.__processo_etl = ProcessoEtl(servico_web_scraping)
        self.__dlx = ConfiguracaoDLX(self.__exchange_dlx)
        self.__chave_links_processados = f'links:processados:{self.__nome_fila.replace("fila_g1_", "")}'

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
                    score = int(noticia.data_hora.timestamp())
                    params = {
                        'score': score,
                        'valor': url
                    }
                    print(f'Inserindo dados da url {url}')
                    id_site = self.__escolha_id_site()
                    print(f'{id_site}')
                    consulta = self.__scripts_banco.realizar_insercao_lote(id_site=id_site, param=noticia)

                    self.__conexao_banco.gravar_registro(chave=id_site, dados=consulta)
                    self.__conexao_log.enviar_url_processada(chave=self.__chave_links_processados, params=params)

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
        if not self.__conexao_log.consultar_url_processada(chave=self.__chave_links_processados, link=url):
            self.__servico_web_scraping.url = url
            if self.processar_noticia(url=url, set_name='a', method=method):
                self.__processo_etl.enviar_noticia(url=url, nome_fila=nome_fila, conexao_log=self.__conexao_log)

                # print(f'Url enviada: {url}')
                # texto_noticia = url.split('/')[-1].split('.')[-2]
                # chave = f'log:g1:{nome_fila}:{texto_noticia}'
                # data_agora = datetime.now()
                # data_formatada = data_agora.strftime("%d-%m-%Y %H:%M:%S")
                # dados = {
                #     'url': url,
                #     'status': EnumStatus.PROCESSADO.name,
                #     'data_envio': data_formatada
                #
                # }
                #
                # self.__conexao_redis.gravar_registro(chave=chave, dados=dados)




            else:
                ch.basic_publish(
                    exchange=self.__exchange_dlx,
                    routing_key=self.__dlq_queue,
                    body=url,
                    properties=pika.BasicProperties(delivery_mode=2)
                )

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
