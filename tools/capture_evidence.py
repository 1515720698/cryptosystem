"""Capture the actual evidence-checking console, not a rendered log graphic."""
from pathlib import Path
import ctypes
import json
import subprocess
import time
import win32con
import win32gui
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'LAB2-GM3000-20241328'
ctypes.windll.user32.SetProcessDPIAware()
command = "$Host.UI.RawUI.WindowTitle='%s'; & python -X utf8 '%s'" % (TITLE, ROOT/'tools/demo_results.py')
process = subprocess.Popen(['powershell.exe', '-NoLogo', '-NoProfile', '-NoExit', '-Command', command],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
time.sleep(6)
windows = []
def callback(hwnd, unused):
    if win32gui.IsWindowVisible(hwnd) and TITLE in win32gui.GetWindowText(hwnd):
        windows.append(hwnd)
win32gui.EnumWindows(callback, None)
if not windows:
    raise RuntimeError('The experimental console window was not found; no screenshot created')
hwnd = windows[-1]
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
win32gui.MoveWindow(hwnd, 30, 30, 1450, 930, True)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(2)
path = ROOT/'images/GM3000三方交叉验证_实际终端.png'
ImageGrab.grab(bbox=win32gui.GetWindowRect(hwnd)).save(path)
(ROOT/'logs/screenshot_metadata.json').write_text(json.dumps({
    'method':'Actual console window screenshot, PIL.ImageGrab', 'title':win32gui.GetWindowText(hwnd),
    'command':command, 'note':'Console rechecks saved hardware results; it does not rerun hardware encryption.'
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(path)
