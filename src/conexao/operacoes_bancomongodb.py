from typing import Dict, Union, Optional, Any

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
    def gravar_registro(self, dados: Dict[str, str], chave: Optional[Union[int, str]] = None):
        filtro = {"id_site": chave}

        self.__colecao.update_one(
            filtro,
            {"$push": {"noticias": {"$each": dados.get("noticias", [])}}},
            upsert=True
        )

    @override
    def enviar_url_processada(self, chave: str, params: Dict[str, Any]) -> None:
        return None

    @override
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        return False

    @override
    def deletar_hset_por_url(self, url: str) -> int:
        return 1
