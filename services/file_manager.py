# ============================================================
# Lexora — Dosya Yöneticisi
# ============================================================
# Güvenli okuma, atomik yazma, çıktı yolu üretimi, geçici dosya yönetimi.
# Kaynak dosya ASLA değiştirilmez; yazma sadece geçici dosya + replace
# ile yapılır.
# ============================================================

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


# ============================================================
# 1) HATA TİPİ
# ============================================================

class FileOperationError(Exception):
    """Dosya işlemi hatası — kullanıcıya Türkçe anahtar taşır."""
    def __init__(self, error_key: str, detail: str = "") -> None:
        super().__init__(detail or error_key)
        self.error_key = error_key
        self.detail = detail


# ============================================================
# 2) OKUMA
# ============================================================

def read_bytes_safe(path: Path) -> bytes:
    """Dosyayı salt-okunur açar, baytları döner. Yazma yapmaz."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as exc:
        raise FileOperationError("file_unreadable", str(exc)) from exc


def read_text_safe(path: Path, encoding: str = "utf-8") -> str:
    """Dosyayı salt-okunur açar, metni döner. Yazma yapmaz."""
    try:
        with open(path, "r", encoding=encoding, newline="") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise FileOperationError("file_unreadable", str(exc)) from exc


# ============================================================
# 3) ÇIKTI YOLU ÜRETİMİ
# ============================================================

def build_output_path(
    source_path: Path,
    output_dir: Path,
    target_lang_code: str,
    overwrite: bool = False,
) -> Path:
    """
    Çıktı dosyası yolunu üretir:
      kaynak.docx + tr  ->  kaynak_TR.docx
    Aynı isimde dosya varsa ve overwrite=False ise '_1', '_2' ekler.

    Hata:
      - output_dir yazılamıyorsa 'permission_denied'
      - kaynak == çıktı ise 'source_file_modified'
    """
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise FileOperationError("permission_denied", str(exc)) from exc

    # Hedef klasör yazılabilir mi?
    if not os.access(output_dir, os.W_OK):
        raise FileOperationError("permission_denied", f"Yazılamaz: {output_dir}")

    base = source_path.stem
    ext = source_path.suffix
    lang_tag = target_lang_code.upper()

    candidate = output_dir / f"{base}_{lang_tag}{ext}"

    # Kaynak ile aynı yol mu? (güvenlik: asla üzerine yazma)
    try:
        if candidate.resolve() == source_path.resolve():
            raise FileOperationError("source_file_modified")
    except OSError:
        pass

    if overwrite or not candidate.exists():
        return candidate

    # Çakışma varsa numaralandır.
    i = 1
    while True:
        candidate = output_dir / f"{base}_{lang_tag}_{i}{ext}"
        if not candidate.exists():
            return candidate
        i += 1


# ============================================================
# 4) ATOMİK YAZMA
# ============================================================

@contextmanager
def atomic_output(final_path: Path) -> Iterator[Path]:
    """
    Atomik yazma bağlamı. Geçici dosya yolu verir; blok başarıyla
    biterse geçici dosya final_path'e taşınır. Hata olursa geçici
    dosya silinir, final_path'e dokunulmaz.

    Kullanım:
        with atomic_output(hedef) as tmp:
            tmp.write_text("içerik")
    """
    final_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_name = f".lexora-{uuid.uuid4().hex}{final_path.suffix}.tmp"
    tmp_path = final_path.parent / tmp_name
    try:
        yield tmp_path
        # Yazma tamamlandıysa atomik olarak devret.
        os.replace(tmp_path, final_path)
    except Exception:
        # Hata olduysa geçici dosyayı temizle.
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise


# ============================================================
# 5) GEÇİCİ DİZİN
# ============================================================

@contextmanager
def temp_workspace() -> Iterator[Path]:
    """
    config.TEMP_DIR altında geçici bir çalışma dizini oluşturur.
    Blok sonunda otomatik temizlenir.
    """
    config.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="lexora-", dir=str(config.TEMP_DIR)))
    try:
        yield workspace
    finally:
        try:
            shutil.rmtree(workspace, ignore_errors=True)
        except OSError:
            pass


# ============================================================
# 6) DOSYA AÇMA (Windows Explorer)
# ============================================================

def open_in_explorer(path: Path) -> None:
    """Verilen klasörü Windows Gezgini'nde açar."""
    if not path.exists():
        raise FileOperationError("file_not_found", str(path))
    try:
        os.startfile(str(path))  # Windows'a özgü
    except OSError as exc:
        raise FileOperationError("unexpected", str(exc)) from exc