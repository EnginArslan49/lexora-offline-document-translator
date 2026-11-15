# ============================================================
# Lexora — TXT İşleyici
# ============================================================
# TXT dosyalarını okur, çevirir, yeni TXT olarak yazar.
# Satır sonları ve boş satır yapısı korunur.
# Kaynak dosya ASLA değiştirilmez.
# ============================================================

from __future__ import annotations

from pathlib import Path
from typing import Callable

from core.translator import CancelToken, translate_text
from services.file_manager import atomic_output
from services.logging_service import get_logger

logger = get_logger(__name__)


class TxtProcessingError(Exception):
    def __init__(self, error_key: str, detail: str = "") -> None:
        super().__init__(detail or error_key)
        self.error_key = error_key
        self.detail = detail


def process_txt(
    source_path: Path,
    output_path: Path,
    encoding: str,
    from_code: str,
    to_code: str,
    cancel_token: CancelToken | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    """
    TXT dosyasını çevirir ve output_path'e yazar.

    Akış:
    1. Kaynak dosyayı belirtilen encoding ile oku.
    2. Satırlara böl; boş satırları koru.
    3. Dolu satırları çeviri motoruna gönder.
    4. Sonucu aynı satır yapısıyla birleştir.
    5. Atomik olarak output_path'e yaz.
    """
    try:
        text = source_path.read_text(encoding=encoding)
    except (OSError, UnicodeDecodeError) as exc:
        raise TxtProcessingError("file_unreadable", str(exc)) from exc

    # Satırları ayır; newline karakterini korumak için splitlines kullanmıyoruz.
    lines = text.split("\n")
    # Çevrilecek dolu satırları topla.
    translatable: list[tuple[int, str]] = [
        (i, line) for i, line in enumerate(lines) if line.strip()
    ]

    if not translatable:
        raise TxtProcessingError("empty_file")

    # Çeviri için metni birleştir; sonra satır satır ayıracağız.
    # Bunun yerine her dolu satırı ayrı ayrı çevirmek daha güvenli
    # (satır sonları korunsun).
    translated_lines = list(lines)  # kopya
    total = len(translatable)

    for count, (idx, line) in enumerate(translatable, start=1):
        if cancel_token is not None and cancel_token.is_cancelled():
            logger.info("TXT çevirisi iptal edildi.")
            raise TxtProcessingError("translation_cancelled")

        result = translate_text(
            line, from_code, to_code,
            cancel_token=cancel_token,
        )
        if result.cancelled:
            raise TxtProcessingError("translation_cancelled")

        translated_lines[idx] = result.translated_text
        if progress_callback is not None:
            progress_callback(count, total)

    final_text = "\n".join(translated_lines)

    # Atomik yazma.
    try:
        with atomic_output(output_path) as tmp:
            tmp.write_text(final_text, encoding="utf-8", newline="")
    except OSError as exc:
        raise TxtProcessingError("output_write_failed", str(exc)) from exc

    logger.info("TXT çevirisi tamamlandı: %s", output_path.name)