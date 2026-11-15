# ============================================================
# Lexora — Storage Servisi (JSON tabanlı kalıcılık)
# ============================================================
# Bu modül SQLite yerine basit JSON dosyaları kullanır:
#   - settings.json  -> kullanıcı ayarları (tema, son dil, pencere konumu)
#   - history.json   -> çeviri geçmişi (son N kayıt)
#
# Tasarım kararları:
# - Atomik yazma: önce .tmp dosyasına yaz, sonra os.replace() ile devir.
#   Bu sayede yazma sırasında uygulama çökse bile dosya bozulmaz.
# - Bozuk/eksik JSON durumunda varsayılan değerlerle başla, eski dosyayı yedekle.
# - Thread-safe: tek RLock ile tüm okuma/yazma işlemleri korunur.
# - Belge içeriği ASLA saklanmaz; sadece meta veri (dosya adı, dil, durum).
# ============================================================

from __future__ import annotations

import json
import os
import shutil
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


# ============================================================
# 1) VERİ MODELLERİ
# ============================================================

@dataclass
class HistoryEntry:
    """Bir çeviri işleminin geçmiş kaydı. Belge içeriği tutulmaz."""
    id: int
    source_file: str
    source_lang: str
    target_lang: str
    status: str
    output_file: str | None = None
    error_message: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    completed_at: str | None = None


# Durum sabitleri — UI ve worker katmanı bu sabitleri kullanır.
STATUS_PENDING: str = "pending"
STATUS_IN_PROGRESS: str = "in_progress"
STATUS_COMPLETED: str = "completed"
STATUS_FAILED: str = "failed"
STATUS_CANCELLED: str = "cancelled"

# İnsan tarafından okunabilir durum adları — geçmiş penceresinde kullanılacak.
STATUS_DISPLAY: dict[str, str] = {
    STATUS_PENDING: "Bekliyor",
    STATUS_IN_PROGRESS: "İşleniyor",
    STATUS_COMPLETED: "Tamamlandı",
    STATUS_FAILED: "Başarısız",
    STATUS_CANCELLED: "İptal edildi",
}


# ============================================================
# 2) YARDIMCI FONKSİYONLAR
# ============================================================

def _atomic_write_json(path: Path, data: Any) -> None:
    """
    Veriyi atomik olarak JSON dosyasına yazar.
    1. Aynı dizinde geçici bir .tmp dosyasına yaz.
    2. Başarıyla yazıldıysa os.replace() ile asıl dosyaya devir.
    Bu sayede yazma sırasında oluşan çökme dosyayı bozmaz.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def _safe_load_json(path: Path, default: Any) -> Any:
    """
    JSON dosyasını güvenle okur. Dosya yoksa veya bozuksa varsayılanı döner.
    Bozuk dosya varsa '.corrupt-<zaman>' uzantısıyla yedekler.
    """
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        # Bozuk dosyayı yedekle, sonra varsayılanı döndür.
        try:
            backup = path.with_name(
                f"{path.name}.corrupt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            shutil.copy2(path, backup)
            logger.warning(
                "Bozuk JSON dosyası yedeklendi: %s -> %s", path.name, backup.name
            )
        except OSError:
            logger.warning("Bozuk JSON dosyası yedeklenemedi: %s", path.name)
        logger.warning("JSON okuma hatası (%s): %s", path.name, exc)
        return default


# ============================================================
# 3) STORAGE SERVİSİ
# ============================================================

class StorageService:
    """
    JSON tabanlı ayar ve geçmiş yöneticisi.
    Tek örnek (singleton) olarak `get_storage()` ile erişilir.
    Test için `StorageService(settings_path=..., history_path=...)` kullanılabilir.
    """

    def __init__(
        self,
        settings_path: Path | None = None,
        history_path: Path | None = None,
    ) -> None:
        self._settings_path = settings_path or config.SETTINGS_FILE_PATH
        self._history_path = history_path or config.HISTORY_FILE_PATH
        self._lock = threading.RLock()

        # Bellekteki önbellek — disk I/O azaltmak için.
        self._settings: dict[str, str] = {}
        self._history: list[dict[str, Any]] = []
        self._next_id: int = 1

        self._load_all()

    # --------------------------------------------------------
    # Yükleme / kalıcılık
    # --------------------------------------------------------

    def _load_all(self) -> None:
        """Ayarları ve geçmişi diskten yükler."""
        with self._lock:
            settings_raw = _safe_load_json(self._settings_path, default={})
            if not isinstance(settings_raw, dict):
                logger.warning("Ayarlar dosyası beklenen formatta değil, sıfırlanıyor.")
                settings_raw = {}
            # Tüm değerleri string'e zorla — şema basit kalsın.
            self._settings = {str(k): str(v) for k, v in settings_raw.items()}

            history_raw = _safe_load_json(self._history_path, default=[])
            if not isinstance(history_raw, list):
                logger.warning("Geçmiş dosyası beklenen formatta değil, sıfırlanıyor.")
                history_raw = []
            self._history = history_raw

            # Sonraki ID'yi belirle.
            max_id = 0
            for entry in self._history:
                try:
                    entry_id = int(entry.get("id", 0))
                    if entry_id > max_id:
                        max_id = entry_id
                except (TypeError, ValueError):
                    continue
            self._next_id = max_id + 1

            logger.info(
                "Storage yüklendi. Ayar: %d, Geçmiş: %d kayıt",
                len(self._settings), len(self._history),
            )

    # --------------------------------------------------------
    # Ayarlar
    # --------------------------------------------------------

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Ayarı döner; yoksa `default`."""
        with self._lock:
            return self._settings.get(key, default)

    def set_setting(self, key: str, value: str) -> None:
        """Ayarı kaydeder ve diske yazar."""
        with self._lock:
            self._settings[key] = str(value)
            self._flush_settings()
            logger.debug("Ayar kaydedildi: %s", key)

    def delete_setting(self, key: str) -> None:
        """Ayarı siler ve diske yazar."""
        with self._lock:
            if key in self._settings:
                del self._settings[key]
                self._flush_settings()

    def get_all_settings(self) -> dict[str, str]:
        """Tüm ayarların kopyasını döner."""
        with self._lock:
            return dict(self._settings)

    def _flush_settings(self) -> None:
        """Ayarları diske atomik yazar. Lock dışından çağrılmamalı."""
        try:
            _atomic_write_json(self._settings_path, self._settings)
        except OSError as exc:
            logger.error("Ayarlar dosyaya yazılamadı: %s", exc)

    # --------------------------------------------------------
    # Geçmiş
    # --------------------------------------------------------

    def add_history_entry(
        self,
        source_file: str,
        source_lang: str,
        target_lang: str,
        status: str = STATUS_PENDING,
        output_file: str | None = None,
        error_message: str | None = None,
    ) -> int:
        """Yeni geçmiş kaydı ekler, ID döner."""
        with self._lock:
            entry = HistoryEntry(
                id=self._next_id,
                source_file=source_file,
                source_lang=source_lang,
                target_lang=target_lang,
                status=status,
                output_file=output_file,
                error_message=error_message,
            )
            self._next_id += 1
            # En yeni başta olsun.
            self._history.insert(0, asdict(entry))
            self._trim_history()
            self._flush_history()
            logger.info("Geçmişe yeni kayıt eklendi. ID: %s", entry.id)
            return entry.id

    def update_history_status(
        self,
        entry_id: int,
        status: str,
        output_file: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Bir kaydın durumunu günceller."""
        with self._lock:
            for entry in self._history:
                if entry.get("id") == entry_id:
                    entry["status"] = status
                    if output_file is not None:
                        entry["output_file"] = output_file
                    if error_message is not None:
                        entry["error_message"] = error_message
                    if status in (STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED):
                        entry["completed_at"] = datetime.now().isoformat(timespec="seconds")
                    self._flush_history()
                    logger.info(
                        "Geçmiş kaydı güncellendi. ID: %s, Durum: %s", entry_id, status
                    )
                    return
        logger.warning("Güncellenecek geçmiş kaydı bulunamadı. ID: %s", entry_id)

    def get_history(
        self,
        limit: int = 100,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Geçmiş kayıtlarını (en yeniden eskiye) döner."""
        with self._lock:
            items = self._history
            if status_filter:
                items = [e for e in items if e.get("status") == status_filter]
            return items[offset:offset + limit]

    def get_history_count(self, status_filter: str | None = None) -> int:
        """Toplam kayıt sayısı."""
        with self._lock:
            if status_filter:
                return sum(1 for e in self._history if e.get("status") == status_filter)
            return len(self._history)

    def get_history_entry(self, entry_id: int) -> dict[str, Any] | None:
        """Tek kayıt getir."""
        with self._lock:
            for entry in self._history:
                if entry.get("id") == entry_id:
                    return dict(entry)
            return None

    def delete_history_entry(self, entry_id: int) -> None:
        """Tek kaydı sil."""
        with self._lock:
            before = len(self._history)
            self._history = [e for e in self._history if e.get("id") != entry_id]
            if len(self._history) != before:
                self._flush_history()
                logger.info("Geçmiş kaydı silindi. ID: %s", entry_id)

    def clear_history(self) -> int:
        """Tüm geçmişi sil, silinen sayıyı döner."""
        with self._lock:
            deleted = len(self._history)
            self._history = []
            self._next_id = 1
            self._flush_history()
            logger.info("Geçmiş temizlendi. Silinen: %s", deleted)
            return deleted

    def _trim_history(self) -> None:
        """MAX_HISTORY_ENTRIES aşılırsa en eskileri buda. Lock dışından çağrılmamalı."""
        max_entries = config.MAX_HISTORY_ENTRIES
        if len(self._history) > max_entries:
            # En yeni başta olduğu için listenin sonundan kesiyoruz.
            removed = len(self._history) - max_entries
            self._history = self._history[:max_entries]
            logger.info("Geçmiş boyutu sınırı aşıldı, %d eski kayıt budandı.", removed)

    def _flush_history(self) -> None:
        """Geçmişi diske atomik yazar. Lock dışından çağrılmamalı."""
        try:
            _atomic_write_json(self._history_path, self._history)
        except OSError as exc:
            logger.error("Geçmiş dosyaya yazılamadı: %s", exc)

    # --------------------------------------------------------
    # Yaşam döngüsü
    # --------------------------------------------------------

    def reload(self) -> None:
        """Diskten yeniden yükle (test ve manuel yenileme için)."""
        with self._lock:
            self._load_all()


# ============================================================
# 4) MODÜL DÜZEYİ TEK ÖRNEK
# ============================================================

_shared_instance: StorageService | None = None


def get_storage() -> StorageService:
    """Uygulama genelindeki tek storage örneğini döner."""
    global _shared_instance
    if _shared_instance is None:
        _shared_instance = StorageService()
    return _shared_instance