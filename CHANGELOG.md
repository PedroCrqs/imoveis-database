# Changelog

---

## 🇧🇷 Português

Todas as mudanças relevantes deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

### [1.3.1] — 2026-05-03

#### Corrigido

- **Fluxo de cadastro de imóvel**: pasta local `imovel_{id}` agora é criada após `add_property` — garantindo que o ID existe antes de ser usado no nome da pasta
- **Origem da pasta**: fluxo parte do Desktop (`~/Desktop/nome_pasta`), copia para "Opções Diretas" no Drive e para `data/imoveis/imovel_{id}`, depois apaga a pasta do Desktop

---

### [1.3.0] — 2026-05-03

#### Adicionado

- **Sistema de backup bidirecional**: `do_backup("upload")` sincroniza banco e pasta `imoveis/` do local para o Drive; `do_backup("download")` faz o inverso. Sync incremental via hash MD5 — só copia arquivos novos ou modificados
- **Sincronização automática de pastas**: `sync_folder` integrado ao `do_backup` — sem chamadas separadas no `main.py`
- **Ciclo de vida do imóvel em "Opções Diretas"**: ao marcar imóvel como vendido/alugado/retirado, a pasta no Drive é removida automaticamente; ao retornar para "Disponível", é restaurada a partir da pasta local
- **Arquivo oculto `.drive_folder_name.txt`**: salvo na pasta local do imóvel para permitir restauração da pasta no Drive com o nome original
- **Colunas `CaminhoDrive` e `LinkPublico`** na tabela `Imoveis`: armazenam o path local da pasta no Drive e o link público para o navegador
- **Atualização automática de `Descrição.txt`**: ao alterar preços via opção [6], os arquivos `Descrição.txt` local e do Drive são atualizados via regex com o padrão de formatação WhatsApp
- **`DRIVE_DIR` centralizado em `database.py`**: elimina import circular entre `repository.py` e `backup.py`
- **Triggers com `IF NOT EXISTS`**: `init_db` agora é idempotente para triggers

#### Corrigido

- Aliases redundantes `IMOVEIS_SRC`/`IMOVEIS_DST` removidos de `backup.py`
- Função `rename_to_id` removida de `main.py` — era definida mas nunca usada
- Condição de restauração de pasta no Drive corrigida — não depende mais de `drive_path` que pode apontar para path inexistente

---

### [1.2.0] — 2026-05-02

#### Adicionado

- Busca de imóveis por condomínio (`[12] Find a property by condominium`)
- `get_neighborhood_name` no repositório — nome do bairro exibido nas consultas

#### Melhorado

- `schema.sql`: remoção da validação de e-mail em `Proprietarios` — campo agora é `NULL`
- Menu principal: exibe nome do bairro além do condomínio nas interações visuais

---

### [1.1.0] — 2026-05-01

#### Adicionado

- Padronização automática de pastas: move e renomeia para `data/imoveis/imovel_{id}` após cadastro
- Auditoria automática via Triggers SQLite para `Valor` e `ImovelStatus`
- Tabela `Auditoria_Imoveis` com log de inserções e atualizações
- Índice `idx_auditoria_imovel` para performance de auditoria

#### Melhorado

- Schema: tipo `REAL` em campos financeiros e de metragem
- `CaminhoArquivo` em `Fotos` com constraint `UNIQUE`
- Tratamento de exceções na CLI para erros de diretório e banco

---

### [1.0.0] — 2026-05-01

#### Adicionado

- Schema SQLite com tabelas `Proprietarios`, `Bairros`, `Condominios`, `Imoveis`, `Fotos`
- Índices em `BairroID` e `ImovelStatus`
- CLI interativa com menu numerado e dispatch table
- Cadastro de bairros, proprietários, condomínios e imóveis
- Upload de fotos via pasta — `0.jpg` como capa automática
- Leitura de descrição a partir de `Descrição.txt`
- Atualização de status com preenchimento automático de `DataVenda`
- Atualização pontual de preços
- Correção de campos via whitelist — proteção contra SQL injection
- Consulta de imóvel por ID com acesso à pasta via `webbrowser`
- Consulta por bairro e listagem de disponíveis
- Consulta de proprietário por ID
- Separação clara entre `main.py` (UI) e `repository.py` (dados)
- `seed.py` com bairros do Rio de Janeiro pré-cadastrados

---

## 🇺🇸 English

All notable changes to this project will be documented here.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

### [1.3.1] — 2026-05-03

#### Fixed

- **Property registration flow**: local folder `imovel_{id}` is now created after `add_property` — ensuring the ID exists before being used in the folder name
- **Folder origin**: flow starts from Desktop (`~/Desktop/folder_name`), copies to "Opções Diretas" on Drive and to `data/imoveis/imovel_{id}`, then deletes the Desktop folder

---

### [1.3.0] — 2026-05-03

#### Added

- **Bidirectional backup system**: `do_backup("upload")` syncs database and `imoveis/` folder from local to Drive; `do_backup("download")` does the reverse. Incremental sync via MD5 hash — only copies new or modified files
- **Automatic folder sync**: `sync_folder` integrated into `do_backup` — no separate calls needed in `main.py`
- **Property lifecycle in "Opções Diretas"**: when marked as sold/rented/withdrawn, Drive folder is automatically removed; when restored to "Disponível", it is recreated from local folder
- **Hidden file `.drive_folder_name.txt`**: saved in local property folder to enable Drive folder restoration with original name
- **Columns `CaminhoDrive` and `LinkPublico`** in `Imoveis` table: store the local Drive path and public browser link
- **Automatic `Descrição.txt` update**: when prices are updated via option [6], both local and Drive `Descrição.txt` files are updated via regex matching WhatsApp formatting
- **`DRIVE_DIR` centralized in `database.py`**: eliminates circular import between `repository.py` and `backup.py`
- **Triggers with `IF NOT EXISTS`**: `init_db` is now idempotent for triggers

#### Fixed

- Redundant `IMOVEIS_SRC`/`IMOVEIS_DST` aliases removed from `backup.py`
- Unused `rename_to_id` function removed from `main.py`
- Drive folder restoration condition fixed — no longer depends on `drive_path` that may point to a deleted path

---

### [1.2.0] — 2026-05-02

#### Added

- Property search by condominium (`[12] Find a property by condominium`)
- `get_neighborhood_name` in repository — neighborhood name displayed in queries

#### Improved

- `schema.sql`: removed email validation in `Proprietarios` — field is now `NULL`
- Main menu: neighborhood name shown alongside condo name in visual interactions

---

### [1.1.0] — 2026-05-01

#### Added

- Automated folder standardization: moves and renames to `data/imoveis/imovel_{id}` after registration
- Automatic auditing via SQLite Triggers for `Valor` and `ImovelStatus`
- `Auditoria_Imoveis` table for insertion and update logs
- `idx_auditoria_imovel` index for audit query performance

#### Improved

- Schema: `REAL` type for financial and area fields
- `UNIQUE` constraint on `CaminhoArquivo` in `Fotos`
- Better exception handling in CLI for directory and database errors

---

### [1.0.0] — 2026-05-01

#### Added

- SQLite schema with tables `Proprietarios`, `Bairros`, `Condominios`, `Imoveis`, `Fotos`
- Indexes on `BairroID` and `ImovelStatus`
- Interactive CLI with numbered menu and dispatch table
- Registration of neighborhoods, owners, condos, and properties
- Photo upload via folder — `0.jpg` automatically set as cover
- Description loaded from `Descrição.txt`
- Status updates with automatic `DataVenda` fill
- Targeted price updates
- Field correction via whitelist — SQL injection protection
- Property lookup by ID with folder access via `webbrowser`
- Lookup by neighborhood and available listings view
- Owner lookup by ID
- Clear separation between `main.py` (UI) and `repository.py` (data)
- `seed.py` with pre-loaded Rio de Janeiro neighborhoods
