# ============================================================
# Lexora — Çeviri Motoru (Argos Translate sarmalayıcı)
# ============================================================
# Argos Translate'i güvenli ve iptal edilebilir şekilde sarar.
# - Dil çifti başına çevirici önbelleğe alınır (her seferinde yükleme yok).
# - Metin cümlelere/parçalara bölünür; her parça arasında iptal kontrolü.
# - Hata durumunda orijinal metin korunur, kullanıcıya rapor edilir.
# ============================================================

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import Callable

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


# ============================================================
# 1) HATA TİPİ
# ============================================================

class TranslationError(Exception):
    def __init__(self, error_key: str, detail: str = "") -> None:
        super().__init__(detail or error_key)
        self.error_key = error_key
        self.detail = detail


# ============================================================
# 2) İPTAL NESNESİ
# ============================================================

class CancelToken:
    """Thread-safe iptal işareti. Worker ve UI arasında paylaşılır."""
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def reset(self) -> None:
        self._event.clear()


# ============================================================
# 3) ÇEVİRİCİ ÖNBELLEĞİ
# ============================================================

# (from_code, to_code) -> ITranslation nesnesi
_translation_cache: dict[tuple[str, str], object] = {}
_cache_lock = threading.Lock()


def _get_translation(from_code: str, to_code: str):
    """
    Verilen dil çifti için Argos ITranslation nesnesini döner.
    Önbellekte varsa yeniden yüklemez.
    Yoksa TranslationError('model_missing') veya ('no_translation_path').
    """
    key = (from_code, to_code)
    with _cache_lock:
        if key in _translation_cache:
            return _translation_cache[key]

    try:
        import argostranslate.translate as argos_translate
        langs = argos_translate.get_installed_languages()
    except Exception as exc:
        raise TranslationError("model_missing", str(exc)) from exc

    from_lang = next((l for l in langs if l.code == from_code), None)
    to_lang = next((l for l in langs if l.code == to_code), None)

    if from_lang is None or to_lang is None:
        raise TranslationError(
            "model_missing",
            f"Yüklü dil bulunamadı: {from_code} veya {to_code}",
        )

    try:
        translation = from_lang.get_translation(to_lang)
    except Exception as exc:
        raise TranslationError("no_translation_path", str(exc)) from exc

    if translation is None:
        raise TranslationError(
            "no_translation_path",
            f"{from_code} -> {to_code} için çeviri yolu yok",
        )

    with _cache_lock:
        _translation_cache[key] = translation
    logger.info("Çevirici önbelleğe alındı: %s -> %s", from_code, to_code)
    return translation


def clear_translation_cache() -> None:
    """Dil paketi değiştiğinde önbelleği temizler."""
    with _cache_lock:
        _translation_cache.clear()
    logger.info("Çeviri önbelleği temizlendi.")


# ============================================================
# 4) METİN PARÇALAMA
# ============================================================

# Cümle sonu: nokta, ünlem, soru, iki nokta + boşluk + büyük harf.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])")


def split_text(text: str, max_chars: int = config.MAX_SEGMENT_CHARS) -> list[str]:
    """
    Metni çeviri için parçalara böler.
    1. Önce cümlelere böl.
    2. Cümle max_chars'ı aşıyorsa zorla böl.
    3. Boş parçaları at.
    """
    if not text.strip():
        return []

    sentences = _SENTENCE_SPLIT_RE.split(text)
    result: list[str] = []

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(sent) <= max_chars:
            result.append(sent)
        else:
            # Uzun cümleyi kelime sınırından böl.
            words = sent.split()
            buf = ""
            for w in words:
                if len(buf) + len(w) + 1 > max_chars and buf:
                    result.append(buf.strip())
                    buf = w
                else:
                    buf = f"{buf} {w}".strip()
            if buf:
                result.append(buf.strip())

    return result


# ============================================================
# 5) ANA ÇEVİRİ FONKSİYONU
# ============================================================

@dataclass
class TranslationResult:
    """Çeviri sonucu."""
    translated_text: str
    total_segments: int
    failed_segments: int
    cancelled: bool


def translate_text(
    text: str,
    from_code: str,
    to_code: str,
    cancel_token: CancelToken | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> TranslationResult:
    """
    Metni çevirir. Her parça arasında iptal kontrolü yapılır.
    progress_callback(mevcut, toplam) her parça sonrası çağrılır.

    Hata durumunda o parça için orijinal metin korunur (boş bırakılmaz).
    """
    segments = split_text(text)
    if not segments:
        return TranslationResult("", 0, 0, False)

    try:
        translation = _get_translation(from_code, to_code)
    except TranslationError:
        raise

    translated_parts: list[str] = []
    failed = 0
    total = len(segments)

    for idx, seg in enumerate(segments):
        if cancel_token is not None and cancel_token.is_cancelled():
            logger.info("Çeviri kullanıcı tarafından iptal edildi. (%d/%d)", idx, total)
            return TranslationResult(
                " ".join(translated_parts), total, failed, cancelled=True
            )

        try:
            translated = translation.translate(seg)
            if translated is None or not translated.strip():
                # Boş çeviri geldiyse orijinali koru.
                translated = seg
                failed += 1
                logger.warning("Boş çeviri döndü, orijinal korundu (parça %d).", idx)
        except Exception as exc:
            translated = seg
            failed += 1
            logger.warning("Parça çevrilemedi (%d): %s", idx, exc)

        translated_parts.append(translated)

        if progress_callback is not None:
            progress_callback(idx + 1, total)

    result_text = " ".join(translated_parts)
    logger.info(
        "Çeviri tamamlandı: %d parça, %d başarısız, iptal=%s",
        total, failed, False,
    )
    return TranslationResult(result_text, total, failed, cancelled=False)