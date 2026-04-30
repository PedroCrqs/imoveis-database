from repository import (
    add_neighborhood,
    add_seller,
    add_condo,
    add_property,
    add_photos,
    update_status,
    update_prices,
    update_field,
    VALID_STATUS,
    IMOVEIS_UPDATABLE,
)
from pathlib import Path
import sqlite3

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

DIVIDER = "─" * 42


def header(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


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


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

MENU = """
{div}
  IMOVEIS DATABASE  —  Main Menu
{div}
  [1] Add neighborhood      [5] Update property status
  [2] Add seller            [6] Update prices
  [3] Add condo             [7] Correct a field
  [4] Add property
{div}
  [0] Exit
{div}""".format(
    div=DIVIDER
)

# ─────────────────────────────────────────────
#  Handlers — INSERT
# ─────────────────────────────────────────────

ZONES = "Zona Oeste | Zona Sudoeste | Zona Sul | Zona Norte"
SUN_OPTS = "Manhã | Tarde | Passante"
TIPOLOGIA = "Apartamento | Casa | Cobertura | Studio"


def handle_add_neighborhood() -> None:
    header("Add Neighborhood")
    print(f"  Zones: {ZONES}")
    name = prompt("Name")
    zone = prompt("Zone")
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
    print(f"  Types: {TIPOLOGIA}")
    tipologia = prompt("Type")
    address = prompt("Address")
    owner_id = prompt_int("Owner (seller) ID")
    neighborhood_id = prompt_int("Neighborhood ID")
    condo_id = prompt_int("Condo ID")
    price = prompt_float("Price (R$)")
    condo_fee = prompt_float("Condo fee (R$)")
    tax = prompt_float("IPTU (R$)")
    size = prompt_int("Size (m2)")
    print(f"\n  Sun options: {SUN_OPTS}")
    sun = prompt("Sun exposure")
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
        size,
        sun,
        neighborhood_id,
        condo_id,
        address,
        description,
    )
    ok(f"Property added with ID {imovel_id}.")

    inserted = add_photos(folder, imovel_id)
    ok(f"{len(inserted)} photo(s) registered.")


# ─────────────────────────────────────────────
#  Handlers — UPDATE
# ─────────────────────────────────────────────


def handle_update_status() -> None:
    header("Update Property Status")
    print(f"  Status options: {' | '.join(sorted(VALID_STATUS))}")
    imovel_id = prompt_int("Property ID")
    status = prompt("New status")
    update_status(imovel_id, status)
    ok(f"Property {imovel_id} marked as '{status}'.")


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
}

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────


def main() -> None:
    while True:
        print(MENU)
        try:
            choice = int(input("\n  Select an option: ").strip())
        except ValueError:
            err("Numbers only. Try again.")
            continue

        if choice == 0:
            print(f"\n{DIVIDER}\n  Goodbye.\n{DIVIDER}\n")
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
