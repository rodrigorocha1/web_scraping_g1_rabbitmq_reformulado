import pytest
from datetime import datetime
from src.models.noticia import Noticia

@pytest.fixture
def noticia_exemplo():
    return Noticia(
        id_noticia="123",
        titulo="Título Exemplo",
        subtitulo="Subtítulo Exemplo",
        autor="Autor Exemplo",
        data_hora=datetime(2024, 7, 1, 14, 30),
        texto="Texto da notícia para teste."
    )



