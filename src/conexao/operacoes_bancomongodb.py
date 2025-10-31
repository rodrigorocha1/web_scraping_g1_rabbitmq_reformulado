from typing import Dict, Any, Union

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
    def gravar_registro(self, dados: Dict[str, Any], chave: Union[int, str] = None):
        filtro = {"id_site": chave}

        self.__colecao.update_one(
            filtro,
            {"$push": {"noticias": {"$each": dados.get("noticias", [])}}},
            upsert=True
        )


    @override
    def enviar_url_processada(self, chave: str, params: Dict):
        pass

    @override
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        pass


if __name__ == '__main__':
    o = OperacoesBancoMongoDB()
    from datetime import datetime

    dados = {
        'id_site': "1",
        'noticias': [
            {
                'id_noticia': 'd5dd0645c7791433694d8180a129859e',
                'titulo': 'Incêndio em pátio credenciado ao Detran em Jaboticabal destruiu ao menos 300 veículos, estima dono',
                'autor': 'Por EPTV e g1 Ribeirão e Franca',
                'data_hora': datetime(2025, 10, 30, 23, 8, 14, 714581),
                'texto': 'Incêndio atingiu pátio credenciado pelo Detran em Jaboticabal (SP)...'
            }
        ]
    }
    o.gravar_registro(dados=dados)
