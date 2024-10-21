import sys
import subprocess
import time
import itertools
import select
import os
import json
from modules.forager import get_mount_points, prompt_user_for_directories
from modules.sentinel import scan_directory, display_risky_items, summarize_risks
from modules.trailmap import generate_report  # Import TrailMap report generator
from modules.horizon import detect_os  # Import Horizon for OS detection
from config.settings import display_menu, user_settings
from config.settings import DEFAULT_MAX_REPORTS, DEFAULT_OUTPUT_DIR, SETTINGS_FILE_PATH

# Application Info
APP_NAME = "BearWatch"
VERSION = "1.0.0"
RELEASE_DATE = "20th October 2024"

#Loads the user settings from the JSON file. If the file doesn't exist, it creates a new file with default values.
def load_settings():
    default_settings = {
        "max_reports": DEFAULT_MAX_REPORTS,
        "output_directory": DEFAULT_OUTPUT_DIR
    }
    
    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            try:
                return json.load(settings_file)
            except json.JSONDecodeError:
                print("Corrupted settings file. Using defaults.")
                return default_settings
    else:
        print("Settings file not found. Creating a new one with default values.")
        save_settings(default_settings)
        return default_settings
    
# Saves the provided settings to the JSON file for persistence.
def save_settings(settings):
    """
    Saves the user settings to the JSON file.
    """
    with open(SETTINGS_FILE_PATH, 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

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
# Debugging statement to verify loaded max_reports
print(f"DEBUG: max_reports loaded from settings: {max_reports}")

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
        try:
            mod = __import__(module)
            time.sleep(0.5)
            print(f"✅ {module} is present and ready.")
        
        except ImportError:
            print_with_cursor(f"❌ {module} is missing. BearWatch cannot function without it.", speed=0.001)
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
                print_with_cursor(f"⚠️ {module} cannot be installed with apt and needs to be installed via pip.", speed=0.001)
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

def handle_report_rollover(max_reports):
    report_dir = user_settings['output_directory']
    
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    # List only the reports that start with 'bearwatch_report' (filter out unrelated files)
    report_files = sorted(
        [f for f in os.listdir(report_dir) if f.startswith('bearwatch_report')],
        key=lambda x: os.path.getmtime(os.path.join(report_dir, x))
    )

    # DEBUG: Print out all report files in the directory
    print(f"DEBUG: All report files detected: {report_files}")
    
    # DEBUG: Number of reports found and allowed
    print(f"DEBUG: Number of report files found: {len(report_files)}")
    print(f"DEBUG: Max reports allowed: {max_reports}")
    
    # If the number of reports exceeds the allowed maximum, delete the oldest files.
    if len(report_files) > max_reports:
        print(f"DEBUG: Too many reports, deleting older files...")
        # Calculate how many files to delete
        files_to_delete = len(report_files) - max_reports
        print(f"DEBUG: Deleting {files_to_delete} files")
        
        for old_report in report_files[:files_to_delete]:
            try:
                os.remove(os.path.join(report_dir, old_report))
                print(f"🗑️ Old report {old_report} has been deleted.")
            except Exception as e:
                print(f"ERROR: Could not delete {old_report}. Reason: {e}")
    else:
        print(f"DEBUG: No reports deleted, within the limit.")

    # DEBUG: Confirm the deletion logic is working.
    remaining_reports = sorted(
        [f for f in os.listdir(report_dir) if f.startswith('bearwatch_report')]
    )
    print(f"DEBUG: Reports after deletion: {remaining_reports}")
    print(f"DEBUG: Output directory in use: {report_dir}")

# Main BearWatch process.
if __name__ == "__main__":
    # Print application info with delay
    print_app_info()
    
    print("🐾 BearWatch is initializing...")
    
    # Display settings menu.
    while True:
        menu_result = display_menu()
        if menu_result == 'scan':
            break  # Exit the menu and proceed to scanning

    # Run component check with the cursor effect.
    check_components()

    # OS detection using Horizon.py
    os_info = detect_os()
    print(f"Detected OS: {os_info['type']}")
    if os_info.get('distro'):
        print(f"Distribution: {os_info['distro']}")

    time.sleep(0.3)
    
    # Get the dynamic safe defaults based on detected OS.
    safe_default_dirs = get_safe_defaults(os_info)

    # Use Forager to get directories.
    print_with_cursor("🐻 BearWatch is identifying directories to scan...", speed=0.001)
    time.sleep(0.3)
    
    # Print the safe default directories before asking the user.
    print(f"Safe default directories based on detected OS: {safe_default_dirs}")

    
    valid_mount_points = get_mount_points()
    
    if valid_mount_points:
        # Prompt the user for a directory scan choice with countdown.
        user_choice = input_with_timeout("🐻 Please select the directories you would like BearWatch to scan:\n"
                                         "If unsure, choose the safe default option (Y) to scan common directories.\n"
                                         "Would you like to use the safe default directories? (Y/N): ", timeout=30)
        
        if user_choice.lower() == 'y':
            # Use the dynamically generated safe defaults.
            directories_to_scan = safe_default_dirs
            print(f"Safe defaults selected: {directories_to_scan}")
        else:
            directories_to_scan = prompt_user_for_directories(valid_mount_points)
        
        if directories_to_scan:
            print(f"BearWatch will scan the following directories: {directories_to_scan}")
            time.sleep(0.3)
            
            # Use Sentinel to scan directories for permission issues.
            print_with_cursor("🐻 Sentinel is now prowling the den for risky permissions...", speed=0.01)
            all_risky_items = []
            
            for directory in directories_to_scan:
                risky_items = scan_directory(directory)
                all_risky_items.extend(risky_items)
                display_risky_items(risky_items, directory)
            
            # Summarize the overall risks and store in summary.
            summary = summarize_risks(all_risky_items)
            
            # Generate the report using TrailMap
            report_file = os.path.join(user_settings['output_directory'], f'bearwatch_report_{int(time.time())}.txt')
            output_dir = user_settings['output_directory']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Debugging print to verify the full report file path
            # print(f"DEBUG: Full report file path: {report_file}")

            generate_report(all_risky_items, summary, output_file=report_file)

            # Call handle_report_rollover after generating the report
            handle_report_rollover(user_settings['max_reports'])
            
        else:
            print_with_cursor("No directories selected for scanning.", speed=0.1)
    else:
        print_with_cursor("No valid mount points found!", speed=0.1)


    time.sleep(0.5)
    # Continue with rest of the BearWatch process.
    print_with_cursor("🐻 BearWatch is on the lookout...", speed=0.1)
