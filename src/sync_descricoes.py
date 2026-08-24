"""
Sincroniza a coluna Descricao dos imóveis com ImovelStatus = 'Disponível'
com o conteúdo do arquivo "Descrição.txt" de cada imóvel.

Fonte única: CaminhoDrive (Imoveis.CaminhoDrive), a pasta sincronizada
automaticamente pelo rclone. A pasta local (get_folder_path) não é usada
aqui de propósito — o rclone é a fonte da verdade.

Uso:
    python scripts/sync_descricoes.py            # dry-run, não altera nada
    python scripts/sync_descricoes.py --apply    # aplica as alterações no banco
"""

import argparse
import sys
from pathlib import Path

from database import pool
from repository import get_available_properties, get_drive_path

DESC_FILENAME = "Descrição.txt"


def find_description_file(property_id: int) -> Path | None:
    folder = get_drive_path(property_id)
    if folder is None:
        return None
    candidate = folder / DESC_FILENAME
    return candidate if candidate.is_file() else None


def sync_descriptions(apply: bool) -> None:
    properties = get_available_properties()
    if not properties:
        print("Nenhum imóvel com status 'Disponível' encontrado.")
        return

    updated = unchanged = missing = errors = 0

    for prop in properties:
        property_id = prop["imovelid"]
        current_description = (prop.get("descricao") or "").strip()

        desc_file = find_description_file(property_id)
        if desc_file is None:
            print(
                f"[FALTANDO]  Imóvel {property_id}: '{DESC_FILENAME}' não encontrado em CaminhoDrive "
                f"(coluna vazia, pasta ausente, ou rclone ainda não sincronizou)."
            )
            missing += 1
            continue

        try:
            new_description = desc_file.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"[ERRO]      Imóvel {property_id}: falha ao ler '{desc_file}' ({exc}).")
            errors += 1
            continue

        if not new_description:
            print(f"[ERRO]      Imóvel {property_id}: '{desc_file}' está vazio.")
            errors += 1
            continue

        if new_description == current_description:
            unchanged += 1
            continue

        print(
            f"[ATUALIZAR] Imóvel {property_id}: descrição muda "
            f"({len(current_description)} -> {len(new_description)} caracteres) "
            f"[Drive: {desc_file}]"
        )
        updated += 1

        if apply:
            with pool.connection() as conn:
                conn.execute(
                    "UPDATE Imoveis SET Descricao = %s WHERE ImovelID = %s",
                    (new_description, property_id),
                )

    print("\n--- Resumo ---")
    print(f"Atualizados:            {updated}{'' if apply else '  (dry-run, nada foi salvo — rode com --apply)'}")
    print(f"Sem alteração:          {unchanged}")
    print(f"Arquivo não encontrado: {missing}")
    print(f"Erros:                  {errors}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as alterações no banco. Sem essa flag, roda em modo dry-run (só mostra o que faria).",
    )
    args = parser.parse_args()

    sync_descriptions(apply=args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
