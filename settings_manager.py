import os
import json
import time  # For updating the scan timestamp
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
                
                # Use logging.debug instead of print
                logging.debug("Settings loaded and merged with defaults.")
            except json.JSONDecodeError:
                logging.warning("Corrupted settings file. Using defaults.")
                save_settings(DEFAULT_SETTINGS)

    # Log final settings at debug level
    logging.debug("Final settings loaded: %s", settings)
    return settings



# Initialize and expose `user_settings`
user_settings = load_settings()

def save_settings(settings=user_settings):
    """
    Save provided settings to the JSON file.
    """
    with open(SETTINGS_FILE_PATH, 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

def update_last_scan_time():
    """
    Updates the last_scan_time in scan_options with the current time.
    """
    user_settings['scan_options']['last_scan_time'] = time.time()  # Store as Unix timestamp
    save_settings(user_settings)

# Helper function to update rollover reports in `report_options`
def set_rollover_reports():
    max_reports = int(input("Enter the maximum number of rollover reports: "))
    user_settings['report_options']['rollover_reports'] = max_reports
    save_settings()

# Helper function to update the report output directory in `report_options`
def set_output_directory():
    output_dir = input("Enter the output directory for reports: ")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    user_settings['report_options']['output_location'] = output_dir
    save_settings()

def reset_settings():
    """
    Reset configuration to default settings.
    """
    save_settings(DEFAULT_SETTINGS)  # Overwrite the settings file with defaults
    print("Configuration has been reset to default settings.")
