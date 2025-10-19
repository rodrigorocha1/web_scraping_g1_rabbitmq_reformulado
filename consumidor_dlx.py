import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from config.config import Config


class ConsumidorDLX:

    def __init__(self, host=Config.URL_RABBITMQ, usuario=Config.USR_RABBITMQ, senha=Config.USR_RABBITMQ):
        self.__conexao = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=Config.PORTA_RABBITMQ,
                virtual_host=Config.VIRTUAL_HOST_RABBITMQ,
                credentials=pika.PlainCredentials(usuario, senha)
            )
        )
        self.__canal = self.__conexao.channel()

    def consumir(self, nome_fila_dlq: str):
        def callback(
                ch: BlockingChannel,
                method: Basic.Deliver,
                properties: BasicProperties,
                body: bytes
        ):
            print(f"[DLX] Mensagem da fila {nome_fila_dlq}: {body.decode()}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.__canal.basic_consume(queue=nome_fila_dlq, on_message_callback=callback)
        print(f"[*] Consumindo fila DLX: {nome_fila_dlq}")
        self.__canal.start_consuming()


if __name__ == '__main__':
    cdlx = ConsumidorDLX()
    cdlx.consumir()
