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
        self.serial = serial

    def run(self):
        try:
            config = Config.load()
            xml_url = Config.get_xml_url(config)
            timeout = Config.get_timeout(config)
            verify_ssl = Config.get_verify_ssl(config)
            
            url = xml_url.format(s=self.serial)
            self.log.emit(f"Fetching XML: {url}")

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
                        "url": pkg.attrib.get("url")
                    })

            if not packages:
                raise RuntimeError("No PKG found.")

            self.finished.emit(packages)

        except Exception as e:
            self.error.emit(str(e))
