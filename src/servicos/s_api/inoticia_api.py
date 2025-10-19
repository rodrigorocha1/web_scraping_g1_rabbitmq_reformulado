from abc import abstractmethod, ABC
from typing import Union, Tuple

from src.models.noticia import Noticia


class INoticiaApi(ABC):

    @abstractmethod
    def checar_conexao(self) -> bool:
        """
        Método para checar a conexão
        :return: Verdadeiro se a conexão da api for feita com sucesso, falso caso contrário
        :rtype: str
        """
        pass

    @abstractmethod
    def salvar_dados(self, noticia: Noticia):
        """
        Método para salvar dados na api
        :param noticia: Recebe o objeto Noticia
        :type noticia: Noticia
        :return: Nada
        :rtype: None
        """
        pass

    @abstractmethod
    def consultar_dados_id(self, id_noticia) -> Union[Tuple[Noticia, bool], bool]:
        """
        método para consultar a noticia pelo id
        :param id_noticia: id da noticia
        :type id_noticia: str
        :return: Tupla com a noticia e verdadeiro ou pode retornar somente falso
        :rtype: Union[Tuple[Noticia, bool], bool]
        """
        pass

    def realizar_login(self):
        """
        Médodo para realizar login
        :return:
        :rtype:
        """
        raise NotImplementedError
