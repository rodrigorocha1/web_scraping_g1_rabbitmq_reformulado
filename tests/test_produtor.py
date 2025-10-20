# tests/test_produtor.py
from unittest.mock import Mock, patch

import pytest

from enuns.enum_status import EnumStatus
from produtor.produtor import Produtor
from src.conexao.conexao_redis import ConexaoRedis
from src.conf_rabbitmq.configuacao_dlx import ConfiguracaoDLX
from src.servicos.extracao.webscrapingbs4g1rss import WebScrapingBs4G1Rss


class FakeScrapingService(WebScrapingBs4G1Rss):


    def abrir_conexao(self):
        return "<rss>Fake RSS</rss>"

    def obter_dados(self, dados):
        return [
            {"url_rss": "https://g1.globo.com/noticia1.html"},
            {"url_rss": "https://g1.globo.com/noticia2.html"}
        ]


class FakeBanco(ConexaoRedis):
    """Simula gravação no Redis sem acesso real"""

    def __init__(self):
        self.registros = {}

    def gravar_registro(self, chave, dados):
        self.registros[chave] = dados


@pytest.fixture
def produtor_fake():
    scraping = FakeScrapingService(url=None)
    banco_fake = FakeBanco()
    produtor = Produtor(servico_web_scraping=scraping, operacao_banco=banco_fake)
    return produtor, banco_fake


@patch("pika.BlockingConnection")
def test_criar_fila_dlx(mock_connection, produtor_fake):
    """Testa se o DLX cria a fila corretamente"""
    mock_channel = Mock()
    mock_connection.return_value.channel.return_value = mock_channel

    dlx = ConfiguracaoDLX()
    dlx.criar_fila_dlx("teste_fila", mock_channel)

    # Verifica se exchange_declare e queue_declare foram chamados
    mock_channel.exchange_declare.assert_called_with(
        exchange='dead_letter_exchange',
        exchange_type='direct',
        durable=True
    )
    mock_channel.queue_declare.assert_any_call(
        queue='teste_fila_dead_letter',
        durable=True,
        arguments={'x-message-ttl': 60000}
    )
    mock_channel.queue_bind.assert_called()


@patch("pika.BlockingConnection")
def test_produtor_envia_mensagem(mock_connection, produtor_fake):
    """Testa se o produtor tenta publicar mensagens e gravar no banco"""
    produtor, banco_fake = produtor_fake
    mock_channel = Mock()
    mock_connection.return_value.channel.return_value = mock_channel

    urls_rss = {
        'fila_g1_teste': 'https://g1.globo.com/rss/g1/teste/'
    }


    with patch("time.sleep", return_value=None):
        with patch.object(produtor.__class__, "rodar", wraps=produtor.rodar) as rodar_mock:
            try:
                produtor.rodar(urls_rss)
            except KeyboardInterrupt:
                pass  # simula interrupção para sair do loop


    assert mock_channel.basic_publish.call_count > 0


    assert len(banco_fake.registros) > 0
    for chave, dados in banco_fake.registros.items():
        assert dados['status'] == EnumStatus.EM_PROCESSO.name
        assert 'url' in dados
        assert 'data_envio' in dados
