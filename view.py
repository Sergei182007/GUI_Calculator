"""Модуль представления калькулятора (тёмный интерфейс на Tkinter без поля ручного ввода)."""

import tkinter as tk
from typing import Callable, Optional

BG = "#1e1f26"
DISPLAY_BG = "#2a2c36"
TEXT = "#f2f2f5"
HINT = "#8b8fa3"
ERROR = "#ff6b6b"

# Стили кнопок: (обычный цвет, цвет при наведении)
STYLES = {
    "num": ("#3a3d4d", "#4a4e63"),
    "op": ("#5b6cff", "#7482ff"),
    "func": ("#4b4f63", "#5f647d"),
    "eq": ("#2ec4a0", "#3ddbb5"),
}

# Раскладка: (подпись на кнопке, передаваемый символ/команда, стиль)
BUTTONS = [
    [("C", "clear", "func"), ("(", "(", "func"), (")", ")", "func"), ("⌫", "back", "func")],
    [("7", "7", "num"), ("8", "8", "num"), ("9", "9", "num"), ("÷", "/", "op")],
    [("4", "4", "num"), ("5", "5", "num"), ("6", "6", "num"), ("×", "*", "op")],
    [("1", "1", "num"), ("2", "2", "num"), ("3", "3", "num"), ("−", "-", "op")],
    [("0", "0", "num"), (".", ".", "num"), ("√", "√", "func"), ("+", "+", "op")],
]

class FlatButton(tk.Label):
    """Плоская кнопка с эффектом наведения и нажатия на базе tk.Label."""

    def __init__(self, master: tk.Widget, text: str, command: Callable[[], None], style: str, **kwargs) -> None:
        """Создаёт стилизованную плоскую кнопку.

        Args:
            master: Родительский виджет.
            text: Текст на кнопке.
            command: Функция, вызываемая при клике.
            style: Ключ стиля из словаря STYLES.
        """
        self.color, self.hover = STYLES[style]
        super().__init__(
            master,
            text=text,
            bg=self.color,
            fg=TEXT,
            font=("Segoe UI", 17, "bold"),
            cursor="hand2",
            **kwargs,
        )
        self.command = command
        self.bind("<Enter>", lambda _e: self.config(bg=self.hover))
        self.bind("<Leave>", lambda _e: self.config(bg=self.color))
        self.bind("<ButtonPress-1>", lambda _e: self.config(bg=BG))
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_release(self, event: tk.Event) -> None:
        """Вызывает команду только если кнопку мыши отпустили в пределах кнопки.

        Args:
            event: Событие отпускания кнопки мыши.
        """
        self.config(bg=self.hover)
        if 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height():
            self.command()

class CalculatorView:
    """Главное окно калькулятора без текстового поля ручного ввода."""

    def __init__(self) -> None:
        """Инициализирует окно, дисплей, кнопочную панель и горячие клавиши."""
        self.root = tk.Tk()
        self.root.title("Калькулятор")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.on_char: Optional[Callable[[str], None]] = None
        self.on_equals: Optional[Callable[[], None]] = None
        self.on_clear: Optional[Callable[[], None]] = None
        self.on_backspace: Optional[Callable[[], None]] = None

        self.status_var = tk.StringVar(value="")
        self.display_var = tk.StringVar(value="0")

        self._build_display()
        self._build_buttons()
        self._bind_keys()

    def _build_display(self) -> None:
        """Создаёт двухстрочный дисплей (верхняя строка — история/ошибка, нижняя — ввод/результат)."""
        display_frame = tk.Frame(self.root, bg=DISPLAY_BG, padx=16, pady=14)
        display_frame.pack(fill="x", padx=14, pady=(14, 10))

        self.status_label = tk.Label(
            display_frame,
            textvariable=self.status_var,
            bg=DISPLAY_BG,
            fg=HINT,
            font=("Segoe UI", 11),
            anchor="e",
            width=26,
        )
        self.status_label.pack(fill="x", pady=(0, 4))

        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_var,
            bg=DISPLAY_BG,
            fg=TEXT,
            font=("Segoe UI", 26, "bold"),
            anchor="e",
            width=14,
        )
        self.display_label.pack(fill="x")

    def _build_buttons(self) -> None:
        """Создаёт сетку плоских кнопок калькулятора."""
        grid_frame = tk.Frame(self.root, bg=BG)
        grid_frame.pack(padx=14, pady=(0, 14))

        for col in range(4):
            grid_frame.columnconfigure(col, minsize=78)
        for row in range(6):
            grid_frame.rowconfigure(row, minsize=58)

        for r, row_items in enumerate(BUTTONS):
            for c, (label, action, style) in enumerate(row_items):
                cmd = self._make_button_command(action)
                btn = FlatButton(grid_frame, text=label, command=cmd, style=style)
                btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

        eq_btn = FlatButton(
            grid_frame,
            text="=",
            command=lambda: self.on_equals and self.on_equals(),
            style="eq",
        )
        eq_btn.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=4, pady=(6, 4))

    def _make_button_command(self, action: str) -> Callable[[], None]:
        """Возвращает функцию-обработчик для кнопки по её действию.

        Args:
            action: Код действия ('clear', 'back' или символ для добавления).

        Returns:
            Функция без аргументов для привязки к кнопке.
        """
        if action == "clear":
            return lambda: self.on_clear and self.on_clear()
        if action == "back":
            return lambda: self.on_backspace and self.on_backspace()
        return lambda: self.on_char and self.on_char(action)

    def _bind_keys(self) -> None:
        """Привязывает клавиши клавиатуры к кнопкам калькулятора."""
        self.root.bind("<Key>", self._on_key_press)

    def _on_key_press(self, event: tk.Event) -> None:
        """Обрабатывает нажатия клавиш с клавиатуры (цифры, операции, Enter, BackSpace, Esc).

        Args:
            event: Событие нажатия клавиши.
        """
        if event.keysym in ("Return", "KP_Enter") or event.char == "=":
            if self.on_equals:
                self.on_equals()
        elif event.keysym == "BackSpace":
            if self.on_backspace:
                self.on_backspace()
        elif event.keysym == "Escape" or event.char.lower() == "c":
            if self.on_clear:
                self.on_clear()
        elif event.char.lower() in ("r", "v"):
            if self.on_char:
                self.on_char("√")
        elif event.char in "0123456789+-*/().":
            if self.on_char:
                self.on_char(event.char)
        elif event.char == ",":
            if self.on_char:
                self.on_char(".")

    def set_display(self, text: str) -> None:
        """Обновляет основной экран калькулятора.

        Args:
            text: Строка текущего выражения или результата.
        """
        self.display_var.set(text)

    def set_status(self, text: str, is_error: bool = False) -> None:
        """Обновляет верхнюю строку дисплея (история выражения или ошибка).

        Args:
            text: Текст статуса или сообщения об ошибке.
            is_error: Если True, текст окрашивается в красный цвет ошибки.
        """
        self.status_label.config(fg=ERROR if is_error else HINT)
        self.status_var.set(text)

    def run(self) -> None:
        """Запускает главный цикл обработки событий Tkinter."""
        self.root.mainloop()