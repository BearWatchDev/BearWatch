import os
import logging
import time

def scan_directory(directory, depth=0, max_depth=3, incremental_scan=False, use_cis_benchmarks=False, last_scan_time=None):
    risky_items = []

    # Ensure depth doesn't exceed the specified max depth
    if depth > max_depth:
        logging.debug(f"Skipping {directory} - exceeded depth limit of {max_depth}.")
        return risky_items

    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    # Recurse into the subdirectory, increasing the depth
                    risky_items.extend(scan_directory(
                        entry.path, depth + 1, max_depth, incremental_scan, use_cis_benchmarks, last_scan_time
                    ))

                elif entry.is_file(follow_symlinks=False):
                    logging.debug(f"Checking file: {entry.path}")

                    # Skip if incremental scan is enabled and file is unchanged
                    if incremental_scan and last_scan_time and os.path.getmtime(entry.path) < last_scan_time:
                        logging.debug(f"Skipping {entry.path} - no recent modifications since last scan.")
                        continue

                    # Check permissions
                    file_mode = os.stat(entry.path).st_mode
                    permissions = {
                        "world_writable": bool(file_mode & 0o002),
                        "suid": bool(file_mode & 0o4000),
                        "sgid": bool(file_mode & 0o2000)
                    }

                    # Log permissions for debugging
                    logging.debug(f"Permissions for {entry.path}: {permissions}")

                    if use_cis_benchmarks:
                        compliance_issues = check_cis_compliance(entry, permissions)
                        if compliance_issues:
                            logging.debug(f"Compliance issues for {entry.path}: {compliance_issues}")
                            risky_items.extend(compliance_issues)
                    else:
                        # Add risky items if SUID/SGID or world-writable permissions are found
                        if permissions["world_writable"] or permissions["suid"] or permissions["sgid"]:
                            logging.debug(f"Risky item detected: {entry.path}")
                            risky_items.append({
                                "path": entry.path,
                                "permissions": permissions
                            })
    except PermissionError:
        logging.warning(f"Permission denied for directory: {directory}")

    return risky_items

# Helper function to check for CIS compliance
def check_cis_compliance(entry, permissions):
    compliance_issues = []
    
    if permissions["suid"] or permissions["sgid"]:
        compliance_issues.append({
            "path": entry.path,
            "permissions": permissions,
            "reason": "SUID/SGID permissions set"
        })
    if permissions["world_writable"]:
        compliance_issues.append({
            "path": entry.path,
            "permissions": permissions,
            "reason": "World-writable file"
        })
    
    return compliance_issues if compliance_issues else None

# Helper functions for specific checks
def is_world_writable(entry):
    """Check if file is world-writable."""
    return bool(os.stat(entry.path).st_mode & 0o002)

def is_orphaned(entry):
    """Check if file has no valid user or group ownership."""
    uid = os.stat(entry.path).st_uid
    gid = os.stat(entry.path).st_gid
    return uid == 0 or gid == 0  # Adjust as needed for orphaned file criteria
