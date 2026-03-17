# way-clicker

A Wayland-aware autoclicker with Qt6 GUI. Supports Linux (Wayland/X11), macOS, and Windows. Drop-in replacement for xclicker on KDE Wayland.

AI was used a lot, human code checking and testing was performed.  
This is mosly a tool I wanted to have, but I'm sharing it becalse why not. 

## Dependencies

```bash
# Arch Linux
sudo pacman -S python pipx git
paru -S dotool

# Debian / Ubuntu
sudo apt install python3 python3-pip pipx git
# Build dotool from source (see below)

# Fedora
sudo dnf install python3 python3-pip pipx git
# Build dotool from source (see below)

# macOS
brew install python3 pipx git

# Windows
winget install -e --id Git.Git
# Check available versions: winget search Python.Python
winget install Python.Python.3.13  # use newest version
pip install pipx
```

### Building dotool from source

If you cant find a binary on your Debian or Fedora system (I didn't) and use wayland you will need to build dotool.

Required: gcc, go, libxkbcommon-dev, scdoc
```bash
git clone https://github.com/alexmajoor/dotool
cd dotool
./build.sh && sudo ./build.sh install
sudo udevadm control --reload && sudo udevadm trigger
```

## Install

```bash
# Clone from codeberg (or mirror)
git clone https://codeberg.org/marvin1099/way-clicker
cd way-clicker
pipx install .
```

Or from GitHub mirror:
```bash
git clone https://github.com/marvin1099/way-clicker
cd way-clicker
pipx install .
```

### Optional: pyautogui (X11 / Windows / macOS)
This is needed for X11/macOS/Windows support.
```bash
pipx install .[x11]
```

## Usage

```bash
way-clicker              # Launch GUI
way-clicker --toggle     # Toggle clicking
way-clicker --start      # Start clicking
way-clicker --stop       # Stop clicking
way-clicker --quit       # Quit GUI
way-clicker --guicheck   # Check if GUI running
way-clicker --nogui      # Never start GUI (for remote commands)
way-clicker --hidden     # Start GUI hidden
```

### CLI Behavior

- Running `way-clicker` without arguments launches the GUI. Press `Ctrl+C` (in terminal) to close, use `Ctrl+Q` in GUI.
- Remote commands (`--toggle`, `--start`, `--stop`, `--quit`) will start the GUI if not running.
- Use `--nogui` to only interact with an existing GUI instance, exit if not running.
- Use `--guicheck` to only perform the action if the GUI was already running.
- Use `--hidden` to start GUI hidden, or toggle visibility if GUI is already running.
- Use `--guicheck` alone to see if the clicker gui is running (works when hidden as well).

### Examples

```bash
way-clicker --guicheck        # Check if GUI is running
way-clicker --nogui --toggle  # Toggle only if GUI is already running
way-clicker --hidden          # Start GUI hidden (this is fully invisible, no tray, use --hidden again to show)
```

## KDE Global Shortcut

System Settings → Shortcuts → Custom Shortcuts, add:
- Action: `way-clicker --guicheck --toggle`

**Note:** Works on any system with a way to set commands to shortcuts globaly.  
**Note:** If you have a other system search online how to add a shortcut to a progamm or script.

**Also:** This will start the GUI if not running (skip via --nogui), and the needs an addional shortcut trigger to start (skip by removing --guicheck). 

### Screenshots
[<img src="https://github.com/user-attachments/assets/01879d77-80dd-4e32-8e70-c5d980098787" alt="Screenshot_20260317_194928" width="44%">](
https://github.com/user-attachments/assets/01879d77-80dd-4e32-8e70-c5d980098787) [<img src="https://github.com/user-attachments/assets/f66c0108-e1c8-424e-b908-ccdfb256c311" alt="Screenshot_20260317_195408" width="30%">](
https://github.com/user-attachments/assets/f66c0108-e1c8-424e-b908-ccdfb256c311)

## Config File

Saved to `~/.config/way-clicker/way-clicker.conf` (INI format via Qt QSettings).

Edit via **File → Settings** in the GUI, or directly in the file.

### Backends

| Setting     | Behaviour                                 |
|-------------|-------------------------------------------|
| `auto`      | runner on Wayland, pyautogui on X11/other |
| `runner`    | Always use runner (custom command)        |
| `pyautogui` | Always use pyautogui                      |

### Default Configuration

The runner backend executes a command with args and/or stdin:

```ini
[General]
backend=auto
button=left
delay_ms=100
runner_command=dotoolc
runner_args=
runner_stdin=click {button}
runner_buttonmap=left:left, middle:middle, right:right
```

So its setup for dotool by default.

#### Runner Tool Examples

| Tool    | runner_command | runner_args    | runner_stdin   | runner_buttonmap                       |
|---------|----------------|----------------|----------------|----------------------------------------|
| dotool  | dotoolc        | (empty)        | click {button} | left:left, middle:middle, right: right |
| ydotool | ydotool        | click {button} | (empty)        | left:0xC0, middle:0xC2, right:0xC1     |
| xdotool | xdotool        | click {button} | (empty)        | left:1, middle:2, right:3              |

- Use `{button}` placeholder in args or stdin
- buttonmap translates left/middle/right to tool-specific values
- Empty args/stdin means that input method won't be used

**Note:** dotoold must be running in the background for clicking to work. Start it with:
```bash
dotoold &
```
Consider adding it to your autostart.

**Important:** If you want to use ydotool it also requires a daemon running. See the [ydotool GitHub](https://github.com/yzhang-gh/ydotool) for setup instructions.
