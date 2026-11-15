# ============================================================
# Lexora — Logging Servisi
# ============================================================
# Uygulamanın tek merkezi loglama noktası.
# Tüm modüller logger'ı buradan alır:
#
#     from services.logging_service import get_logger
#     logger = get_logger(__name__)
#     logger.info("Dosya analizi tamamlandı.")
#
# Tasarım kararları:
# - Normal işlemler  -> lexora.log   (INFO seviyesi)
# - Hatalar          -> errors.log   (ERROR seviyesi ve üzeri)
# - Rotasyon         -> config.py'deki LOG_MAX_BYTES / LOG_BACKUP_COUNT
# - Yazma izni yoksa -> %LOCALAPPDATA%\Lexora\logs dizinine düşülür
#
# Hassas veri koruması:
# Loglanmaması gereken alanları (belge içeriği, çeviri metni vb.)
# yanlışlıkla loglamayı önlemek için bir Filtre kullanılır.
# ============================================================

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Final

import config


# ============================================================
# 1) HASSAS VERİ FİLTRESİ
# ============================================================

# Loglanması yasak anahtar kelimeler. Bir log kaydının mesajında
# bu kelimeler geçiyorsa ve mesaj uzunluğu şüpheli ise (muhtemelen
# bir belge parçası sızmışsa) o kayıt engellenir.
#
# NOT: Bu bir "savunma derinliği" katmanıdır. Asıl sorumluluk,
# geliştiricinin belge içeriğini loglamamasıdır. Ancak filtre,
# yanlışlıkla yapılan sızıntıları da yakalar.
_SENSITIVE_KEYWORDS: Final[tuple[str, ...]] = (
    "document_content",
    "translated_text",
    "source_text",
    "raw_content",
    "paragraph_content",
)

# Bu uzunluğun üzerindeki mesajlar "muhtemelen belge içeriği" sayılır.
# Normal log mesajları nadiren bu kadar uzundur.
_MAX_SAFE_MESSAGE_LENGTH: Final[int] = 500


class SensitiveDataFilter(logging.Filter):
    """
    Yanlışlıkla yapılmış hassas veri loglarını engeller.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:
            # Mesaj formatlanamıyorsa güvenli tarafta kalıp geçir.
            return True

        # Anahtar kelime kontrolü (küçük harfle karşılaştırma).
        lowered = message.lower()
        for keyword in _SENSITIVE_KEYWORDS:
            if keyword in lowered:
                # Kaydı engelle — ancak sistem logu bunu bilsin.
                # (Bu satır, sızıntının filtrelendiğini gösterir ama
                # sızan içeriği yazmaz.)
                sys.stderr.write(
                    "[Lexora] Hassas veri filtresi bir log kaydını engelledi.\n"
                )
                return False

        # Aşırı uzun mesajlar da şüphelidir.
        if len(message) > _MAX_SAFE_MESSAGE_LENGTH:
            sys.stderr.write(
                "[Lexora] Çok uzun bir log kaydı hassas veri filtresi tarafından engellendi.\n"
            )
            return False

        return True


# ============================================================
# 2) LOG DİZİNİNİ BELİRLEME
# ============================================================

def _resolve_log_dir() -> Path:
    """
    Log dizinini belirler:
    Öncelik sırası:
      - Paketlenmiş (EXE) modda: önce kurulum dizini (logs/),
        yazılamazsa %LOCALAPPDATA%\\Lexora\\logs.
      - Geliştirme modunda (kaynak koddan): önce %LOCALAPPDATA%\\Lexora\\logs,
        yazılamazsa kurulum dizini (logs/).

    Bu sıralama, geliştirme sırasında proje kök dizininde gereksiz 'logs/'
    klasörü oluşmasını engeller. Dağıtımda ise brief'e uygun olarak
    önce kurulum dizini denenir.

    Her iki durumda da en az bir yazılabilir dizin döner. Hiçbiri
    yazılamazsa geçici bir yedek yol kullanılır ve stderr'e uyarı yazılır.
    """
    if getattr(sys, "frozen", False):
        # Paketlenmiş uygulama: önce kurulum dizini.
        candidates: tuple[Path, ...] = (
            config.LOG_DIR_PRIMARY,
            config.LOG_DIR_FALLBACK,
        )
    else:
        # Geliştirme modu: önce kullanıcı veri dizini.
        candidates = (
            config.LOG_DIR_FALLBACK,
            config.LOG_DIR_PRIMARY,
        )

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            # Gerçekten yazılabildiğini test edelim.
            probe = candidate / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except (OSError, PermissionError):
            continue

    # Hiçbir aday yazılamıyorsa geçici dizine düş.
    temp_fallback = Path.home() / ".lexora_logs"
    try:
        temp_fallback.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Son çare: geçerli çalışma dizinini kullan.
        temp_fallback = Path.cwd()

    sys.stderr.write(
        f"[Lexora] Uyarı: Standart log dizinleri yazılamadı. "
        f"Geçici konum kullanılıyor: {temp_fallback}\n"
    )
    return temp_fallback


# ============================================================
# 3) LOGGER OLUŞTURMA
# ============================================================

# Logger'ın tüm uygulamada tek örnek olmasını sağlamak için
# modül seviyesinde oluşturuyoruz. get_logger() bu tek örneği
# tüm modüllere dağıtır.
_ROOT_LOGGER_NAME: Final[str] = "lexora"

# Modül import edildiğinde bir kez kurulum yapılır.
_configured: bool = False


def _configure_root_logger() -> None:
    """
    Kök logger'ı bir kez yapılandırır. Birden fazla çağrıda
    tekrar handler eklemez.
    """
    global _configured
    if _configured:
        return

    log_dir = _resolve_log_dir()
    main_log_path = log_dir / config.LOG_FILE_NAME
    error_log_path = log_dir / config.ERROR_LOG_FILE_NAME

    root = logging.getLogger(_ROOT_LOGGER_NAME)
    root.setLevel(logging.DEBUG)
    # Üst logger'a (root) taşmayı engelle.
    root.propagate = False

    # --- Handler 1: Tüm loglar (DEBUG ve üzeri) -> lexora.log ---
    main_handler = logging.handlers.RotatingFileHandler(
        filename=str(main_log_path),
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(
        logging.Formatter(fmt=config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)
    )
    main_handler.addFilter(SensitiveDataFilter())
    root.addHandler(main_handler)

    # --- Handler 2: Yalnızca hatalar -> errors.log ---
    error_handler = logging.handlers.RotatingFileHandler(
        filename=str(error_log_path),
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter(fmt=config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)
    )
    error_handler.addFilter(SensitiveDataFilter())
    root.addHandler(error_handler)

    # --- Handler 3: Geliştirme sırasında konsola da yaz (opsiyonel) ---
    # Paketlenmiş uygulamada konsol penceresi yoktur; bu yüzden
    # yalnızca donanımda stderr varsa eklenir.
    if sys.stderr is not None and getattr(sys, "frozen", False) is False:
        console_handler = logging.StreamHandler(stream=sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter(
                fmt="[%(levelname)s] %(name)s: %(message)s",
            )
        )
        console_handler.addFilter(SensitiveDataFilter())
        root.addHandler(console_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Adlandırılmış bir logger döndürür.

    Parametre:
        name: Modülün __name__ değeri (örn. 'services.file_manager').

    Kullanım:
        from services.logging_service import get_logger
        logger = get_logger(__name__)
        logger.info("Dosya analiz edildi.")

    Dönen logger, 'lexora' kök logger'ının bir alt logger'ıdır.
    Böylece tüm handler'lar ve filtreler otomatik uygulanır.
    """
    _configure_root_logger()

    # Modül adı 'services.file_manager' ise
    # logger adı 'lexora.services.file_manager' olur.
    if name.startswith(_ROOT_LOGGER_NAME + "."):
        full_name = name
    else:
        full_name = f"{_ROOT_LOGGER_NAME}.{name}"

    return logging.getLogger(full_name)


# ============================================================
# 4) KULLANICI DOSTU HATA MESAJLARI
# ============================================================
# Arayüzde gösterilecek Türkçe hata metinleri.
# Exception mesajlarını doğrudan kullanıcıya göstermek yerine,
# bu sözlükten uygun Türkçe mesajı seçeriz.

USER_ERROR_MESSAGES: Final[dict[str, str]] = {
    "file_not_found":       "Seçilen dosya bulunamadı. Lütfen dosyanın yerinde olduğundan emin olun.",
    "file_unreadable":      "Dosya okunamadı. Dosya başka bir program tarafından kullanılıyor veya bozuk olabilir.",
    "file_too_large":       f"Dosya çok büyük. En fazla {config.MAX_INPUT_FILE_SIZE_BYTES // (1024 * 1024)} MB boyutundaki dosyalar destekleniyor.",
    "unsupported_format":   "Desteklenmeyen dosya formatı. Yalnızca .txt ve .docx dosyaları destekleniyor.",
    "format_mismatch":      "Dosya uzantısı ile gerçek içerik uyuşmuyor. Dosya bozuk veya farklı bir formatta olabilir.",
    "invalid_docx":         "Word belgesi geçersiz veya bozuk. Belgeyi Microsoft Word ile açıp yeniden kaydetmeyi deneyin.",
    "encrypted_docx":       "Şifreli Word belgeleri desteklenmiyor. Lütfen belgenin şifresini kaldırıp tekrar deneyin.",
    "zip_bomb":             "Dosya güvenlik kontrolünden geçemedi (şüpheli sıkıştırma oranı).",
    "empty_file":           "Dosya boş veya çevrilecek metin içermiyor.",
    "language_detection":   "Dosyanın dili güvenilir şekilde algılanamadı. Lütfen kaynak dili manuel seçin.",
    "model_missing":        "Gerekli dil paketi yüklü değil. Ayarlar bölümünden dil paketini indirebilirsiniz.",
    "no_translation_path":  "Seçilen dil çifti için çeviri yolu bulunamadı. Farklı bir hedef dil deneyin.",
    "translation_failed":   "Çeviri sırasında bir hata oluştu. Lütfen tekrar deneyin.",
    "translation_cancelled":"Çeviri işlemi iptal edildi.",
    "output_write_failed":  "Çıktı dosyası kaydedilemedi. Hedef klasörün yazma iznini kontrol edin.",
    "output_exists":        "Aynı isimde bir çıktı dosyası zaten var. Üzerine yazmak isteyip istemediğiniz sorulacak.",
    "permission_denied":    "Bu klasöre yazma izniniz yok. Lütfen farklı bir çıktı klasörü seçin.",
    "invalid_path":         "Geçersiz dosya yolu.",
    "source_file_modified": "Kaynak dosyaya müdahale edilemez. Bu bir güvenlik ihlali girişimidir.",
    "unexpected":           "Beklenmeyen bir hata oluştu. Ayrıntılar log dosyasına kaydedildi.",
}


def user_message(key: str, fallback: str | None = None) -> str:
    """
    Kullanıcıya gösterilecek Türkçe hata mesajını döndürür.

    Parametre:
        key: USER_ERROR_MESSAGES sözlüğündeki anahtar.
        fallback: Anahtar bulunamazsa dönecek yedek mesaj.
    """
    return USER_ERROR_MESSAGES.get(key, fallback or USER_ERROR_MESSAGES["unexpected"])