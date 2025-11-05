import pika
from pika.adapters.blocking_connection import BlockingChannel

from src.config.config import Config


class ConexaoRabbitMq:

    def __init__(self):

        self.__credenciais = pika.PlainCredentials(
            Config.USR_RABBITMQ, Config.PWD_RABBITMQ
        )

        self.__parametros_conexao = pika.ConnectionParameters(
            host=Config.URL_RABBITMQ,
            port=Config.PORTA_RABBITMQ,
            virtual_host=Config.VIRTUAL_HOST_RABBITMQ,
            credentials=self.__credenciais,
            heartbeat=600,  # mantém a conexão viva
            blocked_connection_timeout=300
        )

        self.__conexao = None
        self.__canal = None

    def conectar(self) -> BlockingChannel:

        if not self.__conexao or self.__conexao.is_closed:
            self.__conexao = pika.BlockingConnection(self.__parametros_conexao)
            print("✅ Conexão com RabbitMQ estabelecida.")

        if not self.__canal or self.__canal.is_closed:
            self.__canal = self.__conexao.channel()
            print("✅ Canal RabbitMQ criado.")

        return self.__canal

    def fechar(self):

        if self.__canal and self.__canal.is_open:
            self.__canal.close()
            print("🔒 Canal RabbitMQ fechado.")

        if self.__conexao and self.__conexao.is_open:
            self.__conexao.close()
            print("🔒 Conexão RabbitMQ fechada.")

    @property
    def conexao(self):
        return self.__conexao

    @property
    def canal(self):
        return self.__canal
