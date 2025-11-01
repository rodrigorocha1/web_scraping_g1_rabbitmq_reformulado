from datetime import datetime

from bs4 import BeautifulSoup

from enuns.enum_status import EnumStatus
from src.conexao.ioperacao import IOperacao
from src.models.noticia import Noticia
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia


class ProcessoEtl:
    def __init__(self, servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador]):
        self.__servico_web_scraping = servico_web_scraping

    def enviar_noticia(self, url: str, nome_fila: str, conexao_log: IOperacao):
        self.__servico_web_scraping.url = url


        texto_noticia = url.split('/')[-1].split('.')[-2]
        chave = f'log:g1:{nome_fila}:{texto_noticia}'
        data_agora = datetime.now()
        data_formatada = data_agora.strftime("%d-%m-%Y %H:%M:%S")
        dados = {
            'url': url,
            'status': EnumStatus.PROCESSADO.name,
            'data_envio': data_formatada

        }

        conexao_log.gravar_registro(chave=chave, dados=dados)
