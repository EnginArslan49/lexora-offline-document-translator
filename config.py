# ============================================================
# Lexora — Yapılandırma Modülü
# ============================================================
# Bu modül, uygulamanın TÜM sabit değerlerini, dizin yollarını
# ve marka bilgilerini tek merkezde toplar.
#
# Kural: Projenin hiçbir yerinde sihirli sayı (magic number) veya
# sabit string doğrudan yazılmaz. Her şey buradan okunur.
#
# Kullanım:
#     import config
#     print(config.APP_NAME)
# ============================================================

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final


# ============================================================
# 1) UYGULAMA KİMLİĞİ
# ============================================================

APP_NAME: Final[str] = "Lexora"
APP_DISPLAY_NAME: Final[str] = "Lexora"
APP_VERSION: Final[str] = "1.0.1"
APP_DESCRIPTION_TR: Final[str] = "Belgelerinizi çevirin, biçimlendirmelerini koruyun."
APP_DESCRIPTION_EN: Final[str] = "Translate Documents. Preserve Formatting."
APP_ORGANIZATION: Final[str] = "Engin ARSLAN"
APP_DEVELOPER_NAME: Final[str] = "Engin ARSLAN"
APP_DEVELOPER_TITLE: Final[str] = "Software Developer"

# Hakkında sayfasında gösterilecek geliştirici tanıtım metni.
APP_DEVELOPER_BIO: Final[str] = (
    "Lexora, Engin ARSLAN tarafından geliştirilen ücretsiz ve çevrimdışı "
    "belge çeviri uygulamasıdır. Kullanıcıların belgelerini güvenli bir "
    "şekilde çevirebilmeleri ve orijinal biçimlendirmelerini koruyabilmeleri "
    "amacıyla geliştirilmiştir."
)

# Geliştirici desteği çağrısı.
APP_SUPPORT_MESSAGE: Final[str] = (
    "Bu uygulama tamamen ücretsizdir. Geliştiriciye destek olmak için "
    "sosyal medya hesaplarını takip edebilirsiniz."
)

# Sosyal medya bağlantıları — SADECE HTTPS kabul edilir.
SOCIAL_LINKS: Final[dict[str, str]] = {
    "GitHub":    "https://github.com/EnginArslan49?tab=repositories",
    "Instagram": "https://www.instagram.com/49engn04",
    "YouTube":   "https://youtube.com/@ramkafe",
    "LinkedIn":  "https://www.linkedin.com/in/engin-arslan-49e04/",
}


# ============================================================
# 2) DİZİN YOLLARI
# ============================================================
# Uygulama; PyInstaller ile paketlenmiş olabilir veya doğrudan
# kaynak koddan çalışıyor olabilir. Her iki durumu da ele alıyoruz.

def _is_frozen() -> bool:
    """Uygulama PyInstaller ile paketlenmiş mi?"""
    # PyInstaller, çalışma zamanında sys.frozen = True atar.
    return getattr(sys, "frozen", False)


if _is_frozen():
    # PyInstaller: geçici açma dizini (onefile modunda sys._MEIPASS)
    APP_BASE_DIR: Final[Path] = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # EXE'nin gerçek konumu — veri yazmak için kullanılır.
    APP_EXE_DIR: Final[Path] = Path(sys.executable).parent
else:
    # Kaynak koddan çalışıyoruz: config.py'nin bulunduğu dizin.
    APP_BASE_DIR: Final[Path] = Path(__file__).resolve().parent
    APP_EXE_DIR: Final[Path] = APP_BASE_DIR


# Kullanıcı verisi dizini — Windows'ta %LOCALAPPDATA%\Lexora
LOCAL_APPDATA: Final[Path] = Path(
    os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
)
APP_DATA_DIR: Final[Path] = LOCAL_APPDATA / APP_NAME

# Log dizini: önce kurulum (EXE) dizinindeki logs/ denenir; yazılamazsa
# %LOCALAPPDATA%\Lexora\logs kullanılır. Bu kontrol logging_service
# modülünde yapılır; burada sadece iki aday yolu tanımlıyoruz.
LOG_DIR_PRIMARY: Final[Path] = APP_EXE_DIR / "logs"
LOG_DIR_FALLBACK: Final[Path] = APP_DATA_DIR / "logs"

# Argos dil modellerinin indirileceği ve tutulacağı dizin.
ARGOS_MODEL_DIR: Final[Path] = APP_DATA_DIR / "models"

# JSON tabanlı kalıcılık dosyaları.
# Veritabanı kullanmıyoruz; ayarlar ve geçmiş JSON dosyalarında tutulur.
SETTINGS_FILE_PATH: Final[Path] = APP_DATA_DIR / "settings.json"
HISTORY_FILE_PATH: Final[Path] = APP_DATA_DIR / "history.json"

# Geçmiş kayıtlarının maksimum sayısı. Aşılırsa en eski kayıtlar budanır.
MAX_HISTORY_ENTRIES: Final[int] = 200

# Geçici çalışma dosyalarının tutulacağı dizin.
TEMP_DIR: Final[Path] = APP_DATA_DIR / "temp"

# Uygulama ikonları ve statik kaynaklar (paket içinde salt-okunur).
RESOURCES_DIR: Final[Path] = APP_BASE_DIR / "resources"
ICONS_DIR: Final[Path] = RESOURCES_DIR / "icons"
IMAGES_DIR: Final[Path] = RESOURCES_DIR / "images"
STYLES_DIR: Final[Path] = RESOURCES_DIR / "styles"

# Uygulama başlangıcında oluşturulması gereken yazılabilir dizinler.
REQUIRED_DIRS: Final[tuple[Path, ...]] = (
    APP_DATA_DIR,
    ARGOS_MODEL_DIR,
    TEMP_DIR,
)


# ============================================================
# 3) DOSYA GÜVENLİK LİMİTLERİ
# ============================================================
# Kullanıcı büyük veya kötü niyetli bir dosya seçebilir. Aşağıdaki
# limitler validation_service modülü tarafından uygulanır.

# Tek bir kaynak dosyanın izin verilen maksimum boyutu (50 MB).
MAX_INPUT_FILE_SIZE_BYTES: Final[int] = 50 * 1024 * 1024

# DOCX ZIP içeriği için: maksimum entry sayısı (ZIP bomb koruması).
MAX_ZIP_ENTRY_COUNT: Final[int] = 5_000

# DOCX ZIP içeriği için: açılmış toplam boyut üst sınırı (200 MB).
MAX_ZIP_UNCOMPRESSED_SIZE_BYTES: Final[int] = 200 * 1024 * 1024

# Sıkıştırma oranı üst sınırı — 100:1 üzeri şüpheli (ZIP bomb).
MAX_ZIP_COMPRESSION_RATIO: Final[float] = 100.0

# Tek bir çeviri parçasının maksimum karakter sayısı.
# Çok uzun parçalar Argos tarafından yavaş işlenir; bölerek ilerleriz.
MAX_SEGMENT_CHARS: Final[int] = 1_500

# Kaynak dosyadan okunabilecek maksimum toplam karakter sayısı.
MAX_TOTAL_CHARS: Final[int] = 5_000_000  # ~5 milyon karakter ≈ 5 MB metin


# ============================================================
# 4) DESTEKLENEN DOSYA FORMATLARI
# ============================================================
# V1.0 kapsamı: yalnızca TXT ve DOCX. Mimari ileride genişletilebilir.

SUPPORTED_EXTENSIONS: Final[frozenset[str]] = frozenset({".txt", ".docx"})

# Dosya uzantısı → insan tarafından okunabilir format adı.
FORMAT_DISPLAY_NAMES: Final[dict[str, str]] = {
    ".txt": "Metin Belgesi (TXT)",
    ".docx": "Word Belgesi (DOCX)",
}

# DOCX içinde OOXML paketini tanımlayan MIME tipi (İçerik Türü kontrolü için).
DOCX_MIME_TYPE: Final[str] = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


# ============================================================
# 5) ÇEVİRİ MOTORU (ARGOS)
# ============================================================
# Argos, çevrimdışı çeviri için kullanılır. Model yönetimi
# model_manager servisi üzerinden yapılır.

# Argos'un paket dizinini kullanıcı veri dizinine yönlendiriyoruz.
# PyInstaller onefile modunda sys._MEIPASS salt-okunur olduğu için
# Argos'un varsayılan davranışı çalışmaz. Bu ortam değişkenini
# app.py başlangıcında set edeceğiz.
ARGOS_PACKAGE_DIR_ENV: Final[str] = "ARGOS_PACKAGE_DIR"

# Argos'un indirme işlemi için kullandığı temel URL.
# (Argos kendi içinde bu adresi kullanır; biz sadece dokümantasyon amaçlı tutuyoruz.)
ARGOS_DOWNLOAD_INDEX_URL: Final[str] = "https://raw.githubusercontent.com/argosopentech/argospm-index/main/index.json"

# Çeviri sırasında parçalar arasında iptal kontrolü yapma sıklığı.
CANCEL_CHECK_INTERVAL: Final[int] = 1  # her parça sonrası kontrol

# Ara dil (pivot) varsayılanı — doğrudan model yoksa buradan geçilir.
PIVOT_LANGUAGE_CODE: Final[str] = "en"


# ============================================================
# 6) DİL KODLARI VE GÖRÜNÜM ADLARI
# ============================================================
# Argos dil kodları ISO 639-1 (iki harf) kullanır. Lingua de aynı
# kodları destekler. Arayüzde göstermek için Türkçe adlar.

LANGUAGE_DISPLAY_NAMES: Final[dict[str, str]] = {
    "ar": "Arapça",
    "az": "Azerbaycan Türkçesi",
    "bg": "Bulgarca",
    "ca": "Katalanca",
    "cs": "Çekçe",
    "da": "Danca",
    "de": "Almanca",
    "el": "Yunanca",
    "en": "İngilizce",
    "es": "İspanyolca",
    "et": "Estonca",
    "fa": "Farsça",
    "fi": "Fince",
    "fr": "Fransızca",
    "ga": "İrlandaca",
    "he": "İbranice",
    "hi": "Hintçe",
    "hu": "Macarca",
    "id": "Endonezce",
    "it": "İtalyanca",
    "ja": "Japonca",
    "ko": "Korece",
    "lt": "Litvanca",
    "lv": "Letonca",
    "ms": "Malayca",
    "nl": "Felemenkçe",
    "no": "Norveççe",
    "pl": "Lehçe",
    "pt": "Portekizce",
    "ro": "Romence",
    "ru": "Rusça",
    "sk": "Slovakça",
    "sl": "Slovence",
    "sq": "Arnavutça",
    "sv": "İsveççe",
    "th": "Tayca",
    "tr": "Türkçe",
    "uk": "Ukraynaca",
    "ur": "Urduca",
    "vi": "Vietnamca",
    "zh": "Çince",
}


def language_name(code: str) -> str:
    """
    ISO 639-1 dil kodunu Türkçe görünen ada çevirir.
    Bilinmeyen kod için kodun kendisini (büyük harfle) döner.
    """
    return LANGUAGE_DISPLAY_NAMES.get(code.lower(), code.upper())


# ============================================================
# 7) ARAYÜZ — TEMA VE MARKA RENKLERİ
# ============================================================
# Renkler tek merkezde tutulur; QSS dosyaları bu değerleri
# yer tutucu olarak kullanır. Tema değiştiğinde yalnızca bu
# sözlükler değişir.

THEME_LIGHT: Final[str] = "light"
THEME_DARK: Final[str] = "dark"
DEFAULT_THEME: Final[str] = THEME_DARK

# Lexora marka renkleri (her iki temada da geçerli vurgu renkleri).
BRAND_COLORS: Final[dict[str, str]] = {
    "primary_blue":    "#007AFF",   # macOS sistem mavisi
    "cyan":            "#32ADE6",   # camgöbeği vurgu
    "purple":          "#AF52DE",   # mor vurgu
    "success":         "#34C759",
    "warning":         "#FF9500",
    "danger":          "#FF3B30",
}

# Açık tema paleti (macOS Big Sur / Ventura esintili).
LIGHT_PALETTE: Final[dict[str, str]] = {
    "bg_window":       "#F5F5F7",   # ana pencere arka planı
    "bg_sidebar":      "#ECECEC",   # kenar çubuğu
    "bg_surface":      "#FFFFFF",   # kart / panel yüzeyi
    "bg_input":        "#FFFFFF",
    "text_primary":    "#1D1D1F",
    "text_secondary":  "#6E6E73",
    "text_disabled":   "#AEAEB2",
    "border":          "#D2D2D7",
    "shadow":          "rgba(0, 0, 0, 0.10)",
    "accent":          "#007AFF",
}

# Koyu tema paleti (macOS koyu mod esintili).
DARK_PALETTE: Final[dict[str, str]] = {
    "bg_window":       "#1E1E1E",
    "bg_sidebar":      "#252525",
    "bg_surface":      "#2C2C2E",
    "bg_input":        "#3A3A3C",
    "text_primary":    "#F2F2F7",
    "text_secondary":  "#AEAEB2",
    "text_disabled":   "#636366",
    "border":          "#3A3A3C",
    "shadow":          "rgba(0, 0, 0, 0.35)",
    "accent":          "#0A84FF",
}

# Varsayılan pencere boyutları.
WINDOW_DEFAULT_WIDTH: Final[int] = 1100
WINDOW_DEFAULT_HEIGHT: Final[int] = 720
WINDOW_MIN_WIDTH: Final[int] = 900
WINDOW_MIN_HEIGHT: Final[int] = 600

# Yuvarlatılmış köşe yarıçapı (px).
UI_CORNER_RADIUS: Final[int] = 12
UI_CORNER_RADIUS_SMALL: Final[int] = 8
UI_CORNER_RADIUS_LARGE: Final[int] = 16


# ============================================================
# 8) LOG YAPILANDIRMASI
# ============================================================

LOG_FILE_NAME: Final[str] = "lexora.log"
ERROR_LOG_FILE_NAME: Final[str] = "errors.log"
LOG_MAX_BYTES: Final[int] = 1 * 1024 * 1024   # 1 MB
LOG_BACKUP_COUNT: Final[int] = 3
LOG_FORMAT: Final[str] = "[%(asctime)s] %(levelname)s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


# ============================================================
# 9) AYAR ANAHTARLARI (SQLite'da saklanan kullanıcı ayarları)
# ============================================================

SETTING_THEME: Final[str] = "theme"
SETTING_LAST_TARGET_LANG: Final[str] = "last_target_lang"
SETTING_LAST_OUTPUT_DIR: Final[str] = "last_output_dir"
SETTING_WINDOW_GEOMETRY: Final[str] = "window_geometry"


# ============================================================
# 10) YARDIMCI FONKSİYONLAR
# ============================================================

def ensure_required_dirs() -> None:
    """
    Uygulamanın çalışması için gerekli tüm yazılabilir dizinleri
    oluşturur. Zaten varsa sessizce geçer.
    Hata durumunda OSError fırlatır — çağıran taraf ele almalıdır.
    """
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def get_palette(theme: str) -> dict[str, str]:
    """
    Verilen tema adı için renk paletini döner.
    Geçersiz tema verilirse varsayılan temaya düşer.
    """
    if theme == THEME_DARK:
        return DARK_PALETTE
    return LIGHT_PALETTE