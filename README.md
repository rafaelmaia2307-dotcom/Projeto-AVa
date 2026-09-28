# Projeto Aplicado I — Entrega 02

**Aluno:** Rafael Maia  
**Tema:** Modelagem e implementação de banco de dados  
**Empresa:** Schulz S.A.  
**Professor:** Hugo Menezes Barra  
**Prazo do roteiro:** 02/10/2026

**Repositório:** https://github.com/rafaelmaia2307-dotcom/Projeto-AVa

## Arquivos principais

- `01_estrutura.md`: explicação do modelo conceitual com mais de 20 linhas.
- `02_dicionario.md`: os 31 campos das três tabelas, seus tipos e regras.
- `03_banco.sql`: criação das três tabelas SQLite, chaves e restrições.
- `Entrega_02_Rafael_Maia.pdf`: explicação do projeto para acompanhar a entrega.

## Como executar no VS Code

Abra esta pasta no VS Code e use o terminal com Python 3 instalado.
O código usa somente bibliotecas que já acompanham o Python.

```powershell
python 04_importar.py
python testar_banco.py
```

A primeira instrução cria `calibracao.db` e importa a amostra.
O banco também acompanha a entrega já preenchido.
Executar novamente mantém os registros existentes, sem duplicar as leituras.
Para testar a criação em outro arquivo:

```powershell
python 04_importar.py --banco demonstracao.db
```

O resultado esperado é: 2 responsáveis, 1 equipamento e 28 medições.
Os testes usam um banco temporário em memória e não alteram o banco entregue.

O SQL também pode ser executado diretamente em uma ferramenta SQLite:

```sql
.read 03_banco.sql
```

O comando `.read` pertence ao terminal sqlite3; em uma extensão de banco no VS Code,
abra `03_banco.sql` e execute seu conteúdo pela opção da própria extensão.
O DDL cria a estrutura. Os dados são carregados separadamente pelo Python.

## Consultas e dados de apoio

`05_consultas.sql` apresenta os JOINs, as médias, os desvios e o histórico.
`dados_amostra.csv` contém as 28 leituras extraídas das planilhas da Entrega 01.
`medias_referencia.csv` contém as 14 médias salvas na planilha preenchida, usadas nos testes.
Os cadastros usados no exemplo estão definidos em `04_importar.py`.
O arquivo `resultado_testes.txt` registra o resultado da verificação realizada.

## Envio

O roteiro pede um ZIP no AVA com o PDF explicativo e o link dos arquivos no GitHub.
O endereço do repositório da atividade está no PDF e no arquivo `repositorio.txt`.
Repositório: https://github.com/rafaelmaia2307-dotcom/Projeto-AVa
Os arquivos originais das planilhas não fazem parte deste pacote; a amostra usada está nos CSVs.

## Origem das informações

Roteiro: Modelagem de Banco de Dados - Entrega 02 PA I.pdf.
Dados: Registro MMC (1).xlsx e Planilha do Software com a Calibração do Dispositivo.xlsx.
O exemplo usa a data do relatório da máquina e preserva seus valores e o código MMC 500008.
O código AMOSTRA-2026-001 identifica o conjunto neste exercício e não é um número de certificado.
