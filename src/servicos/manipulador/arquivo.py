import os
from abc import ABC, abstractmethod
from typing import Optional

from src.models.noticia import Noticia


class Arquivo(ABC):
    def __init__(self):
        self._caminho_raiz: str = os.getcwd()
        self._nome_arquivo: Optional[str] = None
        self._noticia: Optional[Noticia] = None
        self._diretorio: Optional[str] = None


    @property
    def caminho_completo(self) -> Optional[str]:
        """
        Retorna o caminho completo juntando raiz, diretório e nome do arquivo.
        Retorna None se algum dos componentes não estiver definido.
        """
        if self._diretorio and self._nome_arquivo:
            return os.path.join(self._caminho_raiz, self._diretorio, self._nome_arquivo)
        return None

    @property
    def diretorio(self) -> Optional[str]:
        return self._diretorio

    @diretorio.setter
    def diretorio(self, diretorio: str):
        self._diretorio = diretorio

    @property
    def nome_arquivo(self) -> Optional[str]:
        """
        ṕorpeties para gerar o nome do arquivo
        :return: nome do arquivo
        :rtype:  Optional[str]
        """
        return self._nome_arquivo

    @nome_arquivo.setter
    def nome_arquivo(self, nome_arquivo: str) -> None:
        """
        Método para setar o nome do arquivo
        :param nome_arquivo: nome do arquivo
        :type nome_arquivo: str
        :return: Nada
        :rtype: None
        """
        self._nome_arquivo = nome_arquivo

    def __call__(self):
        self.reset()

    @property
    def noticia(self) -> Optional[Noticia]:
        """
        Método para retornar a noticia
        :return: noticia
        :rtype: Noticia
        """
        return self._noticia

    @noticia.setter
    def noticia(self, nova_noticia: Noticia) -> None:
        """
        Método para setar a noticia
        :param nova_noticia: noticia nova
        :type nova_noticia: Noticia
        :return: Nada
        :rtype: None
        """
        if not isinstance(nova_noticia, Noticia) and nova_noticia is not None:
            raise TypeError("O atributo noticia deve ser uma instância de Noticia ou None")
        self._noticia = nova_noticia

    @abstractmethod
    def _formatar_titulo(self):
        """
        Método para formatar o título
        :return: Nada
        :rtype: None
        """

    @abstractmethod
    def _formatar_subtitulo(self):
        """
        Método para formatar o subtítulo
        :return: Nada
        :rtype: None
        """
        pass

    @abstractmethod
    def _formatar_autor_data(self):
        """
                Método para formatar o subtítulo
                :return: Nada
                :rtype: None
                """
        pass

    @abstractmethod
    def _formatar_texto(self):
        """
        Método para formatar texto
        :return: nada
        :rtype: None
        """
        pass

    @abstractmethod
    def gerar_documento(self):
        """
        Método parta gerar o arquivo docx
        :return: Nada
        :rtype: None
        """
        pass

    def reset(self) -> None:
        """
        Método para resetar o objeto
        :return: Nada
        :rtype: None
        """
        self._caminho_raiz = os.getcwd()
        self._diretorio = None
        self._nome_arquivo = None
        self._noticia = None
