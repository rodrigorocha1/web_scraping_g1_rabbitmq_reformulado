from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# Título, subtítulo, texto, autor, data e hora.

@dataclass
class Noticia:
    id_noticia: str
    titulo: str
    subtitulo: str
    autor: str
    data_hora: Optional[datetime]
    texto: Optional[str] = None
