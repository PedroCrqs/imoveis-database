from database import DB_PATH
from pathlib import Path
import sqlite3

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Campos permitidos para update genérico — whitelist contra SQL injection
IMOVEIS_UPDATABLE = {
    "Tipologia",
    "Valor",
    "ValorCondominio",
    "IPTU",
    "Metragem",
    "Sol",
    "Endereco",
    "Descricao",
    "BairroID",
    "CondominioID",
    "ProprietarioID",
}

VALID_STATUS = {"Disponível", "Vendido", "Alugado", "Retirado de Venda"}


# ─────────────────────────────────────────────
#  INSERT
# ─────────────────────────────────────────────


def add_neighborhood(name: str, zone: str) -> int:
    query = "INSERT INTO Bairros (Nome, BairroZona) VALUES (?, ?)"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute(query, (name, zone))
        conn.commit()
        return cursor.lastrowid


def add_seller(name: str, phone: str, email: str) -> int:
    query = "INSERT INTO Proprietarios (Nome, Telefone, Email) VALUES (?, ?, ?)"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(query, (name, phone, email))
        conn.commit()
        return cursor.lastrowid


def add_condo(name: str, address: str, infra: str, neighborhood_id: int) -> int:
    query = """
        INSERT INTO Condominios (Nome, Endereço, Infraestrutura, BairroID)
        VALUES (?, ?, ?, ?)
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute(query, (name, address, infra, neighborhood_id))
        conn.commit()
        return cursor.lastrowid


def add_property(
    tipologia: str,
    owner_id: int,
    price: float,
    condo_fee: float,
    tax: float,
    size: int,
    sun: str,
    neighborhood_id: int,
    condo_id: int,
    address: str,
    description: str,
) -> int:
    query = """
        INSERT INTO Imoveis (
            Tipologia, ProprietarioID, Valor, ValorCondominio, IPTU,
            Metragem, Sol, BairroID, CondominioID, Endereco, Descricao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute(
            query,
            (
                tipologia,
                owner_id,
                price,
                condo_fee,
                tax,
                size,
                sun,
                neighborhood_id,
                condo_id,
                address,
                description,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def add_photos(folder_path: str, imovel_id: int) -> list[int]:
    """
    Lê todos os arquivos .jpg/.jpeg/.png da pasta.
    O arquivo com stem '0' é marcado como capa (Principal = 1).
    Retorna lista de FotoIDs inseridos.
    """
    folder = Path(folder_path)

    if not folder.is_dir():
        raise NotADirectoryError(f"'{folder_path}' is not a valid directory.")

    photos = sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in PHOTO_EXTENSIONS
    )

    if not photos:
        raise FileNotFoundError(f"No images found in '{folder_path}'.")

    query = "INSERT INTO Fotos (ImovelID, CaminhoArquivo, Principal) VALUES (?, ?, ?)"
    inserted_ids = []

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for photo in photos:
            is_cover = photo.stem == "0"
            cursor = conn.execute(query, (imovel_id, str(photo), is_cover))
            inserted_ids.append(cursor.lastrowid)
        conn.commit()

    return inserted_ids


# ─────────────────────────────────────────────
#  UPDATE
# ─────────────────────────────────────────────


def update_status(imovel_id: int, status: str) -> None:
    """Marca o imóvel como Vendido, Alugado, etc."""
    if status not in VALID_STATUS:
        raise ValueError(f"Invalid status: '{status}'")

    # DataVenda só é preenchida quando o negócio é fechado
    set_date = status in {"Vendido", "Alugado"}
    query = """
        UPDATE Imoveis
        SET ImovelStatus = ?,
            DataVenda = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE ImovelID = ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute(query, (status, set_date, imovel_id))
        conn.commit()

    if cursor.rowcount == 0:
        raise LookupError(f"No property found with ID {imovel_id}.")


def update_prices(
    imovel_id: int,
    price: float | None = None,
    condo_fee: float | None = None,
    tax: float | None = None,
) -> None:
    """Atualiza Valor, ValorCondominio e/ou IPTU. Passa None para manter o valor atual."""
    fields, values = [], []

    if price is not None:
        fields.append("Valor = ?")
        values.append(price)
    if condo_fee is not None:
        fields.append("ValorCondominio = ?")
        values.append(condo_fee)
    if tax is not None:
        fields.append("IPTU = ?")
        values.append(tax)

    if not fields:
        raise ValueError("At least one price field must be provided.")

    values.append(imovel_id)
    query = f"UPDATE Imoveis SET {', '.join(fields)} WHERE ImovelID = ?"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(query, values)
        conn.commit()

    if cursor.rowcount == 0:
        raise LookupError(f"No property found with ID {imovel_id}.")


def update_field(imovel_id: int, field: str, value: str) -> None:
    """
    Correção pontual de qualquer campo permitido.
    'field' é validado contra whitelist — nunca interpolado direto da UI.
    """
    if field not in IMOVEIS_UPDATABLE:
        raise ValueError(f"Field not updatable: '{field}'")

    query = f"UPDATE Imoveis SET {field} = ? WHERE ImovelID = ?"

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute(query, (value, imovel_id))
        conn.commit()

    if cursor.rowcount == 0:
        raise LookupError(f"No property found with ID {imovel_id}.")
