from typing import Dict, Union

import redis
from typing_extensions import override

from src.conexao.ioperacao import IOperacao
from src.config.config import Config


class OperacaoRedis(IOperacao):

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

    @override
    def gravar_registro(self, dados: Dict[str, str], chave: Union[int, str] = None):
        """
        Método para gerar o het
        :param chave: chave de gravação
        :type chave: Union[int, str]
        :param dados: dados de gravação
        :type dados:  Dict[str, str]
        :return: None
        :rtype: Data
        """
        self.__cliente_redis.hset(
            chave, mapping=dados,
        )
        self.__cliente_redis.expire(chave, self.__tempo_expiracao)

    @override
    def enviar_url_processada(self, chave: str, params: Dict):
        self.__cliente_redis.zadd(chave, {params['valor']: params['score']}, )
        self.__cliente_redis.expire(chave, self.__tempo_expiracao)  # TTL

    @override
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        score = self.__cliente_redis.zscore(chave, link)
        print(score, link)
        if score is not None:
            return True
        return False
