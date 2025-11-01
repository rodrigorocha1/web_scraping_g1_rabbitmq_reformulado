# src/tests/test_consumidor_dlx.py
import pytest
from unittest.mock import patch, MagicMock
from consumidor_dlx import ConsumidorDLX

def test_consumidor_dlx_conexao_e_consumo():
    nome_fila_base = "teste_fila"

    # Mock da BlockingConnection e do channel
    with patch("pika.BlockingConnection") as mock_connection:
        mock_chan = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_instance.channel.return_value = mock_chan
        mock_connection.return_value = mock_conn_instance

        # Instancia o consumidor
        consumidor = ConsumidorDLX(nome_fila_base=nome_fila_base)

        # Verifica se o nome da fila DLX está correto
        assert consumidor._ConsumidorDLX__fila_dlq == f"{nome_fila_base}_dead_letter"

        # Mock do método start_consuming para não travar o teste
        mock_chan.start_consuming = MagicMock()

        # Executa o método consumir
        consumidor.consumir()

        # Verifica se basic_consume foi chamado com a fila correta
        mock_chan.basic_consume.assert_called_once()
        args, kwargs = mock_chan.basic_consume.call_args
        assert kwargs["queue"] == f"{nome_fila_base}_dead_letter"
        assert callable(kwargs["on_message_callback"])
        assert kwargs["auto_ack"] is False

        # Verifica se start_consuming foi chamado
        mock_chan.start_consuming.assert_called_once()
