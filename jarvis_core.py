"""
jarvis_core.py
==============
Можно использовать как библиотеку:
    from jarvis_core import JarvisCore
    j = JarvisCore(on_log=..., on_transcript=..., on_status=...)
    j.start()

Можно запустить самостоятельно:
    python jarvis_core.py
"""

import os
import subprocess
import winreg
from re import search
from threading import Timer, Thread

import speech_recognition as sr
import pyttsx3
from pyautogui import hotkey, press, hold
from pyperclip import copy
from rus2num import Rus2Num

try:
    from playsound3 import playsound as _playsound
    def _play_ready():
        try:
            Timer(0.2, _playsound, args=['ready.mp3']).start()
        except Exception:
            pass
except ImportError:
    def _play_ready():
        pass


def _presser(gain, text, condition, pressing_command):
    try:
        gain = int(search(r'\d+', Rus2Num()(text)).group())
        exec(pressing_command)
    except Exception:
        for i in text.split(' '):
            if eval(condition):
                gain += 1
        exec(pressing_command)


class JarvisCore:
    """
    Параметры:
        on_log(text, kind)   — колбэк для лога.  kind: 'success' | 'warn' | 'error' | ''
        on_transcript(text)  — колбэк: что распознал микрофон
        on_status(active)    — колбэк: True = слушает, False = остановлен
    """

    def __init__(self, on_log=None, on_transcript=None, on_status=None):
        import queue
        self.r   = sr.Recognizer()
        self._listening = False
        self._thread    = None

        self.on_log        = on_log        or (lambda text, kind: print(f'[{kind or "LOG"}] {text}'))
        self.on_transcript = on_transcript or (lambda text: print(f'[TRANSCRIPT] {text}'))
        self.on_status     = on_status     or (lambda active: print(f'[STATUS] {"ON" if active else "OFF"}'))

        # pyttsx3 не потокобезопасен — держим его в одном выделенном потоке
        self._tts_queue = queue.Queue()
        Thread(target=self._tts_loop, daemon=True).start()

    # ── Public API ────────────────────────────────────────────

    def start(self):
        """Запустить прослушивание в фоновом потоке."""
        if self._listening:
            return
        self._listening = True
        self.on_status(True)
        self.on_log("Ожидание: 'ДЖАРВИС'...", '')
        self._thread = Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Остановить прослушивание."""
        self._listening = False
        self.on_status(False)
        self.on_log('Микрофон отключён', '')

    def toggle(self):
        self.stop() if self._listening else self.start()

    def run_command(self, text):
        """Выполнить команду из строки (голос или кнопка)."""
        Thread(target=self._process, args=(text,), daemon=True).start()

    # ── Internal ──────────────────────────────────────────────

    def _tts_loop(self):
        tts = pyttsx3.init()
        while True:
            text = self._tts_queue.get()
            try:
                tts.say(text)
                tts.runAndWait()
            except Exception:
                pass
            self._tts_queue.task_done()

    def _speak(self, text):
        self._tts_queue.put(text)

    def _listen_loop(self):
        while self._listening:
            try:
                # Слушаем кодовое слово
                with sr.Microphone() as source:
                    audio = self.r.listen(source, phrase_time_limit=5)
                text = self.r.recognize_google(audio, language='ru-RU')

                if 'джарвис' not in text.lower():
                    continue  # не то слово — слушаем дальше

                self.on_log('Кодовое слово: ДЖАРВИС', 'warn')
                _play_ready()

                # Слушаем команду
                with sr.Microphone() as source:
                    audio2 = self.r.listen(source, phrase_time_limit=7)
                _play_ready()

                try:
                    cmd = self.r.recognize_google(audio2, language='ru-RU')
                except sr.UnknownValueError:
                    self.on_log('Команда не распознана', 'error')
                    continue  # возвращаемся к прослушиванию

                self.on_transcript(cmd)
                self.on_log(f'Команда: "{cmd}"', '')

                # Команда в отдельном потоке — цикл сразу идёт дальше
                Thread(target=self._process, args=(cmd,), daemon=True).start()

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.on_log(f'Ошибка SR: {e}', 'error')
            except Exception as e:
                self.on_log(f'Ошибка: {e}', 'error')

    def _process(self, text):
        tl = text.lower()

        if 'открой' in tl or 'запусти' in tl:
            soft = tl.replace('открой', '').replace('запусти', '').replace(' ', '')
            opened = False
            try:
                with open('base.txt', 'r', encoding='utf-8') as f:
                    for __str in list(f) + ['END']:
                        data = __str.split(',')
                        if __str == 'END':
                            break
                        if data[0] == soft:
                            subprocess.Popen([data[1][1:].replace('\n', '')])
                            self._speak('конечно, сэр')
                            self.on_log(f'Запущено: {soft}', 'success')
                            opened = True
                            break
                        else:
                            try:
                                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{soft}.exe")
                                path = winreg.QueryValue(key, None)
                                winreg.CloseKey(key)
                                subprocess.Popen([path])
                                self._speak('конечно, сэр')
                                self.on_log(f'Запущено: {soft}', 'success')
                                opened = True
                                break
                            except Exception:
                                pass
            except FileNotFoundError:
                pass

            if not opened:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                        fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{soft}.exe")
                    path = winreg.QueryValue(key, None)
                    winreg.CloseKey(key)
                    subprocess.Popen([path])
                    self._speak('конечно, сэр')
                    self.on_log(f'Запущено: {soft}', 'success')
                except Exception:
                    self._speak(f'извините, сэр, я не нашёл {soft}')
                    self.on_log(f'Не найдено: {soft}', 'error')

        if 'закрой' in tl:
            soft = tl.replace('закрой', '').replace(' ', '')
            try:
                if os.system(f'taskkill /im {soft}.exe') == 0:
                    self._speak('конечно, сэр')
                    self.on_log(f'Закрыто: {soft}', 'success')
                elif os.system(f'taskkill /f /im {soft}.exe') == 0:
                    self._speak('конечно, сэр')
                    self.on_log(f'Закрыто: {soft}', 'success')
                else:
                    try:
                        with open('binds.txt', 'r', encoding='utf-8') as f:
                            for __str in f:
                                data = __str.split(',')
                                if data[0] == soft:
                                    os.system(f'taskkill /f /im {data[1]}.exe')
                                    self._speak('конечно, сэр')
                                    self.on_log(f'Закрыто: {soft}', 'success')
                    except FileNotFoundError:
                        self._speak(f'извините, сэр, я не нашёл {soft}')
                        self.on_log(f'Не найдено: {soft}', 'error')
            except Exception:
                self._speak(f'извините, сэр, я не нашёл {soft}')
                self.on_log(f'Не найдено: {soft}', 'error')

        if 'введи' in tl:
            t = text.replace('введи', '').replace('Введи', '')
            copy(t)
            hotkey('ctrl', 'v')
            self._speak('как скажите, сэр')
            self.on_log(f'Введено: "{t.strip()}"', 'success')

        if 'напиши' in tl:
            t = text.replace('напиши', '').replace('Напиши', '')
            copy(t)
            hotkey('ctrl', 'v')
            self._speak('как скажите, сэр')
            self.on_log(f'Введено: "{t.strip()}"', 'success')

        if 'нажми' in tl:
            try:
                t = tl.replace('нажми', '')
                if 'вниз' in t:
                    _presser(0, t, 'i == "вниз"', r"""exec("press('down')\n" * gain)""")
                if 'вверх' in t or 'наверх' in t:
                    _presser(0, t, 'i == "вверх" or i == "наверх"', r"""exec("press('up')\n" * gain)""")
                if 'влево' in t or 'налево' in t:
                    _presser(0, t, 'i == "влево" or i == "налево"', r"""exec("press('left')\n" * gain)""")
                if 'вправо' in t or 'направо' in t:
                    _presser(0, t, 'i == "вправо" or i == "направо"', r"""exec("press('right')\n" * gain)""")
                if 'alltop' in t:
                    _presser(1, t, "i == 'tap' or i == 'tab'",
                             "with hold('alt'):\n" + r"""    exec("press('tab')\n" * gain)""")
                elif ('alt' in t or 'альта' in t or 'альт' in t) and ('tap' in t or 'tab' in t):
                    _presser(0, t, "i == 'tap' or i == 'tab'",
                             "with hold('alt'):\n" + r"""   exec("press('tab')\n" * gain)""")
                elif 'tap' in t or 'tab' in t:
                    _presser(0, t, "i == 'tap' or i == 'tab'", r"""exec("press('tab')\n" * gain)""")
                if ('control' in t or 'ctrl' in t) and 'z' in t:
                    try:
                        exec("hotkey('ctrl', 'z')\n" * int(search(r'\d+', Rus2Num()(t)).group()))
                    except Exception:
                        gain = 0
                        for i in t:
                            if i == 'z':
                                gain += 1
                        exec("hotkey('ctrl', 'z')\n" * gain)
                if 'стереть' in t:
                    exec("press('backspace')\n" * int(search(r'\d+', Rus2Num()(t)).group()))
                if 'enter' in t:
                    _presser(0, t, "i == 'enter'", r"""exec("press('enter')\n" * gain)""")
                self._speak(f'нажал {t}')
                self.on_log(f'Нажато: {t.strip()}', 'success')
            except Exception as e:
                self._speak(f'извините, не удалось нажать')
                self.on_log(f'Ошибка нажатия: {e}', 'error')

        if tl == 'папочка дома' or 'привет' in tl or 'здравствуй' in tl:
            self._speak('здравствуйте, сэр')
            self.on_log('Приветствие', 'success')


# ── Самостоятельный запуск ────────────────────────────────────
if __name__ == '__main__':
    print('Добро пожаловать в JARVIS! Скажите "ДЖАРВИС" чтобы активировать.')
    jarvis = JarvisCore()
    jarvis.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        jarvis.stop()
        print('JARVIS остановлен.')
