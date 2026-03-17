"""
IPC server — Unix socket, receives: toggle | start | stop | quit
"""
from __future__ import annotations
import os, socket, threading
from PySide6.QtCore import QThread, Signal

SOCKET_PATH = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "way-clicker.sock")

class IpcServer(QThread):
    command_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_event = threading.Event()
        self._sock = None

    def run(self):
        try: os.unlink(SOCKET_PATH)
        except OSError: pass
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.bind(SOCKET_PATH)
        self._sock.listen(5)
        self._sock.settimeout(1.0)
        while not self._stop_event.is_set():
            try:
                conn, _ = self._sock.accept()
            except socket.timeout: continue
            except OSError: break
            try:
                data = conn.recv(64).decode().strip()
                if data: self.command_received.emit(data)
            except OSError: pass
            finally: conn.close()
        self._cleanup()

    def stop(self):
        self._stop_event.set()
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(SOCKET_PATH); s.close()
        except OSError: pass
        self.wait()
        self._cleanup()

    def _cleanup(self):
        if self._sock:
            try: self._sock.close()
            except OSError: pass
            self._sock = None
        try: os.unlink(SOCKET_PATH)
        except OSError: pass

def send_command(cmd: str) -> bool:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(2.0); s.connect(SOCKET_PATH)
        s.sendall(cmd.encode()); s.close(); return True
    except OSError: return False

def is_running() -> bool:
    if not os.path.exists(SOCKET_PATH):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(SOCKET_PATH)
        s.close()
        return True
    except OSError:
        return False
