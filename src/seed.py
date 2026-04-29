from database import BASE_DIR, DATA_PATH, SCRIPTS_PATH, DB_PATH, sqlite3


def populate_bairros():
    bairros = [
        ("Laranjeiras", "Zona Sul"),
        ("Flamengo", "Zona Sul"),
        ("Botafogo", "Zona Sul"),
        ("Copacabana", "Zona Sul"),
        ("Recreio dos Bandeirantes", "Zona Sudoeste"),
        ("Barra da Tijuca", "Zona Sudoeste"),
        ("Jacarepaguá", "Zona Sudoeste"),
        ("Freguesia", "Zona Sudoeste"),
        ("Vargem Pequena", "Zona Sudoeste"),
        ("Barra Olímpica", "Zona Sudoeste"),
        ("Vargem Grande", "Zona Sudoeste"),
    ]

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO Bairros (Nome, BairroZona) VALUES (?, ?)", bairros
        )
        conn.commit()
        print(f"✔️ {cursor.rowcount} neighborhoods successfully included!")


if __name__ == "__main__":
    populate_bairros()
