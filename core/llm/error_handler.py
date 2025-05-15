# -*- coding: utf-8 -*-
# Реэкспорт из нового местоположения
from core.common.error_handler import handle_error, handle_llm_error

# Для обеспечения обратной совместимости
__all__ = ["handle_llm_error", "handle_error"]
