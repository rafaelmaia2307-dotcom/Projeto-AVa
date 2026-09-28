PRAGMA foreign_keys = ON;

-- 1. Medições com o equipamento e os dois responsáveis.
SELECT m.codigo_execucao, e.codigo, e.descricao,
       t.nome AS tecnico, s.nome AS solicitante,
       m.data_medicao, m.parametro, m.repeticao,
       m.valor_nominal, m.tolerancia_inferior, m.tolerancia_superior,
       m.valor_obtido, m.unidade, m.status
FROM medicao AS m
JOIN equipamento AS e ON e.id = m.equipamento_id
JOIN tecnico_solicitante AS t ON t.id = m.tecnico_id
JOIN tecnico_solicitante AS s ON s.id = m.solicitante_id
ORDER BY m.codigo_execucao, m.parametro, m.repeticao;

-- 2. As médias são calculadas na consulta para evitar guardar cópias do resultado.
-- A condição HAVING evita apresentar um par incompleto como média de duas leituras.
SELECT codigo_execucao, equipamento_id, parametro, unidade,
       count(*) AS quantidade, avg(valor_obtido) AS media,
       avg(valor_obtido) - valor_nominal AS erro_da_media
FROM medicao
GROUP BY codigo_execucao, equipamento_id, parametro, unidade,
         valor_nominal, tolerancia_inferior, tolerancia_superior
HAVING count(*) = 2 AND count(DISTINCT repeticao) = 2
ORDER BY parametro;

-- 3. Conferência aritmética do desvio informado na origem.
-- 1e-12 é usado apenas para diferenças de representação do tipo REAL.
SELECT parametro, repeticao, linha_origem, desvio_informado,
       valor_obtido - valor_nominal AS desvio_calculado
FROM medicao
WHERE abs(desvio_informado - (valor_obtido - valor_nominal)) > 1e-12
ORDER BY linha_origem;

-- 4. Histórico por equipamento, sem juntar execuções diferentes.
SELECT e.codigo, m.codigo_execucao, m.data_medicao, count(*) AS leituras
FROM equipamento AS e JOIN medicao AS m ON m.equipamento_id=e.id
GROUP BY e.codigo, m.codigo_execucao, m.data_medicao
ORDER BY m.data_medicao, m.codigo_execucao;
