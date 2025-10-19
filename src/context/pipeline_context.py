from typing import Optional, Generic, TypeVar, List, Tuple
from src.models.noticia import Noticia

R1 = TypeVar('R1')


class PipelineContext(Generic[R1]):

    def __init__(self):

        self.rss: Optional[R1] = None
        self.noticia_g1_nao_cadastrada: List[Tuple[str, Noticia]] = []
        self.noticia_g1: List[Tuple[str, Noticia]] = []
