@echo off
chcp 437 >nul

echo === JARVIS Build ===

call .venv\Scripts\activate.bat

.venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed --name "JARVIS" --add-data "jarvis.html;." --add-data "jarvis_core.py;." --add-data "ready.mp3;." --add-data ".venv\Lib\site-packages\pymorphy2_dicts\data;pymorphy2_dicts\data" --exclude-module "PyQt5" --exclude-module "PyQt6" --hidden-import "jarvis_core" --hidden-import "speech_recognition" --hidden-import "pyttsx3" --hidden-import "pyttsx3.drivers" --hidden-import "pyttsx3.drivers.sapi5" --hidden-import "pyttsx3.drivers.nsss" --hidden-import "pyttsx3.drivers.espeak" --hidden-import "pyautogui" --hidden-import "pyperclip" --hidden-import "playsound3" --hidden-import "rus2num" --hidden-import "winreg" --hidden-import "comtypes" --hidden-import "comtypes.client" --hidden-import "comtypes.server" --hidden-import "queue" --hidden-import "threading" --hidden-import "subprocess" --hidden-import "re" --hidden-import "natasha" --hidden-import "pymorphy2" --hidden-import "pymorphy2_dicts" --hidden-import "yargy" --hidden-import "PySide6" --hidden-import "PySide6.QtCore" --hidden-import "PySide6.QtGui" --hidden-import "PySide6.QtWidgets" --hidden-import "PySide6.QtWebEngineWidgets" --hidden-import "PySide6.QtWebEngineCore" --hidden-import "PySide6.QtWebChannel" --hidden-import "PySide6.QtNetwork" --hidden-import "PySide6.QtPositioning" --hidden-import "PySide6.QtPrintSupport" --hidden-import "PySide6.QtQuick" --hidden-import "PySide6.QtQml" --collect-all "speech_recognition" --collect-all "pyttsx3" --collect-all "pyautogui" --collect-all "pyperclip" --collect-all "playsound3" --collect-all "rus2num" --collect-all "natasha" --collect-all "pymorphy2" --collect-all "pymorphy2_dicts" --collect-all "yargy" --collect-all "comtypes" --collect-all "PySide6" jarvis_app.py

echo.
if errorlevel 1 (
    echo BUILD FAILED.
) else (
    echo BUILD OK. Run: dist\JARVIS\JARVIS.exe
)
pause
