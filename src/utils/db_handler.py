import logging
import sqlite3
from datetime import datetime
import os

from typing import Literal
from colorama import Fore, Style, init

LogLevel = Literal[0, 10, 20, 30, 40, 50]


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.BLUE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{log_color}{message}{Style.RESET_ALL}"


class DBHandler(logging.Handler):
    def __init__(self, nome_pacote: str, formato_log: str, debug: LogLevel):
        super().__init__()
        self.__caminho_base = os.getcwd()
        self.__caminho_arquivo = os.path.join('sqlite:///', self.__caminho_base, 'logs.db')
        self.conn = sqlite3.connect(self.__caminho_arquivo )
        self.cursor = self.conn.cursor()
        self.loger = logging.getLogger(nome_pacote)
        self.__FORMATO_LOG = formato_log
        self.__formater = logging.Formatter(self.__FORMATO_LOG)
        self.setFormatter(self.__formater)
        self.loger.addHandler(self)
        self.loger.setLevel(debug)

        stream_handler = logging.StreamHandler()
        color_formatter = ColorFormatter(self.__FORMATO_LOG)
        stream_handler.setFormatter(color_formatter)
        self.loger.addHandler(stream_handler)

    def emit(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        status_code = getattr(record, 'status_code', None)
        mensagem_de_excecao_tecnica = getattr(record, 'mensagem_de_excecao_tecnica', None)
        requisicao = getattr(record, 'requisicao', None)
        url = getattr(record, 'url', None)
        log_entry = self.format(record)
        self.cursor.execute(
            'INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                timestamp,
                record.levelname,
                record.message,

                record.name,
                record.filename,
                record.funcName,

                record.lineno,
                url,
                mensagem_de_excecao_tecnica,
                requisicao,
                status_code
            )
        )

        self.conn.commit()

    def close(self):
        self.conn.close()
        super().close()


if __name__ == '__main__':
    def teste():
        logger = logging.getLogger('meu_logger_db')
        logger.setLevel(logging.DEBUG)
