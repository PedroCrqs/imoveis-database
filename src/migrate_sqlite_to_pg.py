"""
migrate_sqlite_to_pg.py
------------------------
Migra os dados do imoveis.db (SQLite) existente para o PostgreSQL novo.

Uso:
    python src/migrate_sqlite_to_pg.py /caminho/para/imoveis.db

Pressupõe que o schema já foi aplicado no Postgres (rode database.py / init_db()
antes, ou deixe o container "app" fazer isso na subida).

Ordem de migração respeita as Foreign Keys:
    Proprietarios → Bairros → Condominios → Imoveis → Fotos →
    Auditoria_Imoveis → Dispatched_Today → Dispatch_Cycle →
    raw_messages → opportunities

Detalhe importante: os triggers de auditoria (log_imovel_insert,
log_imovel_update_status, log_imovel_update_valor) são DESLIGADOS durante
a migração de `Imoveis`. Sem isso, cada imóvel migrado geraria uma entrada
falsa de "cadastrado agora" em Auditoria_Imoveis — a auditoria REAL (a que
já existe no .db antigo) é copiada logo em seguida, como dado histórico.

Ao final, as sequences (SERIAL) de cada tabela são realinhadas com o maior
ID já usado — senão o próximo INSERT feito pela aplicação colidiria com
os IDs recém-migrados.
"""

import sqlite3
import sys
from pathlib import Path

import psycopg

from database import DATABASE_URL

TABLES_IN_ORDER = [
    "Proprietarios",
    "Bairros",
    "Condominios",
    "Imoveis",
    "Fotos",
    "Auditoria_Imoveis",
    "Dispatched_Today",
    "Dispatch_Cycle",
    "raw_messages",
    "opportunities",
]

# Colunas que mudaram de nome entre o schema SQLite antigo e o novo Postgres.
# Ex: "Condominios.Endereço" (com cedilha) virou "Endereco" (sem cedilha).
COLUMN_RENAMES = {
    "Condominios": {"Endereço": "Endereco"},
}

# Colunas que são INTEGER (0/1) no SQLite mas BOOLEAN de verdade no Postgres.
# psycopg não converte int → bool automaticamente em query parametrizada —
# sem esse cast explícito, o INSERT falha com "column is of type boolean
# but expression is of type integer".
BOOL_COLUMNS = {
    "Fotos": {"Principal"},
}

# Tabelas que têm coluna SERIAL/PRIMARY KEY auto-incrementada e cuja sequence
# precisa ser realinhada após a migração (as duas últimas não têm serial).
SERIAL_COLUMNS = {
    "Proprietarios": "ProprietarioID",
    "Bairros": "BairroID",
    "Condominios": "CondominioID",
    "Imoveis": "ImovelID",
    "Fotos": "FotoID",
    "Auditoria_Imoveis": "LogID",
    "opportunities": "opportunity_id",
}


def table_exists_sqlite(sq_conn: sqlite3.Connection, table: str) -> bool:
    row = sq_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def migrate_table(sq_conn: sqlite3.Connection, pg_conn: psycopg.Connection, table: str) -> int:
    if not table_exists_sqlite(sq_conn, table):
        print(f"  [SKIP] '{table}' não existe no SQLite de origem.")
        return 0

    sq_conn.row_factory = sqlite3.Row
    rows = sq_conn.execute(f"SELECT * FROM {table}").fetchall()

    if not rows:
        print(f"  [OK]   '{table}': 0 registros (vazio).")
        return 0

    source_columns = rows[0].keys()
    renames = COLUMN_RENAMES.get(table, {})
    target_columns = [renames.get(c, c) for c in source_columns]

    col_list = ", ".join(target_columns)
    placeholders = ", ".join(["%s"] * len(target_columns))
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

    bool_cols = BOOL_COLUMNS.get(table, set())

    with pg_conn.cursor() as cur:
        for row in rows:
            values = [
                bool(row[c]) if c in bool_cols else row[c] for c in source_columns
            ]
            cur.execute(insert_sql, values)

    print(f"  [OK]   '{table}': {len(rows)} registro(s) migrado(s).")
    return len(rows)


def reset_sequences(pg_conn: psycopg.Connection) -> None:
    print("\nRealinhando sequences (SERIAL)...")
    with pg_conn.cursor() as cur:
        for table, column in SERIAL_COLUMNS.items():
            # pg_get_serial_sequence espera os nomes em "identifier normal
            # form" — ou seja, já em minúsculo para identificadores criados
            # sem aspas (nosso caso). Passar "ProprietarioID" como veio do
            # dict falha; "proprietarioid" funciona.
            table_lc = table.lower()
            column_lc = column.lower()
            cur.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_lc}', '{column_lc}'),
                    COALESCE((SELECT MAX({column}) FROM {table}), 1),
                    true
                )
                """
            )
    print("  [OK]   Sequences realinhadas.")


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python src/migrate_sqlite_to_pg.py /caminho/para/imoveis.db")
        sys.exit(1)

    sqlite_path = Path(sys.argv[1])
    if not sqlite_path.is_file():
        print(f"❌ Arquivo não encontrado: {sqlite_path}")
        sys.exit(1)

    print(f"Origem:  {sqlite_path}")
    print(f"Destino: {DATABASE_URL}\n")

    sq_conn = sqlite3.connect(sqlite_path)

    with psycopg.connect(DATABASE_URL, autocommit=False) as pg_conn:
        try:
            with pg_conn.cursor() as cur:
                # Desliga os triggers de auditoria só durante a migração de Imoveis,
                # para não gerar logs falsos de "cadastrado agora" para dados antigos.
                cur.execute("ALTER TABLE Imoveis DISABLE TRIGGER ALL;")

            total = 0
            for table in TABLES_IN_ORDER:
                total += migrate_table(sq_conn, pg_conn, table)

            with pg_conn.cursor() as cur:
                cur.execute("ALTER TABLE Imoveis ENABLE TRIGGER ALL;")

            reset_sequences(pg_conn)

            pg_conn.commit()
            print(f"\n✔️  Migração concluída — {total} registro(s) no total.")

        except Exception:
            pg_conn.rollback()
            print("\n❌ Migração abortada, rollback executado. Nenhum dado foi persistido.")
            raise
        finally:
            sq_conn.close()


if __name__ == "__main__":
    main()
