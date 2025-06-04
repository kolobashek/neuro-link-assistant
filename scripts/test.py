import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime

import psutil  # Добавить этот импорт


def run_ui_parallel():
    """Структурированное логирование с управлением приложением"""
    from scripts.app_manager import AppManager

    os.environ["HEADLESS"] = "true"
    os.makedirs("logs", exist_ok=True)

    # Инициализация менеджера приложения
    app_manager = AppManager()

    start_time = time.time()

    # Метаданные сессии
    session_info = {
        "session_id": f"ui_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "test_type": "ui_parallel",
        "timestamp_start": datetime.now().isoformat(),
        "environment": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version.split()[0],
            "working_dir": os.getcwd(),
            "cpu_count": os.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "headless_mode": True,
            "parallel_workers": 2,
        },
        "pytest_args": ["tests/ui/e2e/", "-v", "-n", "2", "--tb=short"],
    }

    # Имена файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/ui_parallel_{timestamp}.log"
    json_file = f"logs/ui_parallel_{timestamp}.json"
    junit_file = f"logs/ui_parallel_{timestamp}_junit.xml"

    print(f"🚀 [UI TESTS] Starting parallel execution...")
    print(f"🔍 [APP] Checking application status...")

    # Проверяем приложение перед тестами
    if not app_manager.is_app_running():
        print(f"⚠️ [APP] Application not running, attempting to start...")
        if not app_manager.start_app():
            print(f"❌ [APP] Failed to start application!")
            sys.exit(1)

    try:
        print(f"🆔 [SESSION] ID: {session_info['session_id']}")
        print(f"📝 [LOGGING] Text log: {log_file}")
        print(f"📊 [LOGGING] JSON report: {json_file}")
        print(f"📋 [LOGGING] JUnit XML: {junit_file}")
        print(
            f"🖥️  [SYSTEM] {session_info['environment']['platform']} | "
            f"Python {session_info['environment']['python_version']} | "
            f"{session_info['environment']['cpu_count']} CPUs | "
            f"{session_info['environment']['memory_gb']}GB RAM"
        )

        # Записываем начальные метаданные в JSON
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"session_start": session_info}, f, indent=2, ensure_ascii=False)

        # Выполняем тесты с детальным логированием
        with open(log_file, "w", encoding="utf-8") as f:
            # Записываем заголовок сессии
            f.write(f"{'='*80}\n")
            f.write(f"NEURO-LINK ASSISTANT - UI TESTS PARALLEL EXECUTION\n")
            f.write(f"{'='*80}\n")
            f.write(f"Session ID: {session_info['session_id']}\n")
            f.write(f"Started: {session_info['timestamp_start']}\n")
            f.write(
                "Platform:"
                f" {session_info['environment']['platform']} {session_info['environment']['platform_version']}\n"
            )
            f.write(f"Python: {session_info['environment']['python_version']}\n")
            f.write(f"Working Dir: {session_info['environment']['working_dir']}\n")
            f.write(f"Parallel Workers: {session_info['environment']['parallel_workers']}\n")
            f.write(f"Headless Mode: {session_info['environment']['headless_mode']}\n")
            f.write(f"{'='*80}\n\n")

            print(f"⏱️  [EXECUTION] Starting pytest with app monitoring...")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/ui/e2e/",
                    "-v",
                    "-n",
                    "2",
                    "--tb=short",
                    "--color=yes",
                    f"--junit-xml={junit_file}",
                    "--durations=10",  # Показать 10 самых медленных тестов
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )

            # Записываем результат
            f.write("PYTEST OUTPUT:\n")
            f.write("-" * 40 + "\n")
            f.write(result.stdout)
            f.write("\n" + "-" * 40 + "\n")

            end_time = time.time()
            duration = round(end_time - start_time, 2)

            f.write(f"\nSESSION SUMMARY:\n")
            f.write(f"{'='*80}\n")
            f.write(f"Ended: {datetime.now().isoformat()}\n")
            f.write(f"Duration: {duration} seconds\n")
            f.write(f"Exit Code: {result.returncode}\n")
            f.write(f"Status: {'PASSED' if result.returncode == 0 else 'FAILED'}\n")
            f.write(f"{'='*80}\n")

            # Консольный вывод с категоризацией
            print(f"📋 [TEST OUTPUT]")
            lines = result.stdout.split("\n")

            for line in lines:
                if line.strip():
                    # Категоризируем вывод
                    if "PASSED" in line:
                        print(f"   ✅ {line}")
                    elif "FAILED" in line:
                        print(f"   ❌ {line}")
                    elif "ERROR" in line:
                        print(f"   🔥 {line}")
                    elif "WARNING" in line or "WARN" in line:
                        print(f"   ⚠️  {line}")
                    elif "collecting" in line.lower():
                        print(f"   🔍 {line}")
                    elif "session starts" in line:
                        print(f"   🎬 {line}")
                    elif "=" in line and len(line) > 50:
                        print(f"   📏 {line}")
                    else:
                        print(f"   📄 {line}")

    except KeyboardInterrupt:
        print(f"\n⚠️ [INTERRUPTED] Tests interrupted, cleaning up...")
        app_manager.stop_app()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ [ERROR] Test execution failed: {e}")
        sys.exit(1)
    finally:
        # Проверяем состояние приложения после тестов
        if app_manager.is_app_running():
            print(f"✅ [APP] Application still running after tests")
        else:
            print(f"⚠️ [APP] Application stopped during tests")

    # Парсим результаты для JSON
    test_results = _parse_pytest_output(result.stdout)

    # Финальные метаданные
    session_info.update(
        {
            "timestamp_end": datetime.now().isoformat(),
            "duration_seconds": duration,
            "exit_code": result.returncode,
            "status": "PASSED" if result.returncode == 0 else "FAILED",
            "test_results": test_results,
            "files_generated": {
                "text_log": log_file,
                "json_report": json_file,
                "junit_xml": junit_file,
            },
        }
    )

    # Обновляем JSON с полными результатами
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(session_info, f, indent=2, ensure_ascii=False)

    # Детальная статистика
    print(f"\n📊 [SUMMARY]")
    print(f"   🆔 Session: {session_info['session_id']}")
    print(f"   ⏱️  Duration: {duration}s")
    print(f"   📈 Status: {'✅ PASSED' if result.returncode == 0 else '❌ FAILED'}")
    if test_results:
        print(
            f"   📋 Tests: {test_results.get('total', 0)} total, "
            f"{test_results.get('passed', 0)} passed, "
            f"{test_results.get('failed', 0)} failed"
        )
    print(f"\n📁 [FILES GENERATED]")
    print(f"   📝 Text Log: {log_file}")
    print(f"   📊 JSON Report: {json_file}")
    print(f"   📋 JUnit XML: {junit_file}")

    sys.exit(result.returncode)


def _parse_pytest_output(output):
    """Парсит вывод pytest для извлечения статистики"""
    results = {"total": 0, "passed": 0, "failed": 0, "errors": 0, "warnings": 0}

    for line in output.split("\n"):
        if " passed" in line and " failed" in line:
            # Строка типа "5 passed, 2 failed in 10.5s"
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed" and i > 0:
                    results["passed"] = int(parts[i - 1])
                elif part == "failed" and i > 0:
                    results["failed"] = int(parts[i - 1])
                elif part == "error" and i > 0:
                    results["errors"] = int(parts[i - 1])
        elif " passed in " in line:
            # Строка типа "5 passed in 10.5s"
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed" and i > 0:
                    results["passed"] = int(parts[i - 1])

    results["total"] = results["passed"] + results["failed"] + results["errors"]
    return results


def run_ui_headless():
    """Структурированное логирование обычных UI тестов"""
    os.environ["HEADLESS"] = "true"

    # Аналогично parallel, но без -n флага
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/ui_headless_{timestamp}.log"
    json_file = f"logs/ui_headless_{timestamp}.json"

    print(f"🧪 [UI TESTS] Starting headless execution...")
    print(f"📝 [LOGGING] Structured logs: {log_file}, {json_file}")

    start_time = time.time()

    with open(log_file, "w", encoding="utf-8") as f:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/ui/e2e/", "-v", "--tb=short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )

        f.write(result.stdout)
        print(result.stdout)

    # Сохраняем JSON отчет
    session_data = {
        "session_id": f"ui_headless_{timestamp}",
        "duration": round(time.time() - start_time, 2),
        "exit_code": result.returncode,
        "timestamp": datetime.now().isoformat(),
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    print(f"\n📊 Результат: {'✅ PASSED' if result.returncode == 0 else '❌ FAILED'}")
    print(f"📄 Логи: {log_file}, {json_file}")

    sys.exit(result.returncode)


def run_ui_normal():
    """Запуск UI тестов в обычном режиме"""
    os.environ.pop("HEADLESS", None)
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/ui/e2e/", "-v"])
    sys.exit(result.returncode)
