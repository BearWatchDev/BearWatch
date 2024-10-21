import os
import psutil
import distro  # For detecting the Linux distribution

def is_wsl():
    """
    Check if the environment is WSL (Windows Subsystem for Linux).
    
    Returns:
        bool: True if WSL is detected, False otherwise.
    """
    return 'microsoft' in os.uname().release.lower()

def get_mount_points():
    """
    Get all valid Linux-native mount points, excluding Windows partitions in WSL.
    
    Returns:
        list: A list of valid directories to scan.
    """
    mount_points = []
    
    for partition in psutil.disk_partitions():
        # Exclude certain paths if running in WSL (like Windows file systems)
        if is_wsl() and partition.device.startswith("/mnt"):
            continue
        mount_points.append(partition.mountpoint)
    
    return mount_points

def get_safe_defaults_by_distro():
    """
    Returns a list of safe default directories based on the detected Linux distribution.
    
    Returns:
        list: Safe default directories.
    """
    distro_name = distro.id()
    
    if distro_name in ['ubuntu', 'debian']:
        return ['/home', '/etc', '/var']
    elif distro_name in ['centos', 'redhat']:
        return ['/home', '/etc', '/var', '/usr/local']
    elif distro_name == 'arch':
        return ['/home', '/etc', '/usr']
    else:
        return ['/home', '/etc']

def prompt_user_for_directories(mount_points):
    """
    Prompt the user to select which directories to scan from the available mount points.
    
    Returns:
        list: A list of selected directories to scan, with a safe default if user is unsure.
    """
    print("🐻 Please select the directories you would like BearWatch to scan:")
    print("If unsure, choose the safe default option (Y) to scan common directories.")
    
    selected_directories = []
    
    # Prompt for default option
    use_default = input("Would you like to use the safe default directories? (Y/N): ").lower()
    
    if use_default == 'y':
        # Get safe default directories based on distro
        selected_directories = get_safe_defaults_by_distro()
        print(f"Safe defaults selected based on detected distro: {selected_directories}")
    else:
        # Let the user select manually
        for i, mount in enumerate(mount_points, 1):
            choice = input(f"{i}. {mount} (Y/N): ").lower()
            if choice == 'y':
                selected_directories.append(mount)
    
    return selected_directories

# Example usage:
if __name__ == "__main__":
    print("🐻 Forager is identifying file systems to scan...")
    
    mounts = get_mount_points()
    
    if mounts:
        print(f"Valid mount points found: {mounts}")
        selected_dirs = prompt_user_for_directories(mounts)
        if selected_dirs:
            print(f"BearWatch will scan the following directories: {selected_dirs}")
        else:
            print("No directories selected for scanning.")
    else:
        print("No valid mount points found!")
