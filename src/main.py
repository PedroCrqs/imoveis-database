from repository import add_neighborhood, add_seller, add_condo, add_property

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

DIVIDER = "─" * 42


def header(title: str) -> None:
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


def prompt(label: str) -> str:
    return input(f"  > {label}: ").strip()


def prompt_int(label: str) -> int:
    return int(input(f"  > {label}: ").strip())


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

MENU = """
{div}
  IMOVEIS DATABASE  —  Main Menu
{div}
  [1] Add neighborhood
  [2] Add seller
  [3] Add condo
  [4] Add property
{div}
  [0] Exit
{div}
""".format(div=DIVIDER)

# ─────────────────────────────────────────────
#  Handlers
# ─────────────────────────────────────────────

SUN_OPTIONS = "Manhã  Tarde  Passante"


def handle_add_neighborhood() -> None:
    header("Add Neighborhood")
    name = prompt("Name")
    zone = prompt("Zone")
    add_neighborhood(name, zone)


def handle_add_seller() -> None:
    header("Add Seller")
    name = prompt("Full name")
    phone = prompt("Phone")
    email = prompt("E-mail")
    add_seller(name, phone, email)


def handle_add_condo() -> None:
    header("Add Condo")
    name = prompt("Name")
    address = prompt("Address")
    infra = prompt("Infrastructure (e.g. pool, gym, security)")
    neighborhood_id = prompt_int("Neighborhood ID")
    add_condo(name, address, infra, neighborhood_id)


def handle_add_property() -> None:
    header("Add Property")
    name = prompt("Property name")
    address = prompt("Address")
    description = prompt("Description")
    owner_id = prompt_int("Owner (seller) ID")
    neighborhood_id = prompt_int("Neighborhood ID")
    condo_id = prompt_int("Condo ID")
    price = prompt_int("Price (R$)")
    condo_fee = prompt_int("Condo fee (R$)")
    tax = prompt_int("IPTU (R$)")
    size = prompt_int("Size (m2)")
    rooms = prompt_int("Number of rooms")
    print(f"\n{SUN_OPTIONS}")
    sun = prompt("Sun exposure")
    add_property(
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
    )


# ─────────────────────────────────────────────
#  Dispatch table  —  avoids a chain of if/elif
# ─────────────────────────────────────────────

HANDLERS = {
    1: handle_add_neighborhood,
    2: handle_add_seller,
    3: handle_add_condo,
    4: handle_add_property,
}

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────


def main() -> None:
    while True:
        print(MENU)
        try:
            choice = int(input("  Select an option: ").strip())
        except ValueError:
            print("\n  [!] Numbers only. Try again.")
            continue

        if choice == 0:
            print(f"\n{DIVIDER}\n  Goodbye.\n{DIVIDER}\n")
            break

        handler = HANDLERS.get(choice)
        if handler is None:
            print("\n  [!] Invalid option. Try again.")
            continue

        try:
            handler()
        except ValueError as e:
            print(f"\n  [!] Invalid input — {e}")
        except Exception as e:
            print(f"\n  [!] Unexpected error — {e}")


if __name__ == "__main__":
    main()
