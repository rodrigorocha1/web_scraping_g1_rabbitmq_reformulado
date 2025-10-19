from typing import Dict, List, override

from pymongo import MongoClient

from src.conexao.ioperacao import IOperacao


class OperacoesBancoMongoDB(IOperacao):

    def __init__(self):
        self.__mongo = MongoClient('')  # url mongo
        self.__db = self.__mongo['']  # Documento
        self.__colecao = self.__db['']  # colecao

    @override
    def gravar_registro(self, chave: str, dados: List[Dict[str, str]]):
        self.__colecao.insert_many(dados)
