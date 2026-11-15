# ============================================================
# Lexora — Güvenlik Testleri
# ============================================================
import zipfile
from pathlib import Path

import pytest

from services.validation_service import (
    ValidationError, is_safe_path, validate_input_file,
)


def test_path_traversal_rejected() -> None:
    assert is_safe_path(Path("C:/Users/x"))


def test_zip_bomb_protection(tmp_path: Path) -> None:
    """Şüpheli sıkıştırma oranı olan DOCX reddedilmeli."""
    p = tmp_path / "bomb.docx"
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "x")
        zf.writestr("word/document.xml", "y")
        # 10 MB sıfır → küçük sıkıştırma → yüksek oran.
        zf.writestr("junk.bin", b"\x00" * (10 * 1024 * 1024))
    with pytest.raises(ValidationError) as exc:
        validate_input_file(p)
    assert exc.value.error_key == "zip_bomb"


def test_source_file_unmodified(sample_txt: Path) -> None:
    """validate_input_file kaynak dosyayı değiştirmemeli."""
    before = sample_txt.read_bytes()
    validate_input_file(sample_txt)
    after = sample_txt.read_bytes()
    assert before == after