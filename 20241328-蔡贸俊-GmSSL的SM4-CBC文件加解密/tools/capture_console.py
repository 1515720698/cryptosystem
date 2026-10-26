from pathlib import Path
import ctypes
from ctypes import wintypes
import subprocess
import time
from PIL import ImageGrab

root = Path(__file__).resolve().parent.parent
images = root / 'images'
images.mkdir(exist_ok=True)
u = ctypes.windll.user32
u.SetProcessDPIAware()
linux = '/mnt/d/HUAWEI/Documents/' + root.name + '/tools/screenshot_run.py'

for phase, filename in [('1', '01-编译与加解密.png'), ('2', '02-diff正确性验证.png')]:
    marker = root / f'logs/screenshot-run/phase{phase}.done'
    if marker.exists():
        marker.unlink()
    title = f'GmSSL-20241328-Evidence-{phase}'
    command = (
        f"$Host.UI.RawUI.WindowTitle='{title}'; "
        "$Host.UI.RawUI.BackgroundColor='Black'; "
        "$Host.UI.RawUI.ForegroundColor='White'; Clear-Host; "
        f"wsl.exe -d openEuler -- python3 '{linux}' {phase}"
    )
    p = subprocess.Popen(['powershell.exe', '-NoLogo', '-NoProfile', '-NoExit',
                          '-Command', command], creationflags=subprocess.CREATE_NEW_CONSOLE)
    hwnd = None
    for _ in range(90):
        found = []
        callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def callback(h, _):
            text = ctypes.create_unicode_buffer(1024)
            u.GetWindowTextW(h, text, 1024)
            if title in text.value and u.IsWindowVisible(h):
                found.append(h)
            return True
        cb = callback_type(callback)
        u.EnumWindows(cb, 0)
        if found and marker.exists():
            hwnd = found[0]
            break
        time.sleep(1)
    if not hwnd:
        raise RuntimeError('Terminal window unavailable; no screenshot claimed')
    u.ShowWindow(hwnd, 3)
    u.SetForegroundWindow(hwnd)
    time.sleep(1)
    u.keybd_event(0x11, 0, 0, 0)
    u.keybd_event(0x30, 0, 0, 0)
    u.keybd_event(0x30, 0, 2, 0)
    u.keybd_event(0x11, 0, 2, 0)
    # Windows Terminal zoom: fit the entire real session in the window.
    for _ in range(2):
        u.keybd_event(0x11, 0, 0, 0)
        u.keybd_event(0xBD, 0, 0, 0)
        u.keybd_event(0xBD, 0, 2, 0)
        u.keybd_event(0x11, 0, 2, 0)
        time.sleep(0.12)
    time.sleep(3)
    rect = wintypes.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(rect))
    ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom)).save(images / filename)
    print(images / filename)
    u.PostMessageW(hwnd, 0x0010, 0, 0)
    time.sleep(1)
