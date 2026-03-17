"""Settings dialog."""
from __future__ import annotations
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QSpinBox)
from .backend import session_info
from .config import Config

class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle("Way-Clicker — Settings")
        self.setMinimumWidth(480)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        backend_box = QGroupBox("Click Backend")
        form = QFormLayout(backend_box)

        self._backend_combo = QComboBox()
        self._backend_combo.addItem("Auto (detect session)", "auto")
        self._backend_combo.addItem("Runner (command)", "runner")
        self._backend_combo.addItem("pyautogui (X11/Win/Mac)", "pyautogui")
        self._backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        form.addRow("Backend:", self._backend_combo)

        self._cmd_edit = QLineEdit()
        self._cmd_edit.setPlaceholderText("dotoolc")
        form.addRow("Command:", self._cmd_edit)

        self._args_edit = QLineEdit()
        self._args_edit.setPlaceholderText("click {button}")
        form.addRow("Args:", self._args_edit)

        self._stdin_edit = QLineEdit()
        self._stdin_edit.setPlaceholderText("click {button}")
        form.addRow("Stdin:", self._stdin_edit)

        self._buttonmap_edit = QLineEdit()
        self._buttonmap_edit.setPlaceholderText("left:left, middle:middle, right:right")
        form.addRow("Button map:", self._buttonmap_edit)

        help_lbl = QLabel(
            "Runner executes a command with args and/or stdin.<br>"
            "Use <b>{button}</b> as placeholder (left/middle/right).<br><br>"
            "<b>dotool (default):</b> stdin=<tt>click {button}</tt><br>"
            "<b>ydotool:</b> args=<tt>click {button}</tt>, buttonmap=<tt>left:0xC0, middle:0xC2, right:0xC1</tt><br>"
            "<b>xdotool:</b> args=<tt>click {button}</tt>, buttonmap=<tt>left:1, middle:2, right:3</tt>"
        )
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet("color: gray; font-size: 11px;")
        form.addRow("", help_lbl)
        layout.addWidget(backend_box)

        delay_box = QGroupBox("Click Settings")
        delay_form = QFormLayout(delay_box)
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(1, 10000)
        self._delay_spin.setSuffix(" ms")
        delay_form.addRow("Delay:", self._delay_spin)
        layout.addWidget(delay_box)

        info_box = QGroupBox("Session Info")
        info_layout = QVBoxLayout(info_box)
        info = session_info()
        text = (
            f"OS: {info['os']}\n"
            f"Session type: {info['xdg_session']}\n"
            f"Wayland: {'yes (' + info['wayland_display'] + ')' if info['wayland'] else 'no'}\n"
            f"pyautogui available: {'yes' if info['pyautogui'] else 'no'}\n"
            f"Config: {self._config.file_path()}"
        )
        lbl = QLabel(text)
        lbl.setStyleSheet("font-family: monospace; font-size: 11px;")
        lbl.setWordWrap(True)
        info_layout.addWidget(lbl)
        layout.addWidget(info_box)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        idx = self._backend_combo.findData(self._config.backend)
        if idx >= 0: self._backend_combo.setCurrentIndex(idx)
        self._cmd_edit.setText(self._config.runner_command)
        self._args_edit.setText(self._config.runner_args)
        self._stdin_edit.setText(self._config.runner_stdin)
        self._buttonmap_edit.setText(self._config.runner_buttonmap)
        self._delay_spin.setValue(self._config.delay_ms)
        self._on_backend_changed()

    def _on_backend_changed(self):
        is_runner = self._backend_combo.currentData() in ("auto", "runner")
        self._cmd_edit.setEnabled(is_runner)
        self._args_edit.setEnabled(is_runner)
        self._stdin_edit.setEnabled(is_runner)
        self._buttonmap_edit.setEnabled(is_runner)

    def _save(self):
        self._config.backend = self._backend_combo.currentData()
        self._config.runner_command = self._cmd_edit.text().strip() or "dotool"
        self._config.runner_args = self._args_edit.text().strip()
        self._config.runner_stdin = self._stdin_edit.text().strip()
        self._config.runner_buttonmap = self._buttonmap_edit.text().strip() or "left:left, middle:middle, right:right"
        self._config.delay_ms = self._delay_spin.value()
        self._config.sync()
        self.accept()
