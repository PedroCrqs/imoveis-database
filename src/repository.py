from database import DB_PATH
import sqlite3


def add_neighborhood(name, zone):
    query = "INSERT INTO Bairros (Nome, BairroZona) VALUES (?, ?)"
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.execute(query, (name, zone))
            conn.commit()
            print(
                f"\n [✔️] Neighborhood '{name}' successfully registered with ID: {cursor.lastrowid}"
            )
    except sqlite3.IntegrityError as e:
        print(f"\n [!] Integrity error: {e} (Check if the zone is valid)")


def add_seller(name, phone, email):
    query = "INSERT INTO Proprietarios (Nome, Telefone, Email) VALUES (?, ?, ?)"
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(query, (name, phone, email))
            conn.commit()
            print(
                f"✔️ Seller '{name}' successfully registered with ID: {cursor.lastrowid}"
            )
    except sqlite3.IntegrityError as e:
        print(f"\n  [!] Integrity error — {e}")


def add_condo(name, address, infra, neighborhood_id):
    query = "INSERT INTO Condominios (Nome, Endereço, Infraestrutura, BairroID) VALUES (?, ?, ?, ?)"
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.execute(query, (name, address, infra, neighborhood_id))
            conn.commit()
            print(
                f"\n [✔️] Condo '{name}' successfully created with ID: {cursor.lastrowid} and linked to neighborhood ID: {neighborhood_id}"
            )
    except sqlite3.IntegrityError as e:
        print(f"\n  [!] Integrity error — {e} (Verify if the neighborhood ID exists)")


def add_property(
    name,
    owner_id,
    price,
    condo_fee,
    tax,
    size,
    rooms,
    sun,
    neighborhood_id,
    condo_id,
    address,
    description,
):
    query = """
        INSERT INTO Imoveis (
            Nome, ProprietarioID, Valor, ValorCondominio, IPTU, 
            Metragem, Quartos, Sol, BairroID, CondominioID, 
            Endereco, Descricao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.execute(
                query,
                (
                    name,
                    owner_id,
                    price,
                    condo_fee,
                    tax,
                    size,
                    rooms,
                    sun,
                    neighborhood_id,
                    condo_id,
                    address,
                    description,
                ),
            )
            conn.commit()
            print(
                f"✔️ Property '{name}' successfully created with ID: {cursor.lastrowid}"
            )
    except sqlite3.IntegrityError as e:
        print(f"❌ Integrity error: {e} (Verify if all IDs and 'Sol' value are valid)")
