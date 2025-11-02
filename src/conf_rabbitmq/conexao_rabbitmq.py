import pika
from pika.exceptions import AMQPConnectionError
from src.config.config import Config


class ConexaoRabbitMq:

    def __init__(self):

        self.__credenciais = pika.PlainCredentials(Config.USR_RABBITMQ, Config.PWD_RABBITMQ)
        self.__parametros_conexao = pika.ConnectionParameters(
            host=Config.URL_RABBITMQ,
            port=Config.PORTA_RABBITMQ,
            virtual_host=Config.VIRTUAL_HOST_RABBITMQ,
            credentials=self.__credenciais
        )
        self.conexao = None  # Armazena a instância da conexão

    def __enter__(self):
        """
        Método chamado ao entrar no bloco 'with'.
        É aqui que a conexão é estabelecida.
        """
        try:
            self.conexao = pika.BlockingConnection(self.__parametros_conexao)
            return self.conexao
        except AMQPConnectionError as e:

            print(f"Erro ao conectar ao RabbitMQ: {e}")
            raise  # Propaga a exceção para quem chamou

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Método chamado ao sair do bloco 'with'.
        Garante que a conexão seja fechada.
        """

        if self.conexao and self.conexao.is_open:
            self.conexao.close()
