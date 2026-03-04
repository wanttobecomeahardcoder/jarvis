import os
import speech_recognition as sr
import pyttsx3
from subprocess import Popen
import subprocess
import winreg
from playsound3 import playsound
from threading import Timer
from pyautogui import hotkey, press, hold
from pyperclip import copy
from rus2num import Rus2Num
from re import search

r = sr.Recognizer()

def presser(gain, text, condition, pressing_command):
    try:
        gain = int(search(r'\d+', Rus2Num()(text)).group())
        exec(pressing_command)
        pyttsx3.speak(f'нажал {text}')
    except:
        for i in text.split(' '):
            if eval(condition):
                gain += 1
        exec(pressing_command)
        pyttsx3.speak(f'нажал {text}')

print('Добро пожаловать в JARVIS!!! Для того чтобы JARVIS услышал команду, просто скажите "JARVIS", подробнее можете прочитать в README.')

while True:
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='ru-RU')
        if 'джарвис' in text.lower():
            with sr.Microphone() as source:
                Timer(0.2, playsound, args=['ready.mp3']).start()
                audio = r.listen(source)
            Timer(0.2, playsound, args=['ready.mp3']).start()
            try:
                text = r.recognize_google(audio, language='ru-RU')
                print(text)
                if 'открой' in text.lower() or 'запусти' in text.lower():
                    soft = text.lower().replace('открой', '').replace('запусти', '').replace(' ', '')
                    with open('base.txt', 'r', encoding='utf-8') as f:
                        for __str in list(f) + ['END']:
                            data = __str.split(',')
                            if __str == 'END':
                                pyttsx3.speak(f'извините, сэр, я не нашёл {soft}')
                                break
                            if data[0] == soft:
                                Popen([data[1][1::].replace('\n', '')])
                                pyttsx3.speak('конечно, сэр')
                                break
                            else:
                                try:
                                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                                         fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{soft}.exe")
                                    path = winreg.QueryValue(key, None)
                                    winreg.CloseKey(key)
                                    subprocess.Popen([path])
                                    pyttsx3.speak('конечно, сэр')
                                    break
                                except:
                                    pass
                if 'закрой' in text.lower():
                    soft = text.lower().replace('закрой', '').replace(' ', '')
                    try:
                        try:
                            if os.system(f'taskkill /im {soft}.exe') == 0:
                                pyttsx3.speak('конечно, сэр')
                            elif os.system(f'taskkill /f /im {soft}.exe') == 0:
                                pyttsx3.speak('конечно, сэр')
                        except:
                            with open('binds.txt', 'r', encoding='utf-8') as f:
                                for __str in f:
                                    data = __str.split(',')
                                    if data[0] == soft:
                                        os.system(f'taskkill /f /im {data[1]}.exe')
                                        pyttsx3.speak('конечно, сэр')
                    except:
                        pyttsx3.speak(f'извините, сэр, я не нашёл {soft}')
                if 'введи' in text.lower():
                    text = text.replace('введи', '').replace('Введи', '')
                    copy(text)
                    hotkey('ctrl', 'v')
                    pyttsx3.speak('как скажите, сэр')
                if 'напиши' in text.lower():
                    text = text.replace('напиши', '').replace('Напиши', '')
                    copy(text)
                    hotkey('ctrl', 'v')
                    pyttsx3.speak('как скажите, сэр')
                if 'нажми' in text.lower():
                    try:
                        text = text.lower().replace('нажми', '')
                        if 'вниз' in text:
                            presser(0, text, 'i == "вниз"', r"""exec("press('down')\n" * gain)""")
                        if 'вверх' in text or 'наверх' in text:
                            presser(0, text, 'i == "вверх" or i == "наверх"', r"""exec("press('up')\n" * gain)""")
                        if 'влево' in text or 'налево' in text:
                            presser(0, text, 'i == "влево" or i == "налево"', r"""exec("press('left')\n" * gain)""")
                        if 'вправо' in text or 'направо' in text:
                            presser(0, text, 'i == "вправо" or i == "направо"', r"""exec("press('right')\n" * gain)""")
                        if 'alltop' in text:
                            presser(1, text, "i == 'tap' or i == 'tab'", "with hold('alt'):\n" + r"""    exec("press('tab')\n" * gain)""")
                        elif ('alt' in text or 'альта' in text or 'альт' in text) and ('tap' in text or 'tab' in text):
                            presser(0, text, "i == 'tap' or i == 'tab'", "with hold('alt'):\n" + r"""   exec("press('tab')\n" * gain)""")
                        elif 'tap' in text or 'tab' in text:
                            presser(0, text, "i == 'tap' or i == 'tab'", r"""exec("press('tab')\n" * gain)""")
                        if ('control' in text or 'ctrl' in text) and 'z' in text:
                            try:
                                exec("hotkey('ctrl', 'z')\n" * int(search(r'\d+', Rus2Num()(text)).group()))
                                pyttsx3.speak(f'нажал {text}')
                            except:
                                gain = 0
                                for i in text:
                                    if i == 'z':
                                        gain += 1
                                exec("hotkey('ctrl', 'z')\n" * gain)
                                pyttsx3.speak(f'нажал {text}')
                        if 'стереть' in text.lower():
                            exec("press('backspace')\n" * int(search(r'\d+', Rus2Num()(text)).group()))
                            pyttsx3.speak(f'нажал {text}')
                        if 'enter' in text:
                            presser(0, text, "i == 'enter'", r"""exec("press('enter')\n" * gain)""")
                    except:
                        pyttsx3.speak(f'извините, не удалось нажать {text}')
                if text.lower() == 'папочка дома':
                    pyttsx3.speak('здравствуйте, сэр')
                if 'привет' in text.lower() or 'здравствуй' in text.lower():
                    pyttsx3.speak('здравствуйте, сэр')
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                pass
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        pass
