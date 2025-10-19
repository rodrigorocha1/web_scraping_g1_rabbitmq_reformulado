from enum import Enum

class EnumStatus(Enum):
    EM_PROCESSO=1
    PROCESSADO=2
    ERRO_ENVIADO_FILA_DLX=3


if __name__ == '__main__':
    # Acessando pelo nome
    print(EnumStatus.PROCESSADO)

    # Ou acessando pelo valor
    es = EnumStatus(2)
    print(es, es.name, es.value)