# Database de Imóveis

> CLI para gerenciamento de imóveis residenciais com SQLite.

---

## 🇧🇷 Português

### Sobre

Sistema de linha de comando para cadastro e consulta de imóveis, condomínios, bairros e proprietários, com auditoria automática de alterações.

### Estrutura do projeto

imoveis-database/
├── data/
│ └── imoveis/ ← pastas dos imóveis (fotos + Descrição.txt)
├── scripts/
│ └── schema.sql
└── src/
├── main.py
├── repository.py
└── ...

### Funcionalidades

| Opção | Função                     |
| ----- | -------------------------- |
| 1     | Cadastrar bairro           |
| 2     | Cadastrar proprietário     |
| 3     | Cadastrar condomínio       |
| 4     | Cadastrar imóvel           |
| 5     | Atualizar status do imóvel |
| 6     | Atualizar preços           |
| 7     | Corrigir um campo          |
| 8     | Buscar imóvel por ID       |
| 9     | Buscar imóveis por bairro  |
| 10    | Listar imóveis disponíveis |
| 11    | Buscar proprietário por ID |

### Diferenciais Técnicos

- **Auditoria Automática:** Todas as alterações de valor e status são registradas via _Triggers_ no SQLite, garantindo integridade e histórico.
- **Performance:** Índices otimizados para consultas de busca por bairro e status.
- **Integridade:** Validação rigorosa de tipos (`REAL`, `CHECK` constraints) e _Foreign Keys_ ativas.

---

## 🇺🇸 English

### About

Command-line interface for managing residential real estate assets, with built-in database auditing.

### Key Features

- **Automatic Auditing:** All price and status changes are logged via SQLite Triggers, ensuring data integrity and history.
- **Performance:** Optimized indexes for fast filtering by neighborhood and status.
- **Integrity:** Strict type validation (`REAL`, `CHECK` constraints) and active _Foreign Keys_.
