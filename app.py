# ============================================================
# Lexora — Uygulama Giriş Noktası
# ============================================================
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import config
from services.model_manager import setup_argos_environment
from services.storage_service import get_storage
from ui.themes.theme_manager import ThemeManager
from ui.main_window import MainWindow


def main() -> int:
    config.ensure_required_dirs()
    setup_argos_environment()

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.APP_ORGANIZATION)

    # İkon.
    icon_path = config.ICONS_DIR / "app.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Tema (storage'dan oku).
    theme = ThemeManager()
    saved = get_storage().get_setting(config.SETTING_THEME, config.DEFAULT_THEME)
    theme.set_theme(saved or config.DEFAULT_THEME)
    theme.apply(app)

    window = MainWindow(theme)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())