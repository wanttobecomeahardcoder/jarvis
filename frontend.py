#!/usr/bin/env python3

from __future__ import annotations

import base64
import json
import math
import os
import queue
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path


# ---------------------------------------------------------------------
# embedded microphone artwork
# ---------------------------------------------------------------------

# встроенная картинка микрофона.
# благодаря этому frontend не зависит от отдельного PNG-файла.
MICROPHONE_PNG_B64 = 'iVBORw0KGgoAAAANSUhEUgAAABoAAAA2CAYAAADZJImDAAAEJklEQVR4nO2YQUwjZRTH/99MC90ynU0v7gjTjYeauNuD7UXaFaMbE6kePNElcbMIId7csCN6IBrXm4oWJB48GHTxYELLFSneTLCtxgQkC8lGTtthMxp1pQ6lpZ0+D6VNKe20IJh1w0smzeR73/u9983rfP/5mMPpQitGgoh8T6+fJPlxpqd/5zbWVy0ric2WJgOwtALIDSlv5fuGx2vHOC0F+0j/Gaap2WZxWLOKtqcXtKLbcw4A+OVEgl9JflaUZJ/hCygkyWB6GvaRK05uY/2vI4NyQ8rA7qAyUy9zEkRkr9+cLARDNzgthY7+p9mRQfr8bSJBhNB/qe7ykCBiezpGJMmwj1zp4leS9xrF4hoNFLyBLhJE8MuJRKNnwPQ02qLTLwFAvqf3FbOKGoKKkuzaC3bXLAD09H0AgCBKRwKVjelptZlPK9YUdFx2CvofgEgQQYJ4YoBybG57OkaZ6QU6CUhuULmmz98mw+vvtJAk40QoAIqS7Cv9ulwPYTOcaHTHWbkCYnoaAA50Hr+xfgcACs/0jprFMnz+fgBgmvpz7RgJ4nkA4LRUimOa+hsAFN0XO/eD1u4zTQUJInb7hl+sBylKss3o6b0BAG2xaPTAuPtidwmk/snxy4mPAKDgDTxf62j79L0nACB3/eY3uSFloLrqgjfQlZmK7JAgwroQDdfuWYbb4yRBBKelwDQ1C/vlUCdWiVh8iwSXBw6na9/VroSvYpWofLFvU8TiW5V7fiYerzfPMh6ZxCqR9cPIxw6nC3A4XeC/iiewStSmTFyrneBwumC/HOrkZ+LxfcD4FrUr4av1/DsuBGxlP+FCwOZwukqawfD6OzNTkU2mp9ExHGwon0gQAUG07T38hhIrMxVJGl5/t3UhGrZ9MPomsNfe/EryniUW/YQEEZmp2R2SZFu9AExPg2lq1gySG1IGDK+/m9NSaL81+U5lblkFVSuawwjD6mrL8que1tsnt4qSbMtMRXZIKv3P2m5Nvtq2EI00Axa8ga7sWFg1E5QHdB0JInYHlTd2Q8NhoLRclqXFCX45Mcu0zU1OS/1BwtkzJMmPFHz+lwvB0HhlK9hY+9X+9muP1UusoYA03B5n7vV35w1fIGBWTTmZ9i8ngta5LxYb+jTT3kVJthnewJOFnheU4qPyc0W35xzT0yhVqP5kXVr82kyhtgyqtt1gyJ8bCyeq27ZVe0i2iQceZF1aTHK/rGmWpcXPDws6VDP8G3swl+4UdAo6BR0epM/GaXv2+6ZfNflgqDsf7HvKzMf0FfT3d3cJABzPnq+c8+SDoW6AyBqb+9HMr9Yqx2j6bJwYqOnhUXYsnAQAa2zO1K82oQrouL/8ahP6z5qhUhHTVLBjrMn2/qgfoErACkjov2S65o0CNDJrLPpD9b3pmWq9KmsDtAr/B5Ab7ixQV9DXAAAAAElFTkSuQmCC'


# ---------------------------------------------------------------------
# размеры окна
# ---------------------------------------------------------------------

WINDOW_W = 750
WINDOW_H = 900

LEFT_W = 200
RIGHT_W = 200

CENTER_W = (
    WINDOW_W
    - LEFT_W
    - RIGHT_W
)


# IPC frontend
SOCKET_PATH = '/tmp/jarvis-ui.sock'

# IPC launcher
CONTROL_SOCKET_PATH = '/tmp/jarvis-control.sock'
# IPC listener control
LISTENER_CONTROL_SOCKET_PATH = '/tmp/jarvis-listener-control.sock'

# путь до проекта
ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------------
# цвета
# ---------------------------------------------------------------------

BG = '#020408'
LEFT_BG = '#080b12'
PANEL = '#070a10'
BORDER = '#172238'

TEXT = '#dce4f2'
MUTED = '#61708b'
MUTED_2 = '#42516a'

CYAN = '#00d9ff'
CYAN_2 = '#009ec0'
CYAN_3 = '#063b4a'

GREEN = '#68ff59'
YELLOW = '#ffd166'
RED = '#ff526b'

CENTER_DARK = '#080d18'


class JarvisFrontend(tk.Tk):
    '''
    Основное окно JARVIS.

    Интерфейс оставлен в исходной компоновке:
    - левая панель подсказок
    - центральный реактор
    - микрофон
    - waveform
    - правая панель логов
    '''

    def __init__(self):
        super().__init__()

        # -------------------------------------------------------------
        # основные настройки окна
        # -------------------------------------------------------------

        self.resizable(
            False,
            False,
        )

        # окно НЕ закрепляется поверх всех остальных
        self.wm_attributes(
            '-topmost',
            False,
        )

        self.configure(
            bg=BG
        )

        # нормальное закрытие через крестик
        self.protocol(
            'WM_DELETE_WINDOW',
            self.close,
        )

        # escape закрывает окно
        self.bind(
            '<Escape>',
            lambda _event: self.close(),
        )

        # alt+F4
        self.bind(
            '<Alt-F4>',
            lambda _event: self.close(),
        )

        # cmd+q
        self.bind(
            '<Command-q>',
            lambda _event: self.close(),
        )

        # -------------------------------------------------------------
        # центрируем окно
        # -------------------------------------------------------------

        self.update_idletasks()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = max(
            0,
            (screen_w - WINDOW_W) // 2,
        )

        pos_y = max(
            0,
            (screen_h - WINDOW_H) // 2,
        )

        self.geometry(
            f'{WINDOW_W}x{WINDOW_H}+{pos_x}+{pos_y}'
        )

        # -------------------------------------------------------------
        # состояние
        # -------------------------------------------------------------

        self.state_name = 'idle'
        self.hover_mic = False

        # -------------------------------------------------------------
        # изображение микрофона
        # -------------------------------------------------------------

        self.microphone_image = tk.PhotoImage(
            data=MICROPHONE_PNG_B64
        )

        # время запуска анимации
        self.t0 = time.perf_counter()

        # очередь IPC-событий
        # потоки никогда напрямую не изменяют tkinter
        self.event_queue = queue.Queue()

        # -------------------------------------------------------------
        # IPC
        # -------------------------------------------------------------

        self.server = None
        self.listener_client = None

        self.stop_event = threading.Event()

        # -------------------------------------------------------------
        # executor
        # -------------------------------------------------------------

        self.executor = None
        self.executor_lock = threading.Lock()

        # -------------------------------------------------------------
        # создаём интерфейс
        # -------------------------------------------------------------

        self._build_ui()

        self._start_executor()

        # слушаем listener / worker
        self._start_ipc()

        # -------------------------------------------------------------
        # циклы анимации и IPC
        # -------------------------------------------------------------

        self.after(
            20,
            self._animation_loop,
        )

        self.after(
            40,
            self._poll_events,
        )

    # =================================================================
    # UI
    # =================================================================

    def _build_ui(self):
        # левая панель
        self.left = tk.Frame(
            self,
            bg=LEFT_BG,
            width=LEFT_W,
            height=WINDOW_H,
        )

        # центральная панель
        self.center = tk.Frame(
            self,
            bg=BG,
            width=CENTER_W,
            height=WINDOW_H,
        )

        # правая панель
        self.right = tk.Frame(
            self,
            bg=BG,
            width=RIGHT_W,
            height=WINDOW_H,
        )

        self.left.place(
            x=0,
            y=0,
            width=LEFT_W,
            height=WINDOW_H,
        )

        self.center.place(
            x=LEFT_W,
            y=0,
            width=CENTER_W,
            height=WINDOW_H,
        )

        self.right.place(
            x=LEFT_W + CENTER_W,
            y=0,
            width=RIGHT_W,
            height=WINDOW_H,
        )

        # вертикальные разделители
        tk.Frame(
            self,
            bg=BORDER,
            width=1,
            height=WINDOW_H,
        ).place(
            x=LEFT_W,
            y=0,
        )

        tk.Frame(
            self,
            bg=BORDER,
            width=1,
            height=WINDOW_H,
        ).place(
            x=LEFT_W + CENTER_W,
            y=0,
        )

        self._build_hints()
        self._build_center()
        self._build_log()

    # -----------------------------------------------------------------
    # левая панель
    # -----------------------------------------------------------------

    def _build_hints(self):
        x = 16
        y = 48
        w = 168

        tk.Label(
            self.left,
            text='ПОДСКАЗКИ КОМАНД',
            bg=LEFT_BG,
            fg=MUTED,
            font=(
                'DejaVu Sans Mono',
                8,
                'bold',
            ),
            anchor='w',
        ).place(
            x=x,
            y=y,
            width=w,
            height=16,
        )

        y += 24

        self._hint(
            x,
            y,
            w,
            68,
            '«Введи»',
            'Вводит продиктованный\nВами текст.',
        )

        y += 78

        self._hint(
            x,
            y,
            w,
            68,
            '«Нажми»',
            'Нажимает продиктованные\nВами клавиши.',
        )

        y += 78

        self._hint(
            x,
            y,
            w,
            82,
            '«Открой/закрой»',
            'Открывает/закрывает\nсказанную Вами\nпрограмму.',
        )

    def _hint(
        self,
        x,
        y,
        w,
        h,
        title,
        description,
    ):
        # карточка отдельной команды
        frame = tk.Frame(
            self.left,
            bg=LEFT_BG,
            highlightthickness=1,
            highlightbackground=BORDER,
        )

        frame.place(
            x=x,
            y=y,
            width=w,
            height=h,
        )

        tk.Label(
            frame,
            text=title,
            bg=LEFT_BG,
            fg=TEXT,
            font=(
                'DejaVu Sans',
                10,
            ),
            anchor='w',
        ).place(
            x=9,
            y=8,
            width=w - 18,
            height=18,
        )

        tk.Label(
            frame,
            text=description,
            bg=LEFT_BG,
            fg=MUTED,
            font=(
                'DejaVu Sans Mono',
                8,
            ),
            justify='left',
            anchor='nw',
        ).place(
            x=9,
            y=30,
            width=w - 18,
            height=h - 36,
        )

    # -----------------------------------------------------------------
    # центр
    # -----------------------------------------------------------------

    def _build_center(self):
        self.center_canvas = tk.Canvas(
            self.center,
            bg=BG,
            highlightthickness=0,
            bd=0,
            width=CENTER_W,
            height=WINDOW_H,
        )

        self.center_canvas.place(
            x=0,
            y=0,
        )

        # центр реактора
        self.cx = CENTER_W / 2
        self.cy = 345

        self.center_canvas.bind(
            '<Motion>',
            self._mouse_move,
        )

        self.center_canvas.bind(
            '<Leave>',
            self._mouse_leave,
        )

        self.center_canvas.bind(
            '<Button-1>',
            self._mic_click,
        )

        # -------------------------------------------------------------
        # badge
        # -------------------------------------------------------------

        self.badge = tk.Label(
            self.center,
            text='●  АКТИВНОЕ  СЛУШАНИЕ',
            bg='#03151c',
            fg=CYAN,
            font=(
                'DejaVu Sans Mono',
                8,
                'bold',
            ),
            padx=8,
            pady=4,
        )

        self.badge.place(
            x=CENTER_W // 2,
            y=510,
            anchor='n',
        )

        # -------------------------------------------------------------
        # заголовок
        # -------------------------------------------------------------

        self.status_title = tk.Label(
            self.center,
            text='Скажите «Jarvis», чтобы\nобратиться к помощнику',
            bg=BG,
            fg=TEXT,
            font=(
                'DejaVu Sans',
                17,
                'bold',
            ),
            justify='center',
            anchor='center',
        )

        self.status_title.place(
            x=CENTER_W // 2,
            y=546,
            anchor='n',
            width=330,
            height=58,
        )

        # -------------------------------------------------------------
        # подзаголовок
        # -------------------------------------------------------------

        self.status_subtitle = tk.Label(
            self.center,
            text='Голосовой центр готов к вводу. Назовите\nкоманду для её выполнения.',
            bg=BG,
            fg=MUTED,
            font=(
                'DejaVu Sans',
                11,
            ),
            justify='center',
        )

        self.status_subtitle.place(
            x=CENTER_W // 2,
            y=604,
            anchor='n',
            width=330,
            height=42,
        )

        # -------------------------------------------------------------
        # waveform
        # -------------------------------------------------------------

        self.wave_canvas = tk.Canvas(
            self.center,
            width=302,
            height=37,
            bg=BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
        )

        self.wave_canvas.place(
            x=CENTER_W // 2,
            y=657,
            anchor='n',
        )

    # -----------------------------------------------------------------
    # правая панель
    # -----------------------------------------------------------------

    def _build_log(self):
        tk.Label(
            self.right,
            text='ЛОГ ГОЛОСОВЫХ КОМАНД',
            bg=BG,
            fg=MUTED,
            font=(
                'DejaVu Sans Mono',
                8,
                'bold',
            ),
            anchor='w',
        ).place(
            x=15,
            y=18,
            width=155,
            height=15,
        )

        tk.Label(
            self.right,
            text='>_',
            bg=BG,
            fg=MUTED,
            font=(
                'DejaVu Sans Mono',
                9,
                'bold',
            ),
            anchor='e',
        ).place(
            x=153,
            y=17,
            width=31,
            height=16,
        )

        self.log = tk.Text(
            self.right,
            bg=BG,
            fg=MUTED,
            insertbackground=CYAN,
            selectbackground='#122238',
            selectforeground=TEXT,
            relief='flat',
            bd=0,
            highlightthickness=0,
            font=(
                'DejaVu Sans Mono',
                8,
            ),
            wrap='word',
            state='disabled',
        )

        self.log.place(
            x=15,
            y=48,
            width=168,
            height=730,
        )

        # карточка live response
        self.stdout_card = tk.Frame(
            self.right,
            bg=BG,
            highlightthickness=1,
            highlightbackground=BORDER,
        )

        self.stdout_card.place(
            x=15,
            y=830,
            width=168,
            height=54,
        )

        self.stdout_dot = tk.Label(
            self.stdout_card,
            text='●',
            bg=BG,
            fg=GREEN,
            font=(
                'DejaVu Sans Mono',
                8,
            ),
        )

        self.stdout_dot.place(
            x=9,
            y=10,
        )

        tk.Label(
            self.stdout_card,
            text='STDOUT  //  LIVE RESPONSE',
            bg=BG,
            fg=MUTED,
            font=(
                'DejaVu Sans Mono',
                7,
            ),
        ).place(
            x=22,
            y=10,
        )

    # =================================================================
    # состояние интерфейса
    # =================================================================

    def set_state(self, state):
        self.state_name = state

        states = {
            'idle': (
                '●  АКТИВНОЕ  СЛУШАНИЕ',
                'Скажите «Jarvis», чтобы\nобратиться к помощнику',
                'Голосовой центр готов к вводу. Назовите\nкоманду для её выполнения.',
                CYAN,
            ),

            'listening': (
                '●  СЛУШАЮ  КОМАНДУ',
                'Говорите, сэр',
                'Запись активна. После паузы прозвучит сигнал.',
                CYAN,
            ),

            'processing': (
                '●  ОБРАБОТКА',
                'Обрабатываю команду',
                'Передаю запрос исполнительному модулю.',
                YELLOW,
            ),

            'speaking': (
                '●  ОТВЕЧАЮ',
                'Выполняю команду',
                'JARVIS отвечает.',
                GREEN,
            ),

            'calibrating': (
                '●  КАЛИБРОВКА',
                'Настройка микрофона',
                'Определяю уровень фонового шума.',
                YELLOW,
            ),

            'error': (
                '●  ОШИБКА',
                'Возникла ошибка',
                'Проверьте состояние модулей.',
                RED,
            ),
        }

        (
            badge,
            title,
            subtitle,
            accent,
        ) = states.get(
            state,
            states['idle'],
        )

        self.badge.configure(
            text=badge,
            fg=accent,
        )

        self.status_title.configure(
            text=title,
            font=(
                'DejaVu Sans',
                17,
                'bold',
            ),
        )

        self.status_subtitle.configure(
            text=subtitle
        )

    # =================================================================
    # анимация
    # =================================================================

    def _animation_loop(self):
        t = (
            time.perf_counter()
            - self.t0
        )

        self._draw_reactor(t)
        self._draw_wave(t)
        self._animate_badge(t)

        self.after(
            20,
            self._animation_loop,
        )

    def _draw_reactor(self, t):
        canvas = self.center_canvas

        canvas.delete(
            'reactor'
        )

        cx = self.cx
        cy = self.cy

        # плавные колебания
        slow = (
            math.sin(t * 1.25)
            + 1.0
        ) / 2.0

        fast = (
            math.sin(t * 2.4)
            + 1.0
        ) / 2.0

        active = (
            self.state_name
            == 'listening'
        )

        processing = (
            self.state_name
            == 'processing'
        )

        if active:
            pulse = (
                1.0
                + 5.0 * slow
            )

            glow = (
                1.0
                + 7.0 * fast
            )

        elif processing:
            pulse = (
                1.0
                + 3.0 * slow
            )

            glow = (
                1.0
                + 4.0 * fast
            )

        else:
            pulse = (
                1.0
                + 2.0 * slow
            )

            glow = (
                1.0
                + 2.0 * fast
            )

        # внешнее кольцо
        radius = 139 + pulse

        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline='#09202d',
            width=1,
            tags='reactor',
        )

        # второе кольцо
        radius = 114 + pulse * 0.6

        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline='#073746',
            width=1,
            tags='reactor',
        )

        # свечение колец
        rings = (
            (
                86 + glow * 0.30,
                '#002d3b',
                9,
            ),
            (
                85 + glow * 0.20,
                '#00495b',
                6,
            ),
            (
                84 + glow * 0.12,
                '#007e98',
                3,
            ),
            (
                83 + glow * 0.08,
                CYAN,
                2,
            ),
        )

        for radius, color, width in rings:
            canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline=color,
                width=width,
                tags='reactor',
            )

        # центральный диск
        disc_r = 55

        if self.hover_mic:
            fill = '#0c1320'
            outline = '#25334b'
        else:
            fill = '#090d17'
            outline = '#18243a'

        canvas.create_oval(
            cx - disc_r,
            cy - disc_r,
            cx + disc_r,
            cy + disc_r,
            fill=fill,
            outline=outline,
            width=2,
            tags='reactor',
        )

        # внутреннее кольцо
        inner = (
            45
            + fast * 1.2
        )

        canvas.create_oval(
            cx - inner,
            cy - inner,
            cx + inner,
            cy + inner,
            outline='#0d1727',
            width=1,
            tags='reactor',
        )

        # микрофон
        self._draw_microphone_icon(
            canvas,
            cx,
            cy,
            active,
            t,
        )

        # маленькие орбитальные точки
        for index in range(4):
            angle = (
                t
                * (
                    0.22
                    + index * 0.025
                )
                + index * math.pi / 2
            )

            radius = 112

            px = (
                cx
                + math.cos(angle)
                * radius
            )

            py = (
                cy
                + math.sin(angle)
                * radius
            )

            canvas.create_oval(
                px - 1,
                py - 1,
                px + 1,
                py + 1,
                fill='#075066',
                outline='',
                tags='reactor',
            )

    def _draw_microphone_icon(
        self,
        canvas,
        cx,
        cy,
        active,
        t,
    ):
        # используем картинку микрофона
        canvas.create_image(
            int(cx),
            int(cy + 10),
            image=self.microphone_image,
            anchor='center',
            tags='reactor',
        )

    def _draw_wave(self, t):
        canvas = self.wave_canvas

        canvas.delete(
            'wave'
        )

        center_y = 18.5

        # количество полос waveform
        bars = 31

        active = (
            self.state_name
            == 'listening'
        )

        processing = (
            self.state_name
            == 'processing'
        )

        for index in range(bars):
            x = (
                68
                + index * 5.5
            )

            wave_a = math.sin(
                t * 7.0
                + index * 0.74
            )

            wave_b = math.sin(
                t * 4.3
                + index * 1.31
            )

            envelope = (
                0.45
                + 0.55
                * abs(
                    math.sin(
                        index * 0.48
                    )
                )
            )

            if active:
                amplitude = (
                    3
                    + abs(wave_a) * 10
                    + abs(wave_b) * 6
                ) * envelope

            elif processing:
                amplitude = (
                    2
                    + abs(wave_a) * 5
                ) * envelope

            else:
                # движение waveform в idle
                amplitude = (
                    1.5
                    + abs(wave_a) * 2.7
                ) * envelope

            canvas.create_line(
                x,
                center_y - amplitude,
                x,
                center_y + amplitude,
                fill=CYAN,
                width=2,
                capstyle='round',
                tags='wave',
            )

    def _animate_badge(self, t):
        # пульсация badge во время записи
        if self.state_name == 'listening':
            value = (
                math.sin(t * 7.0)
                + 1.0
            ) / 2.0

            self.badge.configure(
                bg=(
                    '#03151c'
                    if value < 0.65
                    else '#05212a'
                )
            )

        else:
            self.badge.configure(
                bg='#03151c'
            )

        # индикатор live response
        if int(t * 3) % 2 == 0:
            self.stdout_dot.configure(
                fg=GREEN
            )
        else:
            self.stdout_dot.configure(
                fg='#2d8f2b'
            )

    # =================================================================
    # мышь
    # =================================================================

    def _mouse_move(self, event):
        dx = (
            event.x
            - self.cx
        )

        dy = (
            event.y
            - self.cy
        )

        inside = (
            math.sqrt(
                dx * dx
                + dy * dy
            )
            <= 58
        )

        if inside != self.hover_mic:
            self.hover_mic = inside

    def _mouse_leave(self, _event):
        self.hover_mic = False

    def _mic_click(self, event):
        # ручной запуск записи специально не используется
        #
        # управление голосом остаётся у listener.py,
        # который ждёт wake word «Джарвис»

        dx = (
            event.x
            - self.cx
        )

        dy = (
            event.y
            - self.cy
        )

        if (
            math.sqrt(
                dx * dx
                + dy * dy
            )
            <= 58
        ):
            self._log(
                'MIC: управление голосом через «Джарвис»'
            )

    # =================================================================
    # executor
    # =================================================================

    def _start_executor(self):
        # executor отвечает только за выполнение уже распознанного текста
        executor_path = (
            ROOT
            / 'executor.py'
        )

        if not executor_path.exists():
            self._log(
                'executor.py не найден'
            )

            return

        try:
            self.executor = (
                subprocess.Popen(
                    [
                        sys.executable,
                        str(executor_path),
                    ],
                    cwd=str(ROOT),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
            )

            # читаем ответы executor в отдельном потоке
            threading.Thread(
                target=self._read_executor,
                daemon=True,
            ).start()

            self._log(
                'executor: online'
            )

        except Exception as error:
            self._log(
                f'executor: {error}'
            )

            self.set_state(
                'error'
            )

    def _read_executor(self):
        # читаем JSON Lines от executor
        if (
            not self.executor
            or not self.executor.stdout
        ):
            return

        for line in self.executor.stdout:
            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(
                    line
                )

            except json.JSONDecodeError:
                # если executor вывел обычный текст,
                # показываем его как лог
                event = {
                    'type': 'log',
                    'message': line,
                }

            self.event_queue.put(
                event
            )

    def _set_listener_paused(self, paused):
        # ставим listener на паузу во время выполнения команды
        command = 'pause' if paused else 'resume'

        try:
            with socket.socket(
                socket.AF_UNIX,
                socket.SOCK_STREAM,
            ) as sock:
                sock.settimeout(0.5)

                sock.connect(
                    LISTENER_CONTROL_SOCKET_PATH
                )

                sock.sendall(
                    command.encode('utf-8')
                )

        except (
            FileNotFoundError,
            ConnectionRefusedError,
            BrokenPipeError,
            socket.timeout,
            OSError,
        ):
            self._log(
                f'listener: не удалось отправить {command}'
            )

    def _send_executor(self, payload):
        # отправляем JSON-команду executor
        with self.executor_lock:
            if (
                not self.executor
                or not self.executor.stdin
            ):
                self._log(
                    'executor недоступен'
                )

                return

            try:
                self.executor.stdin.write(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                    )
                    + '\n'
                )

                self.executor.stdin.flush()

            except (
                BrokenPipeError,
                OSError,
            ):
                self._log(
                    'executor: connection lost'
                )

    # =================================================================
    # IPC listener / worker
    # =================================================================

    def _start_ipc(self):
        # перед запуском удаляем старый socket
        try:
            if os.path.exists(
                SOCKET_PATH
            ):
                os.unlink(
                    SOCKET_PATH
                )

        except OSError:
            pass

        try:
            self.server = socket.socket(
                socket.AF_UNIX,
                socket.SOCK_STREAM,
            )

            self.server.bind(
                SOCKET_PATH
            )

            os.chmod(
                SOCKET_PATH,
                0o600,
            )

            self.server.listen(
                4
            )

            # отдельный поток принимает соединения
            threading.Thread(
                target=self._accept_listener,
                daemon=True,
            ).start()

            self._log(
                'IPC: ready'
            )

        except Exception as error:
            self._log(
                f'IPC: {error}'
            )

    def _accept_listener(self):
        # принимаем подключения от listener и Whisper worker
        while not self.stop_event.is_set():
            try:
                client, _ = (
                    self.server.accept()
                )

                self.listener_client = client

                threading.Thread(
                    target=self._read_listener,
                    args=(client,),
                    daemon=True,
                ).start()

            except OSError:
                break

    def _read_listener(self, client):
        # читаем JSON Lines
        buffer = b''

        try:
            while not self.stop_event.is_set():
                chunk = client.recv(
                    4096
                )

                if not chunk:
                    break

                buffer += chunk

                while b'\n' in buffer:
                    raw, buffer = (
                        buffer.split(
                            b'\n',
                            1,
                        )
                    )

                    if not raw:
                        continue

                    try:
                        event = json.loads(
                            raw.decode(
                                'utf-8'
                            )
                        )

                    except json.JSONDecodeError:
                        continue

                    self.event_queue.put(
                        event
                    )

        except OSError:
            pass

        finally:
            try:
                client.close()
            except OSError:
                pass

    # =================================================================
    # события
    # =================================================================

    def _poll_events(self):
        # все изменения Tkinter происходят только из главного потока
        while True:
            try:
                event = (
                    self.event_queue
                    .get_nowait()
                )

            except queue.Empty:
                break

            self._handle_event(
                event
            )

        self.after(
            40,
            self._poll_events,
        )

    def _handle_event(self, event):
        # защита от некорректного IPC-события
        if not isinstance(event, dict):
            self._log(
                f'IPC: некорректное событие: {event!r}'
            )
            return

        event_type = event.get(
            'type'
        )

        # -------------------------------------------------------------
        # состояние
        # -------------------------------------------------------------

        if event_type == 'state':
            state = event.get(
                'state',
                'idle',
            )

            self.set_state(
                state
            )

            # если executor завершился ошибкой — не оставляем listener на паузе
            if state == 'error':
                self._set_listener_paused(False)

        # -------------------------------------------------------------
        # wake word
        # -------------------------------------------------------------

        elif event_type == 'wake':
            self._log(
                'WAKE WORD: ДЖАРВИС'
            )

        # -------------------------------------------------------------
        # готовая команда от Whisper
        # -------------------------------------------------------------

        elif event_type == 'command':
            command = event.get(
                'text',
                '',
            ).strip()

            if command:
                self._log(
                    f'> {command}'
                )

                # сначала полностью останавливаем приём новых команд
                self._set_listener_paused(True)

                # передаём исходный текст executor
                self._send_executor(
                    {
                        'type': 'command',
                        'text': command,
                    }
                )

        # -------------------------------------------------------------
        # ответ executor
        # -------------------------------------------------------------

        elif event_type == 'response':
            # executor закончил — снова разрешаем listener слушать
            self._set_listener_paused(False)

            self._log(
                event.get(
                    'message',
                    'executor: done',
                )
            )

            self.set_state(
                event.get(
                    'state',
                    'idle',
                )
            )

        # -------------------------------------------------------------
        # обычный лог
        # -------------------------------------------------------------

        elif event_type == 'log':
            message = event.get(
                'message',
                '',
            )

            if message:
                self._log(
                    message
                )

        # -------------------------------------------------------------
        # состояние listener
        # -------------------------------------------------------------

        elif event_type == 'listener':
            state = event.get(
                'state'
            )

            if state == 'online':
                self._log(
                    'listener: online'
                )

            elif state == 'offline':
                self._log(
                    'listener: offline'
                )

            elif state == 'error':
                self._log(
                    'listener: error'
                )

        # -------------------------------------------------------------
        # состояние worker
        # -------------------------------------------------------------

        elif event_type == 'worker':
            state = event.get(
                'state'
            )

            if state == 'online':
                self._log(
                    'whisper worker: online'
                )

            elif state == 'offline':
                self._log(
                    'whisper worker: offline'
                )

            elif state == 'starting':
                self._log(
                    'whisper worker: starting'
                )

            elif state == 'error':
                self._log(
                    'whisper worker: error'
                )

    # =================================================================
    # лог
    # =================================================================

    def _log(self, message):
        # добавляем время к каждой записи
        timestamp = time.strftime(
            '%H:%M:%S'
        )

        self.log.configure(
            state='normal'
        )

        self.log.insert(
            'end',
            f'[{timestamp}] {message}\n',
        )

        self.log.see(
            'end'
        )

        self.log.configure(
            state='disabled'
        )

    # =================================================================
    # закрытие
    # =================================================================

    def _tell_launcher_to_shutdown(self):
        # просим launcher закрыть listener + worker + frontend
        try:
            with socket.socket(
                socket.AF_UNIX,
                socket.SOCK_STREAM,
            ) as sock:
                sock.settimeout(0.5)

                sock.connect(
                    CONTROL_SOCKET_PATH
                )

                message = (
                    json.dumps(
                        {
                            'type': 'shutdown',
                        }
                    )
                    + '\n'
                )

                sock.sendall(
                    message.encode(
                        'utf-8'
                    )
                )

        except (
            FileNotFoundError,
            ConnectionRefusedError,
            BrokenPipeError,
            socket.timeout,
            OSError,
        ):
            pass

    def close(self):
        # защищаемся от повторного вызова close()
        if self.stop_event.is_set():
            return

        self.stop_event.set()

        # сначала сообщаем launcher,
        # чтобы он остановил listener и worker
        self._tell_launcher_to_shutdown()

        # корректно просим executor завершиться
        if self.executor:
            self._send_executor(
                {
                    'type': 'shutdown',
                }
            )

            try:
                self.executor.terminate()
            except OSError:
                pass

        # закрываем клиент listener
        if self.listener_client:
            try:
                self.listener_client.close()
            except OSError:
                pass

        # закрываем сервер IPC
        if self.server:
            try:
                self.server.close()
            except OSError:
                pass

        # удаляем socket frontend
        try:
            if os.path.exists(
                SOCKET_PATH
            ):
                os.unlink(
                    SOCKET_PATH
                )

        except OSError:
            pass

        # полностью закрываем Tkinter
        self.destroy()


if __name__ == '__main__':
    app = JarvisFrontend()
    app.mainloop()
