PRAGMA foreign_keys = ON;

CREATE TABLE Imoveis (
    ImovelID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT,
    Valor REAL,
    Condomínio REAL,
    IPTU REAL,
    Metragem INTEGER,
    Quartos INTEGER,
    Sol TEXT CHECK (Sol IN ('Manhã', 'Tarde', 'Passante')),
    BairroID INTEGER,
    CondominioID INTEGER,
    Descrição TEXT,
    DataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);
