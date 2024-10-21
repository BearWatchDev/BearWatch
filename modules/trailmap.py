import os
import time
from datetime import datetime

REPORT_DIR = "reports"  # Default directory to store report files

def generate_report(risky_items, summary, output_file=None):
    """
    Generates a report of the risky permissions found by BearWatch.
    
    Args:
        risky_items (list): List of risky files and directories.
        summary (dict): Summary of the risks (world-writable, SUID, SGID counts).
        output_file (str): Optional file path to save the report. If None, defaults to REPORT_DIR.
    """
    # Timestamp for the report (human-readable)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Unix timestamp (for uniqueness)
    unix_timestamp = int(time.time())

    # Header for the report
    report = []
    report.append("🐾 BearWatch Report")
    report.append(f"Scan Time: {timestamp}")
    report.append("=" * 40)
    
    # Add the summary
    report.append(f"World-writable files: {summary['world_writable']}")
    report.append(f"SUID files: {summary['suid']}")
    report.append(f"SGID files: {summary['sgid']}")
    report.append("=" * 40)
    
    # Add details about risky files
    if risky_items:
        report.append("Detailed Risk Report:")
        for item in risky_items:
            report.append(f"🛠️ Path: {item['path']}, Permissions: {item['permissions']}")
    else:
        report.append("No risky files or directories found.")
    
    # Add the Unix timestamp at the end of the report
    report.append("=" * 40)
    report.append(f"Unix Timestamp: {unix_timestamp}")
    
    # Join all report lines into a single string
    report_content = "\n".join(report)
    
    # Ensure the reports directory exists or output_file path directory exists
    if output_file is None:
        # Use default REPORT_DIR if no output_file is specified
        if not os.path.exists(REPORT_DIR):
            os.makedirs(REPORT_DIR)
        output_file = os.path.join(REPORT_DIR, f"bearwatch_report_{unix_timestamp}.txt")
    else:
        # Ensure the directory of output_file exists
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    # Save the report to a file
    try:
        with open(output_file, 'w') as file:
            file.write(report_content)
        print(f"🐻 BearWatch has saved the report to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save the report: {str(e)}")
    
    # Manage the number of reports (keep only the allowed max)
    report_dir = os.path.dirname(output_file) if output_file else REPORT_DIR
    manage_reports(report_dir)

def manage_reports(report_dir, max_reports=10):
    """
    Ensures only the most recent 'max_reports' are kept in the directory.
    Deletes the oldest reports if the count exceeds the limit.
    
    Args:
        report_dir (str): The directory where the reports are stored.
        max_reports (int): The maximum number of reports to keep.
    """
    # List all files in the report directory
    report_files = [os.path.join(report_dir, f) for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]

    # Sort files by creation time (oldest first)
    report_files.sort(key=os.path.getctime)

    # If the number of reports exceeds the max limit, delete the oldest ones
    if len(report_files) > max_reports:
        # Delete the oldest files
        excess_reports = len(report_files) - max_reports
        for i in range(excess_reports):
            os.remove(report_files[i])
            print(f"🗑️ Old report {report_files[i]} has been deleted due to maximum log entries")