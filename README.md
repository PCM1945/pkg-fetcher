# PKG Fetcher

A PyQt5-based desktop application for fetching and downloading update packages by serial number.

## Overview

PKG Fetcher is a user-friendly GUI application that allows you to:
- Search for update packages using a PKG serial number
- View available packages with details (title, version, size)
- Download selected packages with progress tracking
- Manage your package list with intuitive selection controls

## Features

- **Serial Number Search**: Enter a PKG serial number (e.g., `NPUA80490`) to fetch available packages
- **Package Browse**: View all available packages in a table with columns for:
  - Selection checkbox
  - title
  - Package tag
  - Version number
  - Size in MB
- **Selective Download**: Check/uncheck packages and download only the ones you want
- **Progress Tracking**: Real-time progress bar showing download completion percentage
- **Logging**: Detailed activity log showing all operations and any errors
- **Package Management**: Remove selected packages from the list before downloading

## System Requirements

- Python 3.x
- PyQt5
- requests library

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install PyQt5 requests
   ```
3. A `config.json` file will be automatically created on first run with default settings

## Configuration

The application uses a `config.json` file to manage settings. The file is automatically created on first run with these defaults:

```json
{
  "server": {
    "xml_url": "{add server url}",
    "timeout": 15,
    "verify_ssl": false
  },
  "download": {
    "chunk_size": 1048576,
    "output_directory": "pkgs"
  }
}
```

### Configurable Settings

- **xml_url**: The server URL template. Use `{s}` as placeholder for serial number
- **timeout**: Request timeout in seconds for fetching package information
- **verify_ssl**: Whether to verify SSL certificates (set to `false`)
- **chunk_size**: Download chunk size in bytes (default: 1MB = 1048576 bytes)
- **output_directory**: Directory where downloaded packages are saved (relative to app directory)

## Usage

### Running the Application

```bash
python main.py
```

### Accessing Settings

Click the **⚙ Settings** button in the top-right corner of the application to open the configuration dialog. Here you can:

- **Modify the XML URL**: Change the server endpoint template (use `{s}` for serial number placeholder)
- **Adjust Request Timeout**: Set how long to wait for server responses (5-120 seconds)
- **Toggle SSL Verification**: Enable/disable SSL certificate verification
- **Change Output Directory**: Specify where downloaded packages are saved
- **Adjust Chunk Size**: Modify download chunk size for performance tuning
- **Reset to Defaults**: Restore all settings to their original values

All changes are automatically saved to `config.json`.

### How to Use

1. **Configure Settings** (Optional): Click the "⚙ Settings" button to customize server and download settings
   - The default configuration should work for most users
   - Settings are saved to `config.json` for persistence

2. **Enter Serial Number**: In the "Serial" input field, enter a PKG console serial number (e.g., `NPUA80490`)
   - Press Enter or click the "Search" button
   - The application will fetch available packages from the servers

3. **Browse Packages**: Once fetched, all available packages will appear in the table
   - Check the boxes for packages you want to download
   - View details like title, version, and file size

4. **Download**: 
   - Select the packages you want by checking their checkboxes
   - Click "Download selected" button
   - Progress bar will show download progress
   - Check the log panel for detailed status updates

5. **Manage Packages**:
   - Use "Remove selected" to delete packages from the list before downloading
   - Packages are automatically removed from the list after successful download

## Project Structure

```
rpcsupdater/
├── main.py                          # Main application entry point
├── mainUI.py                        # UI class definition
├── config.py                        # Configuration manager
├── config.json                      # Configuration file (auto-created)
├── main.spec                        # PyInstaller configuration
├── ui/
│   ├── __init__.py                  # UI package initialization
│   ├── FetchThread.py               # Worker thread for fetching packages from servers
│   ├── DownloadThread.py            # Worker thread for downloading packages
│   └── ConfigDialog.py              # Settings dialog UI
├── pkgs/                            # Downloaded packages directory (created automatically)
└── build/                           # PyInstaller build artifacts
```

## Technical Details

### Architecture

The application uses a multi-threaded design to prevent UI freezing:

- **FetchThread.py**: Handles XML parsing from servers
  - Fetches package manifest using serial number
  - Parses XML response containing available games
  - Emits signals with package data back to UI

- **DownloadThread.py**: Manages package downloads
  - Downloads selected packages in sequence
  - Streams data in 1MB chunks for memory efficiency
  - Tracks progress and file sizes
  - Automatically creates `pkgs/` directory

### Data Flow

1. User enters serial → triggers `FetchWorker`
2. `FetchWorker` queries servers (XML endpoint)
3. XML is parsed and packages are returned to UI
4. User selects packages → triggers `DownloadWorker`
5. `DownloadWorker` downloads files to `pkgs/` folder
6. Progress updates via signals throughout process

## Building an Executable

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller main.spec
```

The executable will be generated in the `dist/` folder.

## Error Handling

The application includes:
- Connection timeout handling (15 second timeout for fetch operations)
- HTTP error checking
- File write verification
- Thread cleanup on errors
- User-friendly error dialogs

## Notes

- Configuration is stored in `config.json` and can be modified without code changes
- SSL certificate verification is disabled by default for server connections (configurable)
- Downloaded files are saved to the directory specified in config (default: `pkgs/`)
- All operations run in background threads to keep the UI responsive
- The XML endpoint URL is customizable via config file for different server endpoints

## Troubleshooting

**"No PKG found"**: The serial number may be invalid or the console has no games available for download

**Connection timeout**: Check your internet connection or try again later

**Download fails**: Verify the package URL is still valid and your internet connection is stable

## License

[Add your license here]

## Author

[Add your name/contact here]
