from abc import abstractmethod, ABC
from typing import TypeVar, Generic, Optional

T = TypeVar('T')
U = TypeVar('U')

class IWebScapingBase(ABC, Generic[T, U]):

    @property
    @abstractmethod
    def url(self) -> str:
        """
        Propriedade que retorna a URL atual.
        """
        pass

    @url.setter
    @abstractmethod
    def url(self, url: str) -> None:
        """
        Método porpeties para tratar a url

        :param url: url de conexão
        :type url: str
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def abrir_conexao(self) -> Optional[T]:
        """
        Método que vai representar a conexão do web scraping
        :return: Objeto de conexão
        :rtype: T
        """
        pass

    @abstractmethod
    def obter_dados(self, dados: T) -> U:
        """
        Método genérico pra obter os dados do web scrapinb
        :param dados: o objeto de dados de conexão
        :type dados: T
        :return: dados da extração
        :rtype: U
        """
        pass
