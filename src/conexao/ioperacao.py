from abc import ABC, abstractmethod
from typing import Dict


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro(self, chave: str, dados: Any):
        pass