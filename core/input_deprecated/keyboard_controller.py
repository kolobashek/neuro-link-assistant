"""
Модуль-адаптер для обеспечения обратной совместимости.
Перенаправляет запросы к WindowsKeyboard.
"""

import warnings

from core.platform.windows.input.keyboard import WindowsKeyboard

# Выдаем предупреждение о том, что модуль устарел
warnings.warn(
    "Модуль core.input.keyboard_controller устарел и будет удален в будущих версиях. "
    "Используйте core.platform.windows.input.keyboard или core.common.input.factory вместо него.",
    DeprecationWarning,
    stacklevel=2,
)

# Для обратной совместимости
KeyboardController = WindowsKeyboard
