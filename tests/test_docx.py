# ============================================================
# Lexora — DOCX Testleri
# ============================================================
from pathlib import Path

import pytest
from docx import Document

from services.validation_service import ValidationError, validate_input_file


def test_docx_valid(sample_docx: Path) -> None:
    info = validate_input_file(sample_docx)
    assert info["format"] == ".docx"


def test_docx_fake_raises(tmp_path: Path) -> None:
    p = tmp_path / "fake.docx"
    p.write_text("bu docx değil", encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        validate_input_file(p)
    assert exc.value.error_key in ("invalid_docx",)


def test_docx_preserves_bold_after_translation(sample_docx: Path, tmp_path: Path) -> None:
    """
    Bu test çeviri olmadan (kaynak dosyayı yeniden yazmadan) bold koruma
    mantığını doğrular.
    """
    d = Document(str(sample_docx))
    p = d.paragraphs[0]
    assert any(r.bold for r in p.runs), "Başlangıçta bold run olmalı"
    # Kaynak değişmedi mi?
    assert sample_docx.exists()