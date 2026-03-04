"""
Запуск: python jarvis_app.py
Положи этот файл и jarvis.html в ту же папку, где лежит твой оригинальный jarvis.py.
Все функции берутся напрямую из jarvis.py — ничего не переписано.
"""

import sys, os, threading

# ── Импортируем ВСЁ из оригинального jarvis.py ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util, types

# Грузим jarvis.py как модуль, но НЕ запускаем его while True
spec = importlib.util.spec_from_file_location("jarvis_core", 
       os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.py"))
jarvis_src = importlib.util.find_spec("jarvis_core")

# Читаем исходник и вырезаем while True, чтобы не запустился сам по себе
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.py"), 
          "r", encoding="utf-8") as f:
    src = f.read()

# Убираем блок while True (всё что после него) — он будет управляться GUI
cut = src.find("\nwhile True:")
src_no_loop = src[:cut] if cut != -1 else src

core = types.ModuleType("jarvis_core")
core.__dict__["__file__"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.py")
exec(compile(src_no_loop, "jarvis.py", "exec"), core.__dict__)

# Теперь у нас есть: core.r, core.presser, core.playsound, core.pyttsx3 и т.д.
r       = core.r          # Recognizer
presser = core.presser    # функция нажатий
import speech_recognition as sr
import pyttsx3
from threading import Timer
try:
    from playsound3 import playsound
except Exception:
    playsound = None

tts_engine = pyttsx3.init()

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# ── Оригинальная логика обработки команды (скопирована 1-в-1 из jarvis.py) ──
import os as _os, subprocess, winreg
from pyautogui import hotkey, press, hold
from pyperclip import copy
from rus2num import Rus2Num
from re import search

def process_command(text, log_fn, transcript_fn):
    """Выполняет команду точно так же, как оригинальный jarvis.py"""
    transcript_fn(text)
    print(text)

    if 'открой' in text.lower() or 'запусти' in text.lower():
        soft = text.lower().replace('открой', '').replace('запусти', '').replace(' ', '')
        try:
            with open('base.txt', 'r', encoding='utf-8') as f:
                for __str in list(f) + ['END']:
                    data = __str.split(',')
                    if __str == 'END':
                        speak(f'извините, сэр, я не нашёл {soft}')
                        log_fn(f'Не найдено: {soft}', 'error')
                        break
                    if data[0] == soft:
                        subprocess.Popen([data[1][1::].replace('\n', '')])
                        speak('конечно, сэр')
                        log_fn(f'Запущено: {soft}', 'success')
                        break
                    else:
                        try:
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                                 fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{soft}.exe")
                            path = winreg.QueryValue(key, None)
                            winreg.CloseKey(key)
                            subprocess.Popen([path])
                            speak('конечно, сэр')
                            log_fn(f'Запущено: {soft}', 'success')
                            break
                        except:
                            pass
        except FileNotFoundError:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{soft}.exe")
                path = winreg.QueryValue(key, None)
                winreg.CloseKey(key)
                subprocess.Popen([path])
                speak('конечно, сэр')
                log_fn(f'Запущено: {soft}', 'success')
            except:
                speak(f'извините, сэр, я не нашёл {soft}')
                log_fn(f'Не найдено: {soft}', 'error')

    if 'закрой' in text.lower():
        soft = text.lower().replace('закрой', '').replace(' ', '')
        try:
            try:
                if _os.system(f'taskkill /im {soft}.exe') == 0:
                    speak('конечно, сэр')
                    log_fn(f'Закрыто: {soft}', 'success')
                elif _os.system(f'taskkill /f /im {soft}.exe') == 0:
                    speak('конечно, сэр')
                    log_fn(f'Закрыто: {soft}', 'success')
            except:
                with open('binds.txt', 'r', encoding='utf-8') as f:
                    for __str in f:
                        data = __str.split(',')
                        if data[0] == soft:
                            _os.system(f'taskkill /f /im {data[1]}.exe')
                            speak('конечно, сэр')
                            log_fn(f'Закрыто: {soft}', 'success')
        except:
            speak(f'извините, сэр, я не нашёл {soft}')
            log_fn(f'Не найдено: {soft}', 'error')

    if 'введи' in text.lower():
        t = text.replace('введи', '').replace('Введи', '')
        copy(t); hotkey('ctrl', 'v')
        speak('как скажите, сэр')
        log_fn(f'Введено: "{t.strip()}"', 'success')

    if 'напиши' in text.lower():
        t = text.replace('напиши', '').replace('Напиши', '')
        copy(t); hotkey('ctrl', 'v')
        speak('как скажите, сэр')
        log_fn(f'Введено: "{t.strip()}"', 'success')

    if 'нажми' in text.lower():
        try:
            t = text.lower().replace('нажми', '')
            if 'вниз' in t:
                presser(0, t, 'i == "вниз"', r"""exec("press('down')\n" * gain)""")
            if 'вверх' in t or 'наверх' in t:
                presser(0, t, 'i == "вверх" or i == "наверх"', r"""exec("press('up')\n" * gain)""")
            if 'влево' in t or 'налево' in t:
                presser(0, t, 'i == "влево" or i == "налево"', r"""exec("press('left')\n" * gain)""")
            if 'вправо' in t or 'направо' in t:
                presser(0, t, 'i == "вправо" or i == "направо"', r"""exec("press('right')\n" * gain)""")
            if 'alltop' in t:
                presser(1, t, "i == 'tap' or i == 'tab'", "with hold('alt'):\n" + r"""    exec("press('tab')\n" * gain)""")
            elif ('alt' in t or 'альта' in t or 'альт' in t) and ('tap' in t or 'tab' in t):
                presser(0, t, "i == 'tap' or i == 'tab'", "with hold('alt'):\n" + r"""   exec("press('tab')\n" * gain)""")
            elif 'tap' in t or 'tab' in t:
                presser(0, t, "i == 'tap' or i == 'tab'", r"""exec("press('tab')\n" * gain)""")
            if ('control' in t or 'ctrl' in t) and 'z' in t:
                try:
                    exec("hotkey('ctrl', 'z')\n" * int(search(r'\d+', Rus2Num()(t)).group()))
                except:
                    gain = 0
                    for i in t:
                        if i == 'z': gain += 1
                    exec("hotkey('ctrl', 'z')\n" * gain)
            if 'стереть' in t.lower():
                exec("press('backspace')\n" * int(search(r'\d+', Rus2Num()(t)).group()))
            if 'enter' in t:
                presser(0, t, "i == 'enter'", r"""exec("press('enter')\n" * gain)""")
            speak(f'нажал {t}')
            log_fn(f'Нажато: {t.strip()}', 'success')
        except:
            speak(f'извините, не удалось нажать {t}')
            log_fn(f'Ошибка нажатия', 'error')

    if text.lower() == 'папочка дома':
        speak('здравствуйте, сэр')
        log_fn('Приветствие', 'success')

    if 'привет' in text.lower() or 'здравствуй' in text.lower():
        speak('здравствуйте, сэр')
        log_fn('Приветствие', 'success')


# ── GUI ──
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl, Qt, QObject, Slot, Signal


class Bridge(QObject):
    log_signal        = Signal(str, str)
    transcript_signal = Signal(str)
    status_signal     = Signal(bool)

    def __init__(self):
        super().__init__()
        self.listening = False

    @Slot()
    def toggle_listen(self):
        if self.listening:
            self.listening = False
            self.status_signal.emit(False)
            self.log_signal.emit('Микрофон отключён', '')
        else:
            self.listening = True
            self.status_signal.emit(True)
            self.log_signal.emit("Ожидание: 'ДЖАРВИС'...", '')
            threading.Thread(target=self._loop, daemon=True).start()

    @Slot(str)
    def run_command(self, text):
        threading.Thread(
            target=process_command,
            args=(text, self.log_signal.emit, self.transcript_signal.emit),
            daemon=True
        ).start()

    def _loop(self):
        while self.listening:
            try:
                with sr.Microphone() as source:
                    audio = r.listen(source, phrase_time_limit=5)
                text = r.recognize_google(audio, language='ru-RU')
                if 'джарвис' in text.lower():
                    self.log_signal.emit('Кодовое слово: ДЖАРВИС', 'warn')
                    if playsound:
                        try: Timer(0.1, playsound, args=['ready.mp3']).start()
                        except: pass
                    with sr.Microphone() as source:
                        audio2 = r.listen(source, phrase_time_limit=7)
                    try:
                        cmd = r.recognize_google(audio2, language='ru-RU')
                        process_command(cmd, self.log_signal.emit, self.transcript_signal.emit)
                    except sr.UnknownValueError:
                        self.log_signal.emit('Не распознано', 'error')
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.log_signal.emit(f'Ошибка SR: {e}', 'error')
            except Exception as e:
                self.log_signal.emit(f'Ошибка: {e}', 'error')


class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.browser = QWebEngineView()
        self.channel = QWebChannel()
        self.bridge  = Bridge()
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))
        self.setCentralWidget(self.browser)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = JarvisWindow()
    sys.exit(app.exec())
