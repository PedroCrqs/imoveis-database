import asyncio
import inspect
import shutil
import webbrowser
from pathlib import Path

import psycopg

from add_ref import _inject_ref, _patch_txt
from backup import DRIVE_DIR, sync_photos, update_description_prices
from repository import (
    IMOVEIS_UPDATABLE,
    VALID_STATUS,
    add_condo,
    add_neighborhood,
    add_photos,
    add_property,
    add_seller,
    get_available_properties,
    get_condo_name,
    get_drive_path,
    get_folder_path,
    get_neighborhood_name,
    get_owner,
    get_property,
    get_property_by_condo,
    get_property_by_neighborhood,
    get_public_link,
    update_condo_name,
    update_field,
    update_prices,
    update_status,
)

OP_DIR_PATH = DRIVE_DIR / "Opções Diretas"
DESKTOP_PATH = Path("/home/pedrocrqs/Desktop")

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
    raw = input(f"  > {label} (Enter para pular): ").strip()
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
        err(f"Caminho não encontrado: {folder_path}")


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

MENU = """
{DIV}
      IMOVEIS DATABASE  —  Menu Principal
{DIV}
  [1] Adicionar bairro
  [2] Adicionar proprietário
  [3] Adicionar condomínio
  [4] Adicionar imóvel
  [5] Atualizar status do imóvel
  [6] Atualizar valores
  [7] Corrigir um campo
  [8] Buscar imóvel
  [9] Buscar imóvel por bairro
  [10] Exibir imóveis disponíveis
  [11] Exibir proprietário por ID
  [12] Buscar imóvel por condomínio
  [13] Atualizar nome do condomínio
{DIV}
  [0] Sair
{DIV}""".format(DIV=DIV)

# ─────────────────────────────────────────────
#  Handlers — INSERT
# ─────────────────────────────────────────────

ZONES = ["Zona Oeste", "Zona Sudoeste", "Zona Sul", "Zona Norte"]
ZONES_LABEL = "0: Zona Oeste, 1: Zona Sudoeste, 2: Zona Sul, 3: Zona Norte"
SUN_OPTS = ["Manhã", "Tarde", "Passante"]
SUN_OPTS_LABEL = "0: Manhã, 1: Tarde, 2: Passante"
TIPOLOGIA = ["Apartamento", "Casa", "Cobertura", "Studio", "Garden", "Loja"]
TIPOLOGIA_LABEL = "0: Apartamento, 1: Casa, 2: Cobertura, 3: Studio, 4: Garden, 5: Loja"
VALID_STATUS_LABEL = "0: Disponível | 1: Vendido | 2: Alugado | 3: Retirado de Venda"


def handle_add_neighborhood() -> None:
    header("Adicionar Bairro")
    print(f"  Zonas: {ZONES_LABEL}")
    name = prompt("Nome")
    zone = ZONES[prompt_int("Zona")]
    row_id = add_neighborhood(name, zone)
    ok(f"Bairro '{name}' adicionado com ID {row_id}.")


def handle_add_seller() -> None:
    header("Adicionar Proprietário")
    name = prompt("Nome completo")
    phone = prompt("Telefone")
    email = prompt("E-mail")
    row_id = add_seller(name, phone, email)
    ok(f"Proprietário '{name}' adicionado com ID {row_id}.")


def handle_add_condo() -> None:
    header("Adicionar Condomínio")
    name = prompt("Nome")
    address = prompt("Endereço")
    infra = prompt("Infraestrutura (ex: piscina, academia, portaria)")
    neighborhood_id = prompt_int("ID do Bairro")
    row_id = add_condo(name, address, infra, neighborhood_id)
    ok(f"Condomínio '{name}' adicionado com ID {row_id}.")


async def handle_add_property() -> None:
    header("Adicionar Imóvel")
    print(f"  Tipologias: {TIPOLOGIA_LABEL}")
    tipologia = TIPOLOGIA[prompt_int("Tipo")]
    address = prompt("Endereço")
    owner_id = prompt_int("ID do Proprietário")
    neighborhood_id = prompt_int("ID do Bairro")
    condo_id = parse_optional_int(prompt("ID do Condomínio (Enter para pular)"))
    rooms = prompt_int("Quantidade de quartos")
    park = prompt_int("Vagas de garagem")
    price = prompt_float("Valor de venda (R$)")
    condo_fee = prompt_float("Condomínio (R$)")
    tax = prompt_float("IPTU (R$)")
    size = prompt_int("Metragem (m²)")
    print(f"\n  Posição do sol: {SUN_OPTS_LABEL}")
    sun = SUN_OPTS[prompt_int("Sol")]
    folder_name = prompt("Nome da pasta")
    folder_path = DESKTOP_PATH / folder_name
    public_link = prompt("Link público do Google Drive")
    desc_file = folder_path / "Descrição.txt"
    if not desc_file.is_file():
        raise FileNotFoundError(f"'Descrição.txt' não encontrado em '{folder_path}'.")
    description = desc_file.read_text(encoding="utf-8").strip()

    drive_path = OP_DIR_PATH / folder_name
    if drive_path.exists():
        ok(f"Pasta do Drive '{folder_name}' já existe — mantendo.")
    else:
        shutil.copytree(str(folder_path), str(drive_path))
        ok(f"Pasta copiada para '{OP_DIR_PATH}'.")

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
    ok(f"Imóvel adicionado com ID {imovel_id}.")

    local_folder = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "imoveis"
        / f"imovel_{imovel_id}"
    )
    shutil.copytree(str(folder_path), str(local_folder))
    ok(f"Pasta copiada para '{local_folder}'.")
    inserted = add_photos(str(local_folder), imovel_id)
    ok(f"{len(inserted)} foto(s) cadastrada(s).")
    shutil.rmtree(str(folder_path))

    _patch_txt(local_folder, imovel_id)
    _patch_txt(drive_path, imovel_id)
    new_desc = (local_folder / "Descrição.txt").read_text(encoding="utf-8").strip()
    update_field(imovel_id, "Descricao", new_desc)
    await sync_photos("upload")


# ─────────────────────────────────────────────
#  Handlers — UPDATE
# ─────────────────────────────────────────────


async def handle_update_status() -> None:
    header("Atualizar Status do Imóvel")
    property_id = prompt_int("ID do Imóvel")
    prop = get_property(property_id)
    if prop is None:
        err("Imóvel não encontrado.")
        return

    print(f"  Opções de status: {VALID_STATUS_LABEL}")
    status = VALID_STATUS[prompt_int("Novo status")]
    update_status(property_id, status)

    drive_path = get_drive_path(property_id)

    if status != "Disponível" and drive_path and drive_path.exists():
        local_folder = get_folder_path(property_id)
        if local_folder:
            hidden = local_folder / ".drive_folder_name.txt"
            hidden.write_text(drive_path.name, encoding="utf-8")
        shutil.rmtree(str(drive_path))
        ok(f"Pasta do Drive '{drive_path.name}' removida de 'Opções Diretas'.")

    elif status == "Disponível":
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
                ok(f"Pasta do Drive '{folder_name}' restaurada em 'Opções Diretas'.")

    await sync_photos("upload")
    ok(f"Imóvel {property_id} marcado como '{status}'.")


async def handle_update_prices() -> None:
    header("Atualizar Valores")
    print("  Deixe em branco para manter o valor atual.")
    imovel_id = prompt_int("ID do Imóvel")
    price = prompt_optional_float("Novo valor de venda (R$)")
    condo_fee = prompt_optional_float("Novo condomínio (R$)")
    tax = prompt_optional_float("Novo IPTU (R$)")

    local_folder = get_folder_path(imovel_id)
    drive_folder = get_drive_path(imovel_id)

    if local_folder:
        update_description_prices(local_folder, price, condo_fee, tax)
        description = (
            (local_folder / "Descrição.txt").read_text(encoding="utf-8").strip()
        )
    else:
        description = None

    if drive_folder and drive_folder.exists():
        update_description_prices(drive_folder, price, condo_fee, tax)
    update_prices(imovel_id, price, condo_fee, tax, description)

    # Sincroniza as alterações de preço/descrição para o Drive
    await sync_photos("upload")
    ok(f"Valores atualizados para o imóvel {imovel_id}.")


async def handle_update_field() -> None:
    header("Corrigir um Campo")
    print(f"  Campos atualizáveis: {', '.join(sorted(IMOVEIS_UPDATABLE))}")
    imovel_id = prompt_int("ID do Imóvel")
    field = prompt("Nome do campo")
    value = prompt("Novo valor")
    update_field(imovel_id, field, value)

    # Sincroniza correções de campos para o Drive
    await sync_photos("upload")
    ok(f"Campo '{field}' atualizado para o imóvel {imovel_id}.")


async def handle_update_condo_name() -> None:
    header("Atualizar Nome do Condomínio")
    condo_id = prompt_int("ID do Condomínio")
    name = prompt("Novo nome")
    update_condo_name(condo_id, name)

    # Sincroniza alterações estruturais para o Drive
    await sync_photos("upload")
    ok(f"Nome do condomínio atualizado para o condomínio {condo_id}.")


# ─────────────────────────────────────────────
#  Handlers — SHOW
# ─────────────────────────────────────────────


def handle_find_property() -> None:
    header("Buscar Imóvel")
    property_id = prompt_int("ID do Imóvel")
    prop = get_property(property_id)

    if prop is None:
        err("Imóvel não encontrado.")
        return

    tipology = prop["tipologia"]
    rooms = prop["quartos"]
    metragem = prop["metragem"]
    value = prop["valor"]
    owner = get_owner(prop["proprietarioid"])
    condo_name = display_na(get_condo_name(prop["condominioid"]))
    neighborhood_name = display_na(get_neighborhood_name(prop["bairroid"]))
    status = prop["imovelstatus"]
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
  Proprietário: {owner["nome"]}
  Telefone: {owner["telefone"]}
{DIV}
  Link público: {public}
{DIV}""")

    response = prompt("Enter para voltar / 0 para abrir pasta local")
    if response == "0" and local_folder:
        open_folder(local_folder)


def handle_find_property_by_neighborhood() -> None:
    header("Buscar Imóvel por Bairro")
    neighborhood_id = prompt_int("ID do Bairro")
    neighborhood_name = display_na(get_neighborhood_name(neighborhood_id))
    prop_list = get_property_by_neighborhood(neighborhood_id)
    for prop in prop_list:
        condo_name = display_na(get_condo_name(prop["condominioid"]))
        print(
            f"  ID:{prop['imovelid']} | {condo_name} | {neighborhood_name} | {prop['tipologia']} | R$ {prop['valor']} | {prop['quartos']}qts\n{DIV}"
        )
    prompt("Enter para voltar")


def handle_find_property_by_condo() -> None:
    header("Buscar Imóvel por Condomínio")
    condo_id = prompt_int("ID do Condomínio")
    prop_list = get_property_by_condo(condo_id)
    condo_name = display_na(get_condo_name(condo_id))
    for prop in prop_list:
        neighborhood_name = display_na(get_neighborhood_name(prop["bairroid"]))
        print(
            f"  ID:{prop['imovelid']} | {condo_name} | {neighborhood_name} | {prop['tipologia']} | R$ {prop['valor']} | {prop['quartos']}qts\n{DIV}"
        )
    prompt("Enter para voltar")


def handle_show_available_properties() -> None:
    header("Imóveis Disponíveis")
    prop_list = get_available_properties()
    if not prop_list:
        print("  Nenhum imóvel disponível.")
    for prop in prop_list:
        condo_name = display_na(get_condo_name(prop["condominioid"]))
        neighborhood_name = display_na(get_neighborhood_name(prop["bairroid"]))
        print(
            f"  ID:{prop['imovelid']} | {condo_name} | {neighborhood_name} | {prop['tipologia']} | R$ {prop['valor']} | {prop['quartos']}qts\n{DIV}"
        )
    prompt("Enter para voltar")


def handle_find_owner() -> None:
    header("Buscar Proprietário")
    owner_id = prompt_int("ID do Proprietário")
    owner = get_owner(owner_id)
    if owner is None:
        err("Proprietário não encontrado.")
        return
    print(f"""
{DIV}
  ID:{owner_id} | {owner["nome"]}
  Telefone: {owner["telefone"]}
  E-mail: {display_na(owner["email"])}
{DIV}""")
    prompt("Enter para voltar")


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
    13: handle_update_condo_name,
}

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────


async def main() -> None:
    print('Sincronizando banco de dados...')
    await sync_photos("download")
    while True:
        print(MENU)
        try:
            choice = prompt_int("Selecione uma opção")
        except ValueError:
            err("Apenas números. Tente novamente.")
            continue

        if choice == 0:
            print(f"\n{DIV}\n  Até logo.\n{DIV}\n")
            break

        handler = HANDLERS.get(choice)
        if handler is None:
            err("Opção inválida. Tente novamente.")
            continue

        try:
            if inspect.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        except ValueError as e:
            err(str(e))
            if "Status inválido" in str(e) or "Invalid status" in str(e):
                err(f"Opções válidas: {' | '.join(VALID_STATUS)}")
            elif "Campo não atualizável" in str(e) or "Field not updatable" in str(e):
                err(f"Campos permitidos: {', '.join(sorted(IMOVEIS_UPDATABLE))}")
        except LookupError as e:
            err(str(e))
        except psycopg.IntegrityError as e:
            err(f"Erro de integridade do banco de dados — {e}")
        except (NotADirectoryError, FileNotFoundError) as e:
            err(str(e))
        except Exception as e:
            err(f"Erro inesperado — {e}")


if __name__ == "__main__":
    asyncio.run(main())
