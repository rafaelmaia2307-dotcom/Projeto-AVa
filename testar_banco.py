"""Testes da estrutura, das regras e da importação. Executar: python testar_banco.py."""
import importlib.util
import sqlite3
import unittest
from pathlib import Path

PASTA = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('importacao', PASTA / '04_importar.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class TestesBanco(unittest.TestCase):
    def setUp(self):
        self.db = app.conectar(':memory:')
        self.ddl = (PASTA / '03_banco.sql').read_text(encoding='utf-8')
        self.db.executescript(self.ddl)
        app.importar(self.db)

    def tearDown(self):
        self.db.close()

    def inserir_alterado(self, **mudancas):
        valores = dict(zip(app.CAMPOS, self.db.execute('SELECT ' + ','.join(app.CAMPOS) + ' FROM medicao ORDER BY id LIMIT 1').fetchone()))
        valores['codigo_execucao'] = 'TESTE-002'
        valores.update(mudancas)
        self.db.execute('INSERT INTO medicao (' + ','.join(app.CAMPOS) + ') VALUES (' + ','.join('?' for _ in app.CAMPOS) + ')', tuple(valores[c] for c in app.CAMPOS))

    def test_tres_tabelas_e_reexecucao_ddl(self):
        self.db.executescript(self.ddl)
        tabelas = {r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        self.assertEqual(tabelas, {'tecnico_solicitante', 'equipamento', 'medicao'})
        self.assertEqual(self.db.execute('SELECT count(*) FROM medicao').fetchone()[0], 28)

    def test_reimportacao_nao_duplica(self):
        self.assertEqual(app.importar(self.db), 0)
        self.assertEqual(self.db.execute('SELECT count(*) FROM medicao').fetchone()[0], 28)

    def test_reimportacao_nao_apaga_conferencia(self):
        self.db.execute("UPDATE medicao SET status='CONFERIDO' WHERE id=1")
        app.importar(self.db)
        self.assertEqual(self.db.execute('SELECT status FROM medicao WHERE id=1').fetchone()[0], 'CONFERIDO')

    def test_reimportacao_diferente_e_recusada(self):
        self.db.execute('UPDATE medicao SET valor_obtido=99 WHERE id=1')
        self.db.commit()
        with self.assertRaises(ValueError):
            app.importar(self.db)
        self.assertEqual(self.db.execute('SELECT valor_obtido FROM medicao WHERE id=1').fetchone()[0], 99)

    def test_fk_equipamento_inexistente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.inserir_alterado(equipamento_id=999)

    def test_fk_tecnico_inexistente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.inserir_alterado(tecnico_id=999)

    def test_papeis_trocados(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.inserir_alterado(tecnico_id=2, solicitante_id=1)

    def test_tipo_referenciado_nao_pode_ser_trocado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE tecnico_solicitante SET tipo='SOLICITANTE' WHERE id=1")

    def test_exclusao_de_cadastro_com_historico(self):
        for tabela in ('equipamento', 'tecnico_solicitante'):
            with self.subTest(tabela=tabela), self.assertRaises(sqlite3.IntegrityError):
                self.db.execute('DELETE FROM ' + tabela + ' WHERE id=1')

    def test_repeticao_da_mesma_leitura(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.inserir_alterado(codigo_execucao=app.EXECUCAO)

    def test_nova_execucao_preserva_a_anterior(self):
        self.inserir_alterado()
        self.assertEqual(self.db.execute('SELECT count(*) FROM medicao WHERE codigo_execucao=?', (app.EXECUCAO,)).fetchone()[0], 28)
        self.assertEqual(self.db.execute('SELECT count(*) FROM medicao').fetchone()[0], 29)

    def test_campos_invalidos(self):
        invalidos = [dict(valor_obtido=None), dict(valor_obtido='abc'),
                    dict(repeticao=3), dict(status='APROVADO'),
                    dict(data_medicao='2026-02-31'), dict(data_medicao='2026-13-10'),
                    dict(tolerancia_inferior=10, tolerancia_superior=1)]
        for dados in invalidos:
            with self.subTest(dados=dados), self.assertRaises(sqlite3.IntegrityError):
                self.inserir_alterado(**dados)

    def test_pares_e_medias(self):
        dados = self.db.execute('SELECT parametro,count(*),avg(valor_obtido) FROM medicao GROUP BY parametro').fetchall()
        self.assertEqual(len(dados), 14)
        self.assertTrue(all(r[1] == 2 for r in dados))
        medias = dict((r[0], r[2]) for r in dados)
        import csv
        with (PASTA / 'medias_referencia.csv').open(encoding='utf-8-sig', newline='') as f:
            referencia = list(csv.DictReader(f, delimiter=';'))
        self.assertEqual(len(referencia), 14)
        for r in referencia:
            self.assertAlmostEqual(medias[r['parametro']], float(r['media_planilha']), places=12)

    def test_tres_diferencas_no_desvio(self):
        linhas = self.db.execute('SELECT linha_origem FROM medicao WHERE abs(desvio_informado-(valor_obtido-valor_nominal))>1e-12 ORDER BY linha_origem').fetchall()
        self.assertEqual(linhas, [(14,), (18,), (25,)])

    def test_integridade_e_relacoes(self):
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(), [])
        fks = self.db.execute('PRAGMA foreign_key_list(medicao)').fetchall()
        self.assertEqual(len(fks), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
