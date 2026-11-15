# ============================================================
# Lexora — Hakkında Sayfası
# ============================================================

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

import config


class AboutPage(QWidget):
    """Hakkında içeriği."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        # Logo (varsa).
        logo_path = config.IMAGES_DIR / "logo.png"
        if logo_path.exists():
            logo = QLabel()
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo.setPixmap(pix.scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
                layout.addWidget(logo)

        title = QLabel(config.APP_DISPLAY_NAME)
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        ver = QLabel(f"Sürüm {config.APP_VERSION}  •  {config.APP_DESCRIPTION_EN}")
        ver.setObjectName("SubtitleLabel")
        layout.addWidget(ver)

        desc = QLabel(config.APP_DEVELOPER_BIO)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        dev = QLabel(
            f"<b>{config.APP_DEVELOPER_NAME}</b> — {config.APP_DEVELOPER_TITLE}"
        )
        layout.addWidget(dev)

        support = QLabel(config.APP_SUPPORT_MESSAGE)
        support.setWordWrap(True)
        support.setObjectName("SubtitleLabel")
        layout.addWidget(support)

        row = QHBoxLayout()
        for name, url in config.SOCIAL_LINKS.items():
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
            row.addWidget(btn)
        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()