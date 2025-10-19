
from bs4.element import ResultSet
import re
from typing import List


class Tratamento:

    def limpar_descricao(self, textos: ResultSet) -> str:
        """
        Método para limpar o texto da notícia e criar parágrafos a cada ponto.

        Args:
            textos (ResultSet): Conteúdo do texto HTML da notícia, lista de elementos Tag.

        Returns:
            str: Texto limpo, com parágrafos separados por pontos.
        """
        lista_texto: List[str] = []

        for elemento in textos:
            if (not elemento.find('ul') and
                not elemento.find('div', class_='content-intertitle') and
                "LEIA TAMBÉM:" not in (elemento.text or '')):
                texto_extraido = (elemento.text or '').strip()
                lista_texto.append(texto_extraido)

        padroes_a_remover = [
            r'✅\s*Clique aqui para seguir o canal do g1 Ribeirão e Franca no WhatsApp',
            r'Veja mais notícias da região no g1 Ribeirão Preto e Franca',
            r'VÍDEOS: Tudo sobre Ribeirão Preto, Franca e região',
            r'Veja mais notícias da região no g1 Ribeirão e Franca',
            r'LEIA\s+TAMBÉM:?'

        ]

        texto_completo = '\n\n'.join(lista_texto)

        texto_limpo = texto_completo
        for padrao in padroes_a_remover:
            texto_limpo = re.sub(padrao, '', texto_limpo, flags=re.IGNORECASE)

        return texto_limpo
