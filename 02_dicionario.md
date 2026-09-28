# Dicionário de dados do sistema

Aluno: Rafael Maia.

O dicionário reúne todos os 31 campos das três tabelas. Ele corresponde ao arquivo 03_banco.sql e aos dados usados pelo script 04_importar.py.

Texto corresponde a TEXT; Inteiro corresponde a INTEGER; Real corresponde a REAL no SQLite. As datas usam TEXT no formato AAAA-MM-DD. PK indica chave primária; FK indica chave estrangeira. NULL representa ausência de informação.

Os campos lidos do CSV são convertidos pelo Python. Os ids de cadastro e o código da execução são definidos no script; o id da medição é gerado pelo SQLite. Campos de cadastro vêm da amostra analisada na Entrega 01.

## tecnico_solicitante

| Campo | Tipo no trabalho | Tipo SQLite | Descrição, origem e regra |
| --- | --- | --- | --- |
| id | Inteiro | INTEGER | PK. Identificador do responsável. Os ids 1 e 2 são definidos no cadastro da amostra. |
| nome | Texto | TEXT | Nome da pessoa ou do setor. Obrigatório e não vazio. Ex.: José A. Rosa Jr e Usinagem I. |
| tipo | Texto | TEXT | TECNICO ou SOLICITANTE. Obrigatório. Indica o papel do cadastro. |
| setor | Texto | TEXT | Setor informado no cadastro. Pode ser NULL quando não estiver identificado. |

## equipamento

| Campo | Tipo no trabalho | Tipo SQLite | Descrição, origem e regra |
| --- | --- | --- | --- |
| id | Inteiro | INTEGER | PK. Identificador do equipamento. O script usa 1 para o dispositivo da amostra. |
| codigo | Texto | TEXT | Código único e obrigatório. TAG 703.1208 da planilha preenchida; manter como texto. |
| descricao | Texto | TEXT | Nome obrigatório do equipamento. Ex.: Dispositivo de controle. |
| modelo | Texto | TEXT | Modelo do equipamento. Neste exemplo, Não se aplica, conforme a origem. Aceita NULL. |
| fabricante | Texto | TEXT | Fabricante quando informado. NULL no exemplo, pois a origem traz Não consta. |
| numero_serie | Texto | TEXT | Série quando informada. NULL no exemplo, pois a origem traz ---. |
| resolucao | Real | REAL | Resolução positiva, quando disponível. Na amostra, 0.001. Aceita NULL. |
| unidade | Texto | TEXT | Unidade da resolução: mm ou um. Obrigatória; mm na amostra. |

## medicao

| Campo | Tipo no trabalho | Tipo SQLite | Descrição, origem e regra |
| --- | --- | --- | --- |
| id | Inteiro | INTEGER | PK. Identificador gerado pelo SQLite para cada leitura inserida. |
| codigo_execucao | Texto | TEXT | Código do conjunto de leituras. O script define AMOSTRA-2026-001. Obrigatório. |
| equipamento_id | Inteiro | INTEGER | FK obrigatória para equipamento.id. O script usa o cadastro 1. |
| tecnico_id | Inteiro | INTEGER | FK obrigatória para tecnico_solicitante.id. Deve apontar para tipo TECNICO; id 1 na amostra. |
| solicitante_id | Inteiro | INTEGER | FK obrigatória para tecnico_solicitante.id. Deve apontar para tipo SOLICITANTE; id 2 na amostra. |
| data_medicao | Texto | TEXT | Data válida no formato AAAA-MM-DD, lida do CSV. 2026-08-13 vem de Report!D5. |
| parametro | Texto | TEXT | Nome obrigatório lido do CSV. Origem: Report!A14:A27 e A29:A42. |
| repeticao | Inteiro | INTEGER | 1 ou 2, conforme o bloco de origem. Obrigatória; distingue leituras de mesmo valor. |
| valor_nominal | Real | REAL | Número obrigatório lido do CSV, vindo da coluna C de Report. Zero é válido. |
| tolerancia_superior | Real | REAL | Desvio superior em relação ao nominal, vindo da coluna D. Obrigatório. |
| tolerancia_inferior | Real | REAL | Desvio inferior com seu sinal, vindo da coluna E. Não pode superar a tolerância superior. |
| valor_obtido | Real | REAL | Leitura numérica obrigatória, vinda da coluna B de Report. O Python recusa valores não finitos. |
| desvio_informado | Real | REAL | Desvio vindo da coluna F, mantido mesmo quando diverge da conta. O banco aceita NULL. |
| unidade | Texto | TEXT | Unidade da leitura: mm ou um. Lida do CSV. A unidade mm foi identificada no contexto de F03 e do certificado. |
| status | Texto | TEXT | REGISTRADO ou CONFERIDO. A importação usa REGISTRADO; não representa aprovação do instrumento. |
| arquivo_origem | Texto | TEXT | Nome obrigatório do arquivo que forneceu a leitura. Lido do CSV. |
| aba_origem | Texto | TEXT | Nome obrigatório da aba de origem. Report nesta amostra; lido do CSV. |
| linha_origem | Inteiro | INTEGER | Número inteiro positivo da linha da planilha, lido do CSV. |
| mmc_origem | Texto | TEXT | Código da máquina no relatório. Texto obrigatório; 500008 nesta amostra. |

## Regras que envolvem mais de um campo

- Uma execução não pode repetir a combinação parâmetro e repetição.
- O id do técnico deve ser diferente do id do solicitante, e cada um deve ter seu papel correto.
- Cada leitura aponta para cadastros existentes por três chaves estrangeiras.
- Nominal, tolerâncias e valor obtido de uma leitura usam a mesma unidade.
- Limite inferior = nominal + tolerância inferior. Limite superior = nominal + tolerância superior.
- A média usa as duas leituras. O erro da média é média menos nominal.
- O banco não guarda a média como campo, pois ela pode ser calculada pelas consultas.
- REAL usa aproximação numérica. A comparação dos resultados da amostra usa 1e-12 apenas para conferir diferenças de representação.
- Este modelo não armazena contas de acesso nem calcula a incerteza de calibração. A etapa trata da estrutura e da integridade dos dados.
