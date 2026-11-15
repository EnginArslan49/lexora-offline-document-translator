# ============================================================
# Lexora — Logo Üretici (opsiyonel; bir kez çalıştırılır)
# ============================================================
# resources/images/logo.png ve resources/icons/app.png üretir.
#
# DİKKAT: QPainter.drawText() font kullandığı için bir
# QGuiApplication örneği ZORUNLUDUR. Bu script oluşturup
# logo ürettikten sonra çıkar.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path

# Proje kök dizinini sys.path'e ekle (config.py burada).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPixmap,
)

import config


def make_logo(size: int = 256) -> QImage:
    """Yuvarlatılmış köşeli, gradyan arka planlı, ortada 'L' harfli logo üretir."""
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    r = size * 0.22
    grad_rect = QRectF(0, 0, size, size)
    g = QLinearGradient(0, 0, size, size)
    g.setColorAt(0.0, QColor(config.BRAND_COLORS["primary_blue"]))
    g.setColorAt(0.5, QColor(config.BRAND_COLORS["cyan"]))
    g.setColorAt(1.0, QColor(config.BRAND_COLORS["purple"]))
    p.setBrush(g)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(grad_rect, r, r)

    p.setPen(QColor("#FFFFFF"))
    f = QFont("Segoe UI", int(size * 0.55))
    f.setBold(True)
    p.setFont(f)
    p.drawText(grad_rect, Qt.AlignmentFlag.AlignCenter, "L")
    p.end()
    return img


def main() -> None:
    # QGuiApplication örneği oluştur (QPainter.font için zorunlu).
    # sys.argv'ye --platform offscreen ekleyerek penceresiz çalıştırıyoruz.
    if "--platform" not in sys.argv:
        sys.argv.extend(["--platform", "offscreen"])
    _app = QGuiApplication(sys.argv)

    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    config.ICONS_DIR.mkdir(parents=True, exist_ok=True)

    img = make_logo(256)
    img.save(str(config.IMAGES_DIR / "logo.png"))

    pix = QPixmap.fromImage(img)
    pix.save(str(config.ICONS_DIR / "app.png"))
    print(f"Logo üretildi: {config.IMAGES_DIR / 'logo.png'}")
    print(f"Icon üretildi: {config.ICONS_DIR / 'app.png'}")


if __name__ == "__main__":
    main()