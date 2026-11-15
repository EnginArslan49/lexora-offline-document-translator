# ============================================================
# Lexora — TXT Testleri
# ============================================================
from pathlib import Path

import pytest

from services.validation_service import ValidationError, validate_input_file


def test_txt_utf8(sample_txt: Path) -> None:
    info = validate_input_file(sample_txt)
    assert info["format"] == ".txt"
    assert info["encoding"] in ("utf-8", "utf-8-sig")
    assert "Hello" in str(info["text"])


def test_txt_turkish_chars(tmp_path: Path) -> None:
    p = tmp_path / "tr.txt"
    p.write_text("Merhaba dünya. ÇĞİÖŞÜ çğıöşü.", encoding="utf-8")
    info = validate_input_file(p)
    assert "ÇĞİÖŞÜ" in str(info["text"])


def test_txt_utf8_bom(tmp_path: Path) -> None:
    p = tmp_path / "bom.txt"
    p.write_bytes(b"\xef\xbb\xbfMerhaba")
    info = validate_input_file(p)
    assert info["encoding"] == "utf-8-sig"
    assert str(info["text"]).startswith("Merhaba")


def test_txt_empty_raises(tmp_path: Path) -> None:
    p = tmp_path / "empty.txt"
    p.write_text("   \n\n  ", encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        validate_input_file(p)
    assert exc.value.error_key in ("empty_file",)


def test_unsupported_extension(tmp_path: Path) -> None:
    p = tmp_path / "x.pdf"
    p.write_bytes(b"%PDF")
    with pytest.raises(ValidationError) as exc:
        validate_input_file(p)
    assert exc.value.error_key == "unsupported_format"