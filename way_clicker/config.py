"""
Configuration management using QSettings (INI format).
Stored at ~/.config/way-clicker/way-clicker.conf
"""
from PySide6.QtCore import QSettings

APP_ORG  = "way-clicker"
APP_NAME = "way-clicker"

class Config:
    DEFAULTS = {
        "backend":           "auto",
        "button":            "left",
        "delay_ms":         100,
        "runner_command":   "dotoolc",
        "runner_args":       "",
        "runner_stdin":      "click {button}",
        "runner_buttonmap":  "left:left, middle:middle, right:right",
    }

    def __init__(self):
        self._s = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            APP_ORG, APP_NAME,
        )
        for key, val in self.DEFAULTS.items():
            if not self._s.contains(key):
                self._s.setValue(key, val)
        self._validate_runner_config()
        self._s.sync()

    def _validate_runner_config(self):
        runner_keys = ["runner_command", "runner_args", "runner_stdin", "runner_buttonmap"]
        for key in runner_keys:
            if not self._s.contains(key):
                self._s.setValue(key, self.DEFAULTS[key])
        if self._s.value("wayland_command"):
            self._s.remove("wayland_command")

    def _parse_buttonmap(self) -> dict:
        raw = self._s.value("runner_buttonmap", self.DEFAULTS["runner_buttonmap"])
        mapping = {}
        for pair in raw.split(","):
            if ":" in pair:
                k, v = pair.split(":", 1)
                mapping[k.strip()] = v.strip()
        return mapping

    @property
    def button(self) -> str:
        return self._s.value("button", self.DEFAULTS["button"])
    @button.setter
    def button(self, v: str): self._s.setValue("button", v)

    @property
    def delay_ms(self) -> int:
        return int(self._s.value("delay_ms", self.DEFAULTS["delay_ms"]))
    @delay_ms.setter
    def delay_ms(self, v: int): self._s.setValue("delay_ms", int(v))

    @property
    def backend(self) -> str:
        return self._s.value("backend", self.DEFAULTS["backend"])
    @backend.setter
    def backend(self, v: str): self._s.setValue("backend", v)

    @property
    def runner_command(self) -> str:
        return self._s.value("runner_command", self.DEFAULTS["runner_command"])
    @runner_command.setter
    def runner_command(self, v: str): self._s.setValue("runner_command", v)

    @property
    def runner_args(self) -> str:
        return self._s.value("runner_args", self.DEFAULTS["runner_args"])
    @runner_args.setter
    def runner_args(self, v: str): self._s.setValue("runner_args", v)

    @property
    def runner_stdin(self) -> str:
        return self._s.value("runner_stdin", self.DEFAULTS["runner_stdin"])
    @runner_stdin.setter
    def runner_stdin(self, v: str): self._s.setValue("runner_stdin", v)

    @property
    def runner_buttonmap(self) -> str:
        return self._s.value("runner_buttonmap", self.DEFAULTS["runner_buttonmap"])
    @runner_buttonmap.setter
    def runner_buttonmap(self, v: str): self._s.setValue("runner_buttonmap", v)

    def runner_mapped_button(self, button: str) -> str:
        return self._parse_buttonmap().get(button, button)

    def sync(self): self._s.sync()
    def file_path(self) -> str: return self._s.fileName()
