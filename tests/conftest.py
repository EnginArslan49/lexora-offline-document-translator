# ============================================================
# Lexora — Pytest Paylaşılan Fixture'lar
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path

# Proje kökünü sys.path'e ekle.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

import config


@pytest.fixture
def tmp_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Geçici ayar dosyası."""
    p = tmp_path / "settings.json"
    monkeypatch.setattr(config, "SETTINGS_FILE_PATH", p)
    monkeypatch.setattr(config, "HISTORY_FILE_PATH", tmp_path / "history.json")
    return p


@pytest.fixture
def sample_txt(tmp_path: Path) -> Path:
    """Örnek UTF-8 TXT."""
    p = tmp_path / "ornek.txt"
    p.write_text("Hello world.\n\nThis is a test.", encoding="utf-8")
    return p


@pytest.fixture
def sample_docx(tmp_path: Path) -> Path:
    """Örnek DOCX (bold run'lı)."""
    from docx import Document
    d = Document()
    p = d.add_paragraph()
    p.add_run("Hello ")
    r = p.add_run("bold")
    r.bold = True
    p.add_run(" world.")
    d.save(str(tmp_path / "ornek.docx"))
    return tmp_path / "ornek.docx"