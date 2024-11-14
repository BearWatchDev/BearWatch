import sys
import subprocess
import time
import itertools
import select
import os
import navigator
import logging
import importlib.util
from modules.forager import get_mount_points, prompt_user_for_directories
from modules.sentinel import scan_directory, display_risky_items, summarize_risks
from modules.trailmap import generate_report
from modules.horizon import detect_os
from settings_manager import user_settings, load_settings, update_last_scan_time

# Application Info.
APP_NAME = "BearWatch"
VERSION = "1.0.3"
RELEASE_DATE = "Initial release: 20th October 2024"

# Set up logging based on `logging_level` from `user_settings`
logging_level = logging.getLevelName(user_settings.get("logging_level", "ERROR").upper())
logging.basicConfig(level=logging_level, force=True)  # Use force=True to override existing logging configuration

# Optional: Add a custom filter if needed
class PermissionWarningFilter(logging.Filter):
    def filter(self, record):
        # Suppress only permission denied warnings
        return "Permission denied" not in record.getMessage()

logger = logging.getLogger()
logger.addFilter(PermissionWarningFilter())  # Apply the custom filter

# Configuration file path (pointing to bearwatch_config.json).
CONFIG_DIR = "config"
SETTINGS_FILE_PATH = os.path.join(CONFIG_DIR, "bearwatch_config.json")

# Prints the BearWatch application information, including version and release date, with a typewriter-style effect.
def print_app_info():
    print_with_cursor(f"{APP_NAME} - Version: {VERSION}", speed=0.001)
    time.sleep(0.5)
    print(f"Release Date: {RELEASE_DATE}")
    time.sleep(0.5)
    print("=" * 40)
    time.sleep(0.5)

# Function to create a running cursor (80s-style effect) for any text.
def running_cursor(text, speed=0.001):
    cursor = itertools.cycle(['|', '/', '-', '\\'])
    for char in text:
        sys.stdout.write(char)  # Print the next character of the text.
        sys.stdout.flush()  # Flush the output buffer to show the character immediately.
        time.sleep(speed)  # Small delay between characters for typing effect.
        
        sys.stdout.write(next(cursor))  # Print the next cursor symbol.
        sys.stdout.flush()  # Flush the output buffer to show the cursor immediately.
        time.sleep(0.1)  # Small delay for the cursor effect.
        
        sys.stdout.write('\b \b')  # Backspace twice (clean up the cursor and space it left).
    
    sys.stdout.write(' \b')  # Print a space and backspace to remove the last cursor.
    sys.stdout.flush()
    print()  # Move to a new line after the effect is done.


# Helper function for using the cursor effect across the script.
def print_with_cursor(text, speed=0.001):
    running_cursor(text, speed)

# Returns safe default directories based on the detected OS flavor.
def get_safe_defaults(os_info):
    if os_info['type'] == 'Linux':
        return ['/home', '/etc', '/var']  # Common safe directories for Linux distros.
    elif os_info['type'] == 'WSL':
        return ['/home', '/mnt/c', '/etc']  # WSL often interacts with /mnt/c.
    else:
        return ['/home']  # Minimal safe default for unknown or unsupported OS types.

# Function to check if required modules are installed and up-to-date.
def check_components():
    print_with_cursor("🐻 BearWatch is checking its tools...", speed=0.001)  # Faster speed for effect.

    # List of required modules and their installation commands for apt.
    required_modules = {
        "distro": None,  # Installed via pip, no specific version required.
        "psutil": "python3-psutil"  # Install via apt if missing.
    }

    for module, apt_package in required_modules.items():
        if importlib.util.find_spec(module) is not None:
            print(f"✅ {module} is present and ready.")
        else:
            print_with_cursor(f"❌ {module} is missing. BearWatch cannot function without it.", speed=0.001)
            
            # Install the module if possible
            if apt_package:
                install_prompt = input(f"Would you like BearWatch to install {module} using apt? (requires sudo) (Y/N): ")
                if install_prompt.lower() == 'y':
                    try:
                        subprocess.check_call(['sudo', 'apt', 'install', '-y', apt_package])
                        time.sleep(0.5)
                        print_with_cursor(f"✅ {module} installed successfully via apt.", speed=0.001)
                    except Exception as e:
                        print_with_cursor(f"❌ Failed to install {module}. Error: {e}", speed=0.001)
                else:
                    print_with_cursor(f"⚠️ {module} was not installed. Some functionality may not work.", speed=0.001)
            else:
                # If `apt` is not available or module needs to be installed via pip.
                print_with_cursor(f"⚠️ {module} cannot be installed with apt and needs to be installed via pip.", speed=0.001)
                try:
                    subprocess.check_call(['pip', 'install', module])
                    print(f"✅ {module} installed successfully via pip.")
                except Exception as e:
                    print(f"❌ Failed to install {module} via pip. Error: {e}")

        time.sleep(0.5)

def input_with_timeout(prompt, timeout=15, default='y'):
    print(prompt, flush=True)
    for remaining in range(timeout, 0, -1):
        sys.stdout.write(f"\rYou have {remaining} seconds to respond... ")
        sys.stdout.flush()
        rlist, _, _ = select.select([sys.stdin], [], [], 1)
        if rlist:
            print()
            return sys.stdin.readline().strip()
    running_cursor(f"\n🐾 No input received within {timeout} seconds. Proceeding with the default option: {default}")
    return default



def handle_report_rollover():
    # Fetch the updated max_reports setting directly from user_settings.
    max_reports = user_settings['report_options']['rollover_reports']
    report_dir = user_settings['report_options']['output_location']

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    report_files = sorted(
        [f for f in os.listdir(report_dir) if f.startswith('bearwatch_report')],
        key=lambda x: os.path.getmtime(os.path.join(report_dir, x))
    )

    # Log the detected report files and their count
    logging.debug(f"All report files detected: {report_files}")
    logging.debug(f"Number of report files found: {len(report_files)}")
    logging.debug(f"Max reports allowed: {max_reports}")
    
    if len(report_files) > max_reports:
        logging.debug("Too many reports, deleting older files...")
        files_to_delete = len(report_files) - max_reports
        logging.debug(f"Deleting {files_to_delete} files")
        
        for old_report in report_files[:files_to_delete]:
            try:
                os.remove(os.path.join(report_dir, old_report))
                logging.info(f"🗑️ Old report {old_report} has been deleted.")
            except Exception as e:
                logging.error(f"Could not delete {old_report}. Reason: {e}")
    else:
        logging.debug("No reports deleted, within the limit.")

    remaining_reports = sorted(
        [f for f in os.listdir(report_dir) if f.startswith('bearwatch_report')]
    )
    logging.debug(f"Reports after deletion: {remaining_reports}")
    logging.debug(f"Output directory in use: {report_dir}")

# Start SCAN FUNCTION!
def start_scan():
    # Reload settings to apply any new configurations
    global user_settings
    user_settings = load_settings()

    # Debug output to show last scan time before starting
    last_scan_time = user_settings['scan_options'].get('last_scan_time')
    if last_scan_time:
        logging.debug(f"Last scan timestamp: {last_scan_time}")
        print(f">> Last scan was on: {time.ctime(last_scan_time)}")
    else:
        logging.debug("No previous scan detected.")
        print("No previous scan detected.")

    # Handle report rollover with updated settings
    handle_report_rollover()

    # Detect the OS and display relevant information
    os_info = detect_os()
    print(f"Detected OS: {os_info['type']}")
    if os_info.get('distro'):
        print(f"Distribution: {os_info['distro']}")

    # Determine directories to scan
    directories_to_scan = determine_directories_to_scan(os_info)
    
    # Proceed with scanning if directories are selected
    if directories_to_scan:
        logging.debug(f"Directories to scan: {directories_to_scan}")
        print(f"BearWatch will scan the following directories: {directories_to_scan}")
        time.sleep(0.3)

        # Sentinel scans directories for permission issues
        print_with_cursor("🐻 Sentinel is now prowling the den for risky permissions...", speed=0.01)
        all_risky_items = perform_scan(directories_to_scan)

        # Generate and save the report (summary is displayed in this function)
        generate_and_save_report(all_risky_items)
    else:
        logging.debug("No directories selected for scanning.")
        print_with_cursor("No directories selected for scanning.", speed=0.1)

    time.sleep(0.5)
    print_with_cursor("🐻 BearWatch is on the lookout...", speed=0.1)

def determine_directories_to_scan(os_info):
    default_directory = user_settings['scan_options'].get('default_directory')
    default_scan_preference = user_settings['scan_options'].get('default_scan_preference', 'N')
    directories_to_scan = []

    # Check if the default directory is valid
    if default_directory and os.path.exists(default_directory):
        # Use the saved default preference if it exists
        if default_scan_preference in ['y', 'n']:
            use_default_directory = default_scan_preference
        else:
            # Otherwise, prompt the user with clearer instructions
            use_default_directory = input_with_timeout(
                f"🐻 Would you like to scan your custom directory ({default_directory})? "
                "(Enter 'Y' for Yes, 'N' for No, or press Enter for the default: No): ", timeout=20
            ).lower()

        if use_default_directory == 'y':
            directories_to_scan = [default_directory]
            logging.debug(f"Using custom directory: {default_directory}")
            print(f"Using custom directory for scan: {default_directory}")
        else:
            directories_to_scan = get_safe_defaults(os_info)
            logging.debug(f"Using safe default directories: {directories_to_scan}")
            print(f"Using safe default directories based on OS: {directories_to_scan}")
    else:
        # Fallback to prompt-based selection if no valid default directory is specified
        safe_default_dirs = get_safe_defaults(os_info)
        print_with_cursor("🐻 BearWatch is identifying directories to scan...", speed=0.001)
        print(f"Safe default directories based on detected OS: {safe_default_dirs}")

        valid_mount_points = get_mount_points()
        if valid_mount_points:
            user_choice = input_with_timeout(
                "🐻 Please select the directories you would like BearWatch to scan:\n"
                "If unsure, choose the safe default option (Y) to scan common directories.\n"
                "Would you like to use the safe default directories? (Y/N): ", timeout=30
            ).lower()
            
            if user_choice == 'y':
                directories_to_scan = safe_default_dirs
                logging.debug(f"Safe defaults selected: {directories_to_scan}")
                print(f"Safe defaults selected: {directories_to_scan}")
            else:
                directories_to_scan = prompt_user_for_directories(valid_mount_points)
                logging.debug(f"User-selected directories: {directories_to_scan}")

    return directories_to_scan


def perform_scan(directories_to_scan):
    all_risky_items = []

    for directory in directories_to_scan:
        try:
            # Perform the scan and get risky items
            risky_items = scan_directory(directory)
            logging.debug(f"DEBUG: Structure of risky_items from {directory}: {risky_items}")

            # Validate the structure of `risky_items`
            if isinstance(risky_items, list) and all(isinstance(item, tuple) and len(item) == 2 for item in risky_items):
                all_risky_items.extend(risky_items)
                display_risky_items(risky_items, directory)
            else:
                logging.error(f"Unexpected structure of risky_items from {directory}: {risky_items}")
                continue
        except PermissionError:
            logging.warning(f"Access denied to {directory}. Skipping this directory.")
        except Exception as e:
            logging.error(f"Error scanning {directory}: {str(e)}")

    return all_risky_items

def generate_and_save_report(all_risky_items):
    # Use the summarize_risks function from sentinel.py for consistent summary logic
    summary = summarize_risks(all_risky_items)

    # Define color codes
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    # Display the summary with color coding
    print(f"⚠️ {YELLOW}Summary of risks found in the bear's den:{RESET}")
    print(f"  - World-writable files: {RED}{summary['world_writable']}{RESET}")
    print(f"  - Files with SUID bit set: {RED}{summary['suid']}{RESET}")
    print(f"  - Files with SGID bit set: {RED}{summary['sgid']}{RESET}")

    # Save the report using TrailMap
    output_dir = user_settings['report_options']['output_location']
    report_file = os.path.join(output_dir, f'bearwatch_report_{int(time.time())}.txt')

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate the report using TrailMap
    generate_report(all_risky_items, summary, output_file=report_file)

    # Handle report rollover and update the last scan time
    handle_report_rollover()
    update_last_scan_time()


if __name__ == "__main__":
    # Print application info with delay.
    print_app_info()
    
    print("🐾 BearWatch is initializing...")

    # Load settings
    user_settings = load_settings()

    # Check required components
    check_components()  # This checks for required modules and installs if missing.

    # Main loop for BearWatch settings menu
while True:
    print(">> BearWatch Settings Menu")
    print("=================================")
    print("1. Start scan")
    print("2. Configuration menu")
    print("0. Exit")

    menu_result = input("Please select an option (0-2): ")

    if menu_result == '1':
        start_scan()  # Assuming your scan takes user settings.

    elif menu_result == '2':
        navigator.main_menu()  # Pass user settings for modification.
    elif menu_result == '0':
        print("Exiting BearWatch. Goodbye!")
        break
    else:
        print("Invalid option, please try again.")
