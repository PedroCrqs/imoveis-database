"""
Sincroniza a descrição dos imóveis com ImovelStatus = 'Disponível'.

Fonte da verdade: o arquivo "Descrição.txt" na pasta apontada por
Imoveis.CaminhoDrive ("Opções Diretas", sincronizada pelo rclone).

Para cada imóvel cuja descrição difere do banco, o script:
  1. copia o arquivo para DRIVE_DIR/imoveis/imovel_{id}/ (armazenamento);
  2. atualiza Imoveis.Descricao no banco (só depois de a cópia dar certo).

A pasta local não é gravada aqui: ela é atualizada depois, pelo
sync_photos("download") ao iniciar a UI.

Uso:
    python scripts/sync_descricoes.py            # dry-run, não altera nada
    python scripts/sync_descricoes.py --apply    # copia o arquivo e atualiza o banco
"""

import argparse
import shutil
import sys
from pathlib import Path

import psycopg

from backup import IMOVEIS_DRIVE
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
            f"[Origem: {desc_file}]"
        )

        if apply:
            # Caminho completo do arquivo: se a pasta não existir, o copy2 falha
            # com FileNotFoundError em vez de criar um arquivo "imovel_X" solto.
            destino = IMOVEIS_DRIVE / f"imovel_{property_id}" / DESC_FILENAME

            # 1) Arquivo primeiro: se falhar, o banco não é tocado e a próxima
            #    execução refaz o imóvel.
            try:
                shutil.copy2(desc_file, destino)
            except FileNotFoundError:
                print(f"[ERRO]      Imóvel {property_id}: pasta '{destino.parent}' não existe.")
                errors += 1
                continue
            except OSError as exc:
                print(f"[ERRO]      Imóvel {property_id}: falha ao copiar para '{destino}' ({exc}).")
                errors += 1
                continue

            # 2) Banco por último.
            try:
                with pool.connection() as conn:
                    conn.execute(
                        "UPDATE Imoveis SET Descricao = %s WHERE ImovelID = %s",
                        (new_description, property_id),
                    )
            except psycopg.Error as exc:
                print(f"[ERRO]      Imóvel {property_id}: arquivo copiado, mas o banco falhou ({exc}).")
                errors += 1
                continue

        updated += 1

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
        help="Copia o arquivo para o Drive (imoveis) e atualiza o banco. Sem essa flag, roda em modo dry-run (só mostra o que faria).",
    )
    args = parser.parse_args()

    sync_descriptions(apply=args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
