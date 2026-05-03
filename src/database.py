from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
SCRIPTS_PATH = BASE_DIR / "scripts" / "schema.sql"
DB_PATH = DATA_PATH / "imoveis.db"
DRIVE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "majesto-drive"


def init_db():
    DATA_PATH.mkdir(exist_ok=True)

    try:
        sql_script = SCRIPTS_PATH.read_text(encoding="utf-8")

        with sqlite3.connect(DB_PATH) as conn:
            conn.executescript(sql_script)
            print("✔️ Database structure successfully created!")

    except FileNotFoundError:
        print(f"❌ Error: File {SCRIPTS_PATH} not found.")
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")


if __name__ == "__main__":
    init_db()
