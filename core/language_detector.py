# ============================================================
# Lexora — Dil Algılama Servisi
# ============================================================
# Lingua kütüphanesi ile metnin dilini tespit eder.
# Yalnızca desteklenen dilleri yükler (ilk yüklemede hız için).
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import config
from services.logging_service import get_logger

logger = get_logger(__name__)

# Lingua'nın desteklediği diller — config'teki kodlarla örtüşen alt küme.
# (Lingua daha fazlasını destekler ama biz yalnızca çeviri yapabildiğimiz
# diller için algılama yapıyoruz.)
_SUPPORTED_LINGUA_CODES: tuple[str, ...] = tuple(config.LANGUAGE_DISPLAY_NAMES.keys())

# Güven eşikleri.
CONFIDENCE_HIGH: float = 0.85
CONFIDENCE_MEDIUM: float = 0.60


@dataclass
class DetectionResult:
    """Dil algılama sonucu."""
    code: str            # ISO 639-1
    name: str            # Türkçe görünen ad
    confidence: float    # 0.0 - 1.0
    is_reliable: bool    # CONFIDENCE_MEDIUM üstü mü?


@lru_cache(maxsize=1)
def _build_detector():
    """Lingua detector'ı tek seferlik inşa eder (lru_cache)."""
    from lingua import IsoCode639_1, LanguageDetectorBuilder

    # Lingua 2.x'te ISO 639-1 kodlarıyla detector inşa etmenin doğru yolu:
    #   LanguageDetectorBuilder.from_iso_codes_639_1(IsoCode639_1.EN, ...)
    # IsoCode639_1 enum'ı, Lingua'nın desteklediği dillerin ISO kodlarını içerir.
    # Desteklenmeyen kodlar (az, sq, ur, ga gibi) enum'da yoktur; atlanır.
    iso_codes: list = []
    skipped: list[str] = []

    for code in _SUPPORTED_LINGUA_CODES:
        # Enum üyesini isimle ara: "EN", "TR", "DE" gibi büyük harf.
        enum_name = code.upper()
        member = getattr(IsoCode639_1, enum_name, None)
        if member is None:
            skipped.append(code)
            continue
        iso_codes.append(member)

    if not iso_codes:
        raise RuntimeError(
            f"Lingua için geçerli dil listesi boş. "
            f"Desteklenen kod yok. Denenen: {_SUPPORTED_LINGUA_CODES}"
        )

    # Lingua en az 2 dil ister (single-language mode hariç).
    if len(iso_codes) < 2:
        raise RuntimeError(
            f"Lingua en az 2 dil gerektirir, {len(iso_codes)} bulundu."
        )

    detector = (
        LanguageDetectorBuilder
        .from_iso_codes_639_1(*iso_codes)
        .with_preloaded_language_models()
        .build()
    )
    logger.info(
        "Lingua detector hazır (%d dil yüklendi, %d atlandı: %s).",
        len(iso_codes),
        len(skipped),
        ",".join(skipped) if skipped else "-",
    )
    return detector


def detect_language(text: str, sample_size: int = 2000) -> DetectionResult | None:
    """
    Metnin dilini tespit eder.
    Çok uzun metinlerde ilk `sample_size` karakteri örnek alır (hız).
    Boş/kısa metinde None döner.
    """
    cleaned = text.strip()
    if not cleaned or len(cleaned) < 3:
        return None

    sample = cleaned[:sample_size]
    try:
        detector = _build_detector()
        # Lingua: en olası dili ve tüm güven skorlarını döndürür.
        confidence_values = detector.compute_language_confidence_values(sample)
        if not confidence_values:
            return None
        best = confidence_values[0]
        code = best.language.iso_code_639_1.name.lower()
        confidence = float(best.value)

        result = DetectionResult(
            code=code,
            name=config.language_name(code),
            confidence=confidence,
            is_reliable=confidence >= CONFIDENCE_MEDIUM,
        )
        logger.info(
            "Dil algılandı: %s (%.2f) — güvenilir: %s",
            result.code, result.confidence, result.is_reliable,
        )
        return result
    except Exception as exc:
        logger.warning("Dil algılama başarısız: %s", exc)
        return None