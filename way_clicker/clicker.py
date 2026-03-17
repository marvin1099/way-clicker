"""
Clicker engine — QThread click loop.
"""
from __future__ import annotations
import time
from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal
from .backend import ClickBackend

class ClickerThread(QThread):
    started_clicking = Signal()
    stopped_clicking = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backend: ClickBackend | None = None
        self._button  = "left"
        self._delay_ms = 100
        self._running  = False
        self._mutex    = QMutex()

    def configure(self, backend: ClickBackend, button: str, delay_ms: int):
        with QMutexLocker(self._mutex):
            self._backend  = backend
            self._button   = button
            self._delay_ms = delay_ms

    def start_clicking(self):
        if self.isRunning(): return
        with QMutexLocker(self._mutex):
            if self._backend is None:
                self.error.emit("No backend configured."); return
            if not self._backend.available():
                self.error.emit(f"Backend '{self._backend.name()}' not available.\nCheck the tool is installed."); return
            self._running = True
        self.start()

    def stop_clicking(self):
        with QMutexLocker(self._mutex):
            self._running = False

    def toggle(self):
        if self.isRunning(): self.stop_clicking()
        else:                self.start_clicking()

    @property
    def is_clicking(self) -> bool:
        return self.isRunning() and self._running

    def run(self):
        self.started_clicking.emit()
        while True:
            with QMutexLocker(self._mutex):
                if not self._running: break
                backend, button, delay_ms = self._backend, self._button, self._delay_ms
            try:
                backend.click(button)
            except Exception as e:
                self.error.emit(f"Click error: {e}"); break
            # Interruptible sleep
            slept, chunk = 0, 50
            while slept < delay_ms:
                time.sleep(min(chunk, delay_ms - slept) / 1000)
                slept += chunk
                with QMutexLocker(self._mutex):
                    if not self._running: break
            else:
                continue
            break
        with QMutexLocker(self._mutex):
            self._running = False
        self.stopped_clicking.emit()
