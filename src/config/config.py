from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    URL_FILA = os.environ['URL_FILA']
    USR_FILA = os.environ['USR_FILA']
    PORTA_FILA = os.environ['PORTA_FILA']
    PASSWD_FILA = os.environ['PASSWD_FILA']

    URL_REDIS = os.environ['URL_REDIS']
    PORTA_REDIS = os.environ['PORTA_REDIS']
    DB_REDIS = os.environ['DB']
    USR_REDIS = os.environ['USR_REDIS']
    SENHA_REDIS = os.environ['SENHA_REDIS']
