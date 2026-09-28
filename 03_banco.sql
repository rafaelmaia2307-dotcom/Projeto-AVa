-- Projeto Aplicado I - Entrega 02
-- Aluno: Rafael Maia
-- Executar em SQLite. Ativar as chaves estrangeiras em cada conexão.
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS tecnico_solicitante (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    tipo TEXT NOT NULL CHECK (tipo IN ('TECNICO', 'SOLICITANTE')),
    setor TEXT
);

CREATE TABLE IF NOT EXISTS equipamento (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE CHECK (length(trim(codigo)) > 0),
    descricao TEXT NOT NULL CHECK (length(trim(descricao)) > 0),
    modelo TEXT,
    fabricante TEXT,
    numero_serie TEXT,
    resolucao REAL CHECK (resolucao IS NULL OR
        (typeof(resolucao) IN ('real', 'integer') AND resolucao > 0)),
    unidade TEXT NOT NULL CHECK (unidade IN ('mm', 'um'))
);

CREATE TABLE IF NOT EXISTS medicao (
    id INTEGER PRIMARY KEY,
    codigo_execucao TEXT NOT NULL CHECK (length(trim(codigo_execucao)) > 0),
    equipamento_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    solicitante_id INTEGER NOT NULL,
    data_medicao TEXT NOT NULL CHECK (
        data_medicao GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(data_medicao, '+0 days') IS NOT NULL
        AND date(data_medicao, '+0 days') = data_medicao
    ),
    parametro TEXT NOT NULL CHECK (length(trim(parametro)) > 0),
    repeticao INTEGER NOT NULL CHECK (typeof(repeticao) = 'integer' AND repeticao IN (1, 2)),
    valor_nominal REAL NOT NULL CHECK (typeof(valor_nominal) IN ('real', 'integer')),
    tolerancia_superior REAL NOT NULL CHECK (typeof(tolerancia_superior) IN ('real', 'integer')),
    tolerancia_inferior REAL NOT NULL CHECK (typeof(tolerancia_inferior) IN ('real', 'integer')),
    valor_obtido REAL NOT NULL CHECK (typeof(valor_obtido) IN ('real', 'integer')),
    desvio_informado REAL CHECK (desvio_informado IS NULL OR typeof(desvio_informado) IN ('real', 'integer')),
    unidade TEXT NOT NULL CHECK (unidade IN ('mm', 'um')),
    status TEXT NOT NULL DEFAULT 'REGISTRADO'
        CHECK (status IN ('REGISTRADO', 'CONFERIDO')),
    arquivo_origem TEXT NOT NULL CHECK (length(trim(arquivo_origem)) > 0),
    aba_origem TEXT NOT NULL CHECK (length(trim(aba_origem)) > 0),
    linha_origem INTEGER NOT NULL CHECK (typeof(linha_origem) = 'integer' AND linha_origem > 0),
    mmc_origem TEXT NOT NULL CHECK (length(trim(mmc_origem)) > 0),
    CHECK (tolerancia_inferior <= tolerancia_superior),
    CHECK (tecnico_id <> solicitante_id),
    UNIQUE (codigo_execucao, parametro, repeticao),
    FOREIGN KEY (equipamento_id) REFERENCES equipamento(id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (tecnico_id) REFERENCES tecnico_solicitante(id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (solicitante_id) REFERENCES tecnico_solicitante(id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

-- As duas FKs apontam para a mesma tabela, mas os papéis são diferentes.
CREATE TRIGGER IF NOT EXISTS medicao_papeis_insert
BEFORE INSERT ON medicao
BEGIN
    SELECT RAISE(ABORT, 'tecnico_id deve identificar um TECNICO')
    WHERE NOT EXISTS (SELECT 1 FROM tecnico_solicitante
                     WHERE id = NEW.tecnico_id AND tipo = 'TECNICO');
    SELECT RAISE(ABORT, 'solicitante_id deve identificar um SOLICITANTE')
    WHERE NOT EXISTS (SELECT 1 FROM tecnico_solicitante
                     WHERE id = NEW.solicitante_id AND tipo = 'SOLICITANTE');
END;

CREATE TRIGGER IF NOT EXISTS medicao_papeis_update
BEFORE UPDATE OF tecnico_id, solicitante_id ON medicao
BEGIN
    SELECT RAISE(ABORT, 'tecnico_id deve identificar um TECNICO')
    WHERE NOT EXISTS (SELECT 1 FROM tecnico_solicitante
                     WHERE id = NEW.tecnico_id AND tipo = 'TECNICO');
    SELECT RAISE(ABORT, 'solicitante_id deve identificar um SOLICITANTE')
    WHERE NOT EXISTS (SELECT 1 FROM tecnico_solicitante
                     WHERE id = NEW.solicitante_id AND tipo = 'SOLICITANTE');
END;

CREATE TRIGGER IF NOT EXISTS responsavel_tipo_update
BEFORE UPDATE OF tipo ON tecnico_solicitante
WHEN NEW.tipo <> OLD.tipo
BEGIN
    SELECT RAISE(ABORT, 'Pessoa ou setor ja possui medicoes neste papel')
    WHERE EXISTS (SELECT 1 FROM medicao
                  WHERE tecnico_id = OLD.id OR solicitante_id = OLD.id);
END;

COMMIT;
