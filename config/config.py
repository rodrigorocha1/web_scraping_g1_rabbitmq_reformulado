import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    URL_RABBITMQ = os.environ['URL_RABBITMQ']
    PORTA_RABBITMQ = os.environ['PORTA_RABBITMQ']
    USR_RABBITMQ = os.environ['USR_RABBITMQ']
    PWD_RABBITMQ = os.environ['PWD_RABBITMQ']
    VIRTUAL_HOST_RABBITMQ = os.environ['VIRTUAL_HOST_RABBITMQ']
