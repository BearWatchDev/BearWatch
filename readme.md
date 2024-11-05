BearWatch Documentation
Overview

Overview

BearWatch is a cross-platform file permissions auditing tool designed for system administrators and cybersecurity professionals. Its core function is to identify files and directories with insecure permissions, helping to mitigate risks associated with unauthorized access.

With a focus on user customization, BearWatch allows users to:

    - Specify directories to scan, identifying world-writable files, SUID/SGID files, and other risky permissions.
    - Generate detailed, timestamped reports to document vulnerabilities and maintain compliance.
    - Limit the number of stored reports with a rollover system, ensuring efficient storage usage.
    - Toggle debug logging for deeper insight during troubleshooting, accessible directly from the configuration menu.

BearWatch is ideal for security auditing on Linux systems and WSL environments, giving users the power to proactively manage file permissions. It provides a streamlined interface with customizable options, empowering users to take full control over their environment's security configuration.

    1. Installation
    2. Setup and Configuration
    3. Features
    4. Menu Structure
    5. Usage
    6. Version History
    7. Contributing

1. Installation

    Clone the Repository:

    bash

git clone <repository_url>
cd bearwatch

Install Dependencies: Install any required Python packages by running:

bash

pip install -r requirements.txt

Setup Configuration: Run BearWatch to initialize the default configuration file:

bash

    python overseer.py

2. Setup and Configuration

BearWatch includes a default configuration file settings.json located in the config/ directory. This file stores customizable settings, including logging level, output directory, and rollover report count. The user settings are saved persistently, and the configuration menu allows you to adjust these as needed.

Key Configuration Options:

    Logging Level: Set through the full menu under Report Options.
    Output Directory: Default directory for saving reports.
    Max Reports: Maximum number of reports to retain.

3. Features
Core Features

    Permissions Scanning: Identifies risky file permissions and directories based on safe defaults.
    Report Generation: Generates comprehensive reports of identified risks.
    Report Rollover Management: Limits the number of stored reports to save disk space.
    Debug Logging: Toggle debug logging on/off from the full menu.

4. Menu and Submenu Options

The menu system allows users to configure the application, initiate scans, and manage report generation.

    Set maximum number of rollover reports: Define how many reports BearWatch retains before older reports are deleted.
    Default output directory: Configure where generated reports are saved.
    Start scan: Initiate a scan based on pre-configured directories and options.
    Full configuration menu: Access advanced settings, including scan and report options.

5. Menu Structure

Below is the full menu structure of BearWatch, including main menu options, full configuration menu, and submenus.

BearWatch Main Menu
======================
1. Set maximum number of rollover reports   - [Functional]
2. Set default output directory             - [Functional]
3. Start scan                               - [Functional]
4. Configure using the full menu            - [Functional]
0. Exit                                     - [Functional]

BearWatch Full Configuration Menu
=================================
1. Detail Level                             - [Functional]
2. Number of Rollover Reports               - [Functional]
3. Output Location                          - [Functional]
4. Toggle Debug Logging                     - [Functional]
0. Return to Main Menu                      - [Functional]

Extended Options Menu (BearWatch Main Menu >)
=============================================
1. Scan Options                             - [Functional]
2. Report Options                           - [Functional]
3. Performance Metrics                      - **[Non-functional]**
4. General Options                          - **[Non-functional]**
0. Exit                                     - [Functional]

Scan Options Menu
=================
1. Select Directories to Scan               - [Functional]
2. Exclude Specific File Types              - **[Non-functional]**
3. Set Scan Depth                           - **[Non-functional]**
0. Return to Extended Options Menu          - [Functional]

Report Options Menu
===================
1. Detail Level: summary                    - [Functional]
2. Number of Rollover Reports: 30           - [Functional]
3. Output Location: /home/reports           - [Functional]
4. **Advanced Settings**                    - [Non-functional]
5. **Audit Logs Management**                - [Non-functional]
0. Return to Extended Options Menu          - [Functional]

General Options Menu
====================
1. Change Display Theme                     - **[Non-functional]**
2. Set Notification Preferences             - **[Non-functional]**
3. Manage User Permissions                  - **[Non-functional]**
0. Return to Extended Options Menu          - [Functional]

6. Usage
Running BearWatch

To start BearWatch, run the main script overseer.py:

python overseer.py

Sample Workflow

    Start BearWatch and access the main menu.
    Configure settings via the Full Configuration Menu to set detail level, output location, and logging preferences.
    Start a Scan from the main menu to audit the specified directories.
    View Reports: Reports will be saved in the configured output directory with a timestamped filename.

7. Version History
[1.0.3] - 2024-11-05
- Improved directory scanning and report handling for better performance and user experience.
- Enhanced settings management with streamlined loading and configuration reset functionality.
- Refined debug control for cleaner output and logging based on user preferences.
- Minor bug fixes and user interface optimizations to support smoother operation.

[1.0.2] - 2024-10-29
- Configurations now load dynamically before each scan.
- Enhanced settings_manager.py to handle output locations and rollover settings.
- Refined trailmap.py for report rollover using user-defined limits.
- Modular improvements and bug fixes across overseer.py, navigator.py, and settings.

[1.0.1] - 2024-10-29
Added
- Debug logging toggle accessible via the full configuration menu.

[1.0.0] - 2024-10-20
Initial Release
- Core permissions scanning functionality.
- Safe directory scanning defaults.
- Report rollover management.
- Basic user interface with options for setting reports and output directories.

8. Contributing

Contributions are welcome! Please follow these steps:

    Fork the repository.
    Create a new branch with a descriptive name.
    Make your changes and test thoroughly.
    Submit a pull request with a detailed explanation of your changes.

Questions? bearwatchdev@pm.me