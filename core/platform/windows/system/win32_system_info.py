# -*- coding: utf-8 -*-
"""
Реализация получения системной информации для Windows.
"""
import os
import platform
import socket
from datetime import datetime
from typing import Any, Dict, Optional

import psutil
import wmi

from core.common.error_handler import handle_error
from core.common.system.base import AbstractSystemInfo


class Win32SystemInfo(AbstractSystemInfo):
    """
    Класс для получения системной информации Windows.
    """

    def __init__(self):
        """Инициализация класса системной информации."""
        try:
            self.wmi_client = wmi.WMI()
        except Exception as e:
            handle_error(f"Error initializing WMI: {e}", e, module="system")
            self.wmi_client = None

    def get_os_info(self) -> Dict[str, Any]:
        """
        Получает информацию об операционной системе.

        Returns:
            Dict[str, Any]: Информация об ОС
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
            handle_error(f"Error getting OS info: {e}", e, module="system")
            return {"name": "Windows", "error": str(e)}

    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Получает информацию о процессоре.

        Returns:
            Dict[str, Any]: Информация о CPU
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
            handle_error(f"Error getting CPU info: {e}", e, module="system")
            return {"cores": psutil.cpu_count(), "usage": psutil.cpu_percent(), "error": str(e)}

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Получает информацию о памяти.

        Returns:
            Dict[str, Any]: Информация о памяти
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
            handle_error(f"Error getting memory info: {e}", e, module="system")
            return {"error": str(e)}

    def get_disk_info(self) -> Dict[str, Any]:
        """
        Получает информацию о дисках.

        Returns:
            Dict[str, Any]: Информация о дисках
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
            handle_error(f"Error getting disk info: {e}", e, module="system")
            return {"error": str(e)}

    def get_network_info(self) -> Dict[str, Any]:
        """
        Получает информацию о сетевых интерфейсах.

        Returns:
            Dict[str, Any]: Информация о сетевых интерфейсах
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
            handle_error(f"Error getting network info: {e}", e, module="system")
            return {"hostname": socket.gethostname(), "error": str(e)}

    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о батарее (для ноутбуков).

        Returns:
            Optional[Dict[str, Any]]: Информация о батарее или None, если батарея отсутствует
        """
        try:
            if not hasattr(psutil, "sensors_battery") or psutil.sensors_battery() is None:
                return None

            battery = psutil.sensors_battery()

            battery_info = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secsleft": battery.secsleft,
            }

            # Преобразуем время работы в более читаемый формат

            if (
                battery.secsleft != psutil.POWER_TIME_UNLIMITED
                and battery.secsleft != psutil.POWER_TIME_UNKNOWN
            ):
                hours, remainder = divmod(battery.secsleft, 3600)
                minutes, seconds = divmod(remainder, 60)
                battery_info["time_left"] = f"{hours:02}:{minutes:02}:{seconds:02}"
            elif battery.secsleft == psutil.POWER_TIME_UNLIMITED:
                battery_info["time_left"] = "Неограниченно (подключено к сети)"
            else:
                battery_info["time_left"] = "Неизвестно"

            return battery_info
        except Exception as e:
            handle_error(f"Error getting battery info: {e}", e, module="system")
            return None

    def get_system_uptime(self) -> float:
        """
        Получает время работы системы в секундах.

        Returns:
            float: Время работы системы в секундах
        """
        try:
            return psutil.boot_time() - datetime.now().timestamp()
        except Exception as e:
            handle_error(f"Error getting system uptime: {e}", e, module="system")
            return 0.0

    def get_user_info(self) -> Dict[str, str]:
        """
        Получает информацию о текущем пользователе.

        Returns:
            Dict[str, str]: Информация о пользователе
        """
        try:
            user_info = {
                "username": os.getlogin(),
                "homedir": os.path.expanduser("~"),
                "domain": os.environ.get("USERDOMAIN", ""),
            }

            # Получаем дополнительную информацию из WMI
            if self.wmi_client:
                for user in self.wmi_client.Win32_ComputerSystem():
                    user_info["current_user"] = user.UserName
                    user_info["primary_owner"] = user.PrimaryOwnerName
                    break

            return user_info
        except Exception as e:
            handle_error(f"Error getting user info: {e}", e, module="system")
            return {"username": os.environ.get("USERNAME", "unknown"), "error": str(e)}

    def get_full_system_info(self) -> Dict[str, Any]:
        """
        Получает полную информацию о системе.

        Returns:
            Dict[str, Any]: Вся системная информация
        """
        try:
            system_info = {
                "os": self.get_os_info(),
                "cpu": self.get_cpu_info(),
                "memory": self.get_memory_info(),
                "disk": self.get_disk_info(),
                "network": self.get_network_info(),
                "user": self.get_user_info(),
                "uptime": self.get_system_uptime(),
            }

            # Добавляем информацию о батарее только если она есть
            battery_info = self.get_battery_info()
            if battery_info:
                system_info["battery"] = battery_info

            return system_info
        except Exception as e:
            handle_error(f"Error getting full system info: {e}", e, module="system")
            return {"error": str(e)}

    def get_hardware_info(self) -> Dict[str, Any]:
        """
        Получает детальную информацию об аппаратном обеспечении.

        Returns:
            Dict[str, Any]: Информация об аппаратном обеспечении
        """
        try:
            hardware_info = {
                "cpu": self.get_cpu_info(),
                "memory": self.get_memory_info(),
                "graphics": [],
                "motherboard": {},
                "bios": {},
                "sound": [],
                "usb_controllers": [],
            }

            if self.wmi_client:
                # Информация о видеокартах
                for gpu in self.wmi_client.Win32_VideoController():
                    hardware_info["graphics"].append(
                        {
                            "name": gpu.Name,
                            "adapter_ram": gpu.AdapterRAM,
                            "driver_version": gpu.DriverVersion,
                            "video_processor": gpu.VideoProcessor,
                            "current_resolution": (
                                f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}"
                            ),
                        }
                    )

                # Информация о материнской плате
                for board in self.wmi_client.Win32_BaseBoard():
                    hardware_info["motherboard"] = {
                        "manufacturer": board.Manufacturer,
                        "product": board.Product,
                        "serial_number": board.SerialNumber,
                        "version": board.Version,
                    }

                # Информация о BIOS
                for bios in self.wmi_client.Win32_BIOS():
                    hardware_info["bios"] = {
                        "manufacturer": bios.Manufacturer,
                        "name": bios.Name,
                        "version": bios.Version,
                        "serial_number": bios.SerialNumber,
                        "release_date": bios.ReleaseDate,
                    }

                # Звуковые устройства
                for sound in self.wmi_client.Win32_SoundDevice():
                    hardware_info["sound"].append(
                        {
                            "name": sound.Name,
                            "manufacturer": sound.Manufacturer,
                            "status": sound.Status,
                        }
                    )

                # USB контроллеры
                for usb in self.wmi_client.Win32_USBController():
                    hardware_info["usb_controllers"].append(
                        {
                            "name": usb.Name,
                            "manufacturer": usb.Manufacturer,
                            "device_id": usb.DeviceID,
                            "status": usb.Status,
                        }
                    )

            return hardware_info
        except Exception as e:
            handle_error(f"Error getting hardware info: {e}", e, module="system")
            return {"error": str(e)}
