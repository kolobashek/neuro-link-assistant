"""
Модуль компьютерного зрения для взаимодействия с графическим интерфейсом
"""

from core.vision.element_localization import ElementLocalization
from core.vision.element_recognition import ElementRecognition
from core.vision.image_comparison import ImageComparison
from core.vision.screen_capture import ScreenCapture
from core.vision.screen_changes import ScreenChanges

__all__ = [
    "ScreenCapture",
    "ElementRecognition",
    "ElementLocalization",
    "ImageComparison",
    "ScreenChanges",
]
