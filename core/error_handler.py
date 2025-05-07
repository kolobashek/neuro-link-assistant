# -*- coding: utf-8 -*-
# Реэкспорт из нового местоположения
from core.common.error_handler import handle_error, handle_warning, handle_llm_error, ErrorHandler

# Для обеспечения обратной совместимости
__all__ = ['handle_error', 'handle_warning', 'handle_llm_error', 'ErrorHandler']
