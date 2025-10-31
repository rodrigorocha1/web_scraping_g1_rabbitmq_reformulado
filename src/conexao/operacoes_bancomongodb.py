from typing import Dict, List

from pymongo import MongoClient
from typing_extensions import override

from src.conexao.ioperacao import IOperacao
from src.config.config import Config


class OperacoesBancoMongoDB(IOperacao):

    def __init__(self):
        self.__mongo = MongoClient(Config.URL_MONGODB)  # url mongo
        self.__db = self.__mongo[Config.MONGODB_DOCUMENTO]  # Documento
        self.__colecao = self.__db[Config.MONGODB_COLECAO]

    @override
    def gravar_registro(self, dados: List[Dict[str, str]]):
        with self.__mongo:
            self.__colecao.insert_many(dados)


if __name__ == '__main__':
    o = OperacoesBancoMongoDB()
