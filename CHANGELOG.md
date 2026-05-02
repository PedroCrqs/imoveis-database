# Changelog

---

## 🇧🇷 Português

Todas as mudanças relevantes deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

### [1.2.0] — 2026-05-02

#### Adicionado

- **Incluído no MENU principal**: Função para pesquisar imóveis disponíveis com base no ID do condomínio. Alteração abrange novas funções em main.py e repository.py para pesquisa de imóveis e captura dos nomes dos condomínios.

#### Melhorado

- **schema.sql**: Atualização do schema SQL para remover verificação de e-mail. Essa verificação é desnecessária, visto que eu geralmente não recolho o e-mail do proprietário. Toda comunicação é feita via WhatsApp.
- **Menu principal**: Agora, além do nome do Condomínio, o nome do Bairro também aparece nas interações visuais. Além disso, fiz algumas melhorias visuais do MENU para melhor simetria.

---

### [1.1.0] — 2026-05-01

#### Adicionado

- **Padronização Automática de Pastas**: Nova lógica no `main.py` que move e renomeia automaticamente a pasta de fotos para `data/imoveis/imovel_{id}` após o cadastro bem-sucedido.
- **Gestão de Caminhos Robustos**: Integração com `pathlib.Path.resolve()` para garantir que o script localize as pastas corretamente, independente do diretório de execução.
- **Auditoria Automática**: Implementação de sistema de auditoria via **Triggers** no SQLite para rastrear mudanças críticas em `Valor` e `Status`[cite: 18].
- **Persistência de Histórico**: Criação da tabela `Auditoria_Imoveis` para log de eventos de inserção e atualização[cite: 18].
- **Validação de Dados**: Adição de constraint `CHECK` para garantir o formato correto de e-mail na tabela `Proprietarios`[cite: 18].

#### Melhorado

- **Precisão Numérica**: Atualização do schema SQL para utilizar o tipo `REAL` em campos de valores e metragens[cite: 18].
- **Integridade de Mídia**: Restrição `UNIQUE` aplicada ao `CaminhoArquivo` na tabela `Fotos` para evitar duplicidade[cite: 18].
- **Performance**: Otimização de consultas através do índice `idx_auditoria_imovel`[cite: 18].
- **CLI**: Melhoria no tratamento de exceções (erros de diretório e banco de dados) para uma navegação sem interrupções[cite: 17, 18].

---

### [1.0.0] — 2025-05-01

#### Adicionado

- Schema SQLite com tabelas `Proprietarios`, `Bairros`, `Condominios`, `Imoveis`, `Fotos`
- Índices em `BairroID` e `ImovelStatus` para performance de leitura
- CLI interativa com menu numerado e dispatch table
- Cadastro de bairros, proprietários, condomínios e imóveis
- Upload de fotos via pasta — arquivo `0.jpg` definido como capa automaticamente
- Leitura de descrição a partir de `Descrição.txt` na pasta do imóvel
- Atualização de status do imóvel (`Disponível`, `Vendido`, `Alugado`, `Retirado de Venda`)
- `DataVenda` preenchida automaticamente ao marcar como `Vendido` ou `Alugado`
- Atualização pontual de preços (`Valor`, `ValorCondominio`, `IPTU`)
- Correção de campos via whitelist — proteção contra SQL injection
- Consulta de imóvel por ID com acesso à pasta de fotos via `webbrowser`
- Consulta de imóveis por bairro e listagem de disponíveis
- Consulta de proprietário por ID
- Separação clara entre camada de UI (`main.py`) e camada de dados (`repository.py`)
- `seed.py` com bairros do Rio de Janeiro pré-cadastrados

---

## 🇺🇸 English

All notable changes to this project will be documented here.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

### [1.2.0] — 2026-05-02

#### Added

- **Included in the main MENU**: Function to search for available properties based on the condominium ID. The change includes new functions in main.py and repository.py for property search and capturing condominium names.

#### Improved

- **schema.sql**: Updated the SQL schema to remove email verification. This verification is necessary, as I generally don't collect the owner's email. All communication is done via WhatsApp.
- **Main Menu**: Now, in addition to the Condominium name, the Neighborhood name also appears in the visual interactions. Furthermore, we made some visual improvements to the MENU for better symmetry.

---

### [1.1.0] — 2026-05-01

#### Added

- **Automated Folder Standardization**: Logic to move and rename photo folders to `data/imoveis/imovel_{id}` upon registration.
- **Robust Path Management**: Use of absolute path anchoring with `pathlib` to prevent environment-related errors.
- **Automated Auditing**: SQLite **Triggers** for tracking `Price` and `Status` modifications[cite: 18].

#### Improved

- **SQL Schema**: Switched to `REAL` types for financial accuracy[cite: 18].
- **CLI Robustness**: Better exception handling for directory and database operations[cite: 17, 18].

---

### [1.0.0] — 2026-05-01

#### Added

- SQLite schema with tables `Proprietarios`, `Bairros`, `Condominios`, `Imoveis`, `Fotos`
- Indexes on `BairroID` and `ImovelStatus` for read performance
- Interactive CLI with numbered menu and dispatch table
- Registration of neighborhoods, owners, condos, and properties
- Photo upload via folder — file named `0.jpg` is automatically set as cover
- Description loaded from `Descrição.txt` inside the property folder
- Property status updates (`Disponível`, `Vendido`, `Alugado`, `Retirado de Venda`)
- `DataVenda` auto-filled when status is set to `Vendido` or `Alugado`
- Targeted price updates (`Valor`, `ValorCondominio`, `IPTU`)
- Field correction via whitelist — SQL injection protection
- Property lookup by ID with photo folder access via `webbrowser`
- Property lookup by neighborhood and available listings view
- Owner lookup by ID
- Clear separation between UI layer (`main.py`) and data layer (`repository.py`)
- `seed.py` with pre-loaded Rio de Janeiro neighborhoods
