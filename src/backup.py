import shutil
import hashlib
import asyncio
import re
from pathlib import Path
from database import DATA_PATH, DB_PATH, DRIVE_DIR

BACKUP_PATH = DRIVE_DIR / "imoveis.db"
IMOVEIS_LOCAL = DATA_PATH / "imoveis"
IMOVEIS_DRIVE = DRIVE_DIR / "imoveis"


# Chamar a função sync_folder toda vez que fizermos alguma alteração na .db não é nada prático. Ao adicionar um bloco if dentro do "upload" eu reservo o sync_folder apenas para operações que realmente fazem alguma alteração nos diretórios de imóveis (alteração de preço, inclusão de imóveis ou alteração de status)
async def do_backup(flux: str, sync: bool = False) -> None:
    if flux == "upload":
        await asyncio.to_thread(shutil.copy, DB_PATH, DRIVE_DIR)
        if sync:
            await asyncio.to_thread(sync_folder, IMOVEIS_LOCAL, IMOVEIS_DRIVE)
    elif flux == "download":
        await asyncio.to_thread(shutil.copy, BACKUP_PATH, DATA_PATH)
        await asyncio.to_thread(sync_folder, IMOVEIS_DRIVE, IMOVEIS_LOCAL)


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def sync_folder(src: Path, dst: Path) -> None:
    """Sincroniza apenas arquivos novos ou alterados."""
    dst.mkdir(parents=True, exist_ok=True)

    for src_file in src.rglob("*"):
        if not src_file.is_file():
            continue

        dst_file = dst / src_file.relative_to(src)

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        if not dst_file.exists():
            shutil.copy2(src_file, dst_file)
            continue

        src_stat = src_file.stat()
        dst_stat = dst_file.stat()

        # compara tamanho e data de modificação
        if (
            src_stat.st_size != dst_stat.st_size
            or src_stat.st_mtime > dst_stat.st_mtime
        ):
            shutil.copy2(src_file, dst_file)


def update_description_prices(
    folder: Path,
    price: float | None = None,
    condo_fee: float | None = None,
    tax: float | None = None,
) -> None:
    """Atualiza os valores no Descrição.txt dentro de folder."""
    desc_file = folder / "Descrição.txt"
    if not desc_file.is_file():
        raise FileNotFoundError(f"'Descrição.txt' não encontrado em '{folder}'.")

    text = desc_file.read_text(encoding="utf-8")

    if price is not None:
        text = re.sub(
            r"\*R\$[\s\d.,]+\*",
            f"*R$ {_fmt(price)}*",
            text,
        )
    if condo_fee is not None:
        text = re.sub(
            r"Condomínio: R\$[\s\d.,]+",
            f"Condomínio: R$ {_fmt(condo_fee)}",
            text,
        )
    if tax is not None:
        text = re.sub(
            r"IPTU: R\$[\s\d.,]+",
            f"IPTU: R$ {_fmt(tax)}",
            text,
        )

    desc_file.write_text(text, encoding="utf-8")


def _fmt(value: float) -> str:
    """Formata número no padrão brasileiro: 3.000,00"""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
