import os
import logging
import stat
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings_manager import user_settings

# ANSI escape codes for color output
class Colors:
    HEADER = '\033[95m'
    OK_GREEN = '\033[92m'
    WARNING_YELLOW = '\033[93m'
    FAIL_RED = '\033[91m'
    END_COLOR = '\033[0m'

# Retrieve the debug mode from settings
DEBUG_MODE = user_settings.get("logging_level", "INFO").upper() == "DEBUG"

# Configure logging and apply the debug setting
logging_level = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(level=logging_level, force=True)

def check_permissions(path):
    try:
        if not os.path.exists(path) or not (os.path.isfile(path) or os.path.isdir(path)):
            logging.debug(f"🐻 {path} does not exist or is not a regular file/directory.")
            return None

        file_stats = os.stat(path)
        file_mode = file_stats.st_mode

        if file_mode & stat.S_IWOTH:
            logging.debug(f"🌍 {path} is world-writable.")
            return path, "world_writable"

        if file_mode & stat.S_ISUID:
            logging.debug(f"🔒 {path} has the SUID bit set.")
            return path, "suid"

        if file_mode & stat.S_ISGID:
            logging.debug(f"🔒 {path} has the SGID bit set.")
            return path, "sgid"

    except PermissionError:
        logging.debug(f"🐻 Permission denied for {path}.")
    except Exception as e:
        logging.debug(f"🐻 Error checking {path}: {str(e)}")

    return None

def scan_directory(den):
    risky_items = []

    for root, dirs, files in os.walk(den):
        for item in dirs + files:
            item_path = os.path.join(root, item)
            result = check_permissions(item_path)
            if result:
                # Unpack the tuple directly
                path, permission_type = result
                # Append as a tuple
                risky_items.append((path, permission_type))

    return risky_items

def categorize_risky_items(risky_items):
    from collections import defaultdict
    categories = defaultdict(list)

    for path, permission_type in risky_items:
        categories[permission_type].append(path)
    
    return categories

def display_risky_items(risky_items, directory):
    """
    Display the list of risky files with color-coded output, categorized by type.
    
    Args:
        risky_items (list): List of tuples containing the file path and permission type.
        directory (str): The directory currently being scanned.
    """
    if not risky_items:
        print(f"{Colors.OK_GREEN}✅ The den is secure for {directory}, no pawprints in risky areas!{Colors.END_COLOR}")
        return

    print(f"{Colors.HEADER}⚠️ Pawprints in risky areas for {directory}:{Colors.END_COLOR}")
    categorized_items = categorize_risky_items(risky_items)

    if 'world_writable' in categorized_items and categorized_items['world_writable']:
        print(f"{Colors.FAIL_RED}World-writable files:{Colors.END_COLOR}")
        for path in categorized_items['world_writable']:
            print(f"  - {path} is World Writable!")
        print("Explanation: World-writable files can be modified by any user on the system, posing a risk of unauthorized changes or malicious code injection.\n")

    if 'suid' in categorized_items and categorized_items['suid']:
        print(f"{Colors.WARNING_YELLOW}Files with SUID bit set:{Colors.END_COLOR}")
        for path in categorized_items['suid']:
            print(f"  - {path} has the SUID bit set!")
        print("Explanation: SUID files run with elevated privileges, potentially allowing privilege escalation if misused or exploited.\n")

    if 'sgid' in categorized_items and categorized_items['sgid']:
        print(f"{Colors.WARNING_YELLOW}Files with SGID bit set:{Colors.END_COLOR}")
        for path in categorized_items['sgid']:
            print(f"  - {path} has the SGID bit set!")
        print("Explanation: SGID files run with the group’s permissions, which could be exploited to gain unauthorized access to resources.\n")


def summarize_risks(risky_items):
    """
    Summarize the total number of risky files found, categorized by type.
    
    Args:
        risky_items (list): List of tuples containing the file path and permission type.
    
    Returns:
        dict: A dictionary with counts of world-writable, SUID, and SGID files.
    """
    summary = {
        'world_writable': 0,
        'suid': 0,
        'sgid': 0
    }

    # Count each type of risky permission
    for _, permission_type in risky_items:
        if permission_type == 'world_writable':
            summary['world_writable'] += 1
        elif permission_type == 'suid':
            summary['suid'] += 1
        elif permission_type == 'sgid':
            summary['sgid'] += 1

    print("⚠️ Summary of risks found in the bear's den:")
    print(f"World-writable: {summary['world_writable']}")
    print(f"SUID: {summary['suid']}, SGID: {summary['sgid']}")

    # Post-scan recommendations
    print("\nRecommendations:")
    if summary['world_writable'] > 0:
        print("- Consider restricting world-writable permissions to reduce the risk of unauthorized changes.")
    if summary['suid'] > 0 or summary['sgid'] > 0:
        print("- Review SUID/SGID files to ensure they are necessary and configured securely. Remove these bits if not needed.")
    print("- Run another scan with more directories if necessary to ensure comprehensive coverage of your system.\n")

    return summary


if __name__ == "__main__":
    directory_to_scan = "/home"
    print(f"🐻 Starting scan of the bear's den: {directory_to_scan}")
    risky_items = scan_directory(directory_to_scan)
    display_risky_items(risky_items, directory_to_scan)
    summarize_risks(risky_items)
