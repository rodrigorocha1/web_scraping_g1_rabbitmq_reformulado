import datetime
import json
from types import SimpleNamespace
from typing import Union, Tuple

from src.config.config import Config
from src.models.noticia import Noticia
from src.servicos.s_api.inoticia_api import INoticiaApi
import requests
import logging

from src.utils.db_handler import DBHandler

FORMATO = '%(asctime)s %(filename)s %(funcName)s'
db_handler = DBHandler(nome_pacote='NoticiaAPI', formato_log=FORMATO, debug=logging.DEBUG)

logger = db_handler.loger


class NoticiaAPI(INoticiaApi):

    def __init__(self):
        self.__URL_API = Config.URL_API
        self.__USER_API = Config.USER_API
        self.__SENHA_API = Config.SENHA_API
        self.__ACCEPT = Config.CONTENT_TYPE
        self.__header = {
            'accept': self.__ACCEPT
        }
        self.__variaveis = SimpleNamespace()
        self.__variaveis.token = None

    def checar_conexao(self) -> bool:
        """
        Método para checar a conexão da API
        :return: Api sucesso ou falha
        :rtype: bool
        """
        url = self.__URL_API + '/health'
        response = requests.get(url, headers=self.__header, timeout=10)
        try:
            if response.status_code == 200:
                logger.info(
                    msg='Sucesso ao realizar login na API',
                    extra={
                        'status_code': response.status_code,
                        'url': url,
                        'requisicao' : response.text
                    }
                )
                return True
            logger.error(
                msg='Erro ao realizar login na API',
                extra={
                    'status_code': response.status_code,
                    'url': url,
                    'mensagem_de_excecao_tecnica': response.text,
                    'requisicao': response.text
                }
            )
            return False
        except Exception as e:
            logger.error(
                msg='Erro inesperado',
                extra={
                    'mensagem_de_execao_tecnica': e,
                    'url': url
                }
            )
            return False

    def __verificar_token_valido(self) -> bool:
        """
        Método para verificar o token válido
        :return: Verdadeiro so o token for valido
        :rtype: bool
        """
        return self.__variaveis.token is not None

    def __garantir_token(self):
        """
        Método que valida token
        :return: Nada
        :rtype: None
        """
        if not self.__verificar_token_valido():
            self.realizar_login()

    def realizar_login(self):
        """
        Método para realizar o login na api
        :return: Nada
        :rtype: None
        """
        url = self.__URL_API + '/login'
        payload = json.dumps(
            {
                "username": self.__USER_API,
                "senha": self.__SENHA_API
            }
        )
        response = requests.post(url=url, headers=self.__header, timeout=10, data=payload)
        self.__variaveis.token = response.json()['token']

    def salvar_dados(self, noticia: Noticia):
        """
        Método para salvar a noticia
        :param noticia: recebe a noticia
        :type noticia: Noticia
        """
        noticia_dict = noticia.__dict__.copy()

        if isinstance(noticia_dict.get('data_hora'), datetime.datetime):
            noticia_dict['data_hora'] = noticia_dict['data_hora'].isoformat()
        payload = json.dumps(noticia_dict)
        self.__garantir_token()
        token = self.__variaveis.token
        self.__header['Authorization'] = token

        url = self.__URL_API + '/noticias'
        try:
            response = requests.post(url=url, headers=self.__header, data=payload)
            logger.info(
                msg='Sucesso ao cadastrar noticia',
                extra={
                    'url': url,
                    'status_code': response.status_code,
                    'requisicao': response.text
                }
            )
        except requests.RequestException as e:
            logger.error(
                msg='Erro de requisição ',
                extra={
                    'mensagem_de_execao_tecnica': e
                }
            )
            exit()
        except Exception as e:
            logger.warning(
                msg='Erro inesperado de requisição ',
                extra={
                    'mensagem_de_execao_tecnica': e
                }
            )

    def consultar_dados_id(self, id_noticia: str) -> Union[Tuple[Noticia, bool], bool]:
        """
        Método para consultar a no
        :param id_noticia: id da noticia
        :type id_noticia: st
        :return: A noticia
        :rtype: Noticia | str
        """
        url = f'{self.__URL_API}/noticias/{id_noticia}'
        self.__garantir_token()
        token = self.__variaveis.token
        self.__header['Authorization'] = token
        response = requests.get(url, headers=self.__header, )
        try:
            if response.status_code == 200:
                return Noticia(**response.json()), True
            return False
        except:
            return False


if __name__ == '__main__':
    noticia_api = NoticiaAPI()
    noticia = noticia_api.consultar_dados_id(id_noticia='578a50661d5e4fd98670cef1d6c07886')
    if noticia:
        print(1, noticia)
    else:
        print(2, noticia)
    print(noticia)
    # for i in range(0, 6):
    #     noticia = Noticia(
    #         id_noticia=f'{str(i)}',
    #         data_hora=datetime.datetime.now(),
    #         titulo='a',
    #         subtitulo='a',
    #         texto='a',
    #         autor='a'
    #     )
    #     noticia_api.salvar_dados(noticia=noticia)
