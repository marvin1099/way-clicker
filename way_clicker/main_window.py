"""
Main window for Way-Clicker.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .backend import make_backend
from .clicker import ClickerThread
from .config import Config
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, config: Config, clicker: ClickerThread):
        super().__init__()
        self._config = config
        self._clicker = clicker

        self.setWindowTitle("Way-Clicker")
        self.setMinimumWidth(320)

        self._build_menu()
        self._build_ui()
        self._connect_signals()
        self._apply_config()
        self._update_status(running=False)

    # ── Menu ─────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        settings_act = QAction("Settings…", self)
        settings_act.triggered.connect(self._open_settings)
        file_menu.addAction(settings_act)

        file_menu.addSeparator()

        quit_act = QAction("Quit", self)
        quit_act.setShortcut("Ctrl+Q")
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Status display ───────────────────────────────────────────────────
        status_box = QGroupBox("Status")
        status_layout = QVBoxLayout(status_box)
        self._status_label = QLineEdit("Stopped")
        self._status_label.setReadOnly(True)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 4px;"
        )
        status_layout.addWidget(self._status_label)
        root.addWidget(status_box)

        # ── Click settings ───────────────────────────────────────────────────
        settings_box = QGroupBox("Click Settings")
        settings_form = QVBoxLayout(settings_box)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addWidget(QLabel("Mouse Button:"))
        self._button_combo = QComboBox()
        self._button_combo.addItem("Left",   "left")
        self._button_combo.addItem("Middle", "middle")
        self._button_combo.addItem("Right",  "right")
        self._button_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        btn_row.addWidget(self._button_combo)
        settings_form.addLayout(btn_row)

        # Delay row
        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("Delay (ms):"))
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(10, 60000)
        self._delay_spin.setSingleStep(10)
        self._delay_spin.setSuffix(" ms")
        self._delay_spin.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        delay_row.addWidget(self._delay_spin)
        settings_form.addLayout(delay_row)

        root.addWidget(settings_box)

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_box = QGroupBox()
        btn_layout = QHBoxLayout(btn_box)
        btn_layout.setSpacing(8)

        self._start_btn  = QPushButton("Start")
        self._stop_btn   = QPushButton("Stop")
        self._toggle_btn = QPushButton("Toggle")
        self._quit_btn   = QPushButton("Quit")

        self._start_btn.setMinimumHeight(36)
        self._stop_btn.setMinimumHeight(36)
        self._toggle_btn.setMinimumHeight(36)
        self._quit_btn.setMinimumHeight(36)

        self._start_btn.setObjectName("startBtn")
        self._stop_btn.setObjectName("stopBtn")

        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._stop_btn)
        btn_layout.addWidget(self._toggle_btn)
        btn_layout.addWidget(self._quit_btn)

        root.addWidget(btn_box)

    def _connect_signals(self):
        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self._on_stop)
        self._toggle_btn.clicked.connect(self._on_toggle)
        self._quit_btn.clicked.connect(self.close)

        self._clicker.started_clicking.connect(lambda: self._update_status(True))
        self._clicker.stopped_clicking.connect(lambda: self._update_status(False))
        self._clicker.error.connect(self._on_error)

        # Save delay + button to config when changed
        self._delay_spin.valueChanged.connect(self._on_delay_changed)
        self._button_combo.currentIndexChanged.connect(self._on_button_changed)

    # ── Config ───────────────────────────────────────────────────────────────

    def _apply_config(self):
        """Load config values into UI and clicker."""
        idx = self._button_combo.findData(self._config.button)
        if idx >= 0:
            self._button_combo.setCurrentIndex(idx)
        self._delay_spin.setValue(self._config.delay_ms)
        self._refresh_backend()

    def _refresh_backend(self):
        backend = make_backend(self._config)
        self._clicker.configure(
            backend,
            self._config.button,
            self._config.delay_ms,
        )

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_start(self):
        self._save_ui_to_config()
        self._refresh_backend()
        self._clicker.start_clicking()

    def _on_stop(self):
        self._clicker.stop_clicking()

    def _on_toggle(self):
        if self._clicker.is_clicking:
            self._on_stop()
        else:
            self._on_start()

    def _on_delay_changed(self, value: int):
        self._config.delay_ms = value
        self._config.sync()

    def _on_button_changed(self):
        self._config.button = self._button_combo.currentData()
        self._config.sync()

    def _on_error(self, msg: str):
        QMessageBox.critical(self, "Way-Clicker Error", msg)

    def _save_ui_to_config(self):
        self._config.button = self._button_combo.currentData()
        self._config.delay_ms = self._delay_spin.value()
        self._config.sync()

    def _update_status(self, running: bool):
        if running:
            btn  = self._button_combo.currentText()
            dms  = self._delay_spin.value()
            self._status_label.setText(f"● Running  [{btn} @ {dms}ms]")
            self._status_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; padding: 4px; color: green;"
            )
        else:
            self._status_label.setText("■ Stopped")
            self._status_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; padding: 4px; color: red;"
            )
        # Update button states
        self._start_btn.setEnabled(not running)
        self._stop_btn.setEnabled(running)

    def _open_settings(self):
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            self._refresh_backend()

    # ── IPC commands (called from main via signal) ────────────────────────────

    def handle_ipc_command(self, cmd: str):
        cmd = cmd.strip().lower()
        if cmd == "toggle":
            self._on_toggle()
        elif cmd == "start":
            self._on_start()
        elif cmd == "stop":
            self._on_stop()
        elif cmd == "quit":
            self.show()
            self.raise_()
            self.activateWindow()
            self.close()
        elif cmd == "hidden":
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    # ── Close ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._clicker.stop_clicking()
        self._clicker.wait(2000)
        super().closeEvent(event)
