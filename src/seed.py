from database import pool


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

    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO Bairros (Nome, BairroZona) VALUES (%s, %s)", bairros
        )
        print(f"[OK] {cursor.rowcount} neighborhoods successfully added.")


if __name__ == "__main__":
    populate_bairros()
