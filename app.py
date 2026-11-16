# ============================================================
# Lexora — Uygulama Giriş Noktası
# ============================================================
# - Dizin hazırlığı
# - Argos ortamı
# - Global exception hook (Türkçe hata mesajı + log)
# - Tema yükleme
# ============================================================
from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

import config
from services.logging_service import get_logger, user_message
from services.model_manager import setup_argos_environment
from services.storage_service import get_storage
from ui.themes.theme_manager import ThemeManager


logger = get_logger(__name__)


def _install_exception_hook() -> None:
    """Beklenmeyen hataları yakala, logla, kullanıcıya Türkçe göster."""
    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logger.exception(
            "Yakalanmamış hata: %s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )
        try:
            QMessageBox.critical(
                None, "Beklenmeyen Hata",
                user_message("unexpected"),
            )
        except Exception:
            pass
    sys.excepthook = _hook


def main() -> int:
    config.ensure_required_dirs()
    setup_argos_environment()
    logger.info("Lexora başlatıldı. Sürüm: %s", config.APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.APP_ORGANIZATION)

    _install_exception_hook()

    icon_path = config.ICONS_DIR / "app.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    theme = ThemeManager()
    saved = get_storage().get_setting(config.SETTING_THEME, config.DEFAULT_THEME)
    theme.set_theme(saved or config.DEFAULT_THEME)
    theme.apply(app)

    # MainWindow'u geç import et (QApplication oluştuktan sonra).
    from ui.main_window import MainWindow
    window = MainWindow(theme)
    window.show()
    rc = app.exec()
    logger.info("Lexora kapatıldı. Çıkış kodu: %s", rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())