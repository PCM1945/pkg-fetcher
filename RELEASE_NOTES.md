# Release Notes - PKG Fetcher

## Version 0.9.3 (January 6, 2026)

### Overview
PKG Fetcher v0.9.3 is a stable release of the desktop application for fetching and downloading PlayStation update packages using serial numbers.

### Features

#### Core Functionality
- **Serial Number Search**: Query packages using PKG serial numbers (e.g., NPUA80490)
- **Bulk Processing**: Enter multiple serial numbers at once (one per line) for batch operations
- **Package Discovery**: Fetch and display available packages with details:
  - Selection checkbox for selective downloading
  - Package title
  - Package tag
  - Version number
  - Size information (in MB)

#### Download Management
- **Selective Downloads**: Check/uncheck packages to download only desired items
- **Progress Tracking**: Real-time progress bar showing download completion percentage
- **Activity Logging**: Detailed log panel displaying all operations and errors
- **Package Management**: Remove selected packages from the list before downloading

#### Configuration
- **Settings Dialog** (⚙ button): User-friendly configuration interface
  - XML URL Template: Configurable server endpoint (use `{s}` placeholder for serial number)
  - Request Timeout: Adjustable timeout (5-120 seconds, default: 15s)
  - SSL Verification: Toggle SSL certificate verification
  - Output Directory: Specify package save location (default: `pkgs/`)
  - Chunk Size: Adjust download chunk size for performance tuning (default: 1MB)
  - Reset Option: Restore all settings to defaults

### Technical Details

**Version**: 0.9.3  
**Release Date**: January 6, 2026  
**Platform**: Windows, Linux, macOS

#### Dependencies
- Python 3.x
- PyQt5 (5.15.11)
- requests (2.32.5)

#### Build Information
- Packaged with PyInstaller 6.17.0
- Standalone executable available in `dist/` directory

### System Requirements
- **OS**: Windows 10+, Linux, or macOS
- **Memory**: 256MB minimum
- **Disk Space**: 100MB for application + space for package downloads
- **Network**: Internet connection required for package fetching

### Configuration File
Application automatically creates `config.json` on first run:
```json
{
  "server": {
    "xml_url": "https://a0.ww.np.dl.playstation.net/tpl/np/{s}/{s}-ver.xml",
    "timeout": 15,
    "verify_ssl": false
  },
  "download": {
    "chunk_size": 1048576,
    "output_directory": "pkgs"
  }
}
```

### Installation & Usage

#### Via Python
```bash
pip install -r requirements.txt
python main.py
```

#### Via Executable
Navigate to `dist/` folder and run the standalone executable.

### Usage Workflow
1. Launch the application
2. (Optional) Configure settings via ⚙ Settings button
3. Enter a serial number or multiple IDs in the text area
4. Click "Search" to fetch available packages
5. Select desired packages using checkboxes
6. Click "Download Selected" to begin downloading
7. Monitor progress in the progress bar and activity log

### Known Limitations
- Server URL must be manually configured (no default for security reasons)
- Requires valid internet connection for all operations
- SSL verification disabled by default (configurable)

### Important Notes
⚠️ **Server URL Configuration Required**: The application does not ship with a default server URL. Users must obtain and configure the valid XML server URL endpoint before the application can fetch packages.

### File Structure
```
pkg-fetcher/
├── main.py                 # Main application entry point
├── config.py               # Configuration management
├── config.json             # Configuration file (auto-generated)
├── requirements.txt        # Python dependencies
├── main.spec              # PyInstaller specification
├── README.md              # User documentation
├── RELEASE_NOTES.md       # This file
├── ui/                    # UI components
│   ├── ConfigDialog.py    # Settings dialog
│   ├── DownloadThread.py  # Download worker thread
│   └── FetchThread.py     # Package fetch worker thread
└── dist/                  # Packaged executable
```

### Support
For issues, questions, or feature requests, please refer to the README.md or check the application's activity log for detailed error information.

---

**Release prepared on**: January 6, 2026  
**Status**: Stable Release
