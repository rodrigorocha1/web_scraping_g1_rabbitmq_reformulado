from abc import ABC, abstractmethod
from typing import Any, Union


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro(self, dados: Any, chave: Union[int, str] = None):
        pass
