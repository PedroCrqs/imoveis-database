import re
import shutil
from pathlib import Path

from database import DATA_PATH

# Diretório do Google Drive montado localmente (rclone, Drive for Desktop, etc).
# Ajuste via variável de ambiente se o caminho variar entre ambientes.
import os

DRIVE_DIR = Path(
    os.environ.get(
        "DRIVE_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "majesto-drive"),
    )
)

IMOVEIS_LOCAL = DATA_PATH / "imoveis"
IMOVEIS_DRIVE = DRIVE_DIR / "imoveis"

# NOTA DE MIGRAÇÃO: a versão anterior deste módulo copiava o arquivo
# `imoveis.db` inteiro de/para o Drive antes e depois de cada operação
# (do_backup("download"/"upload")). Isso existia porque o SQLite é um
# arquivo local sem servidor — não havia outra forma de "compartilhar"
# o banco entre máquinas.
#
# Com PostgreSQL isso deixa de existir: o banco é um servidor que várias
# fontes (site, robô de disparo, sentinela, este CLI) acessam diretamente
# e concorrentemente. Manter a cópia do .db aqui seria, na melhor das
# hipóteses, inútil, e na pior, uma fonte de dados desatualizados sendo
# sobrescritos por engano.
#
# O que continua fazendo sentido é sincronizar as FOTOS dos imóveis com o
# Drive — isso é independente do motor de banco de dados.


def file_hash(path: Path) -> str:
    import hashlib

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

        if (
            src_stat.st_size != dst_stat.st_size
            or src_stat.st_mtime > dst_stat.st_mtime
        ):
            shutil.copy2(src_file, dst_file)


async def sync_photos(direction: str) -> None:
    """direction: 'upload' (local → Drive) ou 'download' (Drive → local)."""
    import asyncio

    if direction == "upload":
        await asyncio.to_thread(sync_folder, IMOVEIS_LOCAL, IMOVEIS_DRIVE)
    elif direction == "download":
        await asyncio.to_thread(sync_folder, IMOVEIS_DRIVE, IMOVEIS_LOCAL)
    else:
        raise ValueError(f"Invalid direction: '{direction}'")


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
        text = re.sub(r"\*R\$ ?[\d.,]+\*", f"*R$ {_fmt(price)}*", text)

    if condo_fee is not None:
        text = re.sub(
            r"Condomínio: R\$ ?[\d.,]+", f"Condomínio: R$ {_fmt(condo_fee)}", text
        )

    if tax is not None:
        text = re.sub(r"IPTU: R\$ ?[\d.,]+", f"IPTU: R$ {_fmt(tax)}", text)

    desc_file.write_text(text, encoding="utf-8")


def _fmt(value: float) -> str:
    """Formata número no padrão brasileiro: 3.000,00"""
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
