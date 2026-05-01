# Changelog

---

## 🇧🇷 Português

Todas as mudanças relevantes deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

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

### [1.0.0] — 2025-05-01

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
