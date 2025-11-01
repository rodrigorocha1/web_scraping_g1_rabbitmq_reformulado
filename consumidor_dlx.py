import sys

import pika

from src.config.config import Config


class ConsumidorDLX:
    """
    Consumidor que apenas consome mensagens de uma fila DLX já existente.
    Não recria nem altera a configuração da fila.
    """

    def __init__(self, nome_fila_base: str):
        self.__parametros_conexao = pika.ConnectionParameters(
            host=Config.URL_RABBITMQ,
            port=Config.PORTA_RABBITMQ,
            virtual_host=Config.VIRTUAL_HOST_RABBITMQ,
            credentials=pika.PlainCredentials(Config.USR_RABBITMQ, Config.PWD_RABBITMQ)
        )
        self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
        self.__canal = self.__conexao.channel()

        # Nome da fila DLX já existente
        self.__fila_dlq = f"{nome_fila_base}_dead_letter"

        print(f"[OK] Conectado ao RabbitMQ. Consumindo da DLX: {self.__fila_dlq}")

    def consumir(self):
        def callback(ch, method, properties, body):
            url = body.decode()


            print(f"[DLX] Mensagem recebida: {body.decode()}")

            ch.basic_ack(delivery_tag=method.delivery_tag)


        self.__canal.basic_consume(
            queue=self.__fila_dlq,
            on_message_callback=callback,
            auto_ack=False
        )

        print("[*] Aguardando mensagens na DLX...")
        self.__canal.start_consuming()


if __name__ == "__main__":
    nome_fila = sys.argv[1]
    consumidor = ConsumidorDLX(nome_fila_base=nome_fila)
    consumidor.consumir()
