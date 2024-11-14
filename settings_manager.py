import os
import json
import time
import logging
from config.settings import DEFAULT_MAX_REPORTS, DEFAULT_OUTPUT_DIR, SETTINGS_FILE_PATH

# Define default settings as a single source of truth
DEFAULT_SETTINGS = {
    "logging_level": "INFO",
    "report_options": {
        "detail_level": "summary",
        "rollover_reports": DEFAULT_MAX_REPORTS,
        "output_location": DEFAULT_OUTPUT_DIR
    },
    "scan_options": {
        "default_directory": "/home",
        "file_types": ["*.conf", "*.log"],
        "depth_limit": 3,
        "incremental_scan": True,
        "use_cis_benchmarks": True,
        "last_scan_time": None  # Initialize as None
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

# Load settings from the configuration file or use defaults
def load_settings():
    settings = DEFAULT_SETTINGS.copy()

    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            try:
                loaded_settings = json.load(settings_file)

                # Merge loaded settings with defaults
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in loaded_settings:
                        loaded_settings[key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            loaded_settings[key].setdefault(sub_key, sub_value)

                settings = loaded_settings
                logging.debug("Settings loaded and merged with defaults.")
            except json.JSONDecodeError:
                logging.warning("Corrupted settings file. Using defaults.")
                save_settings(DEFAULT_SETTINGS)

    logging.debug("Final settings loaded: %s", settings)
    return settings

# Initialize and expose `user_settings`
user_settings = load_settings()

# Save settings to the JSON file
def save_settings(settings=user_settings):
    """
    Save provided settings to the JSON file.
    """
    try:
        with open(SETTINGS_FILE_PATH, 'w') as settings_file:
            json.dump(settings, settings_file, indent=4)
        logging.debug("Settings saved successfully: %s", settings)
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")

# Update the last scan time in `scan_options`
def update_last_scan_time():
    """
    Updates the last_scan_time in scan_options with the current time.
    """
    user_settings['scan_options']['last_scan_time'] = time.time()  # Store as Unix timestamp
    save_settings(user_settings)

# Functions to update specific settings and ensure they are saved
def set_rollover_reports():
    """
    Prompt the user to set the maximum number of rollover reports and save.
    """
    max_reports = int(input("Enter the maximum number of rollover reports: "))
    user_settings['report_options']['rollover_reports'] = max_reports
    save_settings()
    logging.debug(f"Rollover reports updated to: {max_reports} and saved.")

def set_output_directory():
    """
    Prompt the user to set the output directory for reports and save.
    """
    output_dir = input("Enter the output directory for reports: ")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    user_settings['report_options']['output_location'] = output_dir
    save_settings()
    logging.debug(f"Output directory updated to: {output_dir} and saved.")

def toggle_debug_logging():
    """
    Toggle the debug logging setting and save.
    """
    current_level = user_settings.get("logging_level", "INFO").upper()
    new_level = "DEBUG" if current_level == "INFO" else "INFO"
    user_settings["logging_level"] = new_level
    save_settings()
    logging.debug(f"Debug logging toggled to: {new_level} and saved.")

def reset_settings():
    """
    Reset configuration to default settings.
    """
    save_settings(DEFAULT_SETTINGS)
    print("Configuration has been reset to default settings.")
