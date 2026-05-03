PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Proprietarios (
    ProprietarioID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome           TEXT NOT NULL,
    Telefone       TEXT NOT NULL,
    Email          TEXT NULL 
);

CREATE TABLE IF NOT EXISTS Bairros (
    BairroID   INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome       TEXT NOT NULL,
    BairroZona TEXT NOT NULL CHECK (BairroZona IN (
        'Zona Oeste', 'Zona Sudoeste', 'Zona Sul', 'Zona Norte'
    ))
);

CREATE TABLE IF NOT EXISTS Condominios (
    CondominioID   INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome           TEXT NOT NULL,
    Endereço       TEXT,
    Infraestrutura TEXT,
    BairroID       INTEGER NOT NULL,
    FOREIGN KEY (BairroID) REFERENCES Bairros (BairroID)
);

CREATE TABLE IF NOT EXISTS Imoveis (
    ImovelID        INTEGER PRIMARY KEY AUTOINCREMENT,
    CondominioID    INTEGER NULL,
    Tipologia       TEXT NOT NULL CHECK (Tipologia IN ('Apartamento', 'Casa', 'Cobertura', 'Studio')),
    Quartos         INTEGER NOT NULL,
    Vagas           INTEGER DEFAULT 0,
    Valor           REAL NOT NULL,
    ValorCondominio REAL NOT NULL,
    IPTU            REAL NOT NULL,
    Metragem        REAL NOT NULL,
    Sol             TEXT CHECK (Sol IN ('Manhã', 'Tarde', 'Passante')),
    BairroID        INTEGER NOT NULL,
    Endereco        TEXT NOT NULL,
    Descricao       TEXT NOT NULL,
    ImovelStatus    TEXT NOT NULL DEFAULT 'Disponível' CHECK (ImovelStatus IN (
        'Disponível', 'Vendido', 'Alugado', 'Retirado de Venda'
    )),
    DataVenda       DATETIME,
    DataCadastro    DATETIME DEFAULT CURRENT_TIMESTAMP,
    ProprietarioID  INTEGER NOT NULL,
    CaminhoDrive TEXT,
    LinkPublico TEXT,
    FOREIGN KEY (BairroID)     REFERENCES Bairros (BairroID),
    FOREIGN KEY (CondominioID) REFERENCES Condominios (CondominioID),
    FOREIGN KEY (ProprietarioID) REFERENCES Proprietarios (ProprietarioID)
);

CREATE TABLE IF NOT EXISTS Fotos (
    FotoID         INTEGER PRIMARY KEY AUTOINCREMENT,
    ImovelID       INTEGER NOT NULL,
    CaminhoArquivo TEXT NOT NULL UNIQUE,
    Principal      BOOLEAN DEFAULT 0,
    DataCadastro   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ImovelID) REFERENCES Imoveis (ImovelID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Auditoria_Imoveis (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    ImovelID INTEGER NOT NULL,
    Operacao TEXT NOT NULL,
    ColunaAlterada TEXT,
    ValorAntigo TEXT,
    ValorNovo TEXT,
    DataHora DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TRIGGERS

-- 1. Registro de Inclusão
DROP TRIGGER IF EXISTS log_imovel_insert;
CREATE TRIGGER log_imovel_insert
AFTER INSERT ON Imoveis
BEGIN
    INSERT INTO Auditoria_Imoveis (ImovelID, Operacao, ColunaAlterada, ValorNovo)
    VALUES (NEW.ImovelID, 'INSERT', 'Tudo', 'Imóvel cadastrado com sucesso');
END;

-- 2. Registro Exato de Status
DROP TRIGGER IF EXISTS log_imovel_update_status;
CREATE TRIGGER log_imovel_update_status
AFTER UPDATE OF ImovelStatus ON Imoveis
WHEN OLD.ImovelStatus <> NEW.ImovelStatus
BEGIN
    INSERT INTO Auditoria_Imoveis (ImovelID, Operacao, ColunaAlterada, ValorAntigo, ValorNovo)
    VALUES (OLD.ImovelID, 'UPDATE', 'ImovelStatus', OLD.ImovelStatus, NEW.ImovelStatus);
END;

-- 3. Registro Exato de Preço (Fundamental para análise estratégica)
DROP TRIGGER IF EXISTS log_imovel_update_valor;
CREATE TRIGGER log_imovel_update_valor
AFTER UPDATE OF Valor ON Imoveis
WHEN OLD.Valor <> NEW.Valor
BEGIN
    INSERT INTO Auditoria_Imoveis (ImovelID, Operacao, ColunaAlterada, ValorAntigo, ValorNovo)
    VALUES (OLD.ImovelID, 'UPDATE', 'Valor', OLD.Valor, NEW.Valor);
END;

-- Índices para Performance
CREATE INDEX IF NOT EXISTS idx_imoveis_bairro ON Imoveis(BairroID);
CREATE INDEX IF NOT EXISTS idx_imoveis_status ON Imoveis(ImovelStatus);
CREATE INDEX IF NOT EXISTS idx_auditoria_imovel ON Auditoria_Imoveis(ImovelID);