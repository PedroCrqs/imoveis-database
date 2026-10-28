# Database de Imóveis

> CLI para gerenciamento de banco de dados de imóveis para imobiliária com PostgreSQL e Docker.

---

## 🇧🇷 Português

### Sobre

Sistema de linha de comando para cadastro e consulta de imóveis, condomínios, bairros e proprietários, com persistência em PostgreSQL, orquestração via Docker Compose e integração com robôs de disparo WhatsApp.

### Estrutura do projeto

```
imoveis-database/
├── data/
│   └── imoveis/                 ← pastas dos imóveis locais (fotos + Descrição.txt)
│       └── imovel_xx/
│           ├── 0.jpg            ← foto de capa
│           ├── 1.jpg
│           └── Descrição.txt
├── scripts/
│   └── schema.sql               ← DDL do banco (PostgreSQL + Triggers PL/pgSQL)
├── src/
│   ├── add_ref.py               ← injeção de _Ref: {id}_ nas descrições
│   ├── backup.py                ← sincronização de fotos com Google Drive (rclone)
│   ├── database.py              ← pooling e conexão com PostgreSQL (psycopg3)
│   ├── main.py                  ← CLI interativa e menu principal
│   ├── migrate_sqlite_to_pg.py  ← migração histórica de dados SQLite → Postgres
│   ├── repository.py            ← camada de acesso a dados (queries e CRUD)
│   ├── seed.py                  ← população inicial de bairros (Zona Sul e Zona Sudoeste)
│   └── sync_descricoes.py       ← sincronização de Descrição.txt do Drive para o banco
├── docker-compose.yml           ← orquestração: db (Postgres 16), imoveis-cli e bots
├── Dockerfile                   ← imagem da CLI Python
└── requirements.txt
```

### Instalação e Execução

#### Modo Local (Ambiente Virtual)

```bash
git clone <repo>
cd imoveis-database
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # configure DATABASE_URL e credenciais
python src/seed.py               # popula os bairros iniciais no banco
python src/main.py               # inicia a CLI interativa
```

#### Modo Docker Compose

```bash
cp .env.example .env             # preencha POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose up -d db          # inicia apenas o banco PostgreSQL
# ou para subir a stack com os robôs de disparo:
docker compose up -d
```

### Funcionalidades

| Opção | Função                           |
| ----- | -------------------------------- |
| 1     | Cadastrar bairro                 |
| 2     | Cadastrar proprietário           |
| 3     | Cadastrar condomínio             |
| 4     | Cadastrar imóvel                 |
| 5     | Atualizar status do imóvel       |
| 6     | Atualizar preços                 |
| 7     | Corrigir um campo                |
| 8     | Buscar imóvel por ID             |
| 9     | Buscar imóveis por bairro        |
| 10    | Listar imóveis disponíveis       |
| 11    | Buscar proprietário por ID       |
| 12    | Buscar imóveis por condomínio    |
| 13    | Atualizar nome de condomínio     |

### Convenções do Sistema

- **Fotos:** coloque todas as imagens `.jpg`/`.jpeg`/`.png` na pasta do imóvel. A foto de capa deve se chamar obrigatoriamente `0` (ex: `0.jpg`).
- **Descrição:** arquivo `Descrição.txt` na pasta do imóvel. Suporta formatação de texto para WhatsApp (`*negrito*`, `_itálico_`). Atualizado automaticamente nas alterações de preço ou via `sync_descricoes.py`.
- **Status do imóvel:** `Disponível` | `Vendido` | `Alugado` | `Retirado de Venda`.
- **Tipologia:** `Apartamento` | `Casa` | `Cobertura` | `Studio` | `Garden` | `Loja`.
- **Cobertura Geográfica:** Rio de Janeiro — Zona Sul (todos os 18 bairros oficiais: Botafogo, Catete, Copacabana, Cosme Velho, Flamengo, Gávea, Glória, Humaitá, Ipanema, Jardim Botânico, Lagoa, Laranjeiras, Leblon, Leme, Rocinha, São Conrado, Urca, Vidigal) e Zona Sudoeste/Oeste (Barra da Tijuca, Recreio dos Bandeirantes, Jacarepaguá, Freguesia, Vargem Pequena, Vargem Grande, Barra Olímpica).
- **Sincronização:** integração com Google Drive via `rclone` (`DRIVE_DIR`), sincronizando arquivos e descrições diretamente com os diretórios de armazenamento.

### Tecnologias

- Python 3.13+
- PostgreSQL 16
- Docker & Docker Compose
- `psycopg` (v3) & `psycopg_pool` (Connection Pooling)
- `pathlib`, `asyncio`, `webbrowser`, `hashlib`

### Diferenciais Técnicos

- **Auditoria Automática:** Todas as inserções e alterações de status e valor são registradas automaticamente na tabela `Auditoria_Imoveis` via Triggers em PL/pgSQL.
- **Connection Pool Robusto:** Gerenciamento de conexões com `ConnectionPool` do psycopg3 compartilhado entre processos e handlers.
- **Performance e Integridade:** Índices em chaves de busca (`BairroID`, `ImovelStatus`, auditoria e filas de despacho) e constraints de validação (`CHECK`, `FOREIGN KEY`).
- **Arquitetura Isolada:** Serviços orquestrados em rede interna Docker bridge (`imoveis-net`), executados com usuário não-root (UID 1000).

---

## 🇺🇸 English

### About

Command-line system for managing selling properties, condos, neighborhoods, and owners, backed by PostgreSQL, Docker Compose orchestration, and integrated with WhatsApp listing automation bots.

### Project Structure

```
imoveis-database/
├── data/
│   └── imoveis/                 ← local property folders (photos + Descrição.txt)
│       └── imovel_xx/
│           ├── 0.jpg            ← cover photo
│           ├── 1.jpg
│           └── Descrição.txt
├── scripts/
│   └── schema.sql               ← Database DDL (PostgreSQL + PL/pgSQL Triggers)
├── src/
│   ├── add_ref.py               ← injection of _Ref: {id}_ into descriptions
│   ├── backup.py                ← photo synchronization with Google Drive (rclone)
│   ├── database.py              ← PostgreSQL connection pooling (psycopg3)
│   ├── main.py                  ← interactive CLI and main menu
│   ├── migrate_sqlite_to_pg.py  ← legacy SQLite → PostgreSQL migration script
│   ├── repository.py            ← data access layer (queries and CRUD)
│   ├── seed.py                  ← seed script for neighborhoods (South and Southwest Zones)
│   └── sync_descricoes.py       ← syncs Descrição.txt from Drive into database
├── docker-compose.yml           ← orchestration: db (Postgres 16), imoveis-cli, and bots
├── Dockerfile                   ← Python CLI image
└── requirements.txt
```

### Setup & Running

#### Local Virtual Environment

```bash
git clone <repo>
cd imoveis-database
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # set DATABASE_URL and credentials
python src/seed.py               # populate initial neighborhoods
python src/main.py               # start interactive CLI
```

#### Docker Compose

```bash
cp .env.example .env             # set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
docker compose up -d db          # start PostgreSQL database only
# or start full stack with dispatch bots:
docker compose up -d
```

### Features

| Option | Function                        |
| ------ | ------------------------------- |
| 1      | Add neighborhood                |
| 2      | Add owner                       |
| 3      | Add condo                       |
| 4      | Add property                    |
| 5      | Update property status          |
| 6      | Update prices                   |
| 7      | Correct a field                 |
| 8      | Find property by ID             |
| 9      | Find properties by neighborhood |
| 10     | Show available properties       |
| 11     | Find owner by ID                |
| 12     | Find properties by condominium  |
| 13     | Update condo name               |

### System Conventions

- **Photos:** Place all `.jpg`/`.jpeg`/`.png` images in the property folder. Cover photo must be named `0` (e.g., `0.jpg`).
- **Description:** `Descrição.txt` inside the property folder. Supports WhatsApp formatting (`*bold*`, `_italic_`). Auto-updated when prices change or via `sync_descricoes.py`.
- **Property Status:** `Disponível` | `Vendido` | `Alugado` | `Retirado de Venda`.
- **Property Typology:** `Apartamento` | `Casa` | `Cobertura` | `Studio` | `Garden` | `Loja`.
- **Geographic Coverage:** Rio de Janeiro — South Zone (all 18 official neighborhoods: Botafogo, Catete, Copacabana, Cosme Velho, Flamengo, Gávea, Glória, Humaitá, Ipanema, Jardim Botânico, Lagoa, Laranjeiras, Leblon, Leme, Rocinha, São Conrado, Urca, Vidigal) and Southwest/West Zone (Barra da Tijuca, Recreio dos Bandeirantes, Jacarepaguá, Freguesia, Vargem Pequena, Vargem Grande, Barra Olímpica).
- **Synchronization:** Google Drive integration via `rclone` (`DRIVE_DIR`), synchronizing images and descriptions directly with storage folders.

### Stack

- Python 3.13+
- PostgreSQL 16
- Docker & Docker Compose
- `psycopg` (v3) & `psycopg_pool` (Connection Pooling)
- `pathlib`, `asyncio`, `webbrowser`, `hashlib`

### Key Features

- **Automatic Auditing:** All insert, status, and price changes are automatically logged to `Auditoria_Imoveis` via PL/pgSQL Triggers.
- **Robust Connection Pool:** Process-wide connection pool via `psycopg_pool.ConnectionPool`.
- **Performance & Data Integrity:** Dedicated indexes on search columns (`BairroID`, `ImovelStatus`, auditing and dispatch queues) and strict constraints (`CHECK`, `FOREIGN KEY`).
- **Containerized Architecture:** Services connected via internal Docker bridge network (`imoveis-net`), executed as non-root user (UID 1000).
