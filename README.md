# Linux Migration Toolkit (LMTK)

LMTK is a desktop application designed to assist users in migrating from Windows to Linux. It streamlines the process by providing tools to gather system information, back up important data, and prepare Linux installation media.

## Features

- **System Information Gathering:** Automatically collects software and hardware details, generating comprehensive Markdown (.md) and HTML (.html) reports for future reference.
- **Data Backup:** Facilitates backing up user data into compressed tar or tar.bz2 archives. Users can select specific source folders and define a destination for the backup.
- **Installation Media Preparation:** Guides users through the process of creating bootable Linux installation media, providing direct links to recommended media writing tools and relevant tutorials.
- **Dual Operating Modes:** Offers both a 'Novice Mode' with guided steps and helpful links for new Linux users, and an 'Expert Mode' for experienced users who prefer a more direct workflow.
- **PowerShell Integration:** Utilizes PowerShell for specific Windows-related operations, such as hardware detection and listing standard home directories.

## Installation

Everything is packed into one executable in release/latest. You'll need PowerShell v.5.11 or later, which is normally installed.

- [Download the latest release](https://github.com/ikostas/lmtk/releases/download/v1.0/LMTK.exe)

## Usage

Upon launching LMTK, you will be presented with a choice between 'Novice Mode' and 'Expert Mode'.

-   **Novice Mode:** Provides guidance and helpful links
-   **Expert Mode:** Provides less comments, assuming you know what to do

Follow the on-screen instructions to gather system information, back up your data, and prepare your installation media.

## Development

To set up and run LMTK, follow these steps:

1.  **Prerequisites:**
    *   **Python 3:** Ensure you have Python 3 installed on your system.
    *   **PowerShell:** LMTK relies on PowerShell for certain functionalities. Please ensure PowerShell is installed and accessible on your Windows system.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/lmtk.git
    cd lmtk
    ```

3.  **Install Dependencies:**
    Install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    python dialog.py
    ```

5.  **Build the Executable:**
    ```bash
    pyinstaller --onefile --distpath release/1.0 --name=LMTK dialog.py
    ```

## License

This project is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

Inspired by the community at reddit.com/r/linuxsucks/.
