from abc import ABC, abstractmethod
from typing import Any, Union, Dict, Optional


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro(self, dados: Any, chave: Optional[Union[int, str]] = None):
        pass

    @abstractmethod
    def enviar_url_processada(self, chave: str, params: Dict):
        pass

    @abstractmethod
    def consultar_url_processada(self, chave: str, link: str) -> bool:
        pass

    @abstractmethod
    def deletar_log_erro(self, chave: str, url: str) -> int:
        pass
