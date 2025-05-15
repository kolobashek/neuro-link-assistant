from unittest.mock import MagicMock, patch

import pytest


class TestSystemInfo:
    """Тесты класса системной информации Windows"""

    @pytest.fixture
    def system_info(self):
        """Создает экземпляр SystemInfo с мок-зависимостями"""
        with patch("wmi.WMI"):
            from core.windows.system_info import SystemInfo

            return SystemInfo()

    @patch("platform.system", return_value="Windows")
    @patch("platform.version", return_value="10.0.19042")
    @patch("platform.release", return_value="10")
    @patch("platform.architecture", return_value=("64bit", ""))
    def test_get_os_info_basic(
        self, mock_arch, mock_release, mock_version, mock_system, system_info
    ):
        """Тест получения базовой информации об ОС"""
        # Настраиваем мок для WMI
        system_info.wmi_client = None

        # Получаем информацию об ОС
        os_info = system_info.get_os_info()

        # Проверяем результат
        assert os_info["name"] == "Windows"
        assert os_info["version"] == "10.0.19042"
        assert os_info["release"] == "10"
        assert os_info["architecture"] == "64bit"

    @patch("platform.system", return_value="Windows")
    @patch("platform.version", return_value="10.0.19042")
    @patch("platform.release", return_value="10")
    @patch("platform.architecture", return_value=("64bit", ""))
    def test_get_os_info_with_wmi(
        self, mock_arch, mock_release, mock_version, mock_system, system_info
    ):
        """Тест получения информации об ОС с использованием WMI"""
        # Создаем мок для WMI
        mock_os_data = MagicMock()
        mock_os_data.BuildNumber = "19042"
        mock_os_data.Caption = "Microsoft Windows 10 Pro"
        mock_os_data.InstallDate = "20210101000000.000000+000"
        mock_os_data.LastBootUpTime = "20210601000000.000000+000"
        mock_os_data.Manufacturer = "Microsoft Corporation"

        mock_wmi_client = MagicMock()
        mock_wmi_client.Win32_OperatingSystem.return_value = [mock_os_data]

        system_info.wmi_client = mock_wmi_client

        # Получаем информацию об ОС
        os_info = system_info.get_os_info()

        # Проверяем результат
        assert os_info["name"] == "Windows"
        assert os_info["version"] == "10.0.19042"
        assert os_info["release"] == "10"
        assert os_info["architecture"] == "64bit"
        assert os_info["build"] == "19042"
        assert os_info["caption"] == "Microsoft Windows 10 Pro"
        assert os_info["install_date"] == "20210101000000.000000+000"
        assert os_info["last_boot"] == "20210601000000.000000+000"
        assert os_info["manufacturer"] == "Microsoft Corporation"

    @patch("psutil.cpu_count", side_effect=lambda logical: 8 if logical else 4)
    @patch("psutil.cpu_percent", return_value=25.0)
    @patch("psutil.cpu_freq")
    def test_get_cpu_info_basic(self, mock_cpu_freq, mock_cpu_percent, mock_cpu_count, system_info):
        """Тест получения базовой информации о CPU"""
        # Настраиваем мок для cpu_freq
        mock_freq = MagicMock()
        mock_freq.current = 2500.0
        mock_cpu_freq.return_value = mock_freq

        # Настраиваем мок для WMI
        system_info.wmi_client = None

        # Получаем информацию о CPU
        cpu_info = system_info.get_cpu_info()

        # Проверяем результат
        assert cpu_info["cores_physical"] == 4
        assert cpu_info["cores_logical"] == 8
        assert cpu_info["usage"] == 25.0
        assert cpu_info["frequency"] == 2500.0

    @patch("psutil.cpu_count", side_effect=lambda logical: 8 if logical else 4)
    @patch("psutil.cpu_percent", return_value=25.0)
    @patch("psutil.cpu_freq")
    def test_get_cpu_info_with_wmi(
        self, mock_cpu_freq, mock_cpu_percent, mock_cpu_count, system_info
    ):
        """Тест получения информации о CPU с использованием WMI"""
        # Настраиваем мок для cpu_freq
        mock_freq = MagicMock()
        mock_freq.current = 2500.0
        mock_cpu_freq.return_value = mock_freq

        # Создаем мок для WMI
        mock_processor = MagicMock()
        mock_processor.Name = "Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz"
        mock_processor.Manufacturer = "Intel"
        mock_processor.Architecture = 9
        mock_processor.MaxClockSpeed = 3800

        mock_wmi_client = MagicMock()
        mock_wmi_client.Win32_Processor.return_value = [mock_processor]

        system_info.wmi_client = mock_wmi_client

        # Получаем информацию о CPU
        cpu_info = system_info.get_cpu_info()

        # Проверяем результат
        assert cpu_info["cores_physical"] == 4
        assert cpu_info["cores_logical"] == 8
        assert cpu_info["usage"] == 25.0
        assert cpu_info["frequency"] == 2500.0
        assert cpu_info["name"] == "Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz"
        assert cpu_info["manufacturer"] == "Intel"
        assert cpu_info["architecture"] == 9
        assert cpu_info["max_clock_speed"] == 3800

    @patch("psutil.virtual_memory")
    @patch("psutil.swap_memory")
    def test_get_memory_info(self, mock_swap_memory, mock_virtual_memory, system_info):
        """Тест получения информации о памяти"""
        # Настраиваем мок для virtual_memory
        mock_memory = MagicMock()
        mock_memory.total = 16 * 1024 * 1024 * 1024  # 16 GB
        mock_memory.available = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_memory.percent = 50.0
        mock_virtual_memory.return_value = mock_memory

        # Настраиваем мок для swap_memory
        mock_swap = MagicMock()
        mock_swap.total = 8 * 1024 * 1024 * 1024  # 8 GB
        mock_swap.used = 2 * 1024 * 1024 * 1024  # 2 GB
        mock_swap.percent = 25.0
        mock_swap_memory.return_value = mock_swap

        # Получаем информацию о памяти
        memory_info = system_info.get_memory_info()

        # Проверяем результат
        assert memory_info["total"] == 16 * 1024  # MB
        assert memory_info["available"] == 8 * 1024  # MB
        assert memory_info["used"] == 8 * 1024  # MB
        assert memory_info["used_percent"] == 50.0
        assert memory_info["swap_total"] == 8 * 1024  # MB
        assert memory_info["swap_used"] == 2 * 1024  # MB
        assert memory_info["swap_percent"] == 25.0

    @patch("psutil.disk_partitions")
    @patch("psutil.disk_usage")
    @patch("os.name", "nt")
    def test_get_disk_info(self, mock_disk_usage, mock_disk_partitions, system_info):
        """Тест получения информации о дисках"""
        # Настраиваем мок для disk_partitions
        mock_partition1 = MagicMock()
        mock_partition1.device = "C:\\"
        mock_partition1.mountpoint = "C:\\"
        mock_partition1.fstype = "NTFS"
        mock_partition1.opts = "rw,fixed"

        mock_partition2 = MagicMock()
        mock_partition2.device = "D:\\"
        mock_partition2.mountpoint = "D:\\"
        mock_partition2.fstype = "NTFS"
        mock_partition2.opts = "rw,fixed"

        mock_disk_partitions.return_value = [mock_partition1, mock_partition2]

        # Настраиваем мок для disk_usage
        def mock_disk_usage_func(path):
            if path == "C:\\":
                mock_usage = MagicMock()
                mock_usage.total = 500 * 1024 * 1024 * 1024  # 500 GB
                mock_usage.free = 250 * 1024 * 1024 * 1024  # 250 GB
                mock_usage.used = 250 * 1024 * 1024 * 1024  # 250 GB
                mock_usage.percent = 50.0
                return mock_usage
            elif path == "D:\\":
                mock_usage = MagicMock()
                mock_usage.total = 1000 * 1024 * 1024 * 1024  # 1 TB
                mock_usage.free = 800 * 1024 * 1024 * 1024  # 800 GB
                mock_usage.used = 200 * 1024 * 1024 * 1024  # 200 GB
                mock_usage.percent = 20.0
                return mock_usage

        mock_disk_usage.side_effect = mock_disk_usage_func

        # Получаем информацию о дисках
        disk_info = system_info.get_disk_info()

        # Проверяем результат
        assert "C:\\" in disk_info
        assert "D:\\" in disk_info
        assert disk_info["C:\\"]["mountpoint"] == "C:\\"
        assert disk_info["C:\\"]["fstype"] == "NTFS"
        assert disk_info["C:\\"]["total"] == 500 * 1024  # MB
        assert disk_info["C:\\"]["free"] == 250 * 1024  # MB
        assert disk_info["C:\\"]["used"] == 250 * 1024  # MB
        assert disk_info["C:\\"]["used_percent"] == 50.0
        assert disk_info["D:\\"]["mountpoint"] == "D:\\"
        assert disk_info["D:\\"]["fstype"] == "NTFS"
        assert disk_info["D:\\"]["total"] == 1000 * 1024  # MB
        assert disk_info["D:\\"]["free"] == 800 * 1024  # MB
        assert disk_info["D:\\"]["used"] == 200 * 1024  # MB
        assert disk_info["D:\\"]["used_percent"] == 20.0
