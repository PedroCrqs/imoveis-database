PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Proprietarios (
    ProprietarioID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome           TEXT NOT NULL,
    Telefone       TEXT,
    Email          TEXT
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
    Tipologia       TEXT NOT NULL CHECK (Tipologia IN ('Apartamento', 'Casa', 'Cobertura', 'Studio')),
    ProprietarioID  INTEGER NOT NULL,
    Valor           REAL NOT NULL,
    ValorCondominio REAL,
    IPTU            REAL,
    Metragem        INTEGER NOT NULL,
    Sol             TEXT CHECK (Sol IN ('Manhã', 'Tarde', 'Passante')),
    BairroID        INTEGER NOT NULL,
    CondominioID    INTEGER,
    Endereco        TEXT NOT NULL,
    Descricao       TEXT,
    ImovelStatus    TEXT NOT NULL DEFAULT 'Disponível' CHECK (ImovelStatus IN (
        'Disponível', 'Vendido', 'Alugado', 'Retirado de Venda'
    )),
    DataVenda       DATETIME,
    DataCadastro    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BairroID)     REFERENCES Bairros (BairroID),
    FOREIGN KEY (CondominioID) REFERENCES Condominios (CondominioID),
    FOREIGN KEY (ProprietarioID) REFERENCES Proprietarios (ProprietarioID)
);

CREATE TABLE IF NOT EXISTS Fotos (
    FotoID         INTEGER PRIMARY KEY AUTOINCREMENT,
    ImovelID       INTEGER NOT NULL,
    CaminhoArquivo TEXT NOT NULL,
    Principal      BOOLEAN DEFAULT 0,
    DataCadastro   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ImovelID) REFERENCES Imoveis (ImovelID) ON DELETE CASCADE
);