# ============================================================
# Lexora — Dil Paketi İndirme Worker'ı
# ============================================================

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from services.logging_service import get_logger
from services.model_manager import update_package_index, install_package

logger = get_logger(__name__)


class ModelDownloadWorker(QObject):
    """Dil paketini arka planda indirir."""

    progress_message = Signal(str)
    finished = Signal(bool, str)  # başarılı mı?, mesaj

    def __init__(self, from_code: str, to_code: str) -> None:
        super().__init__()
        self._from_code = from_code
        self._to_code = to_code

    @Slot()
    def run(self) -> None:
        try:
            self.progress_message.emit("Paket listesi güncelleniyor...")
            if not update_package_index():
                self.finished.emit(False, "İnternet bağlantısı kurulamadı. Lütfen bağlantınızı kontrol edin.")
                return

            self.progress_message.emit(
                f"Paket indiriliyor ({self._from_code.upper()} -> {self._to_code.upper()})... Lütfen bekleyin.")

            success = install_package(self._from_code, self._to_code)
            if success:
                self.progress_message.emit("Kurulum tamamlandı!")
                self.finished.emit(True, "Dil paketi başarıyla yüklendi.")
            else:
                self.finished.emit(False, "Bu dil çifti için paket bulunamadı veya indirilemedi.")

        except Exception as exc:
            logger.exception("Paket indirme hatası")
            self.finished.emit(False, f"Beklenmeyen hata: {str(exc)}")