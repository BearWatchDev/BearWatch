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
from settings_manager import user_settings, save_settings, set_rollover_reports, set_output_directory, load_settings


# Application Info
APP_NAME = "BearWatch"
VERSION = "1.0.1"
RELEASE_DATE = "Initial release: 20th October 2024"

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)  # Set to INFO or ERROR to suppress debug messages

# Configuration file path (pointing to bearwatch_config.json)
CONFIG_DIR = "config"
SETTINGS_FILE_PATH = os.path.join(CONFIG_DIR, "bearwatch_config.json")

# Load settings function to handle defaults and bearwatch_config.json
'''def load_settings():
    # Define default settings, which will be used if they are not present in the config file
    default_settings = {
        "max_reports": DEFAULT_MAX_REPORTS,
        "output_directory": DEFAULT_OUTPUT_DIR,
        "logging_level": "INFO",  # Default to INFO if not previously set
        "report_options": {
            "detail_level": "summary",
            "rollover_reports": 5,
            "output_location": "/home/reports"
        },
        "scan_options": {
            "default_directory": "/home",
            "file_types": ["*.conf", "*.log"],
            "depth_limit": 3,
            "incremental_scan": True,
            "use_cis_benchmarks": True
        },
        "performance_metrics": {
            "enabled": True,
            "output_location": "/home/metrics"
        },
2        "system_settings": {
            "parallel_processing": True,
            "memory_optimization": True,
            "scan_timeout": 300
        }
    }

    # Load settings from the config file if it exists
    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            try:
                # Load the JSON config file
                settings = json.load(settings_file)
                # Update default settings with any loaded values
                default_settings.update(settings)
            except json.JSONDecodeError:
                print("Corrupted settings file. Using defaults.")
                save_settings(default_settings)  # Save defaults if file is corrupted

    # Set the logging level from the loaded settings
    logging_level = default_settings.get('logging_level', 'INFO')
    logging.getLogger().setLevel(logging_level)

    return default_settings
    
# Saves the provided settings to the JSON file for persistence.
def save_settings(settings):
    """
    Saves the user settings to the JSON file.
    """
    with open(SETTINGS_FILE_PATH, 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)'''

#     Prints the BearWatch application information, including version and release date, with a typewriter-style effect.
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
        sys.stdout.write(char)  # Print the next character of the text
        sys.stdout.flush()  # Flush the output buffer to show the character immediately
        time.sleep(speed)  # Small delay between characters for typing effect
        
        sys.stdout.write(next(cursor))  # Print the next cursor symbol.
        sys.stdout.flush()  # Flush the output buffer to show the cursor immediately.
        time.sleep(0.1)  # Small delay for the cursor effect.
        
        sys.stdout.write('\b \b')  # Backspace twice (clean up the cursor and space it left).
    
    sys.stdout.write(' \b')  # Print a space and backspace to remove the last cursor.
    sys.stdout.flush()
    print()  # Move to a new line after the effect is done.

# Get the max reports setting from settings
max_reports = user_settings.get('max_reports', 10)

# Helper function for using the cursor effect across the script.
def print_with_cursor(text, speed=0.001):
    running_cursor(text, speed)

# Returns safe default directories based on the detected OS flavor.
def get_safe_defaults(os_info):
    if os_info['type'] == 'Linux':
        return ['/home', '/etc', '/var']  # Common safe directories for Linux distros
    elif os_info['type'] == 'WSL':
        return ['/home', '/mnt/c', '/etc']  # WSL often interacts with /mnt/c
    else:
        return ['/home']  # Minimal safe default for unknown or unsupported OS types.

# Function to check if required modules are installed and up-to-date.
def check_components():
    print_with_cursor("🐻 BearWatch is checking its tools...", speed=0.001)  # Faster speed for effect

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
                # If `apt` is not available or module needs to be installed via pip
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
    # Fetch the updated max_reports setting directly from user_settings
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

# Continue the BearWatch process after the user selects "Start scan"
def start_scan():
    # Reload settings to apply any new configurations
    global user_settings
    user_settings = load_settings()
    
    # Handle report rollover with updated settings.
    handle_report_rollover()  # No need to pass max_reports, it reads directly from user_settings

    os_info = detect_os()
    print(f"Detected OS: {os_info['type']}")
    if os_info.get('distro'):
        print(f"Distribution: {os_info['distro']}")
    
    # Proceed with scanning logic here...
    safe_default_dirs = get_safe_defaults(os_info)
    print_with_cursor("🐻 BearWatch is identifying directories to scan...", speed=0.001)
    print(f"Safe default directories based on detected OS: {safe_default_dirs}")
    
    valid_mount_points = get_mount_points()
    
    if valid_mount_points:
        # Prompt the user for a directory scan choice with countdown.
        user_choice = input_with_timeout("🐻 Please select the directories you would like BearWatch to scan:\n"
                                         "If unsure, choose the safe default option (Y) to scan common directories.\n"
                                         "Would you like to use the safe default directories? (Y/N): ", timeout=30)
        
        if user_choice.lower() == 'y':
            directories_to_scan = safe_default_dirs
            print(f"Safe defaults selected: {directories_to_scan}")
        else:
            directories_to_scan = prompt_user_for_directories(valid_mount_points)
        
        if directories_to_scan:
            print(f"BearWatch will scan the following directories: {directories_to_scan}")
            time.sleep(0.3)
            
            # Sentinel scans directories for permission issues.
            print_with_cursor("🐻 Sentinel is now prowling the den for risky permissions...", speed=0.01)
            all_risky_items = []
            
            for directory in directories_to_scan:
                risky_items = scan_directory(directory)
                all_risky_items.extend(risky_items)
                display_risky_items(risky_items, directory)
            
            # Summarize the overall risks and store in summary.
            summary = summarize_risks(all_risky_items)
            
            # Generate the report using TrailMap.
            report_file = os.path.join(user_settings['report_options']['output_location'], f'bearwatch_report_{int(time.time())}.txt')
            output_dir = user_settings['report_options']['output_location']  # Use the correct path from report_options

            # Ensure the output directory exists.
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            generate_report(all_risky_items, summary, output_file=report_file)
            handle_report_rollover()
            #DEBUG print(user_settings['report_options']['output_location'])
            
        else:
            print_with_cursor("No directories selected for scanning.", speed=0.1)
    else:
        print_with_cursor("No valid mount points found!", speed=0.1)

    time.sleep(0.5)
    print_with_cursor("🐻 BearWatch is on the lookout...", speed=0.1)



    

if __name__ == "__main__":
    # Print application info with delay
    print_app_info()
    
    print("🐾 BearWatch is initializing...")

    # Load settings
    user_settings = load_settings()

    # Check required components
    check_components()  # This checks for required modules and installs if missing

    # Main loop for BearWatch settings menu
while True:
    print("BearWatch Settings Menu")
    print("==============================")
    print("1. Start scan")
    print("2. Configuration menu")
    print("0. Exit")

    menu_result = input("Please select an option (0-2): ")

    if menu_result == '1':
        start_scan()  # Assuming your scan takes user settings
    elif menu_result == '2':
        navigator.main_menu()  # Pass user settings for modification
    elif menu_result == '0':
        print("Exiting BearWatch. Goodbye!")
        break
    else:
        print("Invalid option, please try again.")
