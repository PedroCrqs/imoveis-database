# Changelog

---

## 🇧🇷 Português

Todas as mudanças relevantes deste projeto serão documentadas aqui.  
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

### [1.1.0] — 2026-05-01

#### Adicionado

- Implementação de sistema de auditoria automática via **Triggers** (Gatilhos) no SQLite.
- Nova tabela `Auditoria_Imoveis` para persistência de histórico de alterações.
- Gatilhos automáticos (`log_imovel_insert`, `log_imovel_update_status`, `log_imovel_update_valor`) que operam em nível de banco de dados.
- Validação de formato de e-mail na tabela `Proprietarios` (`CHECK` constraint).

#### Melhorado

- Refinamento do schema SQL: uso de `REAL` para valores monetários e metragens para maior precisão.
- Adição de restrição `UNIQUE` em `CaminhoArquivo` na tabela `Fotos` para evitar duplicidade.
- Otimização de performance com novos índices: `idx_auditoria_imovel`.
- Melhoria na robustez da CLI: substituição de inputs restritivos por navegação mais fluida no `main.py`.
- Tratamento de exceções aprimorado para evitar crashes durante a navegação.

### [1.0.0] — 2025-05-01

#### Adicionado

- Schema SQLite inicial.
- CLI interativa com menu numerado.
- Upload de fotos e leitura de descrições.
- Funcionalidades básicas de CRUD imobiliário.

---

## 🇺🇸 English

All notable changes to this project will be documented here.  
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

### [1.1.0] — 2026-05-01

#### Added

- Automated audit system via SQLite **Triggers**.
- New `Auditoria_Imoveis` table for activity logging.
- Automated triggers for `INSERT` and updates on `Valor` and `Status` fields.
- Email format validation on `Proprietarios` table.

#### Improved

- SQL schema refinement: `REAL` types for monetary values and area measurements.
- Added `UNIQUE` constraint to `CaminhoArquivo` in `Fotos` table.
- Performance optimization with additional indexes (`idx_auditoria_imovel`).
- Improved CLI robustness and navigation flow.
