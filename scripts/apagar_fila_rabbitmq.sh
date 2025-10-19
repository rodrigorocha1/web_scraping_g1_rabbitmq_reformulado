#!/bin/bash

# Verifica se o nome do container foi fornecido
if [ -z "$1" ]; then
    echo "Uso: $0 nome do container não foi fornecido"
    exit 1
fi

RABBITMQ_CONTAINTER="$1"

echo "Apagando $1"

if [ ! "$(docker ps -q -f name=$RABBITMQ_CONTAINTER)" ]; then
    echo "O Container $RABBITMQ_CONTAINTER não está rodando"
    exit 1
fi

FILAS=$(docker exec -it $RABBITMQ_CONTAINTER rabbitmqctl list_queues -q | awk '{print $1}')

for FILA in $FILAS; do
  echo  "Deletando fila: @FILA"
  docker exec -it $RABBITMQ_CONTAINTER rabbitmqctl delente_queue "$FILA"
done

echo "Todas as filas deletadas"