from os import system, remove
from os import path as ospath
from pathlib import Path
from subprocess import run, DEVNULL, CalledProcessError
from asyncio import run as asyncrun
from edge_tts import Communicate
import json
import sys

# путь до расположения файла
path = str(Path(__file__).resolve().parent)
# буквенные написания цифр для перевода в цифровой вариант
digits_map = {
    "ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4,
    "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9
}

# ---------------------------------------------------------------------
# IPC / вывод
# ---------------------------------------------------------------------

def emit(payload):
    # Все ответы executor идут в stdout как JSON.
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
        ),
        flush=True,
    )


# ---------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------

def speak(text):
    try:
        temp = 't.mp3'

        asyncrun(
            Communicate(
                text,
                'ru-RU-DmitryNeural',
                rate='+20%',
            ).save(temp)
        )

        for cmd in [
            ['ffplay', '-nodisp', '-autoexit', temp],
            ['mpv', '--no-video', temp],
            ['paplay', temp],
        ]:
            try:
                run(
                    cmd,
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                    check=True,
                )
                break

            except (
                    FileNotFoundError,
                    CalledProcessError,
            ):
                continue

        if ospath.exists(temp):
            remove(temp)

    except Exception as error:
        if ospath.exists('t.mp3'):
            try:
                remove('t.mp3')
            except OSError:
                pass

        emit(
            {
                'type': 'log',
                'message': f'tts error: {error}',
            }
        )

# ---------------------------------------------------------------------
# проверка на число
# ---------------------------------------------------------------------

# проверяет только следующее слово
def check_number(possible_number, move) -> int:
    try:
        possible_number = int(possible_number)
        speak(f'нажимаю {move} {possible_number} раз')
        return int(possible_number)
    except (IndexError, ValueError):
        if digits_map.get(possible_number) is not None:
            speak(f'нажимаю {move} {possible_number} раз')
            return digits_map.get(possible_number)
        else:
            speak(f'нажимаю {move}')
            return 1

# ---------------------------------------------------------------------
# алиасы
# ---------------------------------------------------------------------

def get_aliases() -> list:
    aliases = []
    with (open(path + '/support_files/aliases.txt', 'r', encoding='utf-8') as f):
        for i in f:
            aliases += [[i.split(' : ')[0], i.split(' : ')[1]]]
    return aliases

# ---------------------------------------------------------------------
# словарь
# ---------------------------------------------------------------------

# слово:вывод, слово будет проверяться в блоке ввода и выводиться вывод
def get_dictionary() -> list:
    dictionary = []
    with (open(path + '/support_files/dictionary.txt', 'r', encoding='utf-8') as f):
        for i in f:
            dictionary += [[i.split(' : ')[0], i.split(' : ')[1]]]
    return dictionary
    
# ---------------------------------------------------------------------
# кастомные команды
# ---------------------------------------------------------------------

def get_custom_commands() -> list:
    custom_commands = []
    with(open(path + '/support_files/custom_commands.txt', 'r', encoding='utf-8') as f):
        for i in f:
            custom_commands += [[i.split(' : ')[0], i.split(' : ')[1].split(' ')]]
    return custom_commands

aliases = get_aliases()
custom_commands = get_custom_commands()
dictionary = get_dectionary()

def jarvis(text):

    # ---------------------------------------------------------------------
    # ввод
    # ---------------------------------------------------------------------

    if 'введи' in text.lower() or 'веди' in text.lower() or 'напиши' in text.lower():
        text = (
            text.replace('введи', '')
            .replace('Введи', '')
            .replace('напиши', '')
            .replace('Напиши', '')
            .replace('Веди', '')
            .replace('веди', '')
        )
        
        for pair in dictionary:
            if pair[0] == text.lower().replace(' ', '').replace(',', '').replace('.', ''):
                run(['wtype', pair[1]], check=True)
                speak(f'ввёл текст прикреплённый к {pair[0]} в словаре, сэр')
                break
        else:
            run(['wtype', text], check=True)
            speak('как скажите, сэр')

    # ---------------------------------------------------------------------
    # открытие
    # ---------------------------------------------------------------------

    elif 'открой' in text.lower() or 'запусти' in text.lower():
        soft = text.lower().replace('открой', '').replace('запусти', '').replace(' ', '').replace('.', '').replace(',', '')
        if system('which ' + soft) == 0:
            system(soft + ' &')
            speak(f'запускаю {soft}')
        else:
            for alias in aliases:
                if alias[0] == soft:
                    system(alias[1] + ' &')
                    speak(f'запускаю {soft}')
                    break
            else:
                speak(f'не удалось найти {soft}')

    # ---------------------------------------------------------------------
    # закрытие
    # ---------------------------------------------------------------------

    elif 'закрой' in text.lower() or 'заверши' in text.lower():
        soft = text.lower().replace('закрой', '').replace('заверши', '').replace(' ', '').replace('.', '').replace(',', '')
        if system('pgrep ' + soft) != 256:
            system('pkill -15 ' + soft)
            speak(f'закрыл {soft}')
        else:
            for alias in aliases:
                if alias[0] == soft:
                    if system('pgrep ' + alias[1]) != 256:
                        system('pkill -15 ' + alias[1])
                        speak(f'закрыл {soft}')
                        break
            else:
                speak(f'не удалось найти {soft}')

    # ---------------------------------------------------------------------
    # нажатие
    # ---------------------------------------------------------------------

    elif 'нажми' in text.lower():
        try:
            text = text.lower().replace('нажми', '').replace('.', '').replace(',', '').replace('-', ' ').replace('—', ' ').split(' ')[1::] + ['']
            # нажимаем все проговоренные клавиши
            for i, move in enumerate(text):
                print(i, move)
                if move in ('вверх', 'верх', 'наверх'):
                    exec("run(['wtype', '-k', 'Up'], check=True)\n" * check_number(text[i+1], 'вверх'))

                elif move in ('вниз', 'низ'):
                    exec("run(['wtype', '-k', 'Down'], check=True)\n" * check_number(text[i+1], 'вниз'))

                elif move in ('влево', 'лево', 'налево'):
                    exec("run(['wtype', '-k', 'Left'], check=True)\n" * check_number(text[i+1], 'влево'))

                elif move in ('вправо', 'право', 'направо'):
                    exec("run(['wtype', '-k', 'Right'], check=True)\n" * check_number(text[i+1], 'вправо'))

                elif move in ('ентер', 'enter', 'en'):
                    exec("run(['wtype', '-k', 'Return'], check=True)\n" * check_number(text[i+1], 'ентер'))

                elif move in ('tab', 'tap', 'таб', 'тап', 'top', 'топ'):
                    exec("run(['wtype', '-k', 'Tab'], check=True)\n" * check_number(text[i+1], 'таб'))

                elif move in ('launcher', 'лаунчер'):
                    exec("run(['cosmic-launcher'], check=True)\n" * check_number(text[i+1], 'лаунчер'))

                elif move in ('стереть', 'бэкспейс', 'backspace', 'удалить', 'очистить', 'отчистить'):
                    exec("run(['wtype', '-k', 'BackSpace'], check=True)\n" * check_number(text[i+1], 'backspace'))

                elif move in ('эскейп', 'ескейп', 'escape'):
                    exec("run(['wtype', '-k', 'Escape'], check=True)\n" * check_number(text[i+1], 'backspace'))

                elif move in ('пробел', 'спейс', 'space'):
                    exec("run(['wtype', '-k', 'Space'], check=True)\n" * check_number(text[i+1], 'backspace'))

        except (IndexError, ValueError):
            speak('сэр, возникла ошибка, не удалось ничего нажать')

    # ---------------------------------------------------------------------
    # приветствие
    # ---------------------------------------------------------------------

    elif 'привет' in text.lower() or 'здравствуй' in text.lower() or 'дома' in text.lower():
        speak('здравствуйте, сэр, чем я могу вам помочь?')

    # ---------------------------------------------------------------------
    # кастомные команды
    # ---------------------------------------------------------------------

    else:
        for name, command in custom_commands:
            if name in text.lower():
                run(command)
                speak(f'команда {name} выполнена, сэр')

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main():
    # сообщаем frontend, что executor запущен
    emit(
        {
            'type': 'state',
            'state': 'idle',
        }
    )

    emit(
        {
            'type': 'log',
            'message': 'executor ready',
        }
    )

    # получаем уже распознанный текст через stdin
    for line in sys.stdin:
        line = line.strip()


        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue

        # завершение executor
        if message.get('type') == 'shutdown':
            break

        # выполнение команды
        if message.get('type') == 'command':
            text = message.get('text', '')

            if not text:
                continue

            emit(
                {
                    'type': 'state',
                    'state': 'processing',
                }
            )

            try:
                jarvis(text)

                emit(
                    {
                        'type': 'response',
                        'message': 'done',
                        'state': 'idle',
                    }
                )

            except Exception as error:
                emit(
                    {
                        'type': 'log',
                        'message': f'executor error: {error}',
                    }
                )

                emit(
                    {
                        'type': 'state',
                        'state': 'error',
                    }
                )

if __name__ == '__main__':
    main()
