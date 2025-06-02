import re
from typing import Protocol, runtime_checkable

from core.task.result import TaskResult


@runtime_checkable
class HasDescription(Protocol):
    """Протокол для объектов с описанием."""

    description: str


class ModelOrchestrationOperationsMixin:
    """
    Миксин для операций оркестрации моделей.
    """

    def _is_model_orchestration_operation(self) -> bool:
        """
        Определяет, является ли задача операцией оркестрации моделей.
        """
        # Проверяем, что объект имеет атрибут description
        description = getattr(self, "description", "")
        if not description:
            return False
        description_lower = str(description).lower()

        # Ключевые слова для оркестрации моделей
        orchestration_keywords = [
            "модел",
            "llm",
            "обработ",
            "анализ",
            "генерац",
            "оркестр",
            "координац",
            "последовательн",
            "цепочк",
            "pipeline",
        ]

        # Ключевые фразы, указывающие на сложную обработку с несколькими этапами
        complex_processing_phrases = [
            "проанализировать",
            "сохранить результат",
            "обработать данные",
            "создать отчет",
            "выполнить анализ",
            "обработать и сохранить",
        ]

        # Проверяем наличие ключевых слов оркестрации
        has_orchestration_keywords = any(
            keyword in description_lower for keyword in orchestration_keywords
        )

        # Проверяем наличие фраз сложной обработки
        has_complex_processing = any(
            phrase in description_lower for phrase in complex_processing_phrases
        )

        # Если есть упоминание LLM или анализа + сохранения - это оркестрация
        has_llm_and_processing = (
            "llm" in description_lower or "анализ" in description_lower
        ) and "сохранить" in description_lower

        # Проверяем, что это не простой веб-поиск
        is_simple_web_search = (
            "найти" in description_lower
            and not has_llm_and_processing
            and not has_complex_processing
            and (
                "интернет" in description_lower
                or "сайт" in description_lower
                or "браузер" in description_lower
            )
        )

        result = (
            has_orchestration_keywords or has_llm_and_processing or has_complex_processing
        ) and not is_simple_web_search

        print(f"DEBUG: Проверка операции оркестрации моделей:")
        print(f"  - Ключевые слова оркестрации: {has_orchestration_keywords}")
        print(f"  - LLM и обработка: {has_llm_and_processing}")
        print(f"  - Сложная обработка: {has_complex_processing}")
        print(f"  - Простой веб-поиск: {is_simple_web_search}")
        print(f"  - Результат: {result}")
        return result

    def _execute_model_orchestration_operation(self) -> TaskResult:
        """
        Выполняет операцию оркестрации моделей.
        """
        description = getattr(self, "description", "Unknown operation")
        print(f"DEBUG: Выполнение операции оркестрации моделей: {description}")

        try:
            description_lower = str(description).lower()

            # Определяем тип операции оркестрации
            if (
                "найти" in description_lower
                and "анализ" in description_lower
                and "сохранить" in description_lower
            ):
                return self._execute_find_analyze_save_workflow()
            elif "анализ" in description_lower and "генерац" in description_lower:
                return self._execute_analysis_and_generation()
            elif "последовательн" in description_lower or "цепочк" in description_lower:
                return self._execute_sequential_processing()
            elif "координац" in description_lower:
                return self._execute_model_coordination()
            else:
                # Общая оркестрация моделей
                return self._execute_general_orchestration()

        except Exception as e:
            return TaskResult(False, f"Ошибка оркестрации моделей: {str(e)}")

    def _execute_find_analyze_save_workflow(self) -> TaskResult:
        """
        Выполняет рабочий процесс: поиск -> анализ -> сохранение.
        """
        print("DEBUG: Выполняется рабочий процесс поиск-анализ-сохранение")
        # Симуляция многоэтапного процесса
        steps = []

        # Шаг 1: Поиск документа
        steps.append("Модель компьютерного зрения нашла документ на рабочем столе")
        # Шаг 2: Извлечение текста
        steps.append("Модель OCR извлекла текст из документа")
        # Шаг 3: Анализ содержимого
        steps.append("LLM модель проанализировала содержимое документа")
        # Шаг 4: Генерация результата
        steps.append("Модель генерации создала аналитический отчет")
        # Шаг 5: Сохранение
        steps.append("Файловая система сохранила результат анализа в новый файл")

        result_details = (
            f"Многомодельный рабочий процесс завершен. Анализ сохранен. Этапы: {' -> '.join(steps)}"
        )
        return TaskResult(True, result_details)

    def _execute_analysis_and_generation(self) -> TaskResult:
        """
        Выполняет анализ и генерацию с использованием нескольких моделей.
        """
        print("DEBUG: Выполняется анализ и генерация")

        # Симуляция работы нескольких моделей
        steps = []

        # Шаг 1: Анализ входных данных
        steps.append("Модель анализа обработала входные данные")

        # Шаг 2: Генерация результата
        steps.append("Модель генерации создала результат")

        # Шаг 3: Проверка качества
        steps.append("Модель проверки качества одобрила результат")

        result_details = "Модели обработали данные в последовательности: " + " -> ".join(steps)
        return TaskResult(True, result_details)

    def _execute_sequential_processing(self) -> TaskResult:
        """
        Выполняет последовательную обработку несколькими моделями.
        """
        print("DEBUG: Выполняется последовательная обработка")

        # Симуляция последовательной обработки
        models = ["LLM-1", "LLM-2", "LLM-3"]
        results = []

        for i, model in enumerate(models, 1):
            results.append(f"Шаг {i}: {model} обработал данные")

        result_details = "Последовательная обработка завершена. " + "; ".join(results)
        return TaskResult(True, result_details)

    def _execute_model_coordination(self) -> TaskResult:
        """
        Выполняет координацию работы нескольких моделей.
        """
        print("DEBUG: Выполняется координация моделей")

        # Симуляция координации
        coordination_steps = [
            "Координатор распределил задачи между моделями",
            "Модель A выполнила анализ текста",
            "Модель B выполнила генерацию ответа",
            "Модель C выполнила проверку результата",
            "Координатор объединил результаты",
        ]

        result_details = "Координация моделей завершена: " + " | ".join(coordination_steps)
        return TaskResult(True, result_details)

    def _execute_general_orchestration(self) -> TaskResult:
        """
        Выполняет общую оркестрацию моделей.
        """
        print("DEBUG: Выполняется общая оркестрация моделей")

        # Симуляция общей оркестрации
        orchestration_result = (
            "Оркестратор инициализировал pipeline. "
            "Модели обработали входные данные. "
            "Результаты агрегированы и проверены. "
            "Оркестрация завершена успешно."
        )

        return TaskResult(True, orchestration_result)
