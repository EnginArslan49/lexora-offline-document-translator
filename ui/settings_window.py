# ============================================================
# Lexora — Ayarlar Sayfası
# ============================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget,
)

import config
from services.model_manager import list_installed_packages
from services.storage_service import get_storage


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Ayarlar")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        layout.addWidget(QLabel("Tema:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Koyu", config.THEME_DARK)
        self._theme_combo.addItem("Açık", config.THEME_LIGHT)
        current = get_storage().get_setting(config.SETTING_THEME, config.DEFAULT_THEME)
        idx = self._theme_combo.findData(current)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        layout.addWidget(self._theme_combo)

        layout.addWidget(QLabel("Yüklü dil paketleri:"))
        self._pkg_label = QLabel(self._format_packages())
        self._pkg_label.setWordWrap(True)
        self._pkg_label.setObjectName("SubtitleLabel")
        layout.addWidget(self._pkg_label)

        btn = QPushButton("🔄  Dil Paketlerini Yenile")
        btn.clicked.connect(self._refresh_packages)
        layout.addWidget(btn)

        layout.addStretch()

    def _format_packages(self) -> str:
        try:
            pkgs = list_installed_packages()
        except Exception:
            pkgs = []
        if not pkgs:
            return "Yüklü dil paketi yok. İndirmek için ilerideki sürümü bekleyin."
        return "\n".join(f"• {p.from_name} → {p.to_name}" for p in pkgs)

    def _refresh_packages(self) -> None:
        self._pkg_label.setText(self._format_packages())