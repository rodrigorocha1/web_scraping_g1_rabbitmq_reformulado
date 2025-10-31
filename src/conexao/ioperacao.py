from abc import ABC, abstractmethod
from typing import Any, Union, Dict


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro(self, dados: Any, chave: Union[int, str] = None):
        pass

    @abstractmethod
    def enviar_url_processada(self, chave: str, params: Dict):
        pass

    @abstractmethod
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        pass
