import os
import logging
import time

def scan_directory(directory, depth=0, max_depth=3, incremental_scan=False, use_cis_benchmarks=False, last_scan_time=None):
    risky_items = []
    current_time = time.time()

    # Check depth limit
    if depth > max_depth:
        logging.debug(f"Skipping {directory} - exceeded depth limit of {max_depth}.")
        return risky_items

    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    # Recurse into subdirectory with increased depth
                    risky_items.extend(scan_directory(
                        entry.path, depth + 1, max_depth, incremental_scan, use_cis_benchmarks, last_scan_time))

                elif entry.is_file(follow_symlinks=False):
                    # Check incremental scan conditions
                    if incremental_scan and last_scan_time and os.path.getmtime(entry.path) < last_scan_time:
                        logging.debug(f"Skipping {entry.path} - no recent modifications since last scan.")
                        continue

                    # Check CIS benchmarks if enabled
                    if use_cis_benchmarks and not check_cis_compliance(entry):
                        logging.debug(f"File {entry.path} does not meet CIS benchmarks.")
                        risky_items.append({
                            "path": entry.path,
                            "permissions": oct(os.stat(entry.path).st_mode)[-3:]
                        })
                    elif not use_cis_benchmarks:
                        risky_items.append({
                            "path": entry.path,
                            "permissions": oct(os.stat(entry.path).st_mode)[-3:]
                        })

    except PermissionError:
        logging.warning(f"Permission denied for directory: {directory}")

    return risky_items

# Example function to simulate a CIS benchmark check
def check_cis_compliance(entry):
    # Simulate a check for CIS compliance (for demo purposes)
    file_permissions = oct(os.stat(entry.path).st_mode)[-3:]
    return file_permissions not in ['777', '666']  # Replace with actual CIS logic as needed
