import os
import platform
import socket

import psutil
import wmi


class SystemInfo:
    """
    Класс для получения системной информации Windows.
    """

    def __init__(self):
        """Инициализация класса системной информации."""
        try:
            self.wmi_client = wmi.WMI()
        except Exception as e:
            print(f"Error initializing WMI: {e}")
            self.wmi_client = None

    def get_os_info(self):
        """
        Получает информацию об операционной системе.

        Returns:
            dict: Информация об ОС
        """
        try:
            os_info = {}

            # Базовая информация из модуля platform
            os_info["name"] = platform.system()
            os_info["version"] = platform.version()
            os_info["release"] = platform.release()
            os_info["architecture"] = platform.architecture()[0]

            # Дополнительная информация из WMI
            if self.wmi_client:
                for os_data in self.wmi_client.Win32_OperatingSystem():
                    os_info["build"] = os_data.BuildNumber
                    os_info["caption"] = os_data.Caption
                    os_info["install_date"] = os_data.InstallDate
                    os_info["last_boot"] = os_data.LastBootUpTime
                    os_info["manufacturer"] = os_data.Manufacturer
                    break

            return os_info
        except Exception as e:
            print(f"Error getting OS info: {e}")
            return {"name": "Windows", "error": str(e)}

    def get_cpu_info(self):
        """
        Получает информацию о процессоре.

        Returns:
            dict: Информация о CPU
        """
        try:
            cpu_info = {}

            # Базовая информация из psutil
            cpu_info["cores_physical"] = psutil.cpu_count(logical=False)
            cpu_info["cores_logical"] = psutil.cpu_count(logical=True)
            cpu_info["usage"] = psutil.cpu_percent(interval=0.1)
            cpu_info["frequency"] = psutil.cpu_freq().current if psutil.cpu_freq() else None

            # Дополнительная информация из WMI
            if self.wmi_client:
                for processor in self.wmi_client.Win32_Processor():
                    cpu_info["name"] = processor.Name
                    cpu_info["manufacturer"] = processor.Manufacturer
                    cpu_info["architecture"] = processor.Architecture
                    cpu_info["max_clock_speed"] = processor.MaxClockSpeed
                    break

            return cpu_info
        except Exception as e:
            print(f"Error getting CPU info: {e}")
            return {"cores": psutil.cpu_count(), "usage": psutil.cpu_percent(), "error": str(e)}

    def get_memory_info(self):
        """
        Получает информацию о памяти.

        Returns:
            dict: Информация о памяти
        """
        try:
            memory = psutil.virtual_memory()

            memory_info = {
                "total": round(memory.total / (1024 * 1024), 2),  # MB
                "available": round(memory.available / (1024 * 1024), 2),  # MB
                "used": round(memory.used / (1024 * 1024), 2),  # MB
                "used_percent": memory.percent,
            }

            # Информация о подкачке
            swap = psutil.swap_memory()
            memory_info["swap_total"] = round(swap.total / (1024 * 1024), 2)  # MB
            memory_info["swap_used"] = round(swap.used / (1024 * 1024), 2)  # MB
            memory_info["swap_percent"] = swap.percent

            return memory_info
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return {"error": str(e)}

    def get_disk_info(self):
        """
        Получает информацию о дисках.

        Returns:
            dict: Информация о дисках
        """
        try:
            disk_info = {}

            for partition in psutil.disk_partitions():
                if os.name == "nt" and ("cdrom" in partition.opts or partition.fstype == ""):
                    # Пропускаем CD-ROM и неподключенные диски
                    continue

                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": round(usage.total / (1024 * 1024), 2),  # MB
                        "free": round(usage.free / (1024 * 1024), 2),  # MB
                        "used": round(usage.used / (1024 * 1024), 2),  # MB
                        "used_percent": usage.percent,
                    }
                except PermissionError:
                    # Некоторые диски могут быть недоступны
                    continue

            return disk_info
        except Exception as e:
            print(f"Error getting disk info: {e}")
            return {"error": str(e)}

    def get_network_info(self):
        """
        Получает информацию о сетевых интерфейсах.

        Returns:
            dict: Информация о сетевых интерфейсах
        """
        try:
            network_info = {
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "interfaces": {},
            }

            # Получаем информацию о сетевых интерфейсах
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                addresses = []
                for address in interface_addresses:
                    addresses.append(
                        {
                            "family": str(address.family),
                            "address": address.address,
                            "netmask": address.netmask,
                            "broadcast": address.broadcast,
                        }
                    )

                network_info["interfaces"][interface_name] = {"addresses": addresses}

            # Добавляем статистику использования сети
            net_io = psutil.net_io_counters(pernic=True)
            for interface_name, stats in net_io.items():
                if interface_name in network_info["interfaces"]:
                    network_info["interfaces"][interface_name]["stats"] = {
                        "bytes_sent": stats.bytes_sent,
                        "bytes_recv": stats.bytes_recv,
                        "packets_sent": stats.packets_sent,
                        "packets_recv": stats.packets_recv,
                        "errin": stats.errin,
                        "errout": stats.errout,
                        "dropin": stats.dropin,
                        "dropout": stats.dropout,
                    }

            return network_info
        except Exception as e:
            print(f"Error getting network info: {e}")
            return {"hostname": socket.gethostname(), "error": str(e)}
