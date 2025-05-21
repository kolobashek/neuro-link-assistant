"""
Модуль-адаптер для обеспечения обратной совместимости.
Перенаправляет запросы к WindowsMouse.
"""

import warnings

from core.platform.windows.input.mouse import WindowsMouse

# Выдаем предупреждение о том, что модуль устарел
warnings.warn(
    "Модуль core.input.mouse_controller устарел и будет удален в будущих версиях. "
    "Используйте core.platform.windows.input.mouse или core.common.input.factory вместо него.",
    DeprecationWarning,
    stacklevel=2,
)

# Для обратной совместимости
MouseController = WindowsMouse
