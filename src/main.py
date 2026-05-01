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
    get_avaliable_properties,
    get_property_by_neighborhood,
    get_condo_name,
    get_owner,
    get_folder_path,
    VALID_STATUS,
    IMOVEIS_UPDATABLE,
)
from pathlib import Path
import sqlite3
import webbrowser
import os

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
    return input(f"  > {label}: ").strip()


def prompt_int(label: str) -> int:
    return int(input(f"  > {label}: ").strip())


def prompt_float(label: str) -> float:
    return float(input(f"  > {label}: ").strip())


def prompt_optional_float(label: str) -> float | None:
    raw = input(f"  > {label} (Enter to skip): ").strip()
    return float(raw) if raw else None


def parse_optional_int(raw):
    return int(raw) if raw else None


def display_na(raw):
    return raw if raw else "N/A"


def open_property_folder(folder_path: str):
    path = Path(folder_path).resolve()
    if path.exists():
        webbrowser.open(path.as_uri())
    else:
        err(f"Erro: O caminho {folder_path} não existe.")


def change_folder_name(old_path: str, imovel_id: int) -> str:
    old_p = Path(old_path).resolve()
    target_dir = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "imoveis"
        / f"imovel_{imovel_id}"
    )
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    os.rename(str(old_p), str(target_dir))
    return str(target_dir)


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
{DIV}                       
  [0] Exit                  
{DIV}""".format(DIV=DIV)

# ─────────────────────────────────────────────
#  Handlers — INSERT
# ─────────────────────────────────────────────

ZONES = ["Zona Oeste", "Zona Sudoeste", "Zona Sul", "Zona Norte"]
ZONES_LABEL = "0: Zona Oeste, 1: Zona Sudoeste, 2: Zona Sul, 3: Zona Norte"
SUN_OPTS = ["Manhã", "Tarde", "Passante"]
SUN_OPTS_LABEL = "0:  Manhã, 1: Tarde, 2: Passante"
TIPOLOGIA = ["Apartamento", "Casa", "Cobertura", "Studio"]
TIPOLOGIA_LABEL = "0: Apartamento, 1: Casa, 2: Cobertura, 3: Studio"
VALID_STATUS_LABEL = (
    "| 0: Disponível | 1: Vendido | 2: Alugado | 3: Retirado de Venda |"
)


def handle_add_neighborhood() -> None:
    header("Add Neighborhood")
    print(f"  Zones: {ZONES_LABEL}")
    name = prompt("Name")
    zone = ZONES[prompt_int("Zone")]
    row_id = add_neighborhood(name, zone)
    ok(f"Neighborhood '{name}' added with ID {row_id}.")


def handle_add_seller() -> None:
    header("Add Seller")
    name = prompt("Full name")
    phone = prompt("Phone")
    email = prompt("E-mail")
    row_id = add_seller(name, phone, email)
    ok(f"Seller '{name}' added with ID {row_id}.")


def handle_add_condo() -> None:
    header("Add Condo")
    name = prompt("Name")
    address = prompt("Address")
    infra = prompt("Infrastructure (e.g. pool, gym, security)")
    neighborhood_id = prompt_int("Neighborhood ID")
    row_id = add_condo(name, address, infra, neighborhood_id)
    ok(f"Condo '{name}' added with ID {row_id}.")


def handle_add_property() -> None:
    header("Add Property")
    print(f"  Types: {TIPOLOGIA_LABEL}")
    tipologia = TIPOLOGIA[prompt_int("Type")]
    address = prompt("Address")
    owner_id = prompt_int("Owner (seller) ID")
    neighborhood_id = prompt_int("Neighborhood ID")
    raw = prompt("Condo ID (Enter to skip)").strip()
    condo_id = parse_optional_int(raw)
    rooms = prompt_int("Number of rooms")
    park = prompt_int("Number of parks")
    price = prompt_float("Price (R$)")
    condo_fee = prompt_float("Condo fee (R$)")
    tax = prompt_float("IPTU (R$)")
    size = prompt_int("Size (m2)")
    print(f"\n  Sun options: {SUN_OPTS_LABEL}")
    sun = SUN_OPTS[prompt_int("Sun exposure")]
    folder = prompt("Property folder path (photos + Descrição.txt)")

    desc_file = Path(folder) / "Descrição.txt"
    if not desc_file.is_file():
        raise FileNotFoundError(f"'Descrição.txt' not found in '{folder}'.")
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
    )
    ok(f"Property added with ID {imovel_id}.")

    new_folder = change_folder_name(folder, imovel_id)

    inserted = add_photos(new_folder, imovel_id)
    ok(f"{len(inserted)} photo(s) registered.")


# ─────────────────────────────────────────────
#  Handlers — UPDATE
# ─────────────────────────────────────────────


def handle_update_status() -> None:
    header("Update Property Status")
    property_id = prompt_int("Property ID")
    print(f"  Status options: {VALID_STATUS_LABEL}")
    status = VALID_STATUS[prompt_int("New status")]
    update_status(property_id, status)
    ok(f"Property {property_id} marked as '{status}'.")


def handle_update_prices() -> None:
    header("Update Prices")
    print("  Leave blank to keep current value.")
    imovel_id = prompt_int("Property ID")
    price = prompt_optional_float("New price (R$)")
    condo_fee = prompt_optional_float("New condo fee (R$)")
    tax = prompt_optional_float("New IPTU (R$)")
    update_prices(imovel_id, price, condo_fee, tax)
    ok(f"Prices updated for property {imovel_id}.")


def handle_update_field() -> None:
    header("Correct a Field")
    print(f"  Updatable fields: {', '.join(sorted(IMOVEIS_UPDATABLE))}")
    imovel_id = prompt_int("Property ID")
    field = prompt("Field name")
    value = prompt("New value")
    update_field(imovel_id, field, value)
    ok(f"Field '{field}' updated for property {imovel_id}.")


# ─────────────────────────────────────────────
#  Handlers - SHOW
# ─────────────────────────────────────────────


def handle_find_property() -> None:
    header("Find a property")
    property_id = prompt_int("Property ID")
    prop = get_property(property_id)

    if prop is None:
        err("Property not found")
        return

    tipology = prop["Tipologia"]
    rooms = prop["Quartos"]
    m4 = prop["Metragem"]
    value = prop["Valor"]
    owner_id = prop["ProprietarioID"]
    owner = get_owner(owner_id)
    owner_name = owner["Nome"]
    owner_phone = owner["Telefone"]
    condo_id = prop["CondominioID"]
    raw_condo_name = get_condo_name(condo_id)
    condo_name = display_na(raw_condo_name)
    status = prop["ImovelStatus"]
    folder_path = get_folder_path(property_id)
    menu = f"""
{DIV}
            {condo_name}
{DIV}
  Tipo: {tipology}        Metragem: {m4}
  Quartos: {rooms}        Status: {status}
  Valor: {value}              
{DIV}                       
  Proprietário: {owner_name}
  Telefone: {owner_phone}                 
{DIV}
"""
    print(menu)
    response = prompt("Press any button for exit or 0 to access folder")
    if response == "0":
        open_property_folder(folder_path)
        return


def handle_find_property_by_neighborhood() -> None:
    # Only avaliable properties
    header("Find a property by neighborhood")
    neighborhood_id = prompt_int("Neighborhood ID")
    prop_list = get_property_by_neighborhood(neighborhood_id)
    for prop in prop_list:
        prop_id = prop["ImovelID"]
        condo_id = prop["CondominioID"]
        raw_condo_name = get_condo_name(condo_id)
        condo_name = display_na(raw_condo_name)
        value = prop["Valor"]
        tipology = prop["Tipologia"]
        rooms = prop["Quartos"]
        print(f"""
{DIV}
  ID:{prop_id} | {condo_name} | {tipology} | R$ {value} | {rooms}qts
{DIV}""")
    prompt("Enter to return")


def handle_show_avaliable_properties() -> None:
    prop_list = get_avaliable_properties()
    for prop in prop_list:
        prop_id = prop["ImovelID"]
        condo_id = prop["CondominioID"]
        raw_condo_name = get_condo_name(condo_id)
        condo_name = display_na(raw_condo_name)
        value = prop["Valor"]
        tipology = prop["Tipologia"]
        rooms = prop["Quartos"]
        print(f"""
{DIV}
  ID:{prop_id} | {condo_name} | {tipology} | R$ {value} | {rooms}qts
{DIV}""")
    prompt("Enter to return")


def handle_find_owner() -> None:
    header("Find an owner")
    owner_id = prompt_int("Owner ID")
    owner = get_owner(owner_id)
    owner_name = owner["Nome"]
    owner_phone = owner["Telefone"]
    raw_owner_email = owner["Email"]
    owner_email = display_na(raw_owner_email)
    print(f"""
{DIV}
  ID:{owner_id} | {owner_name}
  Telefone: {owner_phone}
  E-mail: {owner_email}
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
    10: handle_show_avaliable_properties,
    11: handle_find_owner,
}

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────


def main() -> None:
    while True:
        print(MENU)
        try:
            choice = prompt_int("Select an option: ")
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
            handler()
        except ValueError as e:
            err(str(e))
            if "Invalid status" in str(e):
                err(f"Valid options: {' | '.join(sorted(VALID_STATUS))}")
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
    main()
