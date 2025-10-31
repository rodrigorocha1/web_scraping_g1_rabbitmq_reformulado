from abc import ABC, abstractmethod
from typing import Any


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro(self, chave: int, dados: Any):
        pass