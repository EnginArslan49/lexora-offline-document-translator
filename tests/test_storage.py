# ============================================================
# Lexora — Storage Testleri
# ============================================================
from pathlib import Path

from services.storage_service import (
    STATUS_COMPLETED, StorageService, _atomic_write_json, _safe_load_json,
)


def test_history_crud(tmp_path: Path) -> None:
    s = StorageService(
        settings_path=tmp_path / "s.json",
        history_path=tmp_path / "h.json",
    )
    eid = s.add_history_entry("a.docx", "en", "tr", STATUS_COMPLETED)
    assert eid == 1
    assert s.get_history_count() == 1
    assert s.get_history_entry(1)["source_file"] == "a.docx"
    s.delete_history_entry(1)
    assert s.get_history_count() == 0


def test_setting_persist(tmp_path: Path) -> None:
    sp, hp = tmp_path / "s.json", tmp_path / "h.json"
    s1 = StorageService(settings_path=sp, history_path=hp)
    s1.set_setting("theme", "light")
    # Yeni süreç simülasyonu:
    s2 = StorageService(settings_path=sp, history_path=hp)
    assert s2.get_setting("theme") == "light"


def test_history_trim(tmp_path: Path, monkeypatch) -> None:
    import config
    monkeypatch.setattr(config, "MAX_HISTORY_ENTRIES", 3)
    s = StorageService(
        settings_path=tmp_path / "s.json",
        history_path=tmp_path / "h.json",
    )
    for i in range(5):
        s.add_history_entry(f"f{i}.txt", "en", "tr")
    assert s.get_history_count() == 3


def test_corrupt_json_recovery(tmp_path: Path) -> None:
    bad = tmp_path / "s.json"
    bad.write_text("bozuk {{{", encoding="utf-8")
    s = StorageService(settings_path=bad, history_path=tmp_path / "h.json")
    assert s.get_setting("theme", "yok") == "yok"
    # Yedek dosya oluştu mu?
    assert any(p.name.startswith("s.json.corrupt-") for p in tmp_path.iterdir())