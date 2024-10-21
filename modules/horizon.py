import platform
import distro

def detect_os():
    """
    Detects the operating system and environment.
    
    Returns:
        dict: A dictionary containing OS type and distribution information.
    """
    os_info = {}

    os_name = platform.system()
    if os_name == 'Linux':
        os_info['type'] = 'Linux'
        os_info['distro'] = distro.name(pretty=True)  # Using distro module for accurate detection
    elif os_name == 'Windows' and 'microsoft' in platform.release().lower():
        os_info['type'] = 'WSL'
    else:
        os_info['type'] = 'Unsupported OS'

    return os_info
