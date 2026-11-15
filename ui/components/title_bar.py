# ============================================================
# Lexora — Custom Başlık Çubuğu (macOS tarzı)
# ============================================================
# Frameless pencerede sürükleme + sağ üstte trafik ışığı butonları.
# Hover durumunda buton içinde simge (×, −, □) siyah olarak belirir.
# ============================================================

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

import config


class _TrafficButton(QPushButton):
    """Hover'da içinde siyah simge beliren renkli trafik ışığı butonu."""

    def __init__(self, color: str, symbol: str, tooltip: str) -> None:
        super().__init__()
        self._color = color
        self._symbol = symbol  # "×", "−", "□"
        self.setObjectName("TrafficButton")
        self.setFixedSize(14, 14)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self._hovered = False

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # Arka plan: renkli daire.
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())

        # Hover'da siyah simge.
        if self._hovered:
            painter.setPen(QColor("#000000"))
            font = QFont()
            font.setBold(True)
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                self._symbol,
            )
        painter.end()


class TitleBar(QWidget):
    """Sürüklenebilir custom başlık çubuğu + sağ üstte pencere kontrolleri."""

    def __init__(self, parent_window: QWidget) -> None:
        super().__init__(parent_window)
        self._parent = parent_window
        self._drag_pos: QPoint | None = None
        self.setObjectName("TitleBar")
        self.setFixedHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Sol: uygulama adı.
        title = QLabel(config.APP_NAME)
        title.setStyleSheet("font-weight: 600; font-size: 13px;")
        layout.addWidget(title)
        layout.addStretch()

        # Sağ: trafik ışıkları (kapat / küçült / büyüt).
        self._btn_min = _TrafficButton("#FEBC2E", "−", "Küçült")
        self._btn_max = _TrafficButton("#28C840", "□", "Büyüt")
        self._btn_close = _TrafficButton("#FF5F57", "×", "Kapat")

        self._btn_min.clicked.connect(self._parent.showMinimized)
        self._btn_max.clicked.connect(self._toggle_maximize)
        self._btn_close.clicked.connect(self._parent.close)

        layout.addWidget(self._btn_min)
        layout.addWidget(self._btn_max)
        layout.addWidget(self._btn_close)

    def _toggle_maximize(self) -> None:
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            self._parent.showMaximized()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self._parent.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            if self._parent.isMaximized():
                self._parent.showNormal()
            self._parent.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)