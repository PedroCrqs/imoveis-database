import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
SCRIPTS_PATH = BASE_DIR / "scripts" / "schema.sql"

# Carrega o .env explicitamente a partir da raiz do projeto (BASE_DIR),
# independente de onde o script for executado.
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/imoveis"
)

pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    kwargs={"row_factory": dict_row},
    open=True,
)
