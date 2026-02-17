"""
Minimal PEP 517 backend for this project.

This backend builds a pure-Python wheel containing:
- cli.py
- client.py
- server.py
- console script entry point: broadcast-server = cli:main

It also supports editable installs by returning a wheel from build_editable.
"""

from __future__ import annotations

import base64
import csv
import hashlib
from io import StringIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT_NAME = "broadcast-server"
DIST_NAME = "broadcast_server"
VERSION = "0.1.0"
SUMMARY = "CLI-based WebSocket broadcast server and client"
REQUIRES_PYTHON = ">=3.10"
DEPENDENCIES = ("websockets>=16.0",)
MODULE_FILES = ("cli.py", "client.py", "server.py")


def _dist_info_dir() -> str:
    return f"{DIST_NAME}-{VERSION}.dist-info"


def _wheel_filename() -> str:
    return f"{DIST_NAME}-{VERSION}-py3-none-any.whl"


def _metadata_text() -> str:
    lines = [
        "Metadata-Version: 2.1",
        f"Name: {PROJECT_NAME}",
        f"Version: {VERSION}",
        f"Summary: {SUMMARY}",
        f"Requires-Python: {REQUIRES_PYTHON}",
    ]
    lines.extend(f"Requires-Dist: {dep}" for dep in DEPENDENCIES)
    return "\n".join(lines) + "\n"


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: custom-build-backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _entry_points_text() -> str:
    return "[console_scripts]\nbroadcast-server = cli:main\n"


def _top_level_text() -> str:
    return "cli\nclient\nserver\n"


def _hash_and_size(data: bytes) -> tuple[str, str]:
    digest = hashlib.sha256(data).digest()
    encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"sha256={encoded}", str(len(data))


def _record_text(files: list[tuple[str, bytes]], record_path: str) -> str:
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")

    for path, data in files:
        digest, size = _hash_and_size(data)
        writer.writerow((path, digest, size))

    writer.writerow((record_path, "", ""))
    return output.getvalue()


def _build_archive(wheel_directory: str) -> str:
    project_root = Path(__file__).resolve().parent
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)

    wheel_name = _wheel_filename()
    wheel_path = wheel_dir / wheel_name
    dist_info = _dist_info_dir()

    files_for_record: list[tuple[str, bytes]] = []

    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as zf:
        for module in MODULE_FILES:
            src = project_root / module
            data = src.read_bytes()
            zf.writestr(module, data)
            files_for_record.append((module, data))

        metadata_files = {
            f"{dist_info}/METADATA": _metadata_text().encode("utf-8"),
            f"{dist_info}/WHEEL": _wheel_text().encode("utf-8"),
            f"{dist_info}/entry_points.txt": _entry_points_text().encode("utf-8"),
            f"{dist_info}/top_level.txt": _top_level_text().encode("utf-8"),
        }

        for path, data in metadata_files.items():
            zf.writestr(path, data)
            files_for_record.append((path, data))

        record_path = f"{dist_info}/RECORD"
        record_data = _record_text(files_for_record, record_path).encode("utf-8")
        zf.writestr(record_path, record_data)

    return wheel_name


def _build_editable_archive(wheel_directory: str) -> str:
    project_root = Path(__file__).resolve().parent
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)

    wheel_name = _wheel_filename()
    wheel_path = wheel_dir / wheel_name
    dist_info = _dist_info_dir()

    files_for_record: list[tuple[str, bytes]] = []

    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as zf:
        pth_path = f"{DIST_NAME}.pth"
        pth_data = f"{project_root}\n".encode("utf-8")
        zf.writestr(pth_path, pth_data)
        files_for_record.append((pth_path, pth_data))

        metadata_files = {
            f"{dist_info}/METADATA": _metadata_text().encode("utf-8"),
            f"{dist_info}/WHEEL": _wheel_text().encode("utf-8"),
            f"{dist_info}/entry_points.txt": _entry_points_text().encode("utf-8"),
            f"{dist_info}/top_level.txt": _top_level_text().encode("utf-8"),
        }

        for path, data in metadata_files.items():
            zf.writestr(path, data)
            files_for_record.append((path, data))

        record_path = f"{dist_info}/RECORD"
        record_data = _record_text(files_for_record, record_path).encode("utf-8")
        zf.writestr(record_path, record_data)

    return wheel_name


def _write_metadata(metadata_directory: str) -> str:
    dist_info = _dist_info_dir()
    target = Path(metadata_directory) / dist_info
    target.mkdir(parents=True, exist_ok=True)

    (target / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (target / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    (target / "entry_points.txt").write_text(_entry_points_text(), encoding="utf-8")
    (target / "top_level.txt").write_text(_top_level_text(), encoding="utf-8")

    return dist_info


def _supported_features() -> list[str]:
    return ["build_editable"]


def get_requires_for_build_wheel(config_settings=None) -> list[str]:
    return []


def get_requires_for_build_editable(config_settings=None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(metadata_directory: str, config_settings=None) -> str:
    return _write_metadata(metadata_directory)


def prepare_metadata_for_build_editable(metadata_directory: str, config_settings=None) -> str:
    return _write_metadata(metadata_directory)


def build_wheel(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    return _build_archive(wheel_directory)


def build_editable(wheel_directory: str, config_settings=None, metadata_directory=None) -> str:
    return _build_editable_archive(wheel_directory)
