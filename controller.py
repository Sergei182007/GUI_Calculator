"""Модуль контроллера калькулятора (управляет состоянием ввода и связывает Model и View)."""

from model import CalculatorModel
from view import CalculatorView

MAX_EXPRESSION_LENGTH = 36

class CalculatorController:
    """Контроллер калькулятора, обрабатывающий нажатия кнопок и клавиш."""

    def __init__(self) -> None:
        """Инициализирует модель, представление и подписывается на события интерфейса."""
        self.model = CalculatorModel()
        self.view = CalculatorView()

        self.expression = ""
        self.just_evaluated = False

        self.view.on_char = self.handle_char
        self.view.on_equals = self.handle_equals
        self.view.on_clear = self.handle_clear
        self.view.on_backspace = self.handle_backspace

    def handle_char(self, char: str) -> None:
        """Добавляет символ с кнопки или клавиатуры в текущее выражение.

        Если только что был вычислен результат: при вводе оператора вычисления
        продолжаются от результата, при вводе цифры/скобки/корня начинается новый ввод.

        Args:
            char: Символ цифры, точки, скобки, корня или арифметической операции.
        """
        if self.just_evaluated:
            if char not in "+-*/":
                self.expression = ""
            self.just_evaluated = False

        if len(self.expression) >= MAX_EXPRESSION_LENGTH:
            self.view.set_status("Достигнута максимальная длина", is_error=True)
            return

        self.expression += char
        self.view.set_status("", is_error=False)
        self.view.set_display(self.expression)

    def handle_backspace(self) -> None:
        """Удаляет последний символ выражения или сбрасывает экран на '0'."""
        self.just_evaluated = False
        self.expression = self.expression[:-1]
        self.view.set_status("", is_error=False)
        self.view.set_display(self.expression if self.expression else "0")

    def handle_clear(self) -> None:
        """Полностью очищает текущее выражение, дисплей и статус."""
        self.expression = ""
        self.just_evaluated = False
        self.view.set_display("0")
        self.view.set_status("", is_error=False)

    def handle_equals(self) -> None:
        """Передаёт накопленное выражение в модель и выводит результат или ошибку."""
        try:
            result = self.model.evaluate(self.expression)
            self.view.set_status(f"{self.expression} =", is_error=False)
            self.view.set_display(result)
            self.expression = result
            self.just_evaluated = True
        except ValueError as err:
            self.view.set_status(str(err), is_error=True)
            self.just_evaluated = False

    def run(self) -> None:
        """Запускает приложение."""
        self.view.run()

if __name__ == "__main__":
    app = CalculatorController()
    app.run()