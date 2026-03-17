#!/usr/bin/env python3
"""
way-clicker — entry point.

Usage:
    way-clicker              Launch GUI
    way-clicker --toggle     Toggle clicking
    way-clicker --start      Start clicking
    way-clicker --stop       Stop clicking
    way-clicker --quit       Quit GUI
    way-clicker --guicheck   Check if GUI running
    way-clicker --nogui      Never start GUI
    way-clicker --hidden     Toggle GUI visibility
    way-clicker --help       Show help
"""

import sys
import subprocess
import time
import signal


def main():
    from way_clicker.ipc import is_running, send_command

    args = sys.argv[1:]

    if "--help" in args:
        print(__doc__)
        sys.exit(0)

    nogui = "--nogui" in args
    guicheck = "--guicheck" in args
    hidden = "--hidden" in args

    remote_cmds = {"--toggle", "--start", "--stop", "--quit"}

    remote_cmd = None
    for arg in args:
        if arg in remote_cmds:
            remote_cmd = arg.lstrip("-")
            break

    if guicheck and not remote_cmd and not hidden:
        if is_running():
            print("way-clicker: running")
            sys.exit(0)
        else:
            print("way-clicker: stopped")
            sys.exit(1)

    was_running = is_running()

    send_hidden = hidden and was_running # if we need to send over hidden flag

    if remote_cmd or send_hidden:
        if not was_running:
            if nogui:
                print("way-clicker: no running instance found.", file=sys.stderr)
                sys.exit(1)
            execute = [sys.executable, "-m", "way_clicker"]
            if hidden:
                execute.append("--hidden")
            proc = subprocess.Popen(
                execute,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            started_in_background = True
            for _ in range(20):
                time.sleep(0.25)
                if is_running():
                    break
            if not is_running():
                print("way-clicker: failed to start GUI.", file=sys.stderr)
                sys.exit(1)
            if guicheck:
                sys.exit(0)
            if started_in_background:
                print("way-clicker: running GUI in the background")
        ok = 0
        if remote_cmd:
            ok = send_command(remote_cmd)
        if send_hidden:
            ok = send_command("hidden") or ok

        sys.exit(0 if ok else 1)

    if not was_running and hidden:
        if nogui:
            print("way-clicker: no running instance found.", file=sys.stderr)
            sys.exit(1)
    elif is_running():
        print("way-clicker: already running.", file=sys.stderr)
        sys.exit(1)

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication

    QCoreApplication.setOrganizationName("way-clicker")
    QCoreApplication.setApplicationName("way-clicker")

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    from way_clicker.config import Config
    from way_clicker.clicker import ClickerThread
    from way_clicker.ipc import IpcServer
    from way_clicker.main_window import MainWindow

    config = Config()
    clicker = ClickerThread()
    window = MainWindow(config, clicker)

    ipc = IpcServer()
    ipc.command_received.connect(window.handle_ipc_command)
    ipc.start()

    quit_state = [False]

    def handle_sigint(signum, frame):
        quit_state[0] = True

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)

    def check_quit():
        if quit_state[0]:
            clicker.stop_clicking()
            window.close()
            app.quit()

    quit_timer = QTimer()
    quit_timer.timeout.connect(check_quit)
    quit_timer.start(100)

    if guicheck:
        window.show()
    elif not hidden:
        window.show()

    exit_code = app.exec()

    ipc.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
