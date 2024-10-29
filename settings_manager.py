import os
import json
from config.settings import DEFAULT_MAX_REPORTS, DEFAULT_OUTPUT_DIR, SETTINGS_FILE_PATH

# Initialize settings with defaults or load from file
def load_settings():
    default_settings = {
        "logging_level": "INFO",
        "report_options": {
            "detail_level": "summary",
            "rollover_reports": DEFAULT_MAX_REPORTS,  # Using default from settings
            "output_location": DEFAULT_OUTPUT_DIR  # Using default from settings
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
        "system_settings": {
            "parallel_processing": True,
            "memory_optimization": True,
            "scan_timeout": 300
        }
    }
    
    if os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, 'r') as settings_file:
            try:
                settings = json.load(settings_file)
                default_settings.update(settings)
            except json.JSONDecodeError:
                print("Corrupted settings file. Using defaults.")
                save_settings(default_settings)
    
    return default_settings

# Initialize and expose `user_settings`
user_settings = load_settings()

# Save settings to JSON file
def save_settings(settings=user_settings):
    with open(SETTINGS_FILE_PATH, 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)

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
