# ============================================================
# Lexora — Ana Pencere
# ============================================================
# Frameless macOS tarzı pencere, sidebar navigasyon, worker entegrasyonu.
# ============================================================

from __future__ import annotations

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

import config
from services.logging_service import get_logger, user_message
from ui.components.title_bar import TitleBar
from ui.themes.theme_manager import ThemeManager
from ui.workers.translation_worker import TranslationWorker

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Lexora ana penceresi."""

    def __init__(self, theme_manager: ThemeManager) -> None:
        super().__init__()
        self._theme = theme_manager
        self._thread: QThread | None = None
        self._worker: TranslationWorker | None = None

        self.setWindowTitle(config.APP_DISPLAY_NAME)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.resize(config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT)

        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._title_bar = TitleBar(self)
        root_layout.addWidget(self._title_bar)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        root_layout.addWidget(body)

        self._sidebar = self._build_sidebar()
        body_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        body_layout.addWidget(self._stack, 1)

        # Sayfalar.
        from ui.components.main_page import MainPage
        from ui.about_window import AboutPage
        from ui.history_window import HistoryPage
        from ui.settings_window import SettingsPage

        self._main_page = MainPage()
        self._main_page.start_translation_requested.connect(self._start_translation)
        self._main_page.cancel_requested.connect(self._cancel_translation)

        self._history_page = HistoryPage()
        self._about_page = AboutPage()
        self._settings_page = SettingsPage()

        self._stack.addWidget(self._main_page)       # 0
        self._stack.addWidget(self._history_page)    # 1
        self._stack.addWidget(self._settings_page)   # 2
        self._stack.addWidget(self._about_page)      # 3

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Uygulama adı.
        brand = QLabel(config.APP_NAME)
        brand.setObjectName("TitleLabel")
        layout.addWidget(brand)
        layout.addSpacing(12)

        self._nav_buttons: list[QPushButton] = []
        items = [
            ("🏠  Ana Ekran", 0), ("🕘  Geçmiş", 1),
            ("⚙️  Ayarlar", 2), ("ℹ️  Hakkında", 3),
        ]
        for label, idx in items:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setChecked(idx == 0)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        theme_btn = QPushButton("🌓  Tema Değiştir")
        theme_btn.setObjectName("NavButton")
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)
        return sidebar

    def _navigate(self, idx: int) -> None:
        for i, b in enumerate(self._nav_buttons):
            b.setChecked(i == idx)
        self._stack.setCurrentIndex(idx)
        if idx == 1:
            self._history_page.refresh()

    def _toggle_theme(self) -> None:
        self._theme.toggle()
        self._theme.apply(QApplication.instance())

    # --- Çeviri akışı ---

    def _start_translation(self, job: dict) -> None:
        if self._thread is not None:
            return  # Zaten çalışıyor

        self._main_page.set_running(True)

        self._thread = QThread(self)
        self._worker = TranslationWorker(job)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._main_page.update_progress)
        self._worker.file_done.connect(self._on_worker_done)
        self._worker.failed.connect(self._on_worker_failed)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()

    def _cancel_translation(self) -> None:
        if self._worker is not None:
            self._worker.cancel()

    def _on_worker_done(self, output_path: str, status: str) -> None:
        self._main_page.show_result(output_path, success=True)

    def _on_worker_failed(self, error_key: str, detail: str) -> None:
        self._main_page.show_result(
            "", success=False, message=user_message(error_key, detail or None)
        )

    def _on_worker_finished(self) -> None:
        if self._thread is not None:
            self._thread.quit()

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._main_page.set_running(False)

    def closeEvent(self, event) -> None:
        if self._worker is not None:
            self._worker.cancel()
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(2000)
        event.accept()