"""
Click backends.

RunnerBackend  - runs a command with args and/or stdin.
PyAutoGuiBackend - uses pyautogui (X11/Windows/macOS).
AutoBackend     - picks the right one automatically.
"""
from __future__ import annotations
import os, platform, shutil, subprocess
from abc import ABC, abstractmethod

def _is_wayland() -> bool:
    return (os.environ.get("WAYLAND_DISPLAY") is not None
            or os.environ.get("XDG_SESSION_TYPE","").lower() == "wayland")

def _pyautogui_available() -> bool:
    try:
        import pyautogui; return True
    except ImportError:
        return False

def _parse_buttonmap(raw: str) -> dict:
    mapping = {}
    for pair in raw.split(","):
        if ":" in pair:
            k, v = pair.split(":", 1)
            mapping[k.strip()] = v.strip()
    return mapping

class ClickBackend(ABC):
    @abstractmethod
    def click(self, button: str) -> None: ...
    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def available(self) -> bool: ...

class RunnerBackend(ClickBackend):
    def __init__(self, command: str, args: str = "", stdin: str = "", buttonmap: str = ""):
        self._command = command
        self._args = args
        self._stdin = stdin
        self._buttonmap = _parse_buttonmap(buttonmap)

    @property
    def command(self): return self._command
    @command.setter
    def command(self, v): self._command = v

    def _map_button(self, button: str) -> str:
        return self._buttonmap.get(button, button)

    def name(self): return f"runner ({self._command})"

    def available(self):
        return shutil.which(self._command.split()[0]) is not None

    def click(self, button: str):
        mapped = self._map_button(button)
        cmd = self._command
        stdin_data = None

        if self._stdin:
            stdin_data = self._stdin.replace("{button}", mapped)
        if self._args:
            arg_str = self._args.replace("{button}", mapped)
            cmd = f"{cmd} {arg_str}"

        if stdin_data:
            subprocess.run(cmd.split(), input=stdin_data + "\n", text=True, check=False)
        elif self._args or "{button}" in cmd:
            subprocess.run(cmd.replace("{button}", mapped), shell=True, check=False)
        else:
            subprocess.run(cmd.split(), check=False)

class PyAutoGuiBackend(ClickBackend):
    def name(self): return "pyautogui"
    def available(self): return _pyautogui_available()
    def click(self, button: str):
        import pyautogui
        pyautogui.click(button=button)

class AutoBackend(ClickBackend):
    def __init__(self, runner_command: str, runner_args: str = "", runner_stdin: str = "", runner_buttonmap: str = ""):
        if _is_wayland():
            self._backend = RunnerBackend(runner_command, runner_args, runner_stdin, runner_buttonmap)
        elif _pyautogui_available():
            self._backend = PyAutoGuiBackend()
        else:
            self._backend = RunnerBackend(runner_command, runner_args, runner_stdin, runner_buttonmap)
    def name(self): return f"auto → {self._backend.name()}"
    def available(self): return self._backend.available()
    def click(self, button: str): self._backend.click(button)
    @property
    def resolved(self): return self._backend

def make_backend(config) -> ClickBackend:
    backend = config.backend
    if backend == "pyautogui":
        return PyAutoGuiBackend()
    elif backend == "runner":
        return RunnerBackend(
            config.runner_command,
            config.runner_args,
            config.runner_stdin,
            config.runner_buttonmap
        )
    else:
        return AutoBackend(
            config.runner_command,
            config.runner_args,
            config.runner_stdin,
            config.runner_buttonmap
        )

def session_info() -> dict:
    return {
        "os":             platform.system(),
        "wayland":        _is_wayland(),
        "wayland_display":os.environ.get("WAYLAND_DISPLAY",""),
        "xdg_session":    os.environ.get("XDG_SESSION_TYPE","unknown"),
        "pyautogui":      _pyautogui_available(),
    }
