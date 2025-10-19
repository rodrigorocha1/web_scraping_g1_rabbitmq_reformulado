from typing import Dict

import redis

from src.conexao.IOperacao import IOperacao
from src.config.config import Config


class ConexaoRedis(IOperacao):

    def __init__(self):
        self.__host = Config.URL_REDIS
        self.__port = Config.PORTA_REDIS
        self.__db = Config.DB_REDIS
        self.__cliente_redis = redis.Redis(
            host=self.__host,
            port=self.__port,
            db=self.__db,
            decode_responses=True
        )
        self.__tempo_expiracao = 604800

    def gravar_registro(self, chave: str, dados: Dict[str, str]):
        """
        Método para gerar o het
        :param chave: chave de gravação
        :type chave: str
        :param dados: dados de gravação
        :type dados:  Dict[str, str]
        :return: None
        :rtype: Data
        """
        self.__cliente_redis.hset(
            chave, mapping=dados,
        )
        self.__cliente_redis.expire(chave, self.__tempo_expiracao)
