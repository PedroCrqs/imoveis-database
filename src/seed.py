import sqlite3
from database import DB_PATH


def populate_bairros() -> None:
    bairros = [
        ("Recreio dos Bandeirantes", "Zona Sudoeste"),
        ("Barra da Tijuca", "Zona Sudoeste"),
        ("Barra Olímpica", "Zona Sudoeste"),
        ("Jacarepaguá", "Zona Sudoeste"),
        ("Freguesia", "Zona Sudoeste"),
        ("Vargem Pequena", "Zona Sudoeste"),
        ("Vargem Grande", "Zona Sudoeste"),
        ("Laranjeiras", "Zona Sul"),
        ("Flamengo", "Zona Sul"),
        ("Botafogo", "Zona Sul"),
        ("Copacabana", "Zona Sul"),
    ]

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO Bairros (Nome, BairroZona) VALUES (?, ?)", bairros
        )
        conn.commit()
        print(f"[OK] {cursor.rowcount} neighborhoods successfully added.")


if __name__ == "__main__":
    populate_bairros()
