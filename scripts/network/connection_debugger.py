"""Объединенный отладчик соединений"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil


class ConnectionDebugger:
    """Отладчик TCP соединений"""

    def __init__(self, port: int = 5000):
        self.port = port
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

    def get_connections_info(self) -> Dict[str, Any]:
        """Собирает информацию о соединениях на порту"""
        connections = []

        for conn in psutil.net_connections():
            try:
                if hasattr(conn, "laddr") and conn.laddr and hasattr(conn.laddr, "port"):
                    if conn.laddr.port == self.port:
                        proc_info = self._get_process_info(conn.pid)
                        raddr_str = self._format_remote_addr(conn)

                        connections.append(
                            {
                                "timestamp": datetime.now().isoformat(),
                                "laddr": f"{conn.laddr.ip}:{conn.laddr.port}",
                                "raddr": raddr_str,
                                "status": conn.status,
                                "pid": conn.pid,
                                "process": proc_info,
                            }
                        )
            except (AttributeError, IndexError):
                continue

        # Дополнительно через netstat
        netstat_lines = self._get_netstat_info()

        return {
            "timestamp": datetime.now().isoformat(),
            "port": self.port,
            "psutil_connections": connections,
            "netstat_lines": netstat_lines,
        }

    def trace_connections(self, duration: int = 300, interval: int = 5) -> List[Dict]:
        """Трассировка соединений в реальном времени"""
        print(f"🔍 Трассировка порта {self.port} в течение {duration}с...")

        start_time = time.time()
        data_log = []

        while (time.time() - start_time) < duration:
            info = self.get_connections_info()
            data_log.append(info)

            conn_count = len(info["psutil_connections"])
            zombie_count = sum(1 for c in info["psutil_connections"] if c["process"] == "ZOMBIE")

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"⏰ {timestamp} | Соединений: {conn_count} | Зомби: {zombie_count}")

            # Детальный вывод зомби-соединений
            if zombie_count > 0:
                print("   🧟 ЗОМБИ-СОЕДИНЕНИЯ:")
                for conn in info["psutil_connections"]:
                    if conn["process"] == "ZOMBIE":
                        print(
                            f"     PID:{conn['pid']} {conn['laddr']} ->"
                            f" {conn['raddr']} ({conn['status']})"
                        )

            time.sleep(interval)

        # Сохраняем логи
        self._save_logs(data_log)
        return data_log

    def _get_process_info(self, pid: Optional[int]) -> Union[Dict[str, Any], str]:
        """Получает информацию о процессе"""
        if not pid:
            return "NO_PID"

        try:
            proc = psutil.Process(pid)
            return {
                "name": proc.name(),
                "cmdline": proc.cmdline(),
                "status": proc.status(),
                "create_time": proc.create_time(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "ZOMBIE"

    def _format_remote_addr(self, conn) -> str:
        """Форматирует удаленный адрес"""
        if hasattr(conn, "raddr") and conn.raddr and hasattr(conn.raddr, "ip"):
            return f"{conn.raddr.ip}:{conn.raddr.port}"
        return "N/A"

    def _get_netstat_info(self) -> List[str]:
        """Получает информацию через netstat"""
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=10)
            return [line for line in result.stdout.split("\n") if f":{self.port}" in line]
        except:
            return []

    def _save_logs(self, data_log: List[Dict]):
        """Сохраняет логи в файлы"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.logs_dir / f"connections_debug_{timestamp}.json"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data_log, f, indent=2, ensure_ascii=False)

        print(f"📁 Логи сохранены в {json_file}")


def trace_port_connections(port: int = 5000, duration: int = 60) -> None:
    """Простая функция для трассировки порта"""
    debugger = ConnectionDebugger(port)
    debugger.trace_connections(duration, interval=2)


def main():
    """CLI для отладки соединений"""
    import argparse

    parser = argparse.ArgumentParser(description="Отладка TCP соединений")
    parser.add_argument("--port", type=int, default=5000, help="Порт для мониторинга")
    parser.add_argument("--duration", type=int, default=300, help="Длительность мониторинга")
    parser.add_argument("--interval", type=int, default=5, help="Интервал проверки")
    parser.add_argument("--once", action="store_true", help="Однократная проверка")

    args = parser.parse_args()

    debugger = ConnectionDebugger(args.port)

    if args.once:
        info = debugger.get_connections_info()
        print(f"📊 Текущее состояние порта {args.port}:")
        print(f"  Соединений: {len(info['psutil_connections'])}")
        for conn in info["psutil_connections"]:
            status = "🧟 ЗОМБИ" if conn["process"] == "ZOMBIE" else "✅ ЖИВОЙ"
            print(f"  {status} PID:{conn['pid']} {conn['laddr']} -> {conn['raddr']}")
    else:
        debugger.trace_connections(args.duration, args.interval)


if __name__ == "__main__":
    main()
