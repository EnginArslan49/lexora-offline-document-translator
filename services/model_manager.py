# ============================================================
# Lexora — Argos Dil Modeli Yöneticisi
# ============================================================
# Argos Translate dil paketlerini listeler, indirir, siler; pivot
# (ara dil) tespiti yapar.
#
# ÖNEMLİ: Bu modül Argos'u import etmez; yalnızca paket listesini ve
# indirme işlemini yönetir. Çeviri işi translator.py'de.
# Import maliyeti yüksek olduğu için Argos lazy yüklenir.
# ============================================================

from __future__ import annotations

import os
from dataclasses import dataclass

import config
from services.logging_service import get_logger

logger = get_logger(__name__)


# ============================================================
# 1) ARGOS ORTAMINI HAZIRLAMA
# ============================================================

def setup_argos_environment() -> None:
    """
    Argos'un paket dizinini kullanıcı veri dizinine yönlendirir.
    Bu, app.py başlangıcında BİR KEZ çağrılmalıdır.
    PyInstaller onefile modunda sys._MEIPASS salt-okunur olduğu için
    Argos varsayılan konumuna yazamaz; bu env değişkeni çözer.
    """
    config.ARGOS_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    os.environ[config.ARGOS_PACKAGE_DIR_ENV] = str(config.ARGOS_MODEL_DIR)
    logger.info("Argos paket dizini ayarlandı: %s", config.ARGOS_MODEL_DIR)


# ============================================================
# 2) VERİ MODELLERİ
# ============================================================

@dataclass
class PackageInfo:
    """Kurulu bir dil paketinin özeti."""
    from_code: str
    from_name: str
    to_code: str
    to_name: str
    package_path: str | None = None


@dataclass
class PivotPlan:
    """Çeviri yolu planı."""
    is_direct: bool             # doğrudan mı?
    pivot_code: str | None = None  # ara dil kodu (varsa)


# ============================================================
# 3) PAKET LİSTESİ
# ============================================================

def list_installed_packages() -> list[PackageInfo]:
    """
    Yüklü Argos paketlerini listeler.
    Dönen liste: her çift için bir PackageInfo.
    """
    setup_argos_environment()
    try:
        import argostranslate.package as argos_pkg
        packages = argos_pkg.get_installed_packages()
    except Exception as exc:
        logger.warning("Argos paket listesi alınamadı: %s", exc)
        return []

    result: list[PackageInfo] = []
    for pkg in packages:
        try:
            result.append(PackageInfo(
                from_code=pkg.from_code,
                from_name=config.language_name(pkg.from_code),
                to_code=pkg.to_code,
                to_name=config.language_name(pkg.to_code),
                package_path=getattr(pkg, "package_path", None),
            ))
        except Exception:
            continue
    logger.info("Yüklü Argos paketi: %d adet", len(result))
    return result


def list_installed_pairs() -> set[tuple[str, str]]:
    """Yüklü (from_code, to_code) çiftleri kümesi."""
    return {(p.from_code, p.to_code) for p in list_installed_packages()}


def list_supported_languages() -> list[str]:
    """
    Yüklü paketlerin kapsadığı dillerin kodlarını döner.
    Arayüzde hedef dil listesi için kullanılır.
    """
    codes: set[str] = set()
    for pkg in list_installed_packages():
        codes.add(pkg.from_code)
        codes.add(pkg.to_code)
    return sorted(codes)


# ============================================================
# 4) PİVOT (ARA DİL) TESPİTİ
# ============================================================

def resolve_translation_path(from_code: str, to_code: str) -> PivotPlan | None:
    """
    İki dil arasındaki çeviri yolunu belirler.
    - Doğrudan paket varsa -> is_direct=True
    - İngilizce üzerinden pivot varsa -> is_direct=False, pivot='en'
    - Hiçbir yol yoksa -> None
    """
    pairs = list_installed_pairs()

    if (from_code, to_code) in pairs:
        return PivotPlan(is_direct=True)

    # Pivot: from_code -> en -> to_code
    pivot = config.PIVOT_LANGUAGE_CODE
    if from_code == pivot or to_code == pivot:
        return None  # Zaten İngilizce, doğrudan olmalıydı
    if (from_code, pivot) in pairs and (pivot, to_code) in pairs:
        return PivotPlan(is_direct=False, pivot_code=pivot)

    return None


# ============================================================
# 5) İNDİRME (Kullanıcı izniyle çağrılır)
# ============================================================

def update_package_index() -> bool:
    """
    Argos paket indeksini indirir (internet gerekir).
    Kullanıcı yeni dil paketi indirmek istediğinde çağırılır.
    Döner: başarılı mı?
    """
    setup_argos_environment()
    try:
        import argostranslate.package as argos_pkg
        argos_pkg.update_package_index()
        logger.info("Argos paket indeksi güncellendi.")
        return True
    except Exception as exc:
        logger.warning("Argos indeks güncellenemedi: %s", exc)
        return False


def install_package(from_code: str, to_code: str) -> bool:
    """
    İndirilebilir paketler arasından (from,to) çiftini bulur ve kurar.
    Başarı durumunda True döner.
    """
    setup_argos_environment()
    try:
        import argostranslate.package as argos_pkg
        available = argos_pkg.get_available_packages()
        for pkg in available:
            if pkg.from_code == from_code and pkg.to_code == to_code:
                download_path = pkg.download()
                argos_pkg.install_from_path(download_path)
                logger.info("Dil paketi kuruldu: %s -> %s", from_code, to_code)
                return True
        logger.warning("Paket bulunamadı: %s -> %s", from_code, to_code)
        return False
    except Exception as exc:
        logger.exception("Paket kurulumu başarısız: %s", exc)
        return False


def uninstall_package(from_code: str, to_code: str) -> bool:
    """Kurulu bir paketi kaldırır."""
    setup_argos_environment()
    try:
        import argostranslate.package as argos_pkg
        for pkg in argos_pkg.get_installed_packages():
            if pkg.from_code == from_code and pkg.to_code == to_code:
                argos_pkg.uninstall(pkg)
                logger.info("Dil paketi kaldırıldı: %s -> %s", from_code, to_code)
                return True
        return False
    except Exception as exc:
        logger.warning("Paket kaldırma başarısız: %s", exc)
        return False