from pathlib import Path

from database import DATA_PATH, pool

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png"}

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
    "LinkPublico",
    "CaminhoDrive",
}

VALID_STATUS = ["Disponível", "Vendido", "Alugado", "Retirado de Venda"]


# ─────────────────────────────────────────────
#  INSERT
# ─────────────────────────────────────────────


def add_neighborhood(name: str, zone: str) -> int:
    query = "INSERT INTO Bairros (Nome, BairroZona) VALUES (%s, %s) RETURNING BairroID"
    with pool.connection() as conn:
        row = conn.execute(query, (name, zone)).fetchone()
        return row["bairroid"]


def add_seller(name: str, phone: str, email: str) -> int:
    query = "INSERT INTO Proprietarios (Nome, Telefone, Email) VALUES (%s, %s, %s) RETURNING ProprietarioID"
    with pool.connection() as conn:
        row = conn.execute(query, (name, phone, email)).fetchone()
        return row["proprietarioid"]


def add_condo(name: str, address: str, infra: str, neighborhood_id: int) -> int:
    # FIX: a coluna no schema Postgres é "Endereco" (sem cedilha) — o schema
    # SQLite antigo usava "Endereço", o que quebraria esse INSERT.
    query = """
        INSERT INTO Condominios (Nome, Endereco, Infraestrutura, BairroID)
        VALUES (%s, %s, %s, %s)
        RETURNING CondominioID
    """
    with pool.connection() as conn:
        row = conn.execute(query, (name, address, infra, neighborhood_id)).fetchone()
        return row["condominioid"]


def add_property(
    tipologia: str,
    owner_id: int,
    price: float,
    condo_fee: float,
    tax: float,
    rooms: int,
    park: int,
    size: int,
    sun: str,
    neighborhood_id: int,
    condo_id: int | None,
    address: str,
    description: str,
    drive_folder: str,
    public_link: str,
) -> int:
    query = """
        INSERT INTO Imoveis (
            Tipologia, Quartos, Vagas, ProprietarioID, Valor, ValorCondominio, IPTU,
            Metragem, Sol, BairroID, CondominioID, Endereco, Descricao,
            CaminhoDrive, LinkPublico
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ImovelID
    """
    with pool.connection() as conn:
        row = conn.execute(
            query,
            (
                tipologia,
                rooms,
                park,
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
                drive_folder,
                public_link,
            ),
        ).fetchone()
        return row["imovelid"]


def add_photos(folder_path: str, property_id: int) -> list[int]:
    """
    Lê todos os .jpg/.jpeg/.png da pasta.
    Arquivo com stem '0' é marcado como capa.
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

    query = "INSERT INTO Fotos (ImovelID, CaminhoArquivo, Principal) VALUES (%s, %s, %s) RETURNING FotoID"
    inserted_ids = []

    with pool.connection() as conn:
        for photo in photos:
            is_cover = int(photo.stem == "0")  # Fotos.Principal é smallint, não boolean
            row = conn.execute(query, (property_id, str(photo), is_cover)).fetchone()
            inserted_ids.append(row["fotoid"])

    return inserted_ids


# ─────────────────────────────────────────────
#  UPDATE
# ─────────────────────────────────────────────


def update_status(property_id: int, status: str) -> None:
    if status not in VALID_STATUS:
        raise ValueError(f"Invalid status: '{status}'")

    set_date = status in {"Vendido", "Alugado"}
    query = """
        UPDATE Imoveis
        SET ImovelStatus = %s,
            DataVenda = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE ImovelID = %s
    """
    with pool.connection() as conn:
        cursor = conn.execute(query, (status, set_date, property_id))
        if cursor.rowcount == 0:
            raise LookupError(f"No property found with ID {property_id}.")


def update_prices(
    property_id: int,
    price: float | None = None,
    condo_fee: float | None = None,
    tax: float | None = None,
    new_description: str | None = None,
) -> None:
    fields, values = [], []

    if price is not None:
        fields.append("Valor = %s")
        values.append(price)
    if condo_fee is not None:
        fields.append("ValorCondominio = %s")
        values.append(condo_fee)
    if tax is not None:
        fields.append("IPTU = %s")
        values.append(tax)
    if new_description is not None:
        fields.append("Descricao = %s")
        values.append(new_description)

    if not fields:
        raise ValueError("At least one price field must be provided.")

    values.append(property_id)
    query = f"UPDATE Imoveis SET {', '.join(fields)} WHERE ImovelID = %s"

    with pool.connection() as conn:
        cursor = conn.execute(query, values)
        if cursor.rowcount == 0:
            raise LookupError(f"No property found with ID {property_id}.")


def update_field(property_id: int, field: str, value: str) -> None:
    if field not in IMOVEIS_UPDATABLE:
        raise ValueError(f"Field not updatable: '{field}'")

    # `field` já é validado contra o whitelist IMOVEIS_UPDATABLE acima —
    # é seguro interpolar o nome da coluna aqui (não é input livre do usuário).
    query = f"UPDATE Imoveis SET {field} = %s WHERE ImovelID = %s"

    with pool.connection() as conn:
        cursor = conn.execute(query, (value, property_id))
        if cursor.rowcount == 0:
            raise LookupError(f"No property found with ID {property_id}.")


def update_condo_name(condo_id: int, name: str) -> None:
    # FIX: o código original tinha um typo ("Condondominios") que nunca
    # funcionou — corrigido para "Condominios".
    query = "UPDATE Condominios SET Nome = %s WHERE CondominioID = %s"

    with pool.connection() as conn:
        cursor = conn.execute(query, (name, condo_id))
        if cursor.rowcount == 0:
            raise LookupError(f"No condo found with ID {condo_id}.")


# ─────────────────────────────────────────────
#  READ
# ─────────────────────────────────────────────


def get_property(property_id: int) -> dict | None:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM Imoveis WHERE ImovelID = %s", (property_id,)
        ).fetchone()


def get_available_properties() -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM Imoveis WHERE ImovelStatus = 'Disponível'"
        ).fetchall()


def get_property_by_neighborhood(neighborhood_id: int) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM Imoveis WHERE BairroID = %s", (neighborhood_id,)
        ).fetchall()


def get_property_by_condo(condo_id: int) -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM Imoveis WHERE CondominioID = %s", (condo_id,)
        ).fetchall()


def get_owner(owner_id: int) -> dict | None:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM Proprietarios WHERE ProprietarioID = %s", (owner_id,)
        ).fetchone()


def get_condo_name(condo_id: int | None) -> str | None:
    if condo_id is None:
        return None
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT Nome FROM Condominios WHERE CondominioID = %s", (condo_id,)
        ).fetchone()
        return row["nome"] if row else None


def get_neighborhood_name(neighborhood_id: int | None) -> str | None:
    if neighborhood_id is None:
        return None
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT Nome FROM Bairros WHERE BairroID = %s", (neighborhood_id,)
        ).fetchone()
        return row["nome"] if row else None


# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
def get_folder_path(property_id: int) -> Path | None:
    """Retorna o Path da pasta local do imóvel baseada na estrutura padrão do container."""
    folder = Path(__file__).resolve().parent.parent / "data" / "imoveis" / f"imovel_{property_id}"
    if folder.is_dir():
        return folder

    with pool.connection() as conn:
        row = conn.execute(
            "SELECT CaminhoArquivo FROM Fotos WHERE ImovelID = %s LIMIT 1",
            (property_id,),
        ).fetchone()
        if row:
            fallback_path = Path(row["caminhoarquivo"]).parent
            if fallback_path.is_dir():
                return fallback_path

    return None

def get_drive_path(property_id: int) -> Path | None:
    """Retorna o Path da pasta do imóvel no Drive."""
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT CaminhoDrive FROM Imoveis WHERE ImovelID = %s", (property_id,)
        ).fetchone()
        if row and row["caminhodrive"]:
            return Path(row["caminhodrive"])
        return None


def get_public_link(property_id: int) -> str | None:
    """Retorna o link público do Drive (URL, não path)."""
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT LinkPublico FROM Imoveis WHERE ImovelID = %s", (property_id,)
        ).fetchone()
        return row["linkpublico"] if row else None
