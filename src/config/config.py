import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class Config:
    URL_RABBITMQ: Final[str] = os.environ['URL_RABBITMQ']
    PORTA_RABBITMQ: Final[int] = os.environ['PORTA_RABBITMQ']
    USR_RABBITMQ: Final[str] = os.environ['USR_RABBITMQ']
    PWD_RABBITMQ: Final[str] = os.environ['PWD_RABBITMQ']
    VIRTUAL_HOST_RABBITMQ: Final[str] = os.environ['VIRTUAL_HOST_RABBITMQ']
    URL_REDIS: Final[str] = os.environ['URL_REDIS']
    PORTA_REDIS: Final[str] = os.environ['PORTA_REDIS']
    USR_REDIS: Final[str] = os.environ['USR_REDIS']
    SENHA_REDIS: Final[str] = os.environ['SENHA_REDIS']
    DB_REDIS: Final[int] = os.environ['DB']
    URL_MONGODB: Final[str] = os.environ['URL_MONGODB']
    MONGODB_DOCUMENTO: Final[str] = os.environ['MONGODB_DOCUMENTO']
    MONGODB_COLECAO: Final[str] = os.environ['MONGODB_COLECAO']
