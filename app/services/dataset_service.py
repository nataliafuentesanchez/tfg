# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from __future__ import annotations

import csv
import random
import sqlite3
from pathlib import Path
from typing import Iterable


def _normalize_image_id(raw_value: str | None) -> str:
    if raw_value is None:
        return ""
    image_id = str(raw_value).strip()
    if not image_id:
        return ""
    image_id = image_id.rsplit(".", 1)[0] if "." in image_id else image_id
    return image_id


def _normalize_label(value: str | None) -> str:
    if value is None:
        return "unknown"
    cleaned = str(value).strip().lower()
    if cleaned in {"nv", "mel", "bkl", "bcc", "akiec", "vasc", "df"}:
        return cleaned
    return cleaned


def split_lesions_by_group(
    metadata: Iterable[dict[str, str]],
    train_ratio: float = 0.8,
    random_state: int = 42,
) -> dict[str, str]:
    lesion_ids = sorted({row["lesion_id"] for row in metadata if row.get("lesion_id")})
    rng = random.Random(random_state)
    rng.shuffle(lesion_ids)

    split_index = max(1, int(round(len(lesion_ids) * train_ratio)))
    train_lesions = set(lesion_ids[:split_index])

    split_map: dict[str, str] = {}
    for lesion_id in lesion_ids:
        split_map[lesion_id] = "train" if lesion_id in train_lesions else "test"
    return split_map


def ingest_dataset(metadata_path: str | Path, image_dir: str | Path, db_path: str | Path) -> dict[str, int]:
    metadata_file = Path(metadata_path)
    image_folder = Path(image_dir)
    database_file = Path(db_path)

    if not metadata_file.exists():
        raise FileNotFoundError(f"No existe el fichero de metadata: {metadata_file}")
    if not image_folder.exists():
        raise FileNotFoundError(f"No existe la carpeta de imagenes: {image_folder}")

    database_file.parent.mkdir(parents=True, exist_ok=True)

    with metadata_file.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    if not rows:
        raise ValueError("El CSV de metadatos no tiene filas.")

    lesion_ids = {row["lesion_id"] for row in rows if row.get("lesion_id")}
    image_index: dict[str, Path] = {}
    for candidate in image_folder.rglob("*"):
        if candidate.is_file() and candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            image_index.setdefault(candidate.stem.lower(), candidate)

    missing_files: list[str] = []
    valid_images = 0

    conn = sqlite3.connect(database_file)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS dataset_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesion_id TEXT NOT NULL,
            image_id TEXT NOT NULL UNIQUE,
            filename TEXT NOT NULL,
            dx TEXT,
            dx_type TEXT,
            age REAL,
            sex TEXT,
            localization TEXT,
            source_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    for row in rows:
        image_id = _normalize_image_id(row.get("image_id"))
        if not image_id:
            continue

        file_path = image_index.get(image_id.lower())
        if file_path is None:
            missing_files.append(f"{image_id}.jpg")
            continue

        filename = file_path.name
        cur.execute(
            """
            INSERT OR REPLACE INTO dataset_images (
                lesion_id, image_id, filename, dx, dx_type, age, sex, localization, source_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("lesion_id", "unknown").strip(),
                image_id,
                filename,
                _normalize_label(row.get("dx")),
                (row.get("dx_type") or "unknown").strip(),
                float(row["age"]) if row.get("age") not in (None, "") else None,
                (row.get("sex") or "unknown").strip(),
                (row.get("localization") or "unknown").strip(),
                str(file_path),
            ),
        )
        valid_images += 1

    conn.commit()
    conn.close()

    return {
        "total_images": valid_images,
        "total_lesions": len(lesion_ids),
        "missing_files": len(missing_files),
    }
