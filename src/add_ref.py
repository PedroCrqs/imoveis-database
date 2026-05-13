"""
add_ref.py
----------
Injeta '_Ref: {ImovelID}_' na terceira linha de todas as descrições,
sincronizando .db, Descrição.txt local e Descrição.txt no Drive.

Restrito a imóveis com status 'Disponível'.
Idempotente: pula imóveis que já estão sincronizados nos três lugares.
"""

import re
import sqlite3
import unicodedata
import asyncio
from pathlib import Path

from database import DB_PATH
from repository import get_folder_path, get_drive_path
from backup import do_backup

REF_PATTERN = re.compile(r"^_Ref: \d+_$", re.MULTILINE)


# ─── helpers ──────────────────────────────────────────────────────────────────


def _inject_ref(text: str, imovel_id: int) -> str | None:
    """
    Insere '_Ref: {id}_' na terceira linha do texto.
    Retorna None se a ref já existir (idempotência).
    """
    if REF_PATTERN.search(text):
        return None

    lines = text.splitlines(keepends=True)
    lines.insert(3, f"_Ref: {imovel_id}_\n")
    return "".join(lines)


def _patch_txt(folder: Path, imovel_id: int) -> bool:
    """
    Atualiza o Descrição.txt dentro de `folder`.
    Retorna True se alterou, False se já estava correto ou arquivo ausente.
    """
    if not folder or not folder.is_dir():
        return False

    desc_file = next(
        (
            f
            for f in folder.iterdir()
            if unicodedata.normalize("NFC", f.name) == "Descrição.txt"
        ),
        None,
    )
    if desc_file is None:
        return False

    original = desc_file.read_text(encoding="utf-8")
    updated = _inject_ref(original, imovel_id)

    if updated is None:
        return False  # já tinha ref

    desc_file.write_text(updated, encoding="utf-8")
    return True


def _read_txt(folder: Path) -> str | None:
    """Lê o conteúdo do Descrição.txt, retorna None se ausente."""
    if not folder or not folder.is_dir():
        return None

    desc_file = next(
        (
            f
            for f in folder.iterdir()
            if unicodedata.normalize("NFC", f.name) == "Descrição.txt"
        ),
        None,
    )
    return desc_file.read_text(encoding="utf-8") if desc_file else None


# ─── função principal ─────────────────────────────────────────────────────────


def add_ref_to_all() -> None:
    """
    Percorre todos os imóveis com status 'Disponível' e garante que a ref
    está nos três lugares: .db, Descrição.txt local e Descrição.txt no Drive.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT ImovelID, Descricao FROM Imoveis WHERE ImovelStatus = 'Disponível'"
        ).fetchall()

    updated_db = 0
    updated_local = 0
    updated_drive = 0
    skipped = 0

    with sqlite3.connect(DB_PATH) as conn:
        for row in rows:
            imovel_id = row["ImovelID"]
            descricao = row["Descricao"]

            # ── .txt local ────────────────────────────────────────────────────
            local_folder = get_folder_path(imovel_id)
            if _patch_txt(local_folder, imovel_id):
                updated_local += 1

            # ── .txt Drive ────────────────────────────────────────────────────
            drive_folder = get_drive_path(imovel_id)
            if _patch_txt(drive_folder, imovel_id):
                updated_drive += 1

            # ── banco ─────────────────────────────────────────────────────────
            # Usa o .txt local como fonte da verdade (já patchado acima).
            # Se o banco já tem ref, pula. Caso contrário, sincroniza.
            if REF_PATTERN.search(descricao):
                skipped += 1
                print(f"  [SKIP] ID {imovel_id} — banco já sincronizado.")
                continue

            # Tenta ler do .txt local; fallback para injetar direto na string do banco
            new_desc = _read_txt(local_folder) or _inject_ref(descricao, imovel_id)

            if new_desc is None:
                skipped += 1
                continue

            conn.execute(
                "UPDATE Imoveis SET Descricao = ? WHERE ImovelID = ?",
                (new_desc.strip(), imovel_id),
            )
            updated_db += 1

        conn.commit()

    print(
        f"\n✔️  Concluído — "
        f"DB: {updated_db} | Local: {updated_local} | Drive: {updated_drive} | "
        f"Pulados: {skipped}"
    )


# ─── entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    add_ref_to_all()
    asyncio.run(do_backup("upload", True))  # backup no drive
