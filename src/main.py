from repository import (
    add_neighborhood,
    add_seller,
    add_condo,
    add_property,
    add_photos,
    update_status,
    update_prices,
    update_field,
    get_property,
    get_available_properties,
    get_property_by_neighborhood,
    get_property_by_condo,
    get_condo_name,
    get_neighborhood_name,
    get_owner,
    get_folder_path,
    get_drive_path,
    get_public_link,
    VALID_STATUS,
    IMOVEIS_UPDATABLE,
)
from backup import (
    do_backup,
    update_description_prices,
    DRIVE_DIR,
)
from pathlib import Path
import asyncio
import sqlite3
import webbrowser
import inspect
import shutil

OP_DIR_PATH = DRIVE_DIR / "Opções Diretas"

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

DIV = "─" * 42


def header(title: str) -> None:
    print(f"\n{DIV}")
    print(f"  {title}")
    print(DIV)


def ok(msg: str) -> None:
    print(f"\n  [OK] {msg}")


def err(msg: str) -> None:
    print(f"\n  [!]  {msg}")


def prompt(label: str) -> str:
    response = input(f"  > {label}: ").strip()
    print(DIV)
    return response


def prompt_int(label: str) -> int:
    response = int(input(f"  > {label}: ").strip())
    print(DIV)
    return response


def prompt_float(label: str) -> float:
    response = float(input(f"  > {label}: ").strip())
    print(DIV)
    return response


def prompt_optional_float(label: str) -> float | None:
    raw = input(f"  > {label} (Enter to skip): ").strip()
    print(DIV)
    return float(raw) if raw else None


def parse_optional_int(raw: str) -> int | None:
    return int(raw) if raw else None


def display_na(raw) -> str:
    return raw if raw else "N/A"


def open_folder(folder_path: Path | str) -> None:
    path = Path(folder_path).resolve()
    if path.exists():
        webbrowser.open(path.as_uri())
    else:
        err(f"Path not found: {folder_path}")


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

MENU = """
{DIV}
      IMOVEIS DATABASE  —  Main Menu
{DIV}
  [1] Add neighborhood        
  [2] Add owner               
  [3] Add condo               
  [4] Add property            
  [5] Update property status  
  [6] Update prices    
  [7] Correct a field
  [8] Find a property
  [9] Find a property by neighborhood
  [10] Show available properties
  [11] Show owner by ID
  [12] Find a property by condominium
{DIV}                       
  [0] Exit                  
{DIV}""".format(DIV=DIV)

# ─────────────────────────────────────────────
#  Handlers — INSERT
# ─────────────────────────────────────────────

ZONES = ["Zona Oeste", "Zona Sudoeste", "Zona Sul", "Zona Norte"]
ZONES_LABEL = "0: Zona Oeste, 1: Zona Sudoeste, 2: Zona Sul, 3: Zona Norte"
SUN_OPTS = ["Manhã", "Tarde", "Passante"]
SUN_OPTS_LABEL = "0: Manhã, 1: Tarde, 2: Passante"
TIPOLOGIA = ["Apartamento", "Casa", "Cobertura", "Studio"]
TIPOLOGIA_LABEL = "0: Apartamento, 1: Casa, 2: Cobertura, 3: Studio"
VALID_STATUS_LABEL = "0: Disponível | 1: Vendido | 2: Alugado | 3: Retirado de Venda"


async def handle_add_neighborhood() -> None:
    header("Add Neighborhood")
    print(f"  Zones: {ZONES_LABEL}")
    name = prompt("Name")
    zone = ZONES[prompt_int("Zone")]
    row_id = add_neighborhood(name, zone)
    await do_backup("upload")
    ok(f"Neighborhood '{name}' added with ID {row_id}.")


async def handle_add_seller() -> None:
    header("Add Seller")
    name = prompt("Full name")
    phone = prompt("Phone")
    email = prompt("E-mail")
    row_id = add_seller(name, phone, email)
    await do_backup("upload")
    ok(f"Seller '{name}' added with ID {row_id}.")


async def handle_add_condo() -> None:
    header("Add Condo")
    name = prompt("Name")
    address = prompt("Address")
    infra = prompt("Infrastructure (e.g. pool, gym, security)")
    neighborhood_id = prompt_int("Neighborhood ID")
    row_id = add_condo(name, address, infra, neighborhood_id)
    await do_backup("upload")
    ok(f"Condo '{name}' added with ID {row_id}.")


async def handle_add_property() -> None:
    header("Add Property")
    print(f"  Types: {TIPOLOGIA_LABEL}")
    tipologia = TIPOLOGIA[prompt_int("Type")]
    address = prompt("Address")
    owner_id = prompt_int("Owner (seller) ID")
    neighborhood_id = prompt_int("Neighborhood ID")
    condo_id = parse_optional_int(prompt("Condo ID (Enter to skip)"))
    rooms = prompt_int("Number of rooms")
    park = prompt_int("Number of parking spots")
    price = prompt_float("Price (R$)")
    condo_fee = prompt_float("Condo fee (R$)")
    tax = prompt_float("IPTU (R$)")
    size = prompt_int("Size (m2)")
    print(f"\n  Sun options: {SUN_OPTS_LABEL}")
    sun = SUN_OPTS[prompt_int("Sun exposure")]

    # Pasta já existe em "Opções Diretas" com nome dinâmico
    drive_folder_name = prompt(
        "Folder name in 'Opções Diretas' (e.g. Apartamento - Acquabella)"
    )
    drive_path = OP_DIR_PATH / drive_folder_name
    public_link = prompt("Google Drive public link")

    desc_file = drive_path / "Descrição.txt"
    if not desc_file.is_file():
        raise FileNotFoundError(f"'Descrição.txt' not found in '{drive_path}'.")
    description = desc_file.read_text(encoding="utf-8").strip()

    imovel_id = add_property(
        tipologia,
        owner_id,
        price,
        condo_fee,
        tax,
        rooms,
        park,
        size,
        sun,
        neighborhood_id,
        condo_id,
        address,
        description,
        str(drive_path),
        public_link,
    )
    ok(f"Property added with ID {imovel_id}.")

    # Copia pasta do Drive para local com nome padronizado
    local_folder = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "imoveis"
        / f"imovel_{imovel_id}"
    )
    shutil.copytree(str(drive_path), str(local_folder))
    ok(f"Folder copied to '{local_folder}'.")

    inserted = add_photos(str(local_folder), imovel_id)
    ok(f"{len(inserted)} photo(s) registered.")

    await do_backup("upload")


# ─────────────────────────────────────────────
#  Handlers — UPDATE
# ─────────────────────────────────────────────


async def handle_update_status() -> None:
    header("Update Property Status")
    property_id = prompt_int("Property ID")
    prop = get_property(property_id)
    if prop is None:
        err("Property not found.")
        return

    print(f"  Status options: {VALID_STATUS_LABEL}")
    status = VALID_STATUS[prompt_int("New status")]
    update_status(property_id, status)

    drive_path = get_drive_path(property_id)

    if status != "Disponível" and drive_path and drive_path.exists():
        # Salva nome da pasta do Drive num .txt oculto na pasta local
        local_folder = get_folder_path(property_id)
        if local_folder:
            hidden = local_folder / ".drive_folder_name.txt"
            hidden.write_text(drive_path.name, encoding="utf-8")
        shutil.rmtree(str(drive_path))
        ok(f"Drive folder '{drive_path.name}' removed from 'Opções Diretas'.")

    elif status == "Disponível":
        # FIX: não depende de drive_path (já deletado). Usa o .txt salvo localmente.
        local_folder = get_folder_path(property_id)
        if local_folder:
            hidden = local_folder / ".drive_folder_name.txt"
            if hidden.is_file():
                folder_name = hidden.read_text(encoding="utf-8").strip()
                restored = OP_DIR_PATH / folder_name
                shutil.copytree(
                    str(local_folder),
                    str(restored),
                    ignore=shutil.ignore_patterns(".*"),
                )
                ok(f"Drive folder '{folder_name}' restored to 'Opções Diretas'.")

    await do_backup("upload")
    ok(f"Property {property_id} marked as '{status}'.")


async def handle_update_prices() -> None:
    header("Update Prices")
    print("  Leave blank to keep current value.")
    imovel_id = prompt_int("Property ID")
    price = prompt_optional_float("New price (R$)")
    condo_fee = prompt_optional_float("New condo fee (R$)")
    tax = prompt_optional_float("New IPTU (R$)")

    local_folder = get_folder_path(imovel_id)
    drive_folder = get_drive_path(imovel_id)

    # Atualiza Descrição.txt local
    if local_folder:
        update_description_prices(local_folder, price, condo_fee, tax)
        description = (
            (local_folder / "Descrição.txt").read_text(encoding="utf-8").strip()
        )
    else:
        description = None

    # Atualiza Descrição.txt no Drive se pasta existir
    if drive_folder and drive_folder.exists():
        update_description_prices(drive_folder, price, condo_fee, tax)

    update_prices(imovel_id, price, condo_fee, tax, description)
    await do_backup("upload")
    ok(f"Prices updated for property {imovel_id}.")


async def handle_update_field() -> None:
    header("Correct a Field")
    print(f"  Updatable fields: {', '.join(sorted(IMOVEIS_UPDATABLE))}")
    imovel_id = prompt_int("Property ID")
    field = prompt("Field name")
    value = prompt("New value")
    update_field(imovel_id, field, value)
    await do_backup("upload")
    ok(f"Field '{field}' updated for property {imovel_id}.")


# ─────────────────────────────────────────────
#  Handlers — SHOW
# ─────────────────────────────────────────────


def handle_find_property() -> None:
    header("Find a property")
    property_id = prompt_int("Property ID")
    prop = get_property(property_id)

    if prop is None:
        err("Property not found.")
        return

    tipology = prop["Tipologia"]
    rooms = prop["Quartos"]
    metragem = prop["Metragem"]
    value = prop["Valor"]
    owner = get_owner(prop["ProprietarioID"])
    condo_name = display_na(get_condo_name(prop["CondominioID"]))
    neighborhood_name = display_na(get_neighborhood_name(prop["BairroID"]))
    status = prop["ImovelStatus"]
    local_folder = get_folder_path(property_id)
    public = display_na(get_public_link(property_id))

    print(f"""
{DIV}
  {condo_name} | {neighborhood_name}
{DIV}
  Tipo: {tipology}        Metragem: {metragem}m²
  Quartos: {rooms}        Status: {status}
  Valor: R$ {value}
{DIV}
  Proprietário: {owner["Nome"]}
  Telefone: {owner["Telefone"]}
{DIV}
  Link público: {public}
{DIV}""")

    response = prompt("Enter to return / 0 to open local folder")
    if response == "0" and local_folder:
        open_folder(local_folder)


def handle_find_property_by_neighborhood() -> None:
    header("Find a property by neighborhood")
    neighborhood_id = prompt_int("Neighborhood ID")
    neighborhood_name = display_na(get_neighborhood_name(neighborhood_id))
    prop_list = get_property_by_neighborhood(neighborhood_id)
    for prop in prop_list:
        condo_name = display_na(get_condo_name(prop["CondominioID"]))
        print(
            f"  ID:{prop['ImovelID']} | {condo_name} | {neighborhood_name} | {prop['Tipologia']} | R$ {prop['Valor']} | {prop['Quartos']}qts\n{DIV}"
        )
    prompt("Enter to return")


def handle_find_property_by_condo() -> None:
    header("Find a property by Condominium")
    condo_id = prompt_int("Condominium ID")
    prop_list = get_property_by_condo(condo_id)
    condo_name = display_na(get_condo_name(condo_id))
    for prop in prop_list:
        neighborhood_name = display_na(get_neighborhood_name(prop["BairroID"]))
        print(
            f"  ID:{prop['ImovelID']} | {condo_name} | {neighborhood_name} | {prop['Tipologia']} | R$ {prop['Valor']} | {prop['Quartos']}qts\n{DIV}"
        )
    prompt("Enter to return")


def handle_show_available_properties() -> None:
    header("Available Properties")
    prop_list = get_available_properties()
    if not prop_list:
        print("  No available properties.")
    for prop in prop_list:
        condo_name = display_na(get_condo_name(prop["CondominioID"]))
        neighborhood_name = display_na(get_neighborhood_name(prop["BairroID"]))
        print(
            f"  ID:{prop['ImovelID']} | {condo_name} | {neighborhood_name} | {prop['Tipologia']} | R$ {prop['Valor']} | {prop['Quartos']}qts\n{DIV}"
        )
    prompt("Enter to return")


def handle_find_owner() -> None:
    header("Find an owner")
    owner_id = prompt_int("Owner ID")
    owner = get_owner(owner_id)
    if owner is None:
        err("Owner not found.")
        return
    print(f"""
{DIV}
  ID:{owner_id} | {owner["Nome"]}
  Telefone: {owner["Telefone"]}
  E-mail: {display_na(owner["Email"])}
{DIV}""")
    prompt("Enter to return")


# ─────────────────────────────────────────────
#  Dispatch table
# ─────────────────────────────────────────────

HANDLERS = {
    1: handle_add_neighborhood,
    2: handle_add_seller,
    3: handle_add_condo,
    4: handle_add_property,
    5: handle_update_status,
    6: handle_update_prices,
    7: handle_update_field,
    8: handle_find_property,
    9: handle_find_property_by_neighborhood,
    10: handle_show_available_properties,
    11: handle_find_owner,
    12: handle_find_property_by_condo,
}

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────


async def main() -> None:
    header("Syncing database...")
    await do_backup("download")
    ok("Sync complete.")

    while True:
        print(MENU)
        try:
            choice = prompt_int("Select an option")
        except ValueError:
            err("Numbers only. Try again.")
            continue

        if choice == 0:
            print(f"\n{DIV}\n  Goodbye.\n{DIV}\n")
            break

        handler = HANDLERS.get(choice)
        if handler is None:
            err("Invalid option. Try again.")
            continue

        try:
            if inspect.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        except ValueError as e:
            err(str(e))
            if "Invalid status" in str(e):
                err(f"Valid options: {' | '.join(VALID_STATUS)}")
            elif "Field not updatable" in str(e):
                err(f"Allowed fields: {', '.join(sorted(IMOVEIS_UPDATABLE))}")
        except LookupError as e:
            err(str(e))
        except sqlite3.IntegrityError as e:
            err(f"Database integrity error — {e}")
        except (NotADirectoryError, FileNotFoundError) as e:
            err(str(e))
        except Exception as e:
            err(f"Unexpected error — {e}")


if __name__ == "__main__":
    asyncio.run(main())
