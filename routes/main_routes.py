from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Список доступных команд с иконками и описаниями
    commands = [
        {
            "main": "открой",
            "alternatives": ["запусти", "открыть"],
            "description": "Открывает программу или файл",
            "icon": "folder-open",
        },
        {
            "main": "найди",
            "alternatives": ["поиск", "найти"],
            "description": "Поиск файлов или информации",
            "icon": "search",
        },
        {
            "main": "установи",
            "alternatives": ["инсталлируй", "установить"],
            "description": "Установка программ и пакетов",
            "icon": "download",
        },
        {
            "main": "скачай",
            "alternatives": ["загрузи", "скачать"],
            "description": "Скачивание файлов из интернета",
            "icon": "cloud-download-alt",
        },
        {
            "main": "напиши",
            "alternatives": ["создай текст", "напиши текст"],
            "description": "Создание текстовых документов",
            "icon": "file-alt",
        },
        {
            "main": "помоги",
            "alternatives": ["справка", "помощь"],
            "description": "Получение справки по использованию",
            "icon": "question-circle",
        },
        # Добавьте остальные команды
    ]

    return render_template("index.html", commands=commands)


# Добавить новые маршруты:
@main_bp.route("/ai_models")
def ai_models():
    return render_template("ai_models.html")


@main_bp.route("/history")
def history():
    return render_template("history.html")


@main_bp.route("/settings")
def settings():
    return render_template("settings.html")


@main_bp.route("/logs")
def logs():
    return render_template("logs.html")
