# Database de Imóveis

> CLI para gerenciamento de imóveis residenciais com SQLite.

---

## 🇧🇷 Português

### Sobre

Sistema de linha de comando para cadastro e consulta de imóveis, condomínios, bairros e proprietários.

### Estrutura do projeto

```
imoveis-database/
├── data/
│   └── imoveis/          ← pastas dos imóveis (fotos + Descrição.txt)
│       └── imovel_xx/
│           ├── 0.jpg     ← capa
│           ├── 1.jpg
│           └── Descrição.txt
├── scripts/
│   └── schema.sql
└── src/
    ├── database.py
    ├── main.py
    ├── repository.py
    └── seed.py
```

### Instalação

```bash
git clone <repo>
cd imoveis-database
python -m venv venv
source venv/bin/activate
python src/seed.py    # popula os bairros iniciais
```

### Uso

```bash
python src/main.py
```

### Funcionalidades

| Opção | Função                        |
| ----- | ----------------------------- |
| 1     | Cadastrar bairro              |
| 2     | Cadastrar proprietário        |
| 3     | Cadastrar condomínio          |
| 4     | Cadastrar imóvel              |
| 5     | Atualizar status do imóvel    |
| 6     | Atualizar preços              |
| 7     | Corrigir um campo             |
| 8     | Buscar imóvel por ID          |
| 9     | Buscar imóveis por bairro     |
| 10    | Listar imóveis disponíveis    |
| 11    | Buscar proprietário por ID    |
| 12    | Buscar imóveis por condomínio |

### Convenções

- **Fotos:** coloque todas as imagens `.jpg`/`.jpeg`/`.png` na pasta do imóvel em "Opções Diretas". A foto de capa deve se chamar `0` (ex: `0.jpg`).
- **Descrição:** arquivo `Descrição.txt` na mesma pasta das fotos. Suporta formatação WhatsApp (`*negrito*`, `_itálico_`). Atualizado automaticamente ao alterar preços.
- **Status do imóvel:** `Disponível` | `Vendido` | `Alugado` | `Retirado de Venda`
- **Backup:** ao abrir, sincroniza Drive → local. Ao operar, sincroniza local → Drive. Incremental por hash MD5.

### Tecnologias

- Python 3.10+
- SQLite3
- pathlib
- webbrowser
- asyncio
- hashlib

### Diferenciais Técnicos

- **Auditoria Automática:** Todas as alterações de valor e status são registradas via _Triggers_ no SQLite, garantindo integridade e histórico.
- **Performance:** Índices otimizados para consultas de busca por bairro e status.
- **Integridade:** Validação rigorosa de tipos (`REAL`, `CHECK` constraints) e _Foreign Keys_ ativas.

---

## 🇺🇸 English

### About

A command-line system for managing residential properties, condos, neighborhoods, and owners. Built to feed a WhatsApp listing automation bot.

### Project structure

```
imoveis-database/
├── data/
│   └── imoveis/          ← property folders (photos + Descrição.txt)
│       └── imovel_xx/
│           ├── 0.jpg     ← cover photo
│           ├── 1.jpg
│           └── Descrição.txt
├── scripts/
│   └── schema.sql
└── src/
    ├── database.py
    ├── main.py
    ├── repository.py
    └── seed.py
```

### Setup

```bash
git clone <repo>
cd imoveis-database
python -m venv venv
source venv/bin/activate
python src/seed.py    # seeds initial neighborhoods
```

### Usage

```bash
python src/main.py
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

### Conventions

- **Photos:** place all `.jpg`/`.jpeg`/`.png` images in the property folder inside "Opções Diretas". Cover photo must be named `0` (e.g. `0.jpg`).
- **Description:** `Descrição.txt` in the same folder as photos. Supports WhatsApp formatting (`*bold*`, `_italic_`). Auto-updated when prices change.
- **Property status:** `Disponível` | `Vendido` | `Alugado` | `Retirado de Venda`
- **Backup:** on open, syncs Drive → local. On every operation, syncs local → Drive. Incremental via MD5 hash.

### Stack

- Python 3.10+
- SQLite3
- pathlib
- webbrowser
- asyncio
- hashlib

### Key Features

- **Automatic Auditing:** All price and status changes are logged via SQLite Triggers, ensuring data integrity and history.
- **Performance:** Optimized indexes for fast filtering by neighborhood and status.
- **Integrity:** Strict type validation (`REAL`, `CHECK` constraints) and active _Foreign Keys_.
