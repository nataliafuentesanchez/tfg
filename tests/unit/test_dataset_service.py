# =============================================================================
# AnalisisImagenes - Proyecto para el analisis de imagenes con metodologia SDD.
# Copyright (c) 2026 Natalia Fuentes Sanchez
# Licensed under the MIT License. See LICENSE for details.
# Built with dbv-specs-ops - https://github.com/davidbuenov/dbv-specs-ops
# =============================================================================

from pathlib import Path

from app.services.dataset_service import ingest_dataset, split_lesions_by_group


def test_split_lesions_by_group_keeps_same_lesion_in_one_split() -> None:
    metadata = [
        {"lesion_id": "L1", "image_id": "ISIC_001", "dx": "mel", "dx_type": "histo"},
        {"lesion_id": "L1", "image_id": "ISIC_002", "dx": "mel", "dx_type": "histo"},
        {"lesion_id": "L2", "image_id": "ISIC_003", "dx": "bkl", "dx_type": "consensus"},
    ]

    split_map = split_lesions_by_group(metadata, train_ratio=0.5, random_state=7)

    assert set(split_map.keys()) == {"L1", "L2"}
    assert split_map["L1"] in {"train", "test"}
    assert split_map["L2"] in {"train", "test"}


def test_ingest_dataset_registers_images_and_uses_image_folder(tmp_path: Path) -> None:
    image_dir = tmp_path / "imagenes"
    image_dir.mkdir()
    (image_dir / "ISIC_001.jpg").write_bytes(b"img1")
    (image_dir / "ISIC_002.jpg").write_bytes(b"img2")

    metadata_path = tmp_path / "metadata.csv"
    metadata_path.write_text(
        "lesion_id,image_id,dx,dx_type,age,sex,localization\n"
        "L1,ISIC_001,mel,histo,60,male,face\n"
        "L1,ISIC_002,mel,histo,60,male,face\n",
        encoding="utf-8",
    )

    db_path = tmp_path / "dataset.sqlite3"
    summary = ingest_dataset(metadata_path, image_dir, db_path)

    assert summary["total_images"] == 2
    assert summary["total_lesions"] == 1
    assert summary["missing_files"] == 0
    assert db_path.exists()


def test_ingest_dataset_finds_images_in_nested_directories(tmp_path: Path) -> None:
    image_dir = tmp_path / "imagenes"
    part_dir = image_dir / "HAM10000_images_part_1"
    part_dir.mkdir(parents=True)
    (part_dir / "ISIC_001.jpg").write_bytes(b"img1")

    metadata_path = tmp_path / "metadata.csv"
    metadata_path.write_text(
        "lesion_id,image_id,dx,dx_type,age,sex,localization\n"
        "L1,ISIC_001,mel,histo,60,male,face\n",
        encoding="utf-8",
    )

    db_path = tmp_path / "dataset.sqlite3"
    summary = ingest_dataset(metadata_path, image_dir, db_path)

    assert summary["total_images"] == 1
    assert summary["total_lesions"] == 1
    assert summary["missing_files"] == 0
    assert db_path.exists()
