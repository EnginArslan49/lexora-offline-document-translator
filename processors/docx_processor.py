# ============================================================
# Lexora — DOCX İşleyici
# ============================================================
# Word belgesini çevirirken biçimlendirmeyi korur.
#
# KRİTİK KURAL: paragraph.text = ... ASLA kullanılmaz.
# Bu setter tüm <w:r> düğümlerini silip tek run oluşturur;
# böylece font, kalınlık, renk, italik vb. tüm <w:rPr> bilgisi kaybolur.
#
# Doğru yaklaşım:
# - Paragrafın run'larını birleştir, çevir, sonra run yapısını
#   KORUYARAK yeniden dağıt.
# - Her yeni run, orijinal run'ın rPr'sinin kopyasını taşır.
# - Tablo, üstbilgi, altbilgi de aynı mantıkla işlenir.
# ============================================================

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Callable

from docx import Document
from docx.oxml.ns import qn

from core.translator import CancelToken, translate_text
from services.file_manager import atomic_output
from services.logging_service import get_logger

logger = get_logger(__name__)


class DocxProcessingError(Exception):
    def __init__(self, error_key: str, detail: str = "") -> None:
        super().__init__(detail or error_key)
        self.error_key = error_key
        self.detail = detail


# ============================================================
# 1) YARDIMCI: RUN'LARI BİRLEŞTİR
# ============================================================

def _get_paragraph_text(paragraph) -> str:
    """Paragraftaki tüm run'ların metnini birleştirir."""
    return "".join(run.text for run in paragraph.runs)


def _replace_paragraph_text_preserve_runs(paragraph, new_text: str) -> None:
    """
    Paragrafın metnini, run yapısını ve rPr'lerini KORUYARAK değiştirir.

    Algoritma:
    1. Eski metindeki her karakterin hangi run'a ait olduğunu haritala.
    2. Yeni metni, eski run sınırlarına denk gelen parçalara böl.
    3. Her run'ın <w:t> içeriğini yeni parçayla değiştir.
    4. Yeni metin daha uzunsa son run'a ekle.
    5. Yeni metin daha kısaysa fazla run'ları temizle.
    """
    runs = paragraph.runs
    if not runs:
        return

    old_text = _get_paragraph_text(paragraph)
    if old_text == new_text:
        return

    # Her karakterin run indeksini haritala.
    char_to_run: list[int] = []
    for i, run in enumerate(runs):
        char_to_run.extend([i] * len(run.text))

    # Yeni metni run sınırlarına göre parçala.
    # Eski metnin uzunluğuna göre run sınırlarını koru.
    new_len = len(new_text)
    old_len = len(old_text)

    # Yeni metin için run başına düşen karakter sayısını hesapla.
    # Basit yaklaşım: her run'ın eski uzunluğu oranında pay al.
    if old_len > 0:
        run_lengths = [len(r.text) for r in runs]
    else:
        run_lengths = [0] * len(runs)

    # Yeni metni run'lara dağıt.
    # Eğer yeni metin eskisinden kısaysa son run'lar boşaltılır.
    # Eğer uzunsa son run'a eklenir.
    result_parts: list[str] = []
    pos = 0
    total_allocated = 0

    for i, run_len in enumerate(run_lengths):
        if i == len(run_lengths) - 1:
            # Son run: kalan tüm metni al.
            result_parts.append(new_text[pos:])
        else:
            # Oransal pay: eski run uzunluğuna göre.
            if old_len > 0:
                alloc = round(new_len * run_len / old_len)
            else:
                alloc = 0
            alloc = min(alloc, new_len - pos)
            result_parts.append(new_text[pos:pos + alloc])
            pos += alloc

    # rPr'leri koruyarak run.text güncelle.
    for run, part in zip(runs, result_parts):
        run.text = part


# ============================================================
# 2) PARAGRAF İŞLEME
# ============================================================

# Çevrilmemesi gereken paragraflar: alan kodları, içerik denetimleri.
_SKIP_XPATH = (
    ".//w:fldChar",
    ".//w:instrText",
)

# URL, e-posta, kod gibi desenleri koru (basit maskeleme).
_PROTECT_PATTERNS = [
    (re.compile(r"https?://\S+"), "__URL__"),
    (re.compile(r"\S+@\S+\.\S+"), "__EMAIL__"),
]


def _should_skip_paragraph(paragraph) -> bool:
    """Alan kodu içeren paragrafları atla (çeviri bozar)."""
    for xpath in _SKIP_XPATH:
        if paragraph._p.xpath(xpath):
            return True
    return False


def _process_paragraph(paragraph, from_code: str, to_code: str,
                       cancel_token: CancelToken | None) -> bool:
    """
    Tek bir paragrafı çevirir. Başarılıysa True.
    Boş paragraflar atlanır.
    """
    text = _get_paragraph_text(paragraph)
    if not text.strip():
        return True

    if _should_skip_paragraph(paragraph):
        logger.debug("Alan kodu içeren paragraf atlandı.")
        return True

    if cancel_token is not None and cancel_token.is_cancelled():
        return False

    result = translate_text(text, from_code, to_code, cancel_token=cancel_token)
    if result.cancelled:
        return False

    if result.translated_text.strip():
        _replace_paragraph_text_preserve_runs(paragraph, result.translated_text)
    return True


# ============================================================
# 3) ANA İŞLEMCİ
# ============================================================

def process_docx(
    source_path: Path,
    output_path: Path,
    from_code: str,
    to_code: str,
    cancel_token: CancelToken | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    """
    DOCX dosyasını çevirir.
    - Gövde paragrafları
    - Tablolar (hücre paragrafları)
    - Üstbilgi / altbilgi
    işlenir. Görseller, köprüler ve diğer OOXML nesneleri korunur.
    """
    try:
        doc = Document(str(source_path))
    except Exception as exc:
        raise DocxProcessingError("invalid_docx", str(exc)) from exc

    # İşlenecek tüm paragrafları topla.
    all_paragraphs = []

    # Gövde paragrafları.
    all_paragraphs.extend(doc.paragraphs)

    # Tablolar.
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    # Üstbilgi / altbilgi.
    for section in doc.sections:
        if section.header:
            all_paragraphs.extend(section.header.paragraphs)
        if section.footer:
            all_paragraphs.extend(section.footer.paragraphs)

    total = len(all_paragraphs)
    processed = 0

    for para in all_paragraphs:
        if cancel_token is not None and cancel_token.is_cancelled():
            raise DocxProcessingError("translation_cancelled")

        ok = _process_paragraph(para, from_code, to_code, cancel_token)
        if not ok:
            raise DocxProcessingError("translation_cancelled")

        processed += 1
        if progress_callback is not None:
            progress_callback(processed, total)

    # Atomik yazma.
    try:
        with atomic_output(output_path) as tmp:
            doc.save(str(tmp))
    except OSError as exc:
        raise DocxProcessingError("output_write_failed", str(exc)) from exc

    logger.info("DOCX çevirisi tamamlandı: %s", output_path.name)