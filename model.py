"""Модуль модели калькулятора (лексический анализ, синтаксический разбор и вычисления)."""

import math
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    """Лексема (токен) математического выражения.

    Attributes:
        type: Тип лексемы ('NUMBER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'SQRT', 'LPAREN', 'RPAREN').
        value: Строковое значение лексемы.
    """

    type: str
    value: str

class Lexer:
    """Лексический анализатор для разбиения строки выражения на список лексем."""

    _SINGLE_CHAR_TOKENS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MUL",
        "/": "DIV",
        "(": "LPAREN",
        ")": "RPAREN",
        "√": "SQRT",
    }

    @classmethod
    def tokenize(cls, expression: str) -> List[Token]:
        """Разбивает входную строку на последовательность лексем.

        Args:
            expression: Строка математического выражения.

        Returns:
            Список объектов Token.

        Raises:
            ValueError: Если выражение пустое, содержит лишние точки
                или недопустимые символы.
        """
        cleaned = expression.strip().replace(",", ".")
        if not cleaned:
            raise ValueError("Введите выражение")

        tokens: List[Token] = []
        i = 0
        length = len(cleaned)

        while i < length:
            ch = cleaned[i]

            if ch.isspace():
                i += 1
                continue

            if ch.isdigit() or ch == ".":
                start = i
                dot_count = 0
                while i < length and (cleaned[i].isdigit() or cleaned[i] == "."):
                    if cleaned[i] == ".":
                        dot_count += 1
                        if dot_count > 1:
                            raise ValueError("Лишняя точка в числе")
                    i += 1

                num_str = cleaned[start:i]
                if num_str == ".":
                    raise ValueError("Некорректное число '.'")
                tokens.append(Token("NUMBER", num_str))
                continue

            if ch in cls._SINGLE_CHAR_TOKENS:
                tokens.append(Token(cls._SINGLE_CHAR_TOKENS[ch], ch))
                i += 1
                continue

            raise ValueError(f"Недопустимый символ '{ch}'")

        return tokens

class RecursiveDescentParser:
    """Синтаксический анализатор и вычислитель методом рекурсивного спуска.

    Грамматика (по возрастанию приоритета операций):
        expression -> term ( ('+' | '-') term )*
        term       -> factor ( ('*' | '/') factor )*
        factor     -> ('+' | '-' | '√') factor | primary
        primary    -> NUMBER | '(' expression ')'
    """

    def __init__(self, tokens: List[Token]):
        """Инициализирует парсер списком лексем.

        Args:
            tokens: Список лексем от Lexer.tokenize.
        """
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Optional[Token]:
        """Возвращает текущую лексему или None, если достигнут конец."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self) -> Token:
        """Возвращает текущую лексему и переходит к следующей."""
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse(self) -> float:
        """Разбирает всё выражение и проверяет отсутствие лишних лексем.

        Returns:
            Итоговое вычисленное значение.

        Raises:
            ValueError: При синтаксической ошибке, делении на 0
                или извлечении корня из отрицательного числа.
        """
        result = self._parse_expression()
        leftover = self._current()
        if leftover is not None:
            if leftover.type == "RPAREN":
                raise ValueError("Лишняя закрывающая скобка ')'")
            raise ValueError(f"Пропущен знак перед '{leftover.value}'")
        return result

    def _parse_expression(self) -> float:
        """Разбирает сложение и вычитание."""
        value = self._parse_term()

        while (token := self._current()) is not None and token.type in ("PLUS", "MINUS"):
            self._consume()
            right = self._parse_term()
            if token.type == "PLUS":
                value += right
            else:
                value -= right

        return value

    def _parse_term(self) -> float:
        """Разбирает умножение и деление."""
        value = self._parse_factor()

        while (token := self._current()) is not None and token.type in ("MUL", "DIV"):
            self._consume()
            right = self._parse_factor()
            if token.type == "MUL":
                value *= right
            else:
                if right == 0:
                    raise ValueError("Деление на ноль невозможно")
                value /= right

        return value

    def _parse_factor(self) -> float:
        """Разбирает унарные операции (+, -, √) и первичные выражения."""
        token = self._current()
        if token is None:
            raise ValueError("Незаконченное выражение")

        if token.type == "PLUS":
            self._consume()
            return self._parse_factor()

        if token.type == "MINUS":
            self._consume()
            return -self._parse_factor()

        if token.type == "SQRT":
            self._consume()
            operand = self._parse_factor()
            if operand < 0:
                raise ValueError("Корень из отрицательного числа")
            return math.sqrt(operand)

        return self._parse_primary()

    def _parse_primary(self) -> float:
        """Разбирает число или выражение в скобках."""
        token = self._current()
        if token is None:
            raise ValueError("Ожидалось число или '('")

        if token.type == "NUMBER":
            self._consume()
            return float(token.value)

        if token.type == "LPAREN":
            self._consume()
            value = self._parse_expression()
            closing = self._current()
            if closing is None or closing.type != "RPAREN":
                raise ValueError("Не хватает закрывающей скобки ')'")
            self._consume()
            return value

        raise ValueError(f"Некорректная операция '{token.value}'")

class CalculatorModel:
    """Модель калькулятора, объединяющая лексер, парсер и форматирование результата."""

    @staticmethod
    def format_result(value: float) -> str:
        """Форматирует числовой результат в строку без лишних нулей.

        Args:
            value: Числовой результат вычисления.

        Returns:
            Отформатированная строка результата.

        Raises:
            ValueError: Если число бесконечно или не определено.
        """
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Число вне допустимых пределов")

        rounded = round(value, 10)
        if rounded == 0:
            return "0"
        if rounded.is_integer() and abs(rounded) < 1e15:
            return str(int(rounded))
        return f"{rounded:g}"

    def evaluate(self, expression: str) -> str:
        """Выполняет лексический и синтаксический разбор выражения и возвращает результат.

        Args:
            expression: Строка с выражением.

        Returns:
            Отформатированный результат вычисления.

        Raises:
            ValueError: При любой ошибке валидации или вычисления.
        """
        tokens = Lexer.tokenize(expression)
        parser = RecursiveDescentParser(tokens)
        try:
            result = parser.parse()
        except OverflowError:
            raise ValueError("Слишком большое число")
        return self.format_result(result)