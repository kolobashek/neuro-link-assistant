from flask import Blueprint, redirect, render_template, request

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


# ✅ ПЕРЕИМЕНОВАНО: ai_models → models
@main_bp.route("/models")
def models():
    return render_template("models.html")


@main_bp.route("/models/<model_id>/settings")
def model_settings(model_id):
    return render_template("model_settings.html", model_id=model_id)


@main_bp.route("/models/browser")
def browser_models():
    """Страница управления браузерными моделями."""
    return render_template("browser.html")


@main_bp.route("/history")
def history():
    return render_template("history.html")


# ✅ НОВЫЙ РОУТ: Детали элемента истории
@main_bp.route("/history/<item_id>")
def history_detail(item_id):
    # Заглушка данных команды (позже заменить на запрос к БД)
    command = {
        "id": item_id,
        "command": "открыть браузер" if item_id == "cmd-001" else f"команда {item_id}",
        "timestamp": "2025-06-17 14:30:15",
        "status": "Выполнено",
        "duration": "2.3 сек",
        "result": f"Команда {item_id} выполнена успешно. Браузер открыт.",
    }
    return render_template("history_details.html", command=command)


@main_bp.route("/settings")
def settings():
    return render_template("settings.html")


@main_bp.route("/logs")
def logs():
    return render_template("logs.html")


@main_bp.route("/help")
def help():
    return render_template("help.html")


@main_bp.route("/tasks")
def tasks():
    return render_template("tasks.html")


@main_bp.route("/tasks/<task_id>")
def task_details(task_id):
    return render_template("task_details.html", task_id=task_id)


@main_bp.route("/tasks/create", methods=["GET", "POST"])
def task_create():
    """Страница создания новой задачи."""
    if request.method == "POST":
        print(f"🔍 [DEBUG] POST data: {request.form}")
        print(f"🔍 [DEBUG] Content-Type: {request.content_type}")

        # Имитируем создание задачи
        import uuid

        task_id = f"task-{uuid.uuid4().hex[:8]}"

        print(f"🔍 [DEBUG] POST /tasks/create - перенаправляем на /tasks/{task_id}")
        return redirect(f"/tasks/{task_id}")

    print("🔍 [DEBUG] GET /tasks/create")
    return render_template("task_create.html")


@main_bp.route("/orchestrator")
def orchestrator():
    """Страница оркестратора моделей."""
    return render_template("orchestrator.html")


@main_bp.route("/workflows")
def workflows():
    """Страница шаблонов и рабочих процессов."""
    return render_template("workflows.html")


@main_bp.route("/analytics")
def analytics():
    return render_template("analytics.html")
