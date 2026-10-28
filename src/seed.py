from database import pool


def populate_bairros() -> None:
    bairros = [
        # Zona Sudoeste
        ("Recreio dos Bandeirantes", "Zona Sudoeste"),
        ("Barra da Tijuca", "Zona Sudoeste"),
        ("Barra Olímpica", "Zona Sudoeste"),
        ("Jacarepaguá", "Zona Sudoeste"),
        ("Freguesia", "Zona Sudoeste"),
        ("Vargem Pequena", "Zona Sudoeste"),
        ("Vargem Grande", "Zona Sudoeste"),
        # Zona Sul
        ("Botafogo", "Zona Sul"),
        ("Catete", "Zona Sul"),
        ("Copacabana", "Zona Sul"),
        ("Cosme Velho", "Zona Sul"),
        ("Flamengo", "Zona Sul"),
        ("Gávea", "Zona Sul"),
        ("Glória", "Zona Sul"),
        ("Humaitá", "Zona Sul"),
        ("Ipanema", "Zona Sul"),
        ("Jardim Botânico", "Zona Sul"),
        ("Lagoa", "Zona Sul"),
        ("Laranjeiras", "Zona Sul"),
        ("Leblon", "Zona Sul"),
        ("Leme", "Zona Sul"),
        ("Rocinha", "Zona Sul"),
        ("São Conrado", "Zona Sul"),
        ("Urca", "Zona Sul"),
        ("Vidigal", "Zona Sul"),
    ]

    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO Bairros (Nome, BairroZona)
            SELECT %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM Bairros WHERE LOWER(Nome) = LOWER(%s)
            )
            """,
            [(nome, zona, nome) for nome, zona in bairros],
        )
        print("[OK] Preenchimento de bairros concluído.")


if __name__ == "__main__":
    try:
        populate_bairros()
    finally:
        pool.close()
