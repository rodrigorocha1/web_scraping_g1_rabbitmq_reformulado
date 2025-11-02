from typing import Dict, Union, Optional

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
    def gravar_registro(self, dados: Dict[str, str], chave: Optional[Union[int, str]] = None):
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
    def deletar_log_erro(self, chave: str, url: str) -> int:
        """
        Método para deletar url da chave log
        :param chave: chave do redis
        :type chave: string
        :param url: url a ser deletada
        :type url: string
        :return: 1 se sucesso o 0 se caso contrário
        :rtype: int
        """
        return self.__cliente_redis.hdel(chave, 'url')

    @override
    def enviar_url_processada(self, chave: str, params: Dict):
        """
        Método para gravar a url processada
        :param chave: chave do redis
        :type chave: str
        :param params: composição dos valores
        :type params: Dict
        :return:
        :rtype:
        """
        self.__cliente_redis.zadd(chave, {params['valor']: params['score']}, )
        self.__cliente_redis.expire(chave, self.__tempo_expiracao)  # TTL

    @override
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        """
        Método para verificar se a url já foi enviada
        :param chave:chave do redis
        :type chave: str
        :param link: link do site do g1
        :type link: str
        :return: retorna verdadeiro se não foi enviado ou falso caso contrário
        :rtype: bool
        """
        score = self.__cliente_redis.zscore(chave, link)
        print(score, link)
        if score is not None:
            return True
        return False
