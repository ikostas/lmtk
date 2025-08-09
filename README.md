# Linux Migration Toolkit (LMTK)

LMTK is a desktop app that helps users migrate from Windows to Linux. It simplifies the process with tools for system info gathering, data backup, and preparing Linux installation media.

## Features

- System Info Reports: Collects hardware and software details, saves them as Markdown and HTML.
- Data Backup: Archives selected folders into .tar or .tar.bz2 files.
- Installation Media Prep: Helps create bootable Linux USBs with links to writing tools and tutorials.
- Novice & Expert Modes: Choose between a guided or streamlined workflow.

## Installation

Unpack the .zip file and launch executable, no installation is required. You'll need PowerShell v.5.11 or later, which is normally installed.

- [Download the latest release](https://github.com/ikostas/lmtk/releases/latest)

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

5.  **Update the Translations:**
    ```bash
    xgettext -o locales/messages.pot *.py
    msgmerge --update locales/de/LC_MESSAGES/messages.po locales/messages.pot
    msgfmt locales/de/LC_MESSAGES/messages.po -o locales/de/LC_MESSAGES/messages.mo
    ```

6.  **Build the Executable:**
    ```bash
    pyinstaller dialog.spec --distpath release/1.1
    ```

## License

This project is licensed under the GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

Inspired by the community at reddit.com/r/linuxsucks/.
