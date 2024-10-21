import os
import sys
import json

# Default settings
DEFAULT_MAX_REPORTS = 10
DEFAULT_OUTPUT_DIR = "reports"
SETTINGS_FILE_PATH = 'config/settings.json'


# Load user settings from the JSON file or use defaults
def load_settings():
    """
    Loads the user settings from the JSON file. If the file doesn't exist, uses default settings.
    """
    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            return json.load(settings_file)
    else:
        return {
            "max_reports": DEFAULT_MAX_REPORTS,
            "output_directory": DEFAULT_OUTPUT_DIR
        }

def save_settings():
    with open(SETTINGS_FILE_PATH, 'w') as settings_file:
        json.dump(user_settings, settings_file)

# Initialize user settings
user_settings = load_settings()

def set_rollover_reports():
    while True:
        try:
            max_reports = int(input(f"Enter the maximum number of rollover reports (current: {user_settings['max_reports']}): "))
            if max_reports < 1:
                print("The number must be at least 1. Please try again.")
            else:
                user_settings['max_reports'] = max_reports
                print(f"Maximum number of rollover reports set to {max_reports}.")
                save_settings()  # Save the updated settings to the config file
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

def set_output_directory():
    """
    Allows the user to set the default output directory for reports.
    """
    while True:
        output_dir = input(f"Enter the default output directory (current: {user_settings['output_directory']}): ").strip()
        
        if output_dir == "":
            print("Directory cannot be empty. Please enter a valid directory.")
            continue  # Ask for input again

        if not os.path.exists(output_dir):
            create_dir = input(f"Directory '{output_dir}' does not exist. Would you like to create it? (Y/N): ")
            if create_dir.lower() == 'y':
                os.makedirs(output_dir)
                print(f"Directory '{output_dir}' created.")
                user_settings['output_directory'] = output_dir
                save_settings()  # Save changes
                break
            else:
                print("Please enter a valid directory.")
        else:
            user_settings['output_directory'] = output_dir
            print(f"Output directory set to {output_dir}.")
            save_settings()  # Save changes
            break

def display_menu():
    """
    Displays a menu for user preferences and allows them to set options.
    """
    print("\n🐻 BearWatch Settings Menu")
    print("=" * 30)
    print("1. Set maximum number of rollover reports")
    print("2. Set default output directory")
    print("3. Start scan")
    print("4. Exit")
    
    choice = input("Please select an option (1-4): ")
    
    if choice == '1':
        set_rollover_reports()
    elif choice == '2':
        set_output_directory()
    elif choice == '3':
        return 'scan'  # Proceed to scanning
    elif choice == '4':
        print("Exiting BearWatch... Goodbye!")
        sys.exit()  # Exit the application
    else:
        print("Invalid option. Please choose a valid number.")
        display_menu()