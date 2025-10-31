from typing import Dict

from typing_extensions import override

from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco


class ScriptMongoDB(IScriptBanco):

    @override
    def realizar_insercao_lote(self, id_site: int, noticia: Noticia) -> Dict:
        doc = {
            "id_site": id_site,
            "noticias": [{
                "id_noticia": noticia.id_noticia,
                "titulo": noticia.titulo,
                "autor": noticia.autor,
                "data_hora": noticia.data_hora,
                "texto": noticia.texto
            }]
        }
        return doc
