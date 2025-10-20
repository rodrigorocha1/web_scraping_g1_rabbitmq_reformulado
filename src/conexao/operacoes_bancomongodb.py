from typing import Dict, List, override

from pymongo import MongoClient

from src.conexao.ioperacao import IOperacao
from src.config.config import Config


class OperacoesBancoMongoDB(IOperacao):

    def __init__(self):
        self.__mongo = MongoClient(Config.URL_MONGODB)  # url mongo
        self.__db = self.__mongo[Config.MONGODB_DOCUMENTO]  # Documento
        self.__colecao = self.__db[Config.MONGODB_COLECAO]  # colecao

    @override
    def gravar_registro(self, chave: str, dados: List[Dict[str, str]]):
        with self.__mongo:
            self.__colecao.insert_many(dados)
