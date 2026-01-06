import os
import requests
import sys
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DownloadWorker(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, packages):
        super().__init__()
        self.packages = packages

    def run(self):
        try:
            config = Config.load()
            output_dir = Config.get_output_directory(config)
            chunk_size = Config.get_chunk_size(config)
            verify_ssl = Config.get_verify_ssl(config)
            
            os.makedirs(output_dir, exist_ok=True)
            total = len(self.packages)
            downloaded_size = 0

            for idx, pkg in enumerate(self.packages, start=1):
                self.log.emit(f"Downloading {pkg['title']} ({pkg['version']})")

                filename = os.path.join(
                    output_dir, pkg["url"].split("/")[-1]
                )

                with requests.get(pkg["url"], stream=True, verify=verify_ssl) as r:
                    r.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                
                # Verify file was written
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    downloaded_size += file_size
                    self.log.emit(f"✓ Saved: {filename} ({file_size / 1024 / 1024:.2f} MB)")
                else:
                    self.log.emit(f"✗ Failed to save: {filename}")

                self.progress.emit(int(idx / total * 100))

            self.log.emit(f"Total downloaded: {downloaded_size / 1024 / 1024:.2f} MB")
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))