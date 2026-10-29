"""Capture a real Windows Terminal window after running the Linux demo."""
from pathlib import Path
import ctypes,subprocess,time
ctypes.windll.user32.SetProcessDPIAware()
import win32gui,win32con,win32api
from PIL import ImageGrab
R=Path(__file__).resolve().parents[1]
linux='/mnt/d/'+R.as_posix()[3:]
title='LAB2-HOURS1-3-VERIFICATION'
cmd="[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); $Host.UI.RawUI.WindowTitle='"+title+"'; wsl -d openEuler -- python3 '"+linux+"/tools/demo_linux.py'"
subprocess.Popen(['powershell.exe','-NoLogo','-NoExit','-Command',cmd],creationflags=subprocess.CREATE_NEW_CONSOLE)
time.sleep(8)
windows=[]
win32gui.EnumWindows(lambda h,p:windows.append(h) if win32gui.IsWindowVisible(h) and title in win32gui.GetWindowText(h) else None,None)
assert windows,'Expected terminal window not found. Existing screenshot has not been replaced.'
h=windows[0]
win32gui.ShowWindow(h,win32con.SW_RESTORE)
win32gui.MoveWindow(h,30,30,1700,850,True)
try:win32gui.SetForegroundWindow(h)
except Exception:pass
time.sleep(1)
win32api.keybd_event(win32con.VK_CONTROL,0,0,0)
for _ in range(4):
    win32api.keybd_event(0xBD,0,0,0)
    win32api.keybd_event(0xBD,0,win32con.KEYEVENTF_KEYUP,0)
win32api.keybd_event(win32con.VK_CONTROL,0,win32con.KEYEVENTF_KEYUP,0)
time.sleep(2)
ImageGrab.grab(bbox=win32gui.GetWindowRect(h)).save(R/'images/实际终端验证截图.png')
print('Captured actual terminal:',title)
