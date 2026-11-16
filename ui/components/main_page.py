# ============================================================
# Lexora — Ana Ekran
# ============================================================
# Sürükle-bırak, dosya seçimi, dil seçimi, çıktı yolu,
# ilerleme çubuğu ve çeviri başlatma butonu.
# ============================================================

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

import config
from services.logging_service import get_logger, user_message

logger = get_logger(__name__)


class DropZone(QFrame):
    """Dosya sürükle-bırak alanı."""

    file_dropped = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName("Card")
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self._label = QLabel(
            "📄  Dosyayı buraya sürükleyin\nveya aşağıdaki butona tıklayın\n\n"
            "Desteklenen formatlar: .txt, .docx"
        )
        self._label.setObjectName("DropZone")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path:
                self.file_dropped.emit(path)


class MainPage(QWidget):
    """Ana çalışma sayfası."""

    start_translation_requested = Signal(dict)
    cancel_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._source_path: Path | None = None
        self._is_running = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Belge Çevirisi")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        sub = QLabel(config.APP_DESCRIPTION_TR)
        sub.setObjectName("SubtitleLabel")
        layout.addWidget(sub)

        self._drop = DropZone()
        self._drop.file_dropped.connect(self._on_file_selected)
        layout.addWidget(self._drop)

        file_row = QHBoxLayout()
        self._btn_pick = QPushButton("📂  Dosya Seç")
        self._btn_pick.clicked.connect(self._pick_file)
        file_row.addWidget(self._btn_pick)
        file_row.addStretch()
        layout.addLayout(file_row)

        self._file_info = QLabel("Henüz dosya seçilmedi.")
        self._file_info.setObjectName("SubtitleLabel")
        layout.addWidget(self._file_info)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Kaynak dil:"))
        self._src_lang = QComboBox()
        self._src_lang.setEditable(False)
        lang_row.addWidget(self._src_lang, 1)
        lang_row.addWidget(QLabel("Hedef dil:"))
        self._tgt_lang = QComboBox()
        lang_row.addWidget(self._tgt_lang, 1)
        layout.addLayout(lang_row)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Çıktı adı:"))
        self._out_name = QLineEdit()
        self._out_name.setPlaceholderText("otomatik")
        out_row.addWidget(self._out_name, 1)
        out_row.addWidget(QLabel("Klasör:"))
        self._out_dir = QLineEdit()
        self._out_dir.setText(str(Path.home() / "Desktop"))
        out_row.addWidget(self._out_dir, 1)
        btn_dir = QPushButton("...")
        btn_dir.setFixedWidth(36)
        btn_dir.clicked.connect(self._pick_dir)
        out_row.addWidget(btn_dir)
        layout.addLayout(out_row)

        action_row = QHBoxLayout()

        # Çeviriyi Başlat Butonu
        self._btn_translate = QPushButton("🚀  Çeviriyi Başlat")
        self._btn_translate.setObjectName("PrimaryButton")
        self._btn_translate.clicked.connect(self._on_start)
        self._btn_translate.setEnabled(False)
        action_row.addWidget(self._btn_translate, 1)

        # Yeni Çeviri Butonu (Başlangıçta gizli)
        self._btn_new = QPushButton("✨  Yeni Çeviri Yap")
        self._btn_new.setObjectName("PrimaryButton")
        self._btn_new.clicked.connect(self._reset_ui)
        self._btn_new.setVisible(False)
        action_row.addWidget(self._btn_new, 1)

        # İptal Butonu (Sadece çalışırken görünür)
        self._btn_cancel = QPushButton("⏹  İptal")
        self._btn_cancel.setVisible(False)
        self._btn_cancel.clicked.connect(self._on_cancel)
        action_row.addWidget(self._btn_cancel)

        layout.addLayout(action_row)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status = QLabel("")
        self._status.setObjectName("SubtitleLabel")
        layout.addWidget(self._status)
        layout.addStretch()

        self._populate_languages()

    def _populate_languages(self) -> None:
        """Mevcut Argos dillerini combobox'lara doldurur."""
        try:
            from services.model_manager import list_supported_languages
            codes = list_supported_languages()
        except Exception:
            codes = []

        for combo in (self._src_lang, self._tgt_lang):
            combo.clear()
            for code in codes:
                combo.addItem(config.language_name(code), code)

        if self._tgt_lang.count() > 0:
            self._tgt_lang.setCurrentIndex(0)

    def _pick_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Dosya Seç", str(Path.home()),
            "Belgeler (*.txt *.docx);;Tüm Dosyalar (*)",
        )
        if path:
            self._on_file_selected(path)

    def _on_file_selected(self, path: str) -> None:
        p = Path(path)
        self._source_path = p
        try:
            from services.validation_service import validate_input_file
            info = validate_input_file(p)
            fmt = config.FORMAT_DISPLAY_NAMES.get(str(info["format"]), info["format"])
            size_kb = int(info["size"]) // 1024
            self._file_info.setText(f"✅ {p.name}  •  {fmt}  •  {size_kb} KB")

            # Otomatik dil algılama (TXT için)
            if info["format"] == ".txt" and "text" in info:
                from core.language_detector import detect_language
                r = detect_language(str(info["text"]))
                if r and r.is_reliable:
                    idx = self._src_lang.findData(r.code)
                    if idx >= 0:
                        self._src_lang.setCurrentIndex(idx)
                        self._status.setText(f"Algılanan dil: {r.name} ({r.confidence:.0%})")

            self._btn_translate.setEnabled(True)
            self._btn_translate.setVisible(True)
            self._btn_new.setVisible(False)

        except Exception as exc:
            err = getattr(exc, "error_key", "unexpected")
            self._file_info.setText(f"❌ {user_message(err)}")
            self._btn_translate.setEnabled(False)

    def _pick_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Çıktı Klasörü", self._out_dir.text())
        if d:
            self._out_dir.setText(d)

    def _on_start(self) -> None:
        if self._source_path is None:
            return
        if self._src_lang.currentData() is None or self._tgt_lang.currentData() is None:
            self._status.setText("⚠️ Lütfen kaynak ve hedef dili seçin.")
            return
        self.start_translation_requested.emit({
            "source": str(self._source_path),
            "src_lang": self._src_lang.currentData(),
            "tgt_lang": self._tgt_lang.currentData(),
            "out_dir": self._out_dir.text(),
            "out_name": self._out_name.text().strip() or None,
        })

    def _on_cancel(self) -> None:
        self.cancel_requested.emit()

    def _reset_ui(self) -> None:
        """Yeni çeviri için arayüzü sıfırlar."""
        self._source_path = None
        self._file_info.setText("Henüz dosya seçilmedi.")
        self._status.setText("")
        self._out_name.clear()

        # Buton durumlarını ayarla
        self._btn_new.setVisible(False)
        self._btn_translate.setVisible(True)
        self._btn_translate.setEnabled(False)  # Dosya seçilene kadar pasif

        # İlerleme çubuğunu sıfırla ve gizle
        self._progress.setValue(0)
        self._progress.setVisible(False)

    # --- Worker'dan gelen güncellemeler için ---

    def set_running(self, running: bool) -> None:
        self._is_running = running
        if running:
            self._btn_translate.setEnabled(False)
            self._btn_new.setVisible(False)
            self._btn_cancel.setVisible(True)
            self._progress.setVisible(True)
            self._progress.setValue(0)
        else:
            self._btn_cancel.setVisible(False)

    def update_progress(self, current: int, total: int) -> None:
        if total > 0:
            self._progress.setMaximum(total)
            self._progress.setValue(current)
            self._status.setText(f"Çevriliyor… {current}/{total}")

    def show_result(self, output_path: str, success: bool, message: str = "") -> None:
        self._is_running = False
        self._progress.setVisible(False)
        self._btn_cancel.setVisible(False)

        if success:
            self._status.setText(f"✅ Tamamlandı: {output_path}")
            # Çeviriyi başlat butonunu gizle, yeni çeviri butonunu göster
            self._btn_translate.setVisible(False)
            self._btn_new.setVisible(True)
        else:
            self._status.setText(f"❌ {message or 'İşlem başarısız.'}")
            # Hata durumunda tekrar denemek için Çeviriyi Başlat butonu açık kalsın
            self._btn_translate.setVisible(True)
            self._btn_translate.setEnabled(True)
            self._btn_new.setVisible(False)