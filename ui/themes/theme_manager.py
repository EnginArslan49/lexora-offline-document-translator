# ============================================================
# Lexora — Tema Yöneticisi
# ============================================================
# Açık/koyu tema QSS'lerini yükler ve uygular.
# Renkler config.py'deki paletlerden gelir.
# ============================================================

from __future__ import annotations

from PySide6.QtWidgets import QApplication

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


class ThemeManager:
    """Tema durumunu yönetir; QSS üretir ve uygular."""

    def __init__(self) -> None:
        self._current = config.DEFAULT_THEME

    @property
    def current(self) -> str:
        return self._current

    def is_dark(self) -> bool:
        return self._current == config.THEME_DARK

    def toggle(self) -> str:
        """Temayı değiştirir, yeni tema adını döner."""
        self._current = (
            config.THEME_LIGHT if self.is_dark() else config.THEME_DARK
        )
        logger.info("Tema değiştirildi: %s", self._current)
        return self._current

    def set_theme(self, theme: str) -> None:
        if theme in (config.THEME_LIGHT, config.THEME_DARK):
            self._current = theme

    def build_stylesheet(self) -> str:
        """Aktif tema için QSS üretir."""
        p = config.get_palette(self._current)
        b = config.BRAND_COLORS
        r = config.UI_CORNER_RADIUS
        rs = config.UI_CORNER_RADIUS_SMALL

        return f"""
        /* === Genel === */
        QWidget {{
            background-color: {p['bg_window']};
            color: {p['text_primary']};
            font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
            font-size: 13px;
        }}
        QMainWindow {{
            background-color: {p['bg_window']};
        }}

        /* === Kart / Panel === */
        QFrame#Card, QFrame#Sidebar {{
            background-color: {p['bg_surface']};
            border-radius: {r}px;
            border: 1px solid {p['border']};
        }}
        QFrame#Sidebar {{
            background-color: {p['bg_sidebar']};
            border: none;
            border-top-left-radius: {r}px;
            border-bottom-left-radius: {r}px;
        }}

        /* === Butonlar === */
        QPushButton {{
            background-color: {p['bg_input']};
            color: {p['text_primary']};
            border: 1px solid {p['border']};
            border-radius: {rs}px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background-color: {p['bg_sidebar']};
        }}
        QPushButton:pressed {{
            background-color: {p['border']};
        }}
        QPushButton#PrimaryButton {{
            background-color: {b['primary_blue']};
            color: #FFFFFF;
            border: none;
            font-weight: 600;
            padding: 10px 20px;
        }}
        QPushButton#PrimaryButton:hover {{
            background-color: {b['cyan']};
        }}
        QPushButton#PrimaryButton:disabled {{
            background-color: {p['text_disabled']};
        }}
        QPushButton#NavButton {{
            text-align: left;
            padding: 10px 14px;
            border: none;
            background: transparent;
        }}
        QPushButton#NavButton:hover {{
            background-color: {p['bg_surface']};
            border-radius: {rs}px;
        }}
        QPushButton#NavButton:checked {{
            background-color: {b['primary_blue']};
            color: #FFFFFF;
            border-radius: {rs}px;
        }}

        /* === Giriş alanları === */
        QLineEdit, QComboBox, QTextEdit, QSpinBox {{
            background-color: {p['bg_input']};
            color: {p['text_primary']};
            border: 1px solid {p['border']};
            border-radius: {rs}px;
            padding: 6px 10px;
            selection-background-color: {b['primary_blue']};
        }}
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
            border: 1px solid {b['primary_blue']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {p['bg_surface']};
            border: 1px solid {p['border']};
            selection-background-color: {b['primary_blue']};
            selection-color: #FFFFFF;
        }}

        /* === İlerleme çubuğu === */
        QProgressBar {{
            background-color: {p['bg_input']};
            border: 1px solid {p['border']};
            border-radius: {rs}px;
            text-align: center;
            height: 22px;
        }}
        QProgressBar::chunk {{
            background-color: {b['primary_blue']};
            border-radius: {rs}px;
        }}

        /* === Başlık etiketleri === */
        QLabel#TitleLabel {{
            font-size: 20px;
            font-weight: 700;
        }}
        QLabel#SubtitleLabel {{
            font-size: 13px;
            color: {p['text_secondary']};
        }}
        QLabel#DropZone {{
            border: 2px dashed {p['border']};
            border-radius: {r}px;
            padding: 30px;
            color: {p['text_secondary']};
        }}
        QLabel#DropZone[dragActive="true"] {{
            border-color: {b['primary_blue']};
            background-color: {p['bg_input']};
        }}

        /* === Başlık çubuğu === */
        QWidget#TitleBar {{
            background-color: {p['bg_sidebar']};
            border-top-left-radius: {r}px;
            border-top-right-radius: {r}px;
        }}
        QPushButton#TrafficButton {{
            border-radius: 7px;
            min-width: 14px;
            max-width: 14px;
            min-height: 14px;
            max-height: 14px;
            border: none;
        }}

        /* === Tablo === */
        QTableWidget {{
            background-color: {p['bg_surface']};
            border: 1px solid {p['border']};
            border-radius: {rs}px;
            gridline-color: {p['border']};
        }}
        QHeaderView::section {{
            background-color: {p['bg_sidebar']};
            color: {p['text_primary']};
            border: none;
            padding: 6px;
            font-weight: 600;
        }}
        """

    def apply(self, app: QApplication) -> None:
        """Stili QApplication'a uygular."""
        app.setStyleSheet(self.build_stylesheet())
        logger.info("Tema uygulandı: %s", self._current)