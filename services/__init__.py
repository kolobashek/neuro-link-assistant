# Экспорт всех сервисов для удобного импорта
from .ai_service import *
from .browser_service import *
from .command_service import *
from .huggingface_service import *

# Новые сервисы
try:
    from .analytics_service import AnalyticsService
    from .system_monitor_service import SystemMonitorService

    __all__ = ["AnalyticsService", "SystemMonitorService"]
except ImportError as e:
    # Если новые сервисы не найдены, продолжаем без них
    __all__ = []
