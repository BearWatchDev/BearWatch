# navigator.py
import json
import os
from settings_manager import user_settings, save_settings, set_rollover_reports, set_output_directory, reset_settings
from utils import toggle_debug_logging

# Configuration file path
CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "bearwatch_config.json")

# Ensure config directory exists
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# Load existing config or create a new one
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "scan_options": {
                "default_directory": "/home",
                "file_types": ["*.conf", "*.log"],
                "depth_limit": 3,
                "incremental_scan": True,
                "use_cis_benchmarks": True
            },
            "report_options": {
                "detail_level": "summary",
                "rollover_reports": 5,
                "output_location": "/home/reports"
            },
            "performance_metrics": {
                "enabled": True,
                "output_location": "/home/metrics"
            },
            "system_settings": {
                "parallel_processing": True,
                "memory_optimization": True,
                "scan_timeout": 300
            }
        }

# Save user preferences to the config file
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def main_menu():
    config = load_config()
    while True:
        print("\nBearWatch Full Configuration Menu")
        print("=================================")
        print("1. Scan Options")
        print("2. Report Options")
        print("3. Performance Metrics")
        print("4. General Options")
        print("5. Reset to Default Settings")
        print("0. Return to Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            scan_options(config)
        elif choice == '2':
            report_options(config)
        elif choice == '3':
            performance_options(config)
        elif choice == '4':
            general_options(config)
        elif choice == '5':
            # Confirmation before resetting
            confirm_reset = input("Are you sure you want to reset all settings to defaults? (Y/N): ")
            if confirm_reset.lower() == 'y':
                reset_settings()
                print("Settings have been reset to defaults.")
            else:
                print("Reset cancelled.")
        elif choice == '0':
            save_config(config)  # Save any changes made
            break
        else:
            print("Invalid option, please try again.")


# Scan options menu
def scan_options(config):
    while True:
        print("\nBearWatch Main Menu > Scan Options >")
        print("1. Default Directory:", config["scan_options"]["default_directory"])
        print("2. File Types:", config["scan_options"]["file_types"])
        print("3. Depth Limit:", config["scan_options"]["depth_limit"])
        print("4. Incremental Scan:", config["scan_options"]["incremental_scan"])
        print("5. Use CIS Benchmarks:", config["scan_options"]["use_cis_benchmarks"])
        print("0. Return to Main Menu")
        
        choice = input("Select an option to change (1-5): ")

        if choice == '1':
            config["scan_options"]["default_directory"] = input("Enter new default directory: ")

        elif choice == '2':
            file_types_input = input("Enter file types (comma-separated, e.g., *.conf, *.log): ")
            
            # Split by comma, strip spaces, and validate each file type
            file_types = [ftype.strip() for ftype in file_types_input.split(',')]
            
            # Filter only valid file types that start with "*."
            valid_file_types = []
            for ftype in file_types:
                if ftype.startswith("*.") and len(ftype) > 2:
                    valid_file_types.append(ftype)
                else:
                    print(f"Invalid file type format ignored: {ftype}")
            
            # Update settings with validated file types if any are valid
            if valid_file_types:
                config["scan_options"]["file_types"] = valid_file_types
                print("File types updated:", valid_file_types)
            else:
                print("No valid file types entered. Please try again.")

        elif choice == '3':
            config["scan_options"]["depth_limit"] = int(input("Enter new depth limit: "))
        
        elif choice == '4':
            config["scan_options"]["incremental_scan"] = input("Enable incremental scan (yes/no): ").lower() == "yes"
        
        elif choice == '5':
            config["scan_options"]["use_cis_benchmarks"] = input("Use CIS Benchmarks (yes/no): ").lower() == "yes"
        
        elif choice == '0':
            break

# Report options menu
def report_options(config):
    while True:
        print("\nBearWatch Main Menu > Report Options >")
        print("1. Detail Level:", config["report_options"]["detail_level"])
        print("2. Number of Rollover Reports:", config["report_options"]["rollover_reports"])
        print("3. Output Location:", config["report_options"]["output_location"])
        print("4. Toggle Debug Logging")
        print("0. Return to Main Menu")
        
        choice = input("Select an option to change (1-4): ")

        if choice == '1':
            config["report_options"]["detail_level"] = input("Enter new detail level (summary/detailed/critical-only): ")
        elif choice == '2':
            config["report_options"]["rollover_reports"] = int(input("Enter number of rollover reports to keep: "))
            save_config(config)  # Ensures the change is saved
            print(f"Maximum number of rollover reports set to {config['report_options']['rollover_reports']}.")
        elif choice == '3':
            config["report_options"]["output_location"] = input("Enter new report output location: ")
        elif choice == '4':
            toggle_debug_logging(user_settings, save_settings)
        elif choice == '0':
            break

# Performance metrics options menu
def performance_options(config):
    while True:
        print("\nBearWatch Main Menu > Performance Metrics >")
        print("1. Enable Performance Metrics:", config["performance_metrics"]["enabled"])
        print("2. Output Location:", config["performance_metrics"]["output_location"])
        print("0. Return to Main Menu")
        
        choice = input("Select an option to change (1-2): ")

        if choice == '1':
            config["performance_metrics"]["enabled"] = input("Enable performance metrics (yes/no): ").lower() == "yes"
        elif choice == '2':
            config["performance_metrics"]["output_location"] = input("Enter new metrics output location: ")
        elif choice == '0':
            break

# General options menu
def general_options(config):
    while True:
        print("\nBearWatch Main Menu > General Options >")
        print("1. Scan Options")
        print("2. Report Options")
        print("3. Performance Options")
        print("4. System Settings")
        print("0. Return to Main Menu")
        
        choice = input("Select an option to change: ")
        if choice == '1':
            scan_options(config)
        elif choice == '2':
            report_options(config)
        elif choice == '3':
            performance_options(config)
        elif choice == '4':
            system_options(config)
        elif choice == '0':
            break

# System settings menu (now focuses only on performance-related settings)
def system_options(config):
    while True:
        print("\nBearWatch Main Menu > General Options > System Settings >")
        print("1. Parallel Processing:", config["system_settings"]["parallel_processing"])
        print("2. Memory Optimization:", config["system_settings"]["memory_optimization"])
        print("3. Scan Timeout:", config["system_settings"]["scan_timeout"])
        print("0. Return to General Options Menu")
        
        choice = input("Select an option to change (1-3): ")

        if choice == '1':
            config["system_settings"]["parallel_processing"] = input("Enable parallel processing (yes/no): ").lower() == "yes"
        elif choice == '2':
            config["system_settings"]["memory_optimization"] = input("Enable memory optimization (yes/no): ").lower() == "yes"
        elif choice == '3':
            config["system_settings"]["scan_timeout"] = int(input("Enter new scan timeout (in seconds): "))
        elif choice == '0':
            break

# Run the menu
if __name__ == "__main__":
    main_menu()
