# ============================================================
# Lexora — Doğrulama Servisi
# ============================================================
# Dosya formatı, boyutu ve güvenliği ile ilgili tüm doğrulamalar.
# Uzantıya güvenmeyiz; dosyanın gerçek içeriğini inceleriz.
#
# Sorumluluklar:
# - Uzantı kontrolü (.txt, .docx)
# - Boyut limitleri
# - TXT: kodlama (UTF-8, BOM, UTF-16, CP1254) tespiti
# - DOCX: ZIP paketi geçerliliği + ZIP bomb koruması
# - DOCX: şifreli belge tespiti
# - DOCX: OOXML içerik türü doğrulaması
# - Path traversal koruması
# ============================================================

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Final

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


# ============================================================
# 1) HATA TİPLERİ
# ============================================================

class ValidationError(Exception):
    """Doğrulama hatası — kullanıcıya Türkçe mesaj anahtarı taşır."""
    def __init__(self, error_key: str, detail: str = "") -> None:
        super().__init__(detail or error_key)
        self.error_key = error_key
        self.detail = detail


# ============================================================
# 2) DESTEKLENEN KODLAMALAR (TXT için)
# ============================================================
# Sırayla denenir; ilk başarılı olan kullanılır.
_TXT_ENCODINGS: Final[tuple[str, ...]] = (
    "utf-8-sig",   # UTF-8 BOM'lu
    "utf-8",       # BOM'suz UTF-8
    "utf-16",      # UTF-16 LE/BE
    "cp1254",      # Türkçe Windows
    "latin-1",     # Son çare (her baytı kabul eder)
)


# ============================================================
# 3) TEMEL KONTROLLER
# ============================================================

def validate_extension(path: Path) -> str:
    """
    Uzantıyı kontrol eder, küçük harfli uzantıyı döner ('.txt' gibi).
    Hata durumunda ValidationError('unsupported_format') fırlatır.
    """
    suffix = path.suffix.lower()
    if suffix not in config.SUPPORTED_EXTENSIONS:
        raise ValidationError("unsupported_format", f"Uzantı: {suffix or '(yok)'}")
    return suffix


def validate_file_size(path: Path) -> int:
    """
    Dosyanın boyutunu kontrol eder, boyutu bayt olarak döner.
    Aşım durumunda ValidationError('file_too_large').
    """
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValidationError("file_unreadable", str(exc)) from exc

    if size == 0:
        raise ValidationError("empty_file")
    if size > config.MAX_INPUT_FILE_SIZE_BYTES:
        raise ValidationError(
            "file_too_large",
            f"{size} bayt > {config.MAX_INPUT_FILE_SIZE_BYTES} bayt",
        )
    return size


def is_safe_path(candidate: Path) -> bool:
    """
    Path traversal koruması: '..' içeren ve çözümlenince kök dışına çıkan
    yolları reddeder. Normalize edilmiş yolu karşılaştırır.
    """
    try:
        # resolve() sembolik bağları ve '..' ifadelerini çözer.
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError):
        return False
    # Windows'ta sürücü harfi köküne bakılır (örn. C:\).
    return resolved.is_absolute()


# ============================================================
# 4) TXT DOĞRULAMA
# ============================================================

def validate_txt(path: Path) -> tuple[str, str]:
    """
    TXT dosyasını doğrular ve kodlamasını tespit eder.
    Döner: (encoding_adı, çözülmüş_metin)
    Hiçbir kodlama ile çözülemezse ValidationError('format_mismatch').
    """
    raw = path.read_bytes()

    # İçerikte null bayt varsa bu büyük olasılıkla binary bir dosyadır;
    # uzantı .txt olsa bile reddederiz.
    if b"\x00" in raw[:1024] and not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        # UTF-16 BOM'lu değilse ve null içeriyorsa reddet.
        if not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            raise ValidationError("format_mismatch", "TXT içinde binary veri var")

    for enc in _TXT_ENCODINGS:
        try:
            text = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        # Çözüldüyse ve boş değilse kabul.
        if text.strip():
            logger.info("TXT kodlaması: %s", enc)
            return enc, text

    raise ValidationError("empty_file", "TXT içeriği çözülemedi veya boş")


# ============================================================
# 5) DOCX DOĞRULAMA (ZIP + OOXML)
# ============================================================

def _check_zip_bomb(zf: zipfile.ZipFile) -> None:
    """
    ZIP bomb koruması:
    - Entry sayısı sınırı
    - Açılmış toplam boyut sınırı
    - Sıkıştırma oranı sınırı
    """
    infos = zf.infolist()
    if len(infos) > config.MAX_ZIP_ENTRY_COUNT:
        raise ValidationError(
            "zip_bomb",
            f"Entry sayısı: {len(infos)} > {config.MAX_ZIP_ENTRY_COUNT}",
        )

    total_uncompressed = 0
    for info in infos:
        total_uncompressed += info.file_size
        # Anormal sıkıştırma oranı kontrolü (küçük dosyalarda gürültü olabilir).
        if info.file_size > 1024 * 1024:  # 1 MB üstü entry'lerde kontrol et
            ratio = info.file_size / max(info.compress_size, 1)
            if ratio > config.MAX_ZIP_COMPRESSION_RATIO:
                raise ValidationError(
                    "zip_bomb",
                    f"Aşırı sıkıştırma oranı: {ratio:.0f}:1 ({info.filename})",
                )

    if total_uncompressed > config.MAX_ZIP_UNCOMPRESSED_SIZE_BYTES:
        raise ValidationError(
            "zip_bomb",
            f"Açılmış boyut: {total_uncompressed} > "
            f"{config.MAX_ZIP_UNCOMPRESSED_SIZE_BYTES}",
        )


def validate_docx(path: Path) -> None:
    """
    DOCX dosyasını doğrular:
    - Geçerli bir ZIP mi?
    - ZIP bomb riski var mı?
    - [Content_Types].xml ve word/document.xml var mı?
    - Şifreli mi? (EncryptedPackage = OLE compound file)
    """
    # İlk kontrol: dosya OLE compound file (şifreli Office belgesi) mı?
    with open(path, "rb") as f:
        header = f.read(8)
    # OLE magic: D0 CF 11 E0 A1 B1 1A E1 (şifreli Office)
    if header == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
        raise ValidationError("encrypted_docx")

    # ZIP doğrulaması.
    if not zipfile.is_zipfile(path):
        raise ValidationError("invalid_docx", "Dosya ZIP değil")

    try:
        with zipfile.ZipFile(path, "r") as zf:
            _check_zip_bomb(zf)
            names = set(zf.namelist())
            # OOXML için zorunlu dosyalar.
            if "[Content_Types].xml" not in names:
                raise ValidationError("invalid_docx", "[Content_Types].xml yok")
            if "word/document.xml" not in names:
                raise ValidationError("invalid_docx", "word/document.xml yok")
    except zipfile.BadZipFile as exc:
        raise ValidationError("invalid_docx", str(exc)) from exc

    logger.info("DOCX doğrulaması geçti: %s", path.name)


# ============================================================
# 6) HASH DOĞRULAMA (Kaynak Dosya Değişmezliği)
# ============================================================

def compute_file_hash(path: Path) -> str:
    """
    Dosyanın SHA-256 hash'ini hesaplar. Kaynak dosyanın değişmediğini
    doğrulamak için kullanılır.
    """
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file_unchanged(path: Path, expected_hash: str) -> bool:
    """Dosya hash'i beklenen değerle eşleşiyor mu?"""
    try:
        return compute_file_hash(path) == expected_hash
    except OSError:
        return False


# ============================================================
# 7) TOPLU DOĞRULAMA
# ============================================================

def validate_input_file(path: Path) -> dict[str, object]:
    """
    Bir dosyayı tüm katmanlardan geçirir. Başarılıysa bilgi sözlüğü döner:
      {
        'path': Path,
        'format': '.txt' | '.docx',
        'size': int,
        'hash': str,
        'encoding': str  (yalnızca TXT için),
        'text': str      (yalnızca TXT için)
      }
    Hata durumunda ValidationError fırlatır.
    """
    if not path.exists():
        raise ValidationError("file_not_found")
    if not path.is_file():
        raise ValidationError("invalid_path")
    if not is_safe_path(path):
        raise ValidationError("invalid_path")

    suffix = validate_extension(path)
    size = validate_file_size(path)
    file_hash = compute_file_hash(path)

    info: dict[str, object] = {
        "path": path,
        "format": suffix,
        "size": size,
        "hash": file_hash,
    }

    if suffix == ".txt":
        encoding, text = validate_txt(path)
        info["encoding"] = encoding
        info["text"] = text
    elif suffix == ".docx":
        validate_docx(path)

    logger.info("Doğrulama başarılı: %s (%d bayt)", path.name, size)
    return info