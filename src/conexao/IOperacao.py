from abc import ABC, abstractmethod
from typing import Dict


class IOperacao(ABC):

    @abstractmethod
    def gravar_registro_log(self, chave: str, dados: Dict[str, str]):
        pass