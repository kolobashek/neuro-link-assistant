# Запуск всех тестов
python -m pytest tests/unit/ -v

# Запуск только определенных групп тестов
# python -m pytest tests/unit/core/web/ -v
# python -m pytest tests/unit/core/web/test_dom_search.py -v

# С покрытием кода
# python -m pytest tests/unit/ -v --cov=core
