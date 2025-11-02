import sys

from pika.exceptions import AMQPConnectionError

from src.conexao.conexao_redis import OperacaoRedis
from src.conexao.ioperacao import IOperacao
from src.conexao.operacoes_bancomongodb import OperacoesBancoMongoDB
from src.conf_rabbitmq.conexao_rabbitmq import ConexaoRabbitMq
from src.processo_etl.processo_etl import ProcessoEtl
from src.scripts_banco.iscript_banco import IScriptBanco
from src.scripts_banco.script_mongo_db import ScriptMongoDB
from src.servicos.extracao.webscrapingsiteg1 import WebScrapingG1


class ConsumidorDLX:

    def __init__(
            self,
            nome_fila: str,
            conexao_banco: IOperacao,
            script_banco: IScriptBanco,
            conexao_log: IOperacao
    ):

        self.__conexao = ConexaoRabbitMq()
        self.__nome_fila = nome_fila
        self.__conexao_log = conexao_log
        self.__chave_links_processados = f'links:processados:{self.__nome_fila.replace("fila_g1_", "")}'
        self.__chave_links_erros = f'log:g1:erro_dlx:{nome_fila}'

        self.__fila_dlq = f"{nome_fila}_dead_letter"
        self.__processo_etl = ProcessoEtl(
            servico_web_scraping=servico_web_scraping,
            conexao_banco=conexao_banco,
            script_banco=script_banco,
            conexao_log=self.__conexao_log
        )

        print(f"[OK] Conectado ao RabbitMQ. Consumindo da DLX: {self.__fila_dlq}")

    def consumir(self):

        def callback(ch, method, properties, body):
            url = body.decode()

            print(f"[DLX] Mensagem recebida: {body.decode()}")

            flag = self.__processo_etl.processar_noticia(
                url=url,
                nome_fila=self.__nome_fila,  # <-- CORRIGIDO: deve usar self.
                chave_links_processados=self.__chave_links_processados
            )[0]

            if flag:
                self.__conexao_log.deletar_log_erro(url=url)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        try:

            with self.__conexao as conexao:

                canal = conexao.channel()

                canal.basic_consume(
                    queue=self.__fila_dlq,
                    on_message_callback=callback,
                    auto_ack=False
                )

                print(f"[*] Aguardando mensagens na DLX: {self.__fila_dlq}...")

                canal.start_consuming()

        except AMQPConnectionError as e:
            print(f"[ERRO] Falha ao conectar no RabbitMQ: {e}")
        except KeyboardInterrupt:
            print("\n[INFO] Consumidor interrompido pelo usuário.")

        finally:
            print("[INFO] Conexão com RabbitMQ fechada.")


if __name__ == "__main__":
    nome_fila = sys.argv[1]
    servico_web_scraping = WebScrapingG1(url=None, parse="html.parser")
    consumidor = ConsumidorDLX(
        nome_fila=nome_fila,
        conexao_log=OperacaoRedis(),
        conexao_banco=OperacoesBancoMongoDB(),
        script_banco=ScriptMongoDB()
    )
    consumidor.consumir()
