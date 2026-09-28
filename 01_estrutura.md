# Organização dos dados — Entrega 02

Aluno: Rafael Maia.
Projeto Aplicado I — Schulz S.A. — 2026.2.

O banco deste trabalho organiza os dados usados nas medições do dispositivo de controle.
Ele foi dividido em três tabelas, como solicitado no roteiro: técnico/solicitante, equipamento e medição.
A primeira tabela se chama tecnico_solicitante e guarda o nome, o tipo e o setor do responsável.
O campo tipo diferencia um técnico de um solicitante, que pode ser um setor da empresa.
Assim, Usinagem I pode ser cadastrada como solicitante, sem ser tratada como uma pessoa que realizou a medição.
Cada responsável recebe um id, usado para ligar seu cadastro às medições.
O nome não é usado como chave, porque pessoas diferentes podem ter o mesmo nome.
O técnico e o solicitante usam registros separados, mesmo ficando na mesma tabela.
Na tabela equipamento ficam o código, a descrição, o modelo, o fabricante e o número de série.
Ela também guarda a resolução e sua unidade quando essas informações estão disponíveis.
O código do equipamento é texto, pois uma identificação como 703.1208 não representa um número para cálculo.
Esse código é único no cadastro e evita criar duas fichas para o mesmo equipamento.
Na tabela medicao fica uma linha para cada leitura recebida da máquina.
Cada linha contém parâmetro, repetição, valor nominal, tolerâncias, valor obtido, unidade e status.
O campo equipamento_id é uma chave estrangeira que aponta para o equipamento medido.
Os campos tecnico_id e solicitante_id apontam para os responsáveis cadastrados na primeira tabela.
Um equipamento pode ter várias medições, mas cada medição pertence a um único equipamento.
Um técnico pode estar relacionado a várias medições, assim como um solicitante pode solicitar várias delas.
Essas ligações são relações de um para muitos, também chamadas de 1:N.
Na amostra existem 14 parâmetros, com duas leituras cada, totalizando 28 registros de medição.
As duas leituras continuam separadas, inclusive quando têm exatamente o mesmo valor.
O campo codigo_execucao agrupa as leituras de um mesmo atendimento sem criar uma quarta tabela.
Uma nova execução deve receber outro código para preservar as medições anteriores.
A combinação de execução, parâmetro e repetição é única, impedindo a gravação repetida da mesma leitura.
Os nomes dos responsáveis e a descrição do equipamento ficam em seus cadastros, evitando copiá-los em todas as medições.
Isso reduz erros como escrever o mesmo nome de duas formas ou corrigir a descrição em apenas parte das linhas.
O cadastro do equipamento pode ser consultado por uma ligação com as medições, usando JOIN no SQL.
A média e o erro são calculados nas consultas a partir das leituras; não são guardados como outra cópia do resultado.
O desvio informado pela planilha é mantido para permitir a comparação com o desvio calculado.
Arquivo, aba, linha e código da MMC são guardados junto da leitura para localizar sua origem.
O status REGISTRADO informa que o dado entrou no banco; CONFERIDO identifica uma conferência posterior.
Esses status não indicam aprovação metrológica nem liberação de um certificado.
As chaves estrangeiras ficam ativas em cada conexão por meio de PRAGMA foreign_keys = ON.
Com isso, não é possível salvar uma medição que aponte para um equipamento inexistente.
Também não é possível excluir um cadastro que ainda esteja ligado a medições.
Regras adicionais conferem datas, valores obrigatórios, repetições e os papéis dos responsáveis.
Como o roteiro limita o modelo a três tabelas, a data e o código da execução aparecem em mais de uma leitura.
Essa é uma simplificação desta etapa; cadastros de pessoas e equipamentos continuam separados dos resultados.
Para guardar a execução completa, o script grava suas 28 leituras em uma única transação.
Se a gravação falhar, a transação é desfeita e não deixa apenas parte da importação no banco.

## Dados usados no exemplo

As leituras vieram de Registro MMC (1).xlsx, aba Report, linhas 14 a 27 e 29 a 42.
O técnico foi mantido como aparece nesse relatório: José A. Rosa Jr.
O equipamento 703.1208 e o solicitante Usinagem I vieram da planilha preenchida da Entrega 01.
A ligação desses cadastros às leituras foi usada como demonstração do modelo.
A data guardada é 13/08/2026, que aparece no relatório da máquina, e não a data de outro cadastro.
A MMC de origem continua como 500008; o código diferente encontrado na outra planilha não foi colocado no lugar dela.
Fabricante e número de série sem informação foram gravados como NULL, sem inventar valores.
O arquivo dados_amostra.csv contém somente os campos usados na importação desta etapa.
Não foi fornecido um novo script Python junto do roteiro; o arquivo 04_importar.py foi preparado para ler essa amostra.
O dicionário descreve todos os campos das três tabelas e identifica quais são lidos ou criados pelo script.
