# Changelog

---

## 🇧🇷 Português

Todas as mudanças relevantes deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

### [2.1.1] — 2026-08-28

#### Corrigido

- **`Fotos.Principal` incompatível com Postgres em `add_photos()`**: o insert enviava um `bool` nativo do Python (`photo.stem == "0"`), mas a coluna `Principal` no banco real é `SMALLINT` (herdada da migração do SQLite, que não possui tipo `boolean`) — nunca foi convertida para `boolean` de fato, apesar do `schema.sql` declarar isso desde a v2.0.0. O erro (`column "principal" is of type smallint but expression is of type boolean`) só surgiu no imóvel 102, primeiro cadastro cuja pasta continha um arquivo `0.jpg`/`0.png` (capa = `True`); com `False`, o bug ficava mascarado. Corrigido convertendo o valor para `int` antes do insert (`int(photo.stem == "0")`)
- **`schema.sql` desatualizado em relação ao banco real**: declaração de `Fotos.Principal` corrigida de `BOOLEAN DEFAULT FALSE` para `SMALLINT DEFAULT 0`, refletindo o tipo real da coluna em produção. Sem efeito no banco já existente (`CREATE TABLE IF NOT EXISTS` não altera tabelas criadas) — mudança apenas documental, para impedir a mesma confusão de diagnóstico no futuro

---

### [2.1.0] — 2026-08-24

#### Adicionado

- **`sync_descricoes.py`**: novo script (`scripts/`) que sincroniza a coluna `Descricao` dos imóveis com status `Disponível` a partir do arquivo `Descrição.txt` de cada imóvel. Fonte única de verdade: `Imoveis.CaminhoDrive` (pasta sincronizada via rclone) — a pasta local não é usada de propósito. Roda em modo dry-run por padrão; usa `--apply` para persistir as alterações no banco

#### Corrigido

- **Carregamento de variáveis de ambiente em `database.py`**: `DATABASE_URL` era lido diretamente de `os.environ`, sem chamada a `load_dotenv()`. Como o `.env` nunca era carregado, a conexão sempre caía no valor padrão hardcoded (`postgres:postgres@localhost`), causando falha de autenticação (`password authentication failed for user "postgres"`) mesmo com credenciais corretas no `.env`. Corrigido com `load_dotenv(BASE_DIR / ".env")`, usando caminho absoluto para não depender do diretório de onde o script é executado
- **`CaminhoDrive` duplicado entre imóveis diferentes**: identificado, durante a primeira execução do `sync_descricoes.py`, que os imóveis 74 e 95 apontavam para a mesma pasta no Drive (`.../Prédio Baixo - Gleba B - Rua Demosthenes Madureira de Pinho`), fazendo o imóvel 95 receber a descrição do imóvel 74. Corrigido o valor de `CaminhoDrive` do imóvel 95 no banco para apontar para a pasta correta (`...de Pinho C`)

---

### [2.0.0] — 2026-08-24

#### Adicionado

- **Migração completa de SQLite para PostgreSQL**: `database.py` reescrito com `psycopg` (v3) e `psycopg_pool.ConnectionPool` compartilhado por todo o processo. `repository.py` totalmente adaptado — placeholders `?` → `%s`, `cursor.lastrowid` → `RETURNING`, `row_factory=dict_row` para acesso estruturado por chaves
- **`schema.sql` traduzido para PL/pgSQL**: `AUTOINCREMENT` → `SERIAL`; triggers convertidas para `FUNCTION` + `TRIGGER` (`log_imovel_insert`, `log_imovel_update_status`, `log_imovel_update_valor`)
- **Trigger e índices recuperados**: `log_imovel_update_valor` (perdida em traduções anteriores) restaurada, junto com `idx_auditoria_imovel`, `idx_dispatched_date`, `idx_cycle_instance`
- **`migrate_sqlite_to_pg.py`**: script de migração respeitando a ordem de Chaves Estrangeiras (`Proprietarios → Bairros → Condominios → Imoveis → Fotos → Auditoria_Imoveis → Dispatched_Today → Dispatch_Cycle`), com triggers de auditoria desativadas durante a cópia (`ALTER TABLE ... DISABLE/ENABLE TRIGGER ALL`), transação única com rollback integral em caso de falha, e realinhamento de sequences ao final
- **Dockerização**: `Dockerfile` (`python:3.12-slim` + `psycopg[binary]`) e `docker-compose.yml` orquestrando Postgres 16 (`db`), a CLI (`imoveis-cli`) e as 3 instâncias do robô de disparo (`wpp-account1/2/3`) — todos os serviços rodando como usuário não-root (`user: "1000:1000"`); `shm_size: 2gb` adicionado aos bots para evitar crashes do Chromium/Puppeteer por `/dev/shm` insuficiente
- **`.dockerignore`**: exclui diretórios de dados/runtime (`pgdata/`, `data/`, `drive-mount/`) do contexto de build

#### Removido

- **Sincronização do arquivo `.db` via Drive**: `backup.py` não copia mais o SQLite de/para o Google Drive — o Postgres é acessado diretamente por todos os serviços (CLI, site, robôs). A sincronização de fotos (`sync_photos`, upload/download em lote entre `data/imoveis/` e a pasta do Drive) permanece e foi **testada e confirmada funcionando** após a migração

#### Corrigido

- **Mapeamento de colunas**: `add_condo()` usava a coluna legada com cedilha (`Endereço`) em vez do nome correto no Postgres (`Endereco`); typo histórico em `update_condo_name()` corrigido
- **Tipos incompatíveis com o Postgres**: cast explícito de `Fotos.Principal` (inteiro 0/1 no SQLite) para `bool` antes do `INSERT`
- **Case-folding causando `relation "Proprietarios" does not exist`**: `migrate_sqlite_to_pg.py` envolvia tabelas/colunas em aspas duplas, tornando-as case-sensitive, enquanto o `schema.sql` as cria sem aspas (Postgres dobra para minúsculo automaticamente). Corrigido removendo as aspas no `INSERT`, no `DISABLE/ENABLE TRIGGER`, e com `.lower()` explícito em `pg_get_serial_sequence()` (que recebe os nomes como string literal, sem passar pelo fold de case do parser SQL)
- **Sintaxe YAML inválida em `environment` dos `wpp-account1/2/3`**: mistura de sintaxe de lista com sintaxe de mapa no mesmo bloco, causando falha no `docker compose up -d`. Corrigido padronizando para `- CHAVE=valor`

#### Conhecido / pendências desta versão

> Itens abaixo **não foram validados em produção** e não devem ser lidos como resolvidos — documentados aqui para rastreabilidade.

- **`DESKTOP_PATH` (`/home/pedrocrqs/Desktop`) hardcoded em `main.py`, sem bind-mount correspondente no `docker-compose.yml`**: o fluxo de cadastro de imóvel novo (que depende dessa pasta de staging) ainda não foi testado dentro do container — provável falha até o volume ser adicionado
- **`CaminhoDrive` legado com `~` literal nunca expande**: nenhuma chamada a `.expanduser()` existe no código. Imóveis cadastrados antes da migração, com `CaminhoDrive` salvo como `~/majesto-drive/...`, têm o path tratado literalmente pelo `pathlib` — afeta a gestão da pasta "Opções Diretas" em `handle_update_status()`. Diferente da sincronização em lote de fotos (que usa `DRIVE_DIR` diretamente e já foi testada), esse fluxo por imóvel ainda não foi exercitado
- **Volumes de `wpp-account1/2/3` apontando para o mesmo caminho no host** (`../wpp-scheduler/data`), apesar de comentários no `docker-compose.yml` indicarem isolamento — separação real (subpasta por conta) ainda não aplicada
- **`pgdata` migrado de bind-mount (`./pgdata`) para volume nomeado do Docker**: confirmar que os dados já migrados foram carregados para o volume novo antes de depender dele em produção
- **Acesso ao Drive migrado de sidecar `rclone`+FUSE dentro do Docker para mount no host**: `imoveis-cli` agora recebe `/home/pedrocrqs/majesto-drive` via bind-mount (`DRIVE_DIR` aponta pra lá), assumindo que o `rclone` roda fora do container (ex: via systemd) — mais simples e testado para sync em lote, mas depende da configuração do host permanecer estável

---

### [1.6.0] — 2026-06-25

#### Adicionado

- **Atualização de nome de condomínio**: adicionadas as funções `update_condo_name` no `repository.py` e `handle_update_condo_name` no `main.py`, permitindo alterar o nome de condomínios já cadastrados diretamente pela CLI
- **Nova opção `[13] Update condo name`** adicionada ao menu principal

#### Corrigido

- **Fluxo de backup após alterações**: adicionada a chamada `do_backup("upload", True)` após operações de atualização de imóveis para garantir a sincronização correta entre banco de dados, pasta local e Drive
- Corrigido problema em que alterações realizadas nos imóveis eram persistidas apenas localmente, sem serem enviadas ao backup remoto

---

### [1.5.1] — 2026-06-18

#### Corrigido

- **do_backup(download) adicionado**: antes de cada operação que vá alterar a database ou a pasta de arquivos para evitar conflito com alterações feitas pelo robô.

---

### [1.5.0] — 2026-05-12

#### Adicionado

- **Referência de ID nos anúncios** (`add_ref.py`): novo módulo que injeta `_Ref: {ImovelID}_` na terceira linha do `Descrição.txt`, sincronizando `.db`, pasta local e pasta no Drive. Restrito a imóveis com status `Disponível`. Idempotente via regex — nunca duplica a linha
- **`add_ref_to_all()`**: função de migração que aplica a referência em todos os imóveis disponíveis existentes, tratando o caso em que o `.txt` já foi patchado mas o banco ainda não foi atualizado (usa o `.txt` local como fonte da verdade)
- **Normalização NFC**: `_patch_txt` normaliza o nome do arquivo via `unicodedata.normalize("NFC")` para compatibilidade com filesystems que salvam em NFD

#### Corrigido

- **Ref injetada no cadastro**: ao cadastrar um novo imóvel, `_patch_txt` é chamado nas pastas local e do Drive imediatamente após a criação, e o banco é atualizado com a descrição já contendo a ref

---

### [1.4.2] — 2026-05-11

#### Corrigido

- **Regex de Preços**: Ajustado o padrão de busca em `update_description_prices` para evitar a captura de quebras de linha (`\n`). O uso anterior de `\s` causava espaçamentos duplos indesejados no arquivo `Descrição.txt`.
- **TypeError no Processamento**: Removida a criação acidental de uma tupla na atribuição da variável `text`, que gerava o erro `expected string or bytes-like object, got 'tuple'`.
- **Saneamento de Formatação**: Removida a inserção manual de `\n` nas f-strings de substituição de Condomínio e IPTU para preservar a estrutura original do documento.

---

### [1.4.1] — 2026-05-07

#### Corrigido

- **Performance do `sync_folder`**: removida comparação via hash MD5 de todos os arquivos durante o backup incremental. O sistema agora compara apenas `st_size` e `st_mtime`, reduzindo drasticamente operações de I/O, uso de CPU e tempo de sincronização em diretórios grandes
- **Mapeamento de `CaminhoDrive` e `LinkPublico`**: corrigida inversão dos parâmetros no fluxo de cadastro de imóveis — os campos agora são persistidos corretamente na tabela `Imoveis`

---

### [1.4.0] — 2026-05-05

#### Adicionado

- **Integração com o robô wpp-scheduler**: Agora a database irá alimentar o ciclo de disparos automáticos de mensagens efetuados pelo robô wpp-scheduler. Para tanto, foram criadas duas novas tabelas para o imoveis.db: `Dispatch_Cicle` e `Dispatched_Today`. Sendo esta responsável por impedir que o robô dispare a mesma mensagem no mesmo dia (ainda que em diferentes instâncias) e aquela responsável pelo controle do ciclo de disparos do robô, fazendo com que ele só volte a disparar o mesmo imóvel quando todos os imóveis com status DISPONÍVEL da tabela `Imoveis`forem disparados, reiniciando o ciclo.

#### Corrigido

- Função `do_backup()` causando lentidão desnecessária no sistema efetuanco `sync_folder` desnecessáriamente mesmo quando a mudança é apenas no arquivo .db. A solução foi adicionar um segundo argumento booleano `sync=False` na função principal e adicionar um bloco `if` identado ao `do_backup("upload")` que só executa quando `sync == True`
- A chamada `do_backup("upload", True)` só irá ocorrer em três momentos: 1º: ao adicionar um novo imóvel, 2º: ao trocar o preço de um imóvel, 3º: ao trocar o status do imóvel

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

### [2.1.1] — 2026-08-28

#### Fixed

- **`Fotos.Principal` type mismatch with Postgres in `add_photos()`**: the insert sent a native Python `bool` (`photo.stem == "0"`), but the `Principal` column in the real database is `SMALLINT` (inherited from the SQLite migration, which has no `boolean` type) — it was never actually converted to `boolean`, despite `schema.sql` declaring it as such since v2.0.0. The error (`column "principal" is of type smallint but expression is of type boolean`) only surfaced on property 102, the first registration whose folder contained a `0.jpg`/`0.png` file (cover = `True`); with `False`, the bug stayed masked. Fixed by converting the value to `int` before the insert (`int(photo.stem == "0")`)
- **`schema.sql` out of sync with the real database**: `Fotos.Principal` declaration corrected from `BOOLEAN DEFAULT FALSE` to `SMALLINT DEFAULT 0`, reflecting the column's actual type in production. No effect on the existing database (`CREATE TABLE IF NOT EXISTS` doesn't alter already-created tables) — documentation-only change, to prevent the same diagnostic confusion in the future

---

### [2.1.0] — 2026-08-24

#### Added

- **`sync_descricoes.py`**: new script (`scripts/`) that syncs the `Descricao` column for properties with status `Disponível` from each property's `Descrição.txt` file. Single source of truth: `Imoveis.CaminhoDrive` (folder synced via rclone) — the local folder is intentionally not used. Runs in dry-run mode by default; use `--apply` to persist changes to the database

#### Fixed

- **Environment variable loading in `database.py`**: `DATABASE_URL` was being read directly from `os.environ`, with no `load_dotenv()` call. Since the `.env` file was never loaded, the connection always fell back to the hardcoded default (`postgres:postgres@localhost`), causing authentication failures (`password authentication failed for user "postgres"`) even with correct credentials in `.env`. Fixed with `load_dotenv(BASE_DIR / ".env")`, using an absolute path so it doesn't depend on the directory the script is run from
- **Duplicate `CaminhoDrive` across different properties**: identified, during the first run of `sync_descricoes.py`, that properties 74 and 95 pointed to the same Drive folder (`.../Prédio Baixo - Gleba B - Rua Demosthenes Madureira de Pinho`), causing property 95 to receive property 74's description. Fixed property 95's `CaminhoDrive` value in the database to point to the correct folder (`...de Pinho C`)

---

### [2.0.0] — 2026-08-24

#### Added

- **Complete migration from SQLite to PostgreSQL**: `database.py` rewritten using `psycopg` (v3) with a `psycopg_pool.ConnectionPool` shared across the whole process. `repository.py` fully adapted — `?` placeholders → `%s`, `cursor.lastrowid` → `RETURNING`, `row_factory=dict_row` for structured key-based access
- **`schema.sql` translated to PL/pgSQL**: `AUTOINCREMENT` → `SERIAL`; triggers converted to `FUNCTION` + `TRIGGER` (`log_imovel_insert`, `log_imovel_update_status`, `log_imovel_update_valor`)
- **Recovered trigger and indexes**: `log_imovel_update_valor` (lost in earlier translations) restored, along with `idx_auditoria_imovel`, `idx_dispatched_date`, `idx_cycle_instance`
- **`migrate_sqlite_to_pg.py`**: migration script respecting Foreign Key order (`Proprietarios → Bairros → Condominios → Imoveis → Fotos → Auditoria_Imoveis → Dispatched_Today → Dispatch_Cycle`), with audit triggers disabled during the copy (`ALTER TABLE ... DISABLE/ENABLE TRIGGER ALL`), a single transaction with full rollback on failure, and sequence realignment at the end
- **Dockerization**: `Dockerfile` (`python:3.12-slim` + `psycopg[binary]`) and `docker-compose.yml` orchestrating Postgres 16 (`db`), the CLI (`imoveis-cli`), and the 3 dispatch bot instances (`wpp-account1/2/3`) — all services running as a non-root user (`user: "1000:1000"`); `shm_size: 2gb` added to the bots to prevent Chromium/Puppeteer crashes from insufficient `/dev/shm`
- **`.dockerignore`**: excludes data/runtime directories (`pgdata/`, `data/`, `drive-mount/`) from the build context

#### Removed

- **`.db` file sync via Drive**: `backup.py` no longer copies the SQLite file to/from Google Drive — Postgres is accessed directly by all services (CLI, site, bots). Photo sync (`sync_photos`, bulk upload/download between `data/imoveis/` and the Drive folder) remains and has been **tested and confirmed working** after the migration

#### Fixed

- **Column mapping**: `add_condo()` used the legacy column with a cedilla (`Endereço`) instead of the correct Postgres name (`Endereco`); a long-standing typo in `update_condo_name()` fixed
- **Types incompatible with Postgres**: explicit cast of `Fotos.Principal` (0/1 integer in SQLite) to `bool` before `INSERT`
- **Case-folding causing `relation "Proprietarios" does not exist`**: `migrate_sqlite_to_pg.py` wrapped tables/columns in double quotes, making them case-sensitive, while `schema.sql` creates them unquoted (Postgres auto-folds to lowercase). Fixed by removing the quotes in the `INSERT`, in `DISABLE/ENABLE TRIGGER`, and with an explicit `.lower()` in `pg_get_serial_sequence()` (which takes names as string literals, bypassing the SQL parser's case-folding)
- **Invalid YAML syntax in `wpp-account1/2/3`'s `environment`**: list syntax mixed with map syntax in the same block, causing `docker compose up -d` to fail. Fixed by standardizing to `- KEY=value`

#### Known / pending in this version

> The items below have **not been validated in production** and should not be read as resolved — documented here for traceability.

- **`DESKTOP_PATH` (`/home/pedrocrqs/Desktop`) hardcoded in `main.py`, with no matching bind mount in `docker-compose.yml`**: the new-property registration flow (which depends on this staging folder) has not yet been tested inside the container — likely to fail until the volume is added
- **Legacy `CaminhoDrive` values with a literal `~` never expand**: no `.expanduser()` call exists anywhere in the codebase. Properties registered before the migration, with `CaminhoDrive` stored as `~/majesto-drive/...`, have the path treated literally by `pathlib` — affects "Opções Diretas" folder management in `handle_update_status()`. Unlike the bulk photo sync (which uses `DRIVE_DIR` directly and has been tested), this per-property flow has not yet been exercised
- **`wpp-account1/2/3` volumes pointing at the same host path** (`../wpp-scheduler/data`), despite inline comments in `docker-compose.yml` suggesting isolation — real separation (a distinct subfolder per account) is still pending
- **`pgdata` moved from a bind mount (`./pgdata`) to a Docker-managed named volume**: confirm previously migrated data was carried over into the new volume before relying on this in production
- **Drive access moved from an in-Docker `rclone`+FUSE sidecar to a host-level mount**: `imoveis-cli` now receives `/home/pedrocrqs/majesto-drive` via bind mount (`DRIVE_DIR` points there), assuming `rclone` runs outside the container (e.g. via systemd) — simpler, and tested for bulk sync, but depends on the host configuration remaining stable

---

### [1.6.0] — 2026-06-25

#### Added

- **Condo name update support**: added `update_condo_name` in `repository.py` and `handle_update_condo_name` in `main.py`, allowing existing condominium names to be updated directly from the CLI
- **New `[13] Update condo name`** option added to the main menu

#### Fixed

- **Backup flow after updates**: added `do_backup("upload", True)` after property update operations to ensure proper synchronization between database, local folders and Drive
- Fixed an issue where property changes were being saved locally but were not propagated to the remote backup

---

### [1.5.1] — 2026-06-18

#### Fixed

- **do_backup(download) added**: before each operation that will modify the database or file folder to avoid conflicts with changes made by the robot.

---

### [1.5.0] — 2026-05-12

#### Added

- **Property ID reference in listings** (`add_ref.py`): new module that injects `_Ref: {ImovelID}_` on the third line of `Descrição.txt`, syncing `.db`, local folder, and Drive folder. Restricted to properties with status `Disponível`. Idempotent via regex — never duplicates the line
- **`add_ref_to_all()`**: migration function that applies the reference to all existing available properties, handling the case where the `.txt` was already patched but the database was not yet updated (uses local `.txt` as source of truth)
- **NFC normalization**: `_patch_txt` normalizes filenames via `unicodedata.normalize("NFC")` for compatibility with filesystems that store in NFD

#### Fixed

- **Ref injected on registration**: when registering a new property, `_patch_txt` is called on both local and Drive folders immediately after creation, and the database is updated with the description already containing the ref

---

### [1.4.2] — 2026-05-11

#### Fixed

- **Price Regex**: Adjusted the search pattern in `update_description_prices` to prevent capturing newlines (`\n`). The previous use of `\s` was causing unwanted double spacing in `Descrição.txt`.
- **Processing TypeError**: Fixed an accidental tuple assignment to the `text` variable that caused the `expected string or bytes-like object, got 'tuple'` error.
- **Formatting Cleanup**: Removed manual `\n` insertion in replacement f-strings for Condo and Tax fees to preserve the original document structure.

---

### [1.4.1] — 2026-05-07

#### Fixed

- **`sync_folder` performance**: removed MD5 hash comparison for all files during incremental backup. The system now compares only `st_size` and `st_mtime`, drastically reducing I/O operations, CPU usage, and synchronization time on large directories
- **`CaminhoDrive` and `LinkPublico` mapping**: fixed inverted parameter order during property creation flow — fields are now correctly persisted in the `Imoveis` table

---

### [1.4.0] — 2026-05-05

#### Added

- **Integration with the wpp-scheduler bot**: Now the database will feed the cycle of automatic occasional message dispatches by the wpp-scheduler robot. To this end, two new tables were created for imoveis.db: `Dispatch_Cicle` and `Dispatched_Today`. The latter is responsible for preventing the robot from dispatching the same message on the same day (even in different instances), and the former is responsible for controlling the robot's dispatch cycle, ensuring that it only dispatches the same property again when all properties with the AVAILABLE status in the `Imóveis` table have been dispatched, restarting the cycle.

#### Fixed

- The `do_backup()` function causes unnecessary system slowdown by occasionally performing `sync_folder` even when the change is only in the .db file. The solution was to add a second boolean argument `sync=False` to the main function and add an `if` block identified with `do_backup("upload")` that is only executed when `sync == True`
- The call `do_backup("upload", True)` will only occur in three moments: 1st: when adding a new property, 2nd: when changing the price of a property, 3rd: when changing the status of the property

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
