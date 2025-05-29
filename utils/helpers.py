import logging
import re
import time

logger = logging.getLogger("neuro_assistant")


def extract_code_from_response(response):
    """Извлекает код Python из ответа нейросети"""
    if not response:
        return None

    # Ищем код между тройными обратными кавычками
    code_start = response.find("")
    if code_start != -1:
        code_start += 9  # длина "python"
        code_end = response.find("", code_start)
        if code_end != -1:
            return response[code_start:code_end].strip()

    # Если не нашли с указанием языка, ищем просто между тройными кавычками
    code_start = response.find("")
    if code_start != -1:
        code_start += 3  # длина ""
        code_end = response.find("", code_start)
        if code_end != -1:
            return response[code_start:code_end].strip()

    return None


def extract_math_expression(text):
    """Извлекает математическое выражение из текста"""
    # Ищем числа и математические операторы
    pattern = r"(\d+\s*[\+\-\*\/]\s*\d+)"
    matches = re.findall(pattern, text)

    if matches:
        return matches[0].replace(" ", "")

    return None


def add_interrupt_checks(code):
    """
    Добавляет проверки прерывания в код

    Вставляет проверки check_interrupt() после каждого вызова time.sleep()
    и в начало каждого цикла for/while
    """
    if not code:
        return code

    # Добавляем проверку после каждого time.sleep()
    code = re.sub(
        r"(time\.sleep\([^)]+\))",
        r'\1\n    if check_interrupt(): return "Выполнение прервано пользователем"',
        code,
    )

    # Добавляем проверку в начало каждого цикла for
    code = re.sub(
        r"(for\s+[^:]+:)",
        r'\1\n    if check_interrupt(): return "Выполнение прервано пользователем"',
        code,
    )

    # Добавляем проверку в начало каждого цикла while
    code = re.sub(
        r"(while\s+[^:]+:)",
        r'\1\n    if check_interrupt(): return "Выполнение прервано пользователем"',
        code,
    )

    # Добавляем проверку в начало кода
    code = 'if check_interrupt(): return "Выполнение прервано пользователем"\n' + code

    return code


def check_interrupt_during_operation(operation_name, interval=0.5, max_time=30):
    """
    Выполняет проверку прерывания во время длительных операций

    Args:
        operation_name: Название операции для логирования
        interval: Интервал проверки в секундах
        max_time: Максимальное время выполнения в секундах

    Returns:
        True, если операция должна быть прервана, False в противном случае
    """
    from app import command_interrupt_flag
    from utils.logging_utils import detailed_logger

    start_time = time.time()
    elapsed_time = 0

    while elapsed_time < max_time:
        # Проверяем флаг прерывания
        if command_interrupt_flag:
            detailed_logger.info(
                f"Операция '{operation_name}' прервана пользователем после"
                f" {elapsed_time:.1f} секунд"
            )
            return True

        # Ждем указанный интервал
        time.sleep(interval)

        # Обновляем прошедшее время
        elapsed_time = time.time() - start_time

    # Если превышено максимальное время
    detailed_logger.warning(
        f"Операция '{operation_name}' превысила максимальное время выполнения ({max_time} секунд)"
    )
    return False
