from typing import Dict

from typing_extensions import override

from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco


class ScriptMongoDB(IScriptBanco):

    @override
    def realizar_insercao_lote(self, id_site: int, param: Noticia) -> Dict:
        doc = {
            "id_site": id_site,
            "noticias": [{
                "id_noticia": param.id_noticia,
                "titulo": param.titulo,
                "autor": param.autor,
                "data_hora": param.data_hora,
                "texto": param.texto
            }]
        }

        return doc
