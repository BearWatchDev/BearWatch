# utils.py
import logging

def toggle_debug_logging(user_settings, save_settings_func):
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
        logging.getLogger().setLevel(logging.INFO)
        user_settings['logging_level'] = 'INFO'
        print("Debug logging disabled.")
    else:
        logging.getLogger().setLevel(logging.DEBUG)
        user_settings['logging_level'] = 'DEBUG'
        print("Debug logging enabled.")
    save_settings_func(user_settings)
    
    # Save the updated user_settings
    save_settings_func(user_settings)