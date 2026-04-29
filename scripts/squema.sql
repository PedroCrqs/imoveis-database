PRAGMA foreign_keys = ON;

CREATE TABLE Proprietarios (
    ProprietarioID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    Telefone TEXT,
    Email TEXT
);

CREATE TABLE Bairros(
    BairroID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    BairroZona CHECK (BairroZona IN ('Zona Oeste', 'Zona Sudoeste', 'Zona Sul', 'Zona Norte'))

);

CREATE TABLE Condominios(
    CondominioID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    Endereço TEXT,
    Infraestrutura TEXT,
    BairroID INTEGER,
    FOREIGN KEY (BairroID) REFERENCES Bairros (BairroID)
);

CREATE TABLE Imoveis (
    ImovelID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    ProprietarioID INTEGER,
    Valor REAL,
    ValorCondominio REAL,
    IPTU REAL,
    Metragem INTEGER,
    Quartos INTEGER,
    Sol TEXT CHECK (Sol IN ('Manhã', 'Tarde', 'Passante')),
    BairroID INTEGER,
    CondominioID INTEGER,
    Endereco TEXT,
    Descricao TEXT,
    DataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BairroID) REFERENCES Bairros (BairroID),
    FOREIGN KEY (CondominioID) REFERENCES Condominios (CondominioID),
    FOREIGN KEY (ProprietarioID) REFERENCES Proprietarios (ProprietarioID)
);
