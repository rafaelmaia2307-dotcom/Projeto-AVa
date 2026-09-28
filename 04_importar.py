"""Cria as três tabelas e importa a amostra com a biblioteca padrão do Python."""
import argparse
import csv
import math
import sqlite3
from datetime import date
from pathlib import Path

PASTA = Path(__file__).resolve().parent
EXECUCAO = 'AMOSTRA-2026-001'
CAMPOS = (
    'codigo_execucao', 'equipamento_id', 'tecnico_id', 'solicitante_id',
    'data_medicao', 'parametro', 'repeticao', 'valor_nominal',
    'tolerancia_superior', 'tolerancia_inferior', 'valor_obtido',
    'desvio_informado', 'unidade', 'status', 'arquivo_origem',
    'aba_origem', 'linha_origem', 'mmc_origem',
)


def conectar(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def ler_dados(arquivo):
    registros = []
    chaves = set()
    with Path(arquivo).open(encoding='utf-8-sig', newline='') as f:
        for linha in csv.DictReader(f, delimiter=';'):
            date.fromisoformat(linha['data_medicao'])
            numeros = [float(linha[c]) for c in (
                'valor_nominal', 'tolerancia_superior', 'tolerancia_inferior',
                'valor_obtido', 'desvio_informado')]
            if not all(math.isfinite(v) for v in numeros):
                raise ValueError('A medição deve conter números finitos.')
            parametro = linha['parametro'].strip()
            repeticao = int(linha['repeticao'])
            chave = (parametro, repeticao)
            if chave in chaves:
                raise ValueError('Parâmetro e repetição duplicados no CSV.')
            chaves.add(chave)
            registros.append((EXECUCAO, 1, 1, 2, linha['data_medicao'],
                parametro, repeticao, *numeros, linha['unidade'], 'REGISTRADO',
                linha['arquivo_origem'], linha['aba_origem'],
                int(linha['linha_origem']), linha['mmc_origem']))
    parametros = {p for p, _ in chaves}
    if len(parametros) != 14 or len(registros) != 28:
        raise ValueError('Esta amostra deve ter 14 parâmetros e 28 leituras.')
    if any((p, r) not in chaves for p in parametros for r in (1, 2)):
        raise ValueError('Cada parâmetro deve ter as repetições 1 e 2.')
    return registros


def importar(conexao, arquivo=PASTA / 'dados_amostra.csv'):
    registros = ler_dados(arquivo)
    with conexao:
        # Cadastros da demonstração: técnico do relatório F01 e solicitante de F03.
        pessoas = [(1, 'José A. Rosa Jr', 'TECNICO', None),
                   (2, 'Usinagem I', 'SOLICITANTE', 'Usinagem I')]
        for pessoa in pessoas:
            atual = conexao.execute('SELECT id,nome,tipo,setor FROM tecnico_solicitante WHERE id=?', (pessoa[0],)).fetchone()
            if atual is None:
                conexao.execute('INSERT INTO tecnico_solicitante VALUES (?,?,?,?)', pessoa)
            elif atual != pessoa:
                raise ValueError('O cadastro existente difere da amostra; nenhum valor foi substituído.')
        equipamento = (1, '703.1208', 'Dispositivo de controle', 'Não se aplica', None, None, 0.001, 'mm')
        atual = conexao.execute('SELECT * FROM equipamento WHERE id=1').fetchone()
        if atual is None:
            conexao.execute('INSERT INTO equipamento VALUES (?,?,?,?,?,?,?,?)', equipamento)
        elif atual != equipamento:
            raise ValueError('O equipamento existente difere da amostra.')
        existentes = conexao.execute(
            'SELECT ' + ','.join(CAMPOS) + ' FROM medicao WHERE codigo_execucao=?',
            (EXECUCAO,)).fetchall()
        if existentes:
            # O status pode ter mudado por uma conferência posterior; comparar os dados de origem.
            sem_status = lambda r: r[:13] + r[14:]
            if sorted(map(sem_status, existentes)) != sorted(map(sem_status, registros)):
                raise ValueError('A execução já existe com dados diferentes; use outra identificação após analisar a origem.')
            return 0
        sql = 'INSERT INTO medicao (' + ','.join(CAMPOS) + ') VALUES (' + ','.join('?' for _ in CAMPOS) + ')'
        conexao.executemany(sql, registros)
    return len(registros)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--banco', type=Path, default=PASTA / 'calibracao.db')
    args = parser.parse_args()
    conexao = conectar(args.banco)
    try:
        conexao.executescript((PASTA / '03_banco.sql').read_text(encoding='utf-8'))
        adicionadas = importar(conexao)
        totais = {t: conexao.execute('SELECT count(*) FROM ' + t).fetchone()[0]
                  for t in ('tecnico_solicitante', 'equipamento', 'medicao')}
        print('Banco:', args.banco)
        print('Novas leituras:', adicionadas)
        print('Totais:', totais)
        print('Integridade:', conexao.execute('PRAGMA integrity_check').fetchone()[0])
        print('Problemas de FK:', conexao.execute('PRAGMA foreign_key_check').fetchall())
    finally:
        conexao.close()


if __name__ == '__main__':
    main()
