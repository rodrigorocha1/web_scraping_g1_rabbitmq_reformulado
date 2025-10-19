E TABLE IF NOT EXISTS logs (
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    
    logger_name TEXT NOT NULL,
    filename TEXT NOT NULL,
    func_name TEXT NOT NULL,
    
    line_no INTEGER NOT NULL,
    url TEXT  ,
    mensagem_de_excecao_tecnica TEXT ,
    
    requisicao TEXT,
    status_code INTEGER
);


SELECT *
FROM logs
ORDER By 1 DESC;




