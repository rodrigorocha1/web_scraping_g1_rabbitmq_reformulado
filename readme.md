# Reformulação Web Scraping Distribuído com RabbitMQ + Python + MongoDB

O objetivo do projeto é propor um sistema distribuído de coleta e armazenamento de dados do **G1 RSS** e salvar no **MongoDB**.

**Autor:** Rodrigo  
**Data:** 04/11/2025  

![Thumbnail](./assets/img/posts/refomulacao_web_scrapping_rabbitmq/thumb.png)

## 🧰 Tecnologias Utilizadas

- **Python 3.11**
- **RabbitMQ**
- **Banco de dados NoSQL de chave-valor:** Redis
- **Banco de dados NoSQL de documentos:** MongoDB

---

## Arquitetura da Solução

### Estrutura do Banco Redis

#### Links Processados

Os links serão guardados em um **conjunto ordenado de strings únicas (ZSET)**, com ordenamento para registrar os históricos de links processados.  
Essa estrutura permite **evitar que o mesmo link seja processado novamente**.

**Exemplo de comando Redis:**

```redis
ZADD links:processados:ribeirao_preto 1697725200 "link_do_site"
```


### Descrição dos Parâmetros

- **`links:processados:ribeirao_preto`** → É a **chave (key)** que identifica de forma única o conjunto de links processados.  
  - Nesse caso, o sufixo `ribeirao_preto` indica que os links pertencem ao site do **G1 da região de Ribeirão Preto**.

- **`1697725200`** → É o **score (pontuação)** que o Redis utiliza para manter os elementos ordenados dentro do conjunto.  
  - Neste exemplo, o valor representa um **timestamp** (número de segundos desde **1º de janeiro de 1970**).

- **`"link_do_site"`** → É o **valor (membro)** armazenado no conjunto, representando o **link da notícia do site G1** que foi processada.



### – Log de cada URL na fila

Os logs de cada URL serão gravados no banco **Redis**, sempre informando se é o **primeiro envio** ou **envio da fila DLX**.  
Cada log será armazenado como um **par de chave-valor (HSET)**, registrando todas as informações relevantes do processamento.

**Exemplo de comando Redis:**

```Redis
url da notícia:
https://g1.globo.com/sp/ribeirao-preto-franca/noticia/2025/10/19/o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp.ghtml

HSET log:g1:ribeirao_preto:o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp \
url "https://g1.globo.com/sp/ribeirao-preto-franca/noticia/2025/10/19/o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp.ghtml" \
status "enviado" \
data "2025-10-19T13:00:00" \
mensagem ""
```

| Campo / Valor       | Descrição                                                                                                                                          |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chave principal** | `log:g1:ribeirao_preto:o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp`<br>Identifica de forma única o log no Redis. |
| **url**             | Armazena o endereço da notícia processada.                                                                                                         |
| **status**          | Indica o estado atual do processamento da notícia.<br>Valores possíveis: `ENVIADO`, `EM_PROCESSO`, `PROCESSADO`, `ERRO_ENVIADO_FILA_DLX`.          |
| **data**            | Representa a data e hora em que o registro foi gravado no Redis, no formato ISO (`YYYY-MM-DDTHH:MM:SS`).                                           |
| **mensagem**        | Campo opcional utilizado para armazenar mensagens adicionais ou erros ocorridos durante o processamento.                                           |



###  Registro de Erro na Fila DLX

Quando o processamento de uma URL falha, ela é encaminhada para a **DLX (Dead Letter Exchange)** do RabbitMQ.  
O **Redis** pode ser utilizado para armazenar o histórico de erros e a contagem de falhas, facilitando o monitoramento e o reprocessamento posterior.

---

#### 📘 Exemplo de comando Redis

```bash
HSET log:g1:ribeirao_preto:o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp:dlx \
url "https://g1.globo.com/sp/ribeirao-preto-franca/noticia/2025/10/19/o-que-se-sabe-sobre-assedio-a-adolescentes-no-transporte-escolar-de-colina-sp" \
status "erro" \
data "2025-10-19T13:00:00" \
mensagem "mensagem de erro da dlx"
```

| Campo        | Descrição                                                                                                              |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **url**      | URL da notícia que apresentou falha no processamento.                                                                  |
| **status**   | Indica o estado atual do processamento. Pode assumir os valores: `EM_PROCESSO`, `PROCESSADO`, `ERRO_ENVIADO_FILA_DLX`. |
| **data**     | Data e hora do registro do erro no Redis (ISO 8601).                                                                   |
| **mensagem** | Mensagem opcional contendo detalhes do erro ocorrido.                                                                  |



🔁 Reprocessamento

Quando o reprocessamento da URL for feito com sucesso, o registro correspondente deve ser removido da lista de logs de erro no Redis, garantindo que apenas erros pendentes permaneçam registrados.



##  📌 Requisitos Funcionais

- **RF1** – O sistema deve permitir que um componente **Produtor** colete links RSS e publique tarefas de scraping em uma fila **RabbitMQ**.  
- **RF2** – O sistema deve suportar **múltiplas filas** para diferentes fontes de notícias.  
- **RF3** – O sistema deve permitir **reprocessamento** de mensagens.

---

##  ⚙️ Requisitos Não Funcionais

- **RNF1** – O sistema deve permitir **adicionar novos workers dinamicamente**, sem a necessidade de parar o sistema.  
- **RNF2** – O sistema deve ser **executável via Docker Compose**, em qualquer ambiente.  
- **RNF3** – Caso o sistema falhe, a **mensagem deve permanecer na fila** até que outro consumidor assuma o processamento.


###  – 📐 Diagrama de Classes

<div style="text-align: center;">
  <img 
    src="https://github.com/rodrigorocha1/web_scraping_g1_rabbitmq_reformulado/blob/master/docs/diagrama_clase_v2.png?raw=true"
    alt="Diagrama de classe"
    style="width: 1200px; max-width: 100%; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); margin-bottom: 30px;"
  />
</div>  

<div >

</div>  

A figura acima mostra o diagrama de classes.  
É importante destacar a **modularidade do código**, ou seja, podemos adicionar ou remover **serviços de extração de dados** e **serviços de banco de dados** sem interferir no funcionamento do código.

[![Assistir ao vídeo de demonstração do projeto](https://img.shields.io/badge/🎬%20Assistir%20ao%20vídeo-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/JLkdLCLx3kc)