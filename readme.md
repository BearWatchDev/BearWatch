BearWatch Documentation
Overview

BearWatch is a cross-platform file permissions auditing tool designed for system administrators and cybersecurity professionals. Its core function is to identify files and directories with insecure permissions, helping to mitigate risks associated with unauthorized access.

With a focus on user customization, BearWatch allows users to:

    Specify directories to scan, identifying world-writable files, SUID/SGID files, orphaned files, and other risky permissions.
    Generate detailed, timestamped reports to document vulnerabilities and maintain compliance.
    Limit the number of stored reports with a rollover system, ensuring efficient storage usage.
    Toggle debug logging for deeper insight during troubleshooting, accessible directly from the configuration menu.
    Optionally enforce CIS benchmarks, adding another layer of security compliance checks.

BearWatch is ideal for security auditing on Linux systems and WSL environments, giving users the power to proactively manage file permissions. It provides a streamlined interface with customizable options, empowering users to take full control over their environment's security configuration.

1. Installation
Clone the Repository:

git clone <repository_url>
cd bearwatch

Install Dependencies:

Install any required Python packages by running:

pip install -r requirements.txt

Setup Configuration:

Run BearWatch to initialize the default configuration file:

python overseer.py

2. Setup and Configuration

BearWatch includes a default configuration file bearwatch_config.json located in the config/ directory. This file stores customizable settings, including logging level, output directory, and rollover report count. The user settings are saved persistently, and the configuration menu allows you to adjust these as needed.

Key Configuration Options:

    Logging Level: Set through the full menu under Report Options.
    Output Directory: Default directory for saving reports.
    Max Reports: Maximum number of reports to retain.
    
3. Features
Core Features

    Permissions Scanning: Identifies risky file permissions and directories based on safe defaults.
    CIS Benchmarks: Toggle to enforce compliance checks based on CIS benchmarks. *
    Report Generation: Generates comprehensive reports of identified risks.
    Report Rollover Management: Limits the number of stored reports to save disk space.
    Debug Logging: Toggle debug logging on/off from the full menu.

New Enhancements (Version 1.0.3)

    Enhanced Risk Detection: Added checks for orphaned files and CIS compliance.
    Settings Persistence: Improved settings management and loading processes.
    Detailed Error Handling: More robust error logging for skipped files.

    * Current CIS Benchmarks Implemented:

    SUID/SGID File Checks
        Objective: Identify files with SUID (Set User ID) or SGID (Set Group ID) bits set, which can pose a risk if misconfigured.
        Rationale: Files with SUID/SGID permissions can run with elevated privileges, potentially leading to privilege escalation if not properly managed.

    World-Writable File Detection
        Objective: Identify files or directories that are world-writable, which could allow any user to modify or delete critical files.
        Rationale: World-writable permissions (mode 777) are considered a security risk as they can be exploited by attackers to modify files or inject malicious code.

    Orphaned File Detection
        Objective: Identify files with no valid user or group ownership.
        Rationale: Orphaned files could indicate a misconfiguration or leftover artifacts from user management activities, which could be a sign of poor security hygiene.

4. Menu Structure
BearWatch Main Menu

1. Start scan
2. Configuration menu
0. Exit

BearWatch Full Configuration Menu

1. Scan Options
2. Report Options
3. Performance Metrics
4. General Options
5. Reset to Default Settings
0. Return to Main Menu

Scan Options Menu

1. Default Directory: /home
2. File Types: ['*.conf', '*.log']
3. Depth Limit: 3
4. Incremental Scan: True
5. Use CIS Benchmarks: [Toggle]
0. Return to Full Configuration Menu

Report Options Menu

1. Detail Level: summary
2. Number of Rollover Reports: 30
3. Output Location: /home/bearwatch/reports
4. Toggle Debug Logging
0. Return to Full Configuration Menu

Performance Metrics Menu

(Currently non-functional but planned for future development)
General Options Menu

(Currently non-functional but planned for future development)

5. Usage
Running BearWatch

To start BearWatch, run the main script:

python overseer.py

Sample Workflow

    Start BearWatch and access the main menu.
    Configure settings via the Full Configuration Menu to set detail level, output location, and logging preferences.
    Start a Scan from the main menu to audit the specified directories.
    View Reports: Reports will be saved in the configured output directory with a timestamped filename.

6. Version History
[1.0.3] - 2024-11-05

    New CIS Compliance Checks: Added functionality for checking CIS benchmarks, including orphaned files.
    Enhanced Error Logging: Detailed warnings for permissions not in expected formats.
    Improved User Interaction: Display detailed settings before a scan and streamlined settings management.
    Fixed Dictionary Issues: Resolved type errors during permissions checks.
    Debugging Updates: Enhanced debug logging for deeper troubleshooting insights.
    Report Rollover: Added refined rollover management to maintain efficient storage.

[1.0.2] - 2024-10-29

    Dynamic Configurations: Configurations now load dynamically before each scan.
    Rollover Settings: Updated trailmap.py for report rollover using user-defined limits.
    Modular Improvements: Improved modularity and fixed bugs in overseer.py and navigator.py.

[1.0.1] - 2024-10-21

    Debug Logging Toggle: Accessible via the full configuration menu.

[1.0.0] - 2024-10-20

    Initial Release: Core functionality for permissions scanning, safe defaults, and report management.

7. Contributing

Contributions are welcome! Please follow these steps:

    Fork the repository.
    Create a new branch with a descriptive name.
    Make your changes and test thoroughly.
    Submit a pull request with a detailed explanation of your changes.

Questions? bearwatchdev@pm.me