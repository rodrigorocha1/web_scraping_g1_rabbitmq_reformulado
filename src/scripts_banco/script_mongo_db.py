from typing import Dict

from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco


class ScriptMongoDB(IScriptBanco):

    def realizar_insercao_lote(self, noticia: Noticia) -> Dict:
        doc = {
            "id_site": "g1",
            "noticias": [{
                "id_noticia": noticia.id_noticia,
                "titulo": noticia.titulo,
                "autor": noticia.autor,
                "data_hora": noticia.data_hora,
                "texto": noticia.texto
            }]
        }
        return doc
