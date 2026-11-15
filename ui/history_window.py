# ============================================================
# Lexora — Geçmiş Sayfası
# ============================================================

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from services.storage_service import STATUS_DISPLAY, get_storage


class HistoryPage(QWidget):
    """Geçmiş kayıtlarını tabloda gösterir."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Çeviri Geçmişi")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        btn_refresh = QPushButton("🔄  Yenile")
        btn_refresh.clicked.connect(self.refresh)
        toolbar.addWidget(btn_refresh)
        btn_clear = QPushButton("🗑️  Tümünü Sil")
        btn_clear.clicked.connect(self._clear_all)
        toolbar.addWidget(btn_clear)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["Tarih", "Dosya", "Kaynak", "Hedef", "Durum", "Çıktı"]
        )
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

        self.refresh()

    def refresh(self) -> None:
        rows = get_storage().get_history(limit=200)
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(r.get("created_at", "")))
            self._table.setItem(i, 1, QTableWidgetItem(r.get("source_file", "")))
            self._table.setItem(i, 2, QTableWidgetItem(r.get("source_lang", "")))
            self._table.setItem(i, 3, QTableWidgetItem(r.get("target_lang", "")))
            st = r.get("status", "")
            self._table.setItem(i, 4, QTableWidgetItem(STATUS_DISPLAY.get(st, st)))
            self._table.setItem(i, 5, QTableWidgetItem(r.get("output_file") or ""))

    def _clear_all(self) -> None:
        if QMessageBox.question(
            self, "Onay", "Tüm geçmiş silinsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            get_storage().clear_history()
            self.refresh()