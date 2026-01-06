from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox, QProgressBar, QTextEdit
)

import requests
import xml.etree.ElementTree as ET
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

from PyQt5.QtCore import QObject, pyqtSignal


class FetchWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, serial):
        super().__init__()
        # Accept both a single serial (string) or a list of serials
        if isinstance(serial, list):
            self.serials = serial
        else:
            self.serials = [serial]

    def run(self):
        try:
            config = Config.load()
            xml_url = Config.get_xml_url(config)
            timeout = Config.get_timeout(config)
            verify_ssl = Config.get_verify_ssl(config)
            
            # Check if XML URL is configured
            if not xml_url or xml_url.strip() == "" or "{add server url}" in xml_url.lower():
                raise RuntimeError(
                    "Server URL is not configured.\n\n"
                    "Please:\n"
                    "1. Click the ⚙ Settings button\n"
                    "2. Enter the server URL in the 'XML URL Template' field\n"
                    "3. Save the settings\n\n"
                    "The URL should be in format: https://example.com/path/{s}-ver.xml\n"
                    "(where {s} is the serial number placeholder)"
                )
            
            all_packages = []

            for serial in self.serials:
                url = xml_url.format(s=serial)
                self.log.emit(f"Fetching XML for {serial}: {url}")

                try:
                    r = requests.get(url, timeout=timeout, verify=verify_ssl)
                    r.raise_for_status()

                    root = ET.fromstring(r.text)
                    packages = []

                    for tag in root.findall("tag"):
                        tag_name = tag.attrib.get("name")
                        for pkg in tag.findall("package"):
                            packages.append({
                                "title": pkg.findtext(".//TITLE"),
                                "tag": tag_name,
                                "version": pkg.attrib.get("version"),
                                "size": int(pkg.attrib.get("size", 0)),
                                "url": pkg.attrib.get("url"),
                                "serial": serial
                            })

                    if packages:
                        self.log.emit(f"  Found {len(packages)} package(s) for {serial}")
                        all_packages.extend(packages)
                    else:
                        self.log.emit(f"  No packages found for {serial}")

                except Exception as e:
                    self.log.emit(f"  {serial} file not available")
                    #self.log.emit(f"  Error fetching {serial}: {str(e)}")
                    continue

            if not all_packages:
                raise RuntimeError("No PKG found for any serial.")

            self.finished.emit(all_packages)

        except Exception as e:
            self.error.emit(str(e))
