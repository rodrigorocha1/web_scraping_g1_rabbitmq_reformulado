from typing import Optional, Dict
from src.config.config import Config
import redis
import hashlib


class ConexaoRedis:

    def __init__(self):
        self.__host = Config.URL_REDIS
        self.__port = Config.PORTA_REDIS
        self.__db = Config.DB_REDIS
        self.__cliente_redis = redis.Redis(
            host=self.__host,
            port=self.__port,
            db=self.__db,
            decode_responses=True
        )


    def e_membro(self, set_name: str, valor: str) -> bool:
        return bool(self.__cliente_redis.sismember(set_name, valor))

    def adicionar_set(self, set_name: str, valor: str, ttl_seconds: Optional[int] = None):
        self.__cliente_redis.sadd(set_name, valor)
        print('Set adicionado')
        if ttl_seconds:
            aux_key = f"ttl:{set_name}:{valor}"
            self.__cliente_redis.setex(aux_key, ttl_seconds, "1")


    @staticmethod
    def gerar_hash_id(url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def enviar_noticia(self, url: str, dados: Dict):
        hash_id = self.gerar_hash_id(url)
        self.__cliente_redis.hset(f"noticia:{hash_id}", mapping=dados)
        return hash_id

    def obter_noticia(self, url: str) -> Dict:
        hash_id = self.gerar_hash_id(url)
        return self.__cliente_redis.hgetall(f"noticia:{hash_id}")


    def incrementar_contador(self, nome_contador: str, valor: int = 1):
        self.__cliente_redis.incrby(nome_contador, valor)

    def obter_contador(self, nome_contador: str) -> int:
        value = self.__cliente_redis.get(nome_contador)
        return int(value) if value else 0


    def push_reprocessar(self, url: str):
        self.__cliente_redis.lpush("fila:reprocessar", url)

    def pop_reprocessar(self) -> Optional[str]:
        return self.__cliente_redis.rpop("fila:reprocessar")


    def close(self):
        try:
            self.__cliente_redis.close()
        except Exception:
            pass
