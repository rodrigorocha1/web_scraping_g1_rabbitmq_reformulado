from abc import ABC, abstractmethod
from typing import Dict

from src.models.noticia import Noticia


class IScriptBanco(ABC):

    @abstractmethod
    def realizar_insercao_lote(self, param: Noticia) -> Dict:
        pass
