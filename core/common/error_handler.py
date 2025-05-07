
# ������������ ���������� ������
import logging
import traceback
import sys

# ��������� �����������
logger = logging.getLogger('error_handler')

def handle_error(message, exception=None, module='general', log_level='error'):
    """
    ��������� ������ � ������������
    
    Args:
        message (str): ��������� �� ������
        exception (Exception, optional): ����������, ��������� ������
        module (str, optional): ������, � ������� ��������� ������
        log_level (str, optional): ������� ����������� ('error', 'warning', 'critical')
    
    Returns:
        bool: True, ���� ������ ����������, False � ��������� ������
    """
    # ��������� ������ ���������
    full_message = f"[{module}] {message}"
    
    # ���� ������������� ����������, ��������� �����������
    if exception:
        trace = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        full_message += f"\nException: {str(exception)}\nTraceback: {trace}"
    
    # �������� � ����������� �� ������
    if log_level.lower() == 'warning':
        logger.warning(full_message)
    elif log_level.lower() == 'critical':
        logger.critical(full_message)
    else:
        logger.error(full_message)
    
    return True

def handle_llm_error(message, exception=None, model=None, prompt=None):
    """
    ������������������ ���������� ������ ��� LLM
    
    Args:
        message (str): ��������� �� ������
        exception (Exception, optional): ����������, ��������� ������
        model (str, optional): ������ LLM, ��������� ������
        prompt (str, optional): ������, ��������� ������
    
    Returns:
        bool: True, ���� ������ ����������, False � ��������� ������
    """
    # ��������� ������ ������
    details = f"LLM Error"
    if model:
        details += f" in model {model}"
    if prompt:
        # �������� ������� �������
        max_prompt_length = 100
        short_prompt = prompt[:max_prompt_length] + "..." if len(prompt) > max_prompt_length else prompt
        details += f"\nPrompt: {short_prompt}"
    
    # ���������� ����� ���������� � ������� 'llm'
    return handle_error(f"{message}\n{details}", exception, module='llm')
