from pika.adapters.blocking_connection import BlockingChannel


class ConfiguracaoDLX:
    def __init__(self, exchange_dlx: str = 'dead_letter_exchange'):
        self.__exchange_dlx = exchange_dlx
        print('DLX INICIALIZADO')

    def criar_fila_dlx(self, nome_fila: str, canal: BlockingChannel):
        fila_dlq = f"{nome_fila}_dead_letter"


        canal.exchange_declare(
            exchange=self.__exchange_dlx,
            exchange_type='direct',
            durable=True
        )


        canal.queue_declare(
            queue=fila_dlq,
            durable=True,
            arguments={"x-message-ttl": 60000}
        )


        canal.queue_bind(
            exchange=self.__exchange_dlx,
            queue=fila_dlq,
            routing_key=fila_dlq
        )


        args = {
            "x-dead-letter-exchange": self.__exchange_dlx,
            "x-dead-letter-routing-key": fila_dlq
        }

        canal.queue_declare(queue=nome_fila, durable=True, arguments=args)
