# ============================================================
# Lexora — Çeviri Worker'ı (QObject + moveToThread)
# ============================================================
# UI thread'ini bloklamadan çeviri yapar. Sinyallerle ilerleme
# ve sonuç bildirir. Aynı anda tek dosya işler.
# ============================================================

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from core.translator import CancelToken
from services.file_manager import build_output_path
from services.logging_service import get_logger
from services.storage_service import (
    STATUS_COMPLETED, STATUS_FAILED, STATUS_IN_PROGRESS, STATUS_CANCELLED,
    get_storage,
)
from services.validation_service import validate_input_file

logger = get_logger(__name__)


class TranslationWorker(QObject):
    """Tek dosya için çeviri yapan worker."""

    progress = Signal(int, int)
    file_done = Signal(str, str)          # çıktı yolu, durum
    failed = Signal(str, str)             # error_key, detail
    finished = Signal()

    def __init__(self, job: dict) -> None:
        super().__init__()
        self._job = job
        self._cancel = CancelToken()
        self._history_id: int | None = None

    @Slot()
    def cancel(self) -> None:
        self._cancel.cancel()

    @Slot()
    def run(self) -> None:
        storage = get_storage()
        try:
            src = Path(self._job["source"])
            out_dir = Path(self._job["out_dir"])
            src_lang = self._job["src_lang"]
            tgt_lang = self._job["tgt_lang"]

            # Geçmişe "işleniyor" olarak ekle.
            self._history_id = storage.add_history_entry(
                source_file=src.name,
                source_lang=src_lang,
                target_lang=tgt_lang,
                status=STATUS_IN_PROGRESS,
            )

            info = validate_input_file(src)
            fmt = info["format"]

            out_path = build_output_path(src, out_dir, tgt_lang, overwrite=True)

            # Kullanıcı manuel bir çıktı adı girdiyse:
            if self._job.get("out_name"):
                user_name = self._job["out_name"].strip()
                # Eğer kullanıcı zaten uzantıyı yazmadıysa, kaynak dosyanın uzantısını ekle.
                if not user_name.lower().endswith(fmt):
                    user_name += fmt
                out_path = out_dir / user_name

            def on_progress(cur: int, total: int) -> None:
                self.progress.emit(cur, total)

            if fmt == ".txt":
                from processors.txt_processor import process_txt
                process_txt(
                    src, out_path, str(info["encoding"]), src_lang, tgt_lang,
                    cancel_token=self._cancel, progress_callback=on_progress,
                )
            elif fmt == ".docx":
                from processors.docx_processor import process_docx
                process_docx(
                    src, out_path, src_lang, tgt_lang,
                    cancel_token=self._cancel, progress_callback=on_progress,
                )
            else:
                self._fail("unsupported_format", str(fmt))
                return

            if self._cancel.is_cancelled():
                storage.update_history_status(
                    self._history_id, STATUS_CANCELLED,
                )
                self.failed.emit("translation_cancelled", "")
            else:
                storage.update_history_status(
                    self._history_id, STATUS_COMPLETED,
                    output_file=str(out_path),
                )
                self.file_done.emit(str(out_path), STATUS_COMPLETED)
        except Exception as exc:
            err = getattr(exc, "error_key", "unexpected")
            self._fail(err, str(exc))
        finally:
            self.finished.emit()

    def _fail(self, error_key: str, detail: str) -> None:
        if self._history_id is not None:
            try:
                get_storage().update_history_status(
                    self._history_id, STATUS_FAILED, error_message=error_key,
                )
            except Exception:
                pass
        self.failed.emit(error_key, detail)