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
for phase, name in [('1', '01-密钥生成与编译'), ('2', '02-加解密与diff验证'), ('3', '03-签名验签与篡改验证')]:
    marker = root / f'logs/screenshot-run/phase{phase}.done'
    if marker.exists():
        marker.unlink()
    title = f'SM2-20241328-Evidence-{phase}'
    command = (f"$Host.UI.RawUI.WindowTitle='{title}'; "
        "$Host.UI.RawUI.BackgroundColor='Black'; "
        "$Host.UI.RawUI.ForegroundColor='White'; Clear-Host; "
        f"wsl.exe -d openEuler -- python3 '{linux}' {phase}")
    p = subprocess.Popen(['powershell.exe', '-NoLogo', '-NoProfile', '-NoExit', '-Command', command],
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    hwnd = None
    for _ in range(90):
        found = []
        cbtype = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def callback(h, _):
            text = ctypes.create_unicode_buffer(1024)
            u.GetWindowTextW(h, text, 1024)
            if title in text.value and u.IsWindowVisible(h):
                found.append(h)
            return True
        cb = cbtype(callback)
        u.EnumWindows(cb, 0)
        if found and marker.exists():
            hwnd = found[0]
            break
        time.sleep(1)
    if not hwnd:
        raise RuntimeError('Real terminal capture unavailable')
    u.ShowWindow(hwnd, 3)
    u.SetForegroundWindow(hwnd)
    time.sleep(1)
    def key(vk):
        u.keybd_event(0x11, 0, 0, 0)
        u.keybd_event(vk, 0, 0, 0)
        u.keybd_event(vk, 0, 2, 0)
        u.keybd_event(0x11, 0, 2, 0)
    key(0x30)
    for _ in range(2):
        key(0xBD)
        time.sleep(.15)
    time.sleep(2)
    rect = wintypes.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(rect))
    shot = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    shot.save(images / (name + '.png'))
    # Preserve the full raw window; crop only unused area for report display.
    width = shot.width if phase == '1' else min(2200, shot.width)
    shot.crop((0, 0, width, min(1350, shot.height))).save(images / (name + '-展示.png'))
    print(images / (name + '.png'))
    u.PostMessageW(hwnd, 0x0010, 0, 0)
    time.sleep(1)
