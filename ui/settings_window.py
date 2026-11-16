# ============================================================
# Lexora — Ayarlar Sayfası
# ============================================================

from __future__ import annotations

import config
from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget
)

from services.model_manager import list_installed_packages, list_installed_pairs
from services.storage_service import get_storage
from ui.workers.model_download_worker import ModelDownloadWorker


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: ModelDownloadWorker | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Ayarlar")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # --- Tema ---
        layout.addWidget(QLabel("<b>Tema:</b>"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Açık", config.THEME_LIGHT)
        self._theme_combo.addItem("Koyu", config.THEME_DARK)
        current = get_storage().get_setting(config.SETTING_THEME, config.DEFAULT_THEME)
        idx = self._theme_combo.findData(current)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        layout.addWidget(self._theme_combo)

        layout.addSpacing(10)

        # --- Dil Paketleri ---
        layout.addWidget(QLabel("<b>Dil Paketi Yönetimi:</b>"))

        pkg_row = QHBoxLayout()
        pkg_row.addWidget(QLabel("Kaynak:"))
        self._src_combo = QComboBox()
        pkg_row.addWidget(self._src_combo, 1)

        pkg_row.addWidget(QLabel("Hedef:"))
        self._tgt_combo = QComboBox()
        pkg_row.addWidget(self._tgt_combo, 1)

        self._btn_download = QPushButton("📥 İndir ve Kur")
        self._btn_download.clicked.connect(self._start_download)
        pkg_row.addWidget(self._btn_download)
        layout.addLayout(pkg_row)

        self._status_label = QLabel("")
        self._status_label.setObjectName("SubtitleLabel")
        layout.addWidget(self._status_label)

        layout.addWidget(QLabel("<b>Yüklü Paketler:</b>"))
        self._pkg_label = QLabel(self._format_packages())
        self._pkg_label.setWordWrap(True)
        self._pkg_label.setObjectName("SubtitleLabel")
        layout.addWidget(self._pkg_label)

        btn = QPushButton("🔄  Listeyi Yenile")
        btn.clicked.connect(self._refresh_packages)
        layout.addWidget(btn)

        layout.addStretch()
        self._populate_combos()

    def _populate_combos(self) -> None:
        """Desteklenen tüm dilleri combo box'lara doldurur."""
        codes = sorted(config.LANGUAGE_DISPLAY_NAMES.keys())
        for code in codes:
            name = config.language_name(code)
            self._src_combo.addItem(name, code)
            self._tgt_combo.addItem(name, code)

        # Varsayılan olarak İngilizce -> Türkçe seçelim
        idx_en = self._src_combo.findData("en")
        if idx_en >= 0: self._src_combo.setCurrentIndex(idx_en)
        idx_tr = self._tgt_combo.findData("tr")
        if idx_tr >= 0: self._tgt_combo.setCurrentIndex(idx_tr)

    def _format_packages(self) -> str:
        try:
            pkgs = list_installed_packages()
        except Exception:
            pkgs = []
        if not pkgs:
            return "Yüklü dil paketi yok."
        return "\n".join(f"• {p.from_name} → {p.to_name}" for p in pkgs)

    def _refresh_packages(self) -> None:
        self._pkg_label.setText(self._format_packages())

    def _start_download(self) -> None:
        if self._thread is not None:
            return  # Zaten indiriliyor

        from_code = self._src_combo.currentData()
        to_code = self._tgt_combo.currentData()

        if from_code == to_code:
            QMessageBox.warning(self, "Uyarı", "Kaynak ve hedef dil aynı olamaz.")
            return

        # Paket zaten yüklü mü?
        if (from_code, to_code) in list_installed_pairs():
            QMessageBox.information(self, "Bilgi", "Bu dil paketi zaten yüklü.")
            return

        self._btn_download.setEnabled(False)
        self._status_label.setText("İndirme başlatılıyor...")

        self._thread = QThread(self)
        self._worker = ModelDownloadWorker(from_code, to_code)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress_message.connect(self._status_label.setText)
        self._worker.finished.connect(self._on_download_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()

    def _on_download_finished(self, success: bool, message: str) -> None:
        self._status_label.setText(message)
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self._refresh_packages()
        else:
            QMessageBox.critical(self, "Hata", message)

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._btn_download.setEnabled(True)