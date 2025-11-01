from datetime import datetime
from typing import Tuple

from bs4 import BeautifulSoup

from enuns.enum_status import EnumStatus
from src.conexao.ioperacao import IOperacao
from src.models.noticia import Noticia
from src.scripts_banco.iscript_banco import IScriptBanco
from src.servicos.extracao.iwebscrapingbase import IWebScapingBase

TIPO_SCRAPING = BeautifulSoup
DadosG1Gerador = Noticia


class ProcessoEtl:
    def __init__(
            self,
            servico_web_scraping: IWebScapingBase[BeautifulSoup, DadosG1Gerador],
            script_banco: IScriptBanco,
            conexao_banco: IOperacao,
            conexao_log: IOperacao

    ):
        self.__servico_web_scraping = servico_web_scraping
        self.__scripts_banco = script_banco
        self.__conexao_banco = conexao_banco
        self.__conexao_log = conexao_log

    def enviar_noticia(self, url: str, nome_fila: str, ):
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

        self.__conexao_log.gravar_registro(chave=chave, dados=dados)

    def __escolha_id_site(self, nome_fila: str) -> int:
        match nome_fila:
            case 'fila_g1_ribeirao_preto':
                return 1
            case 'fila_g1_para':
                return 2
            case 'fila_g1_tecnologia':
                return 3
            case _:
                raise ValueError(f"Fila desconhecida: {nome_fila}")

    def processar_noticia(self, url: str, chave_links_processados: str, nome_fila: str) -> Tuple[bool, str]:
        try:
            self.__servico_web_scraping.url = url
            dados = self.__servico_web_scraping.abrir_conexao()
            if dados:
                noticia = self.__servico_web_scraping.obter_dados(dados=dados)
                if len(noticia.texto) > 0 or noticia.texto is not None:
                    score = int(noticia.data_hora.timestamp())
                    params = {
                        'score': score,
                        'valor': url
                    }
                    id_site = self.__escolha_id_site(nome_fila=nome_fila)
                    consulta = self.__scripts_banco.realizar_insercao_lote(id_site=id_site, param=noticia)

                    self.__conexao_banco.gravar_registro(chave=id_site, dados=consulta)
                    self.__conexao_log.enviar_url_processada(
                        chave=chave_links_processados,
                        params=params
                    )

            return True, 'Sucesso'
        except Exception as e:
            return False, f'Erro: {str(e)}'
