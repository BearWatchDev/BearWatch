import os

# ANSI escape codes for color output
class Colors:
    HEADER = '\033[95m'
    OK_GREEN = '\033[92m'
    WARNING_YELLOW = '\033[93m'
    FAIL_RED = '\033[91m'
    END_COLOR = '\033[0m'

def check_permissions(path):
    """
    Check the permissions of a file or directory (the bear's territory).
    
    Returns:
        dict: A dictionary containing information about world-writable and SUID/SGID flags.
    """
    permission_info = {}
    
    try:
        # Get the file's status
        file_stats = os.stat(path)
        file_mode = file_stats.st_mode
        
        # Check if the file/directory is world-writable
        is_world_writable = bool(file_mode & 0o002)
        permission_info['world_writable'] = is_world_writable
        
        # Check for SUID (Set User ID) or SGID (Set Group ID) bits
        is_suid = bool(file_mode & 0o4000)
        is_sgid = bool(file_mode & 0o2000)
        permission_info['suid'] = is_suid
        permission_info['sgid'] = is_sgid
        
    except Exception as e:
        permission_info['error'] = f"🐻 Error checking {path}: {str(e)}"
    
    return permission_info

def scan_directory(den):
    """
    The bear prowls through its den, scanning for risky permissions.
    
    Args:
        den (str): The directory path (the bear's den) to scan.
    
    Returns:
        list: A list of files and directories with unsafe permissions (pawprints in risky areas).
    """
    risky_items = []
    
    for root, dirs, files in os.walk(den):
        # Check each file and directory in the bear's den
        for item in dirs + files:
            item_path = os.path.join(root, item)
            permissions = check_permissions(item_path)
            
            # Collect any items with unsafe permissions
            if permissions.get('world_writable') or permissions.get('suid') or permissions.get('sgid'):
                risky_items.append({
                    'path': item_path,
                    'permissions': permissions
                })
    
    return risky_items

# Function to categorize risky items by type
def categorize_risky_items(risky_items):
    from collections import defaultdict
    categories = defaultdict(list)
    for item in risky_items:
        path = item['path']
        permissions = item['permissions']
        if permissions['world_writable']:
            categories['world_writable'].append(path)
        if permissions['suid']:
            categories['suid'].append(path)
        if permissions['sgid']:
            categories['sgid'].append(path)
    return categories

# Function to display risky items with color-coded output
def display_risky_items(risky_items, directory):
    """
    Display the list of risky files with color-coded output, categorized by type.
    
    Args:
        risky_items (list): List of files/directories with risky permissions.
        directory (str): The directory currently being scanned.
    """
    if not risky_items:
        print(f"{Colors.OK_GREEN}✅ The den is secure for {directory}, no pawprints in risky areas!{Colors.END_COLOR}")
        return
    
    print(f"{Colors.HEADER}⚠️ Pawprints in risky areas for {directory}:{Colors.END_COLOR}")
    
    # Categorize the risky items by permission type
    categorized_items = categorize_risky_items(risky_items)
    
    if categorized_items['world_writable']:
        print(f"{Colors.FAIL_RED}World-writable files:{Colors.END_COLOR}")
        for path in categorized_items['world_writable']:
            print(f"🛠️ {path}")
    
    if categorized_items['suid']:
        print(f"{Colors.WARNING_YELLOW}Files with SUID bit set:{Colors.END_COLOR}")
        for path in categorized_items['suid']:
            print(f"🛠️ {path}")
    
    if categorized_items['sgid']:
        print(f"{Colors.WARNING_YELLOW}Files with SGID bit set:{Colors.END_COLOR}")
        for path in categorized_items['sgid']:
            print(f"🛠️ {path}")

# Debug-enabled summarize_risks function
def summarize_risks(risky_items):
    """
    Summarize the total number of risky files found, categorized by type.
    
    Args:
        risky_items (list): List of files/directories with risky permissions.
    
    Returns:
        dict: A dictionary with counts of world-writable, SUID, and SGID files.
    """
    if not risky_items:
        return {
            'world_writable': 0,
            'suid': 0,
            'sgid': 0
        }

    total_world_writable = sum(1 for item in risky_items if item['permissions']['world_writable'])
    total_suid = sum(1 for item in risky_items if item['permissions']['suid'])
    total_sgid = sum(1 for item in risky_items if item['permissions']['sgid'])

    print(f"{Colors.HEADER}Summary of risks found in the bear's den:{Colors.END_COLOR}")
    print(f"{Colors.FAIL_RED}World-writable: {total_world_writable}{Colors.END_COLOR}")
    print(f"{Colors.WARNING_YELLOW}SUID: {total_suid}, SGID: {total_sgid}{Colors.END_COLOR}")
    
    # Return the summary as a dictionary
    return {
        'world_writable': total_world_writable,
        'suid': total_suid,
        'sgid': total_sgid
    }
