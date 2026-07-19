import os
from pathlib import Path

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
SCRIPTS_PATH = BASE_DIR / "scripts" / "schema.sql"

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/imoveis"
)

# Pool compartilhado por todo o processo. Aberto uma vez, reaproveitado em
# cada operação — evita o custo de handshake TCP a cada query, que fazia
# sentido no SQLite (arquivo local) mas seria desperdício num banco remoto.
pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    kwargs={"row_factory": dict_row},
    open=True,
)


def init_db() -> None:
    """Aplica o schema.sql no banco. Idempotente (CREATE TABLE/FUNCTION usam
    IF NOT EXISTS / OR REPLACE) — seguro rodar em todo deploy/subida do container."""
    DATA_PATH.mkdir(exist_ok=True)

    try:
        sql_script = SCRIPTS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ Error: File {SCRIPTS_PATH} not found.")
        return

    try:
        with pool.connection() as conn:
            conn.execute(sql_script)
        print("✔️ Database structure successfully created!")
    except psycopg.Error as e:
        print(f"❌ PostgreSQL error: {e}")


if __name__ == "__main__":
    init_db()
