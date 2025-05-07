
# Windows-����������� ���������� ���������� ����������
import os
import subprocess
import psutil
import time
from core.common.error_handler import handle_error

class WindowsProcessManager:
    """���������� ���������� � Windows"""
    
    def start_process(self, command, shell=True, cwd=None, env=None):
        """
        ��������� �������
        
        Args:
            command (str): ������� ��� �������
            shell (bool): ������������ �� ��������
            cwd (str, optional): ������� ����������
            env (dict, optional): ���������� ���������
        
        Returns:
            int: ID �������� ��� None � ������ ������
        """
        try:
            process = subprocess.Popen(
                command, 
                shell=shell, 
                cwd=cwd, 
                env=env
            )
            return process.pid
        except Exception as e:
            handle_error(f"������ ��� ������� �������� '{command}': {e}", e, module='process')
            return None
    
    def kill_process(self, pid):
        """
        ��������� ������� �� ID
        
        Args:
            pid (int): ID ��������
        
        Returns:
            bool: True, ���� ������� ������� ��������
        """
        try:
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process.terminate()
                
                # ���� ���������� ��������
                gone, still_alive = psutil.wait_procs([process], timeout=3)
                if still_alive:
                    # ���� ������� �� ����������, ������� ���
                    process.kill()
                return True
            else:
                handle_error(f"������� � ID {pid} �� ������", module='process', log_level='warning')
                return False
        except Exception as e:
            handle_error(f"������ ��� ���������� �������� {pid}: {e}", e, module='process')
            return False
    
    def is_process_running(self, name):
        """
        ���������, ������� �� ������� � ��������� ������
        
        Args:
            name (str): ��� ��������
        
        Returns:
            bool: True, ���� ������� �������
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception as e:
            handle_error(f"������ ��� �������� �������� {name}: {e}", e, module='process')
            return False
    
    def get_process_by_name(self, name):
        """
        �������� ������ ��������� � ��������� ������
        
        Args:
            name (str): ��� ��������
        
        Returns:
            list: ������ �������� ���������
        """
        try:
            matching_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc)
            return matching_processes
        except Exception as e:
            handle_error(f"������ ��� ��������� �������� {name}: {e}", e, module='process')
            return []
    
    def get_all_processes(self):
        """
        �������� ������ ���� ���������� ���������
        
        Returns:
            list: ������ �������� ���������
        """
        try:
            return list(psutil.process_iter(['pid', 'name', 'username']))
        except Exception as e:
            handle_error(f"������ ��� ��������� ������ ���������: {e}", e, module='process')
            return []
