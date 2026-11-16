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
    margin = size * 0.1
    grad_rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)

    # Dış beyaz çerçeve
    p.setBrush(QColor("#FFFFFF"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(0, 0, size, size), r + margin, r + margin)

    # Gradyan iç zemin
    g = QLinearGradient(grad_rect.topLeft(), grad_rect.bottomRight())
    g.setColorAt(0.0, QColor(config.BRAND_COLORS["primary_blue"]))
    g.setColorAt(0.5, QColor(config.BRAND_COLORS["cyan"]))
    g.setColorAt(1.0, QColor(config.BRAND_COLORS["purple"]))
    p.setBrush(g)
    p.drawRoundedRect(grad_rect, r, r)

    # "L" harfi
    p.setPen(QColor("#FFFFFF"))
    f = QFont("Segoe UI", int(size * 0.4))
    f.setBold(True)
    p.setFont(f)
    p.drawText(grad_rect, Qt.AlignmentFlag.AlignCenter, "L")
    p.end()
    return img


def main() -> None:
    import sys
    if "--platform" not in sys.argv:
        sys.argv.extend(["--platform", "offscreen"])
    from PySide6.QtGui import QGuiApplication
    _app = QGuiApplication(sys.argv)

    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    config.ICONS_DIR.mkdir(parents=True, exist_ok=True)

    # PNG üret
    img = make_logo(256)
    img.save(str(config.IMAGES_DIR / "logo.png"))

    # Pillow ile ICO üret (PyInstaller için zorunlu)
    try:
        from PIL import Image
        # Qt QImage'i Pillow Image'a çevir
        img.save(str(config.ICONS_DIR / "app.png"))
        pil_img = Image.open(str(config.ICONS_DIR / "app.png"))
        # Windows için gerekli çoklu boyutlar
        icon_sizes = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]
        pil_img.save(str(config.ICONS_DIR / "app.ico"), format="ICO", sizes=icon_sizes)
        print(f"ICO üretildi: {config.ICONS_DIR / 'app.ico'}")
    except ImportError:
        print("UYARI: Pillow yüklü değil. ICO üretilemedi. `pip install pillow` çalıştırın.")

    print(f"Logo üretildi: {config.IMAGES_DIR / 'logo.png'}")


if __name__ == "__main__":
    main()