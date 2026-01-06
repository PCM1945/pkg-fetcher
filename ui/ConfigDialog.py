from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QCheckBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class ConfigDialog(QDialog):
    """Configuration dialog for PKG Fetcher settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.config = Config.load()
        self._build_ui()
        self._load_values()
    
    def _build_ui(self):
        """Build the configuration UI."""
        layout = QVBoxLayout()
        
        # Server Settings
        layout.addWidget(QLabel("<b>Server Settings</b>"))
        
        # XML URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("XML URL Template:"))
        self.xml_url_input = QLineEdit()
        self.xml_url_input.setToolTip("Use {s} as placeholder for serial number")
        url_layout.addWidget(self.xml_url_input)
        layout.addLayout(url_layout)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Request Timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(5)
        self.timeout_spin.setMaximum(120)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)
        
        # SSL Verification
        self.verify_ssl_check = QCheckBox("Verify SSL Certificate")
        layout.addWidget(self.verify_ssl_check)
        
        layout.addSpacing(20)
        
        # Download Settings
        layout.addWidget(QLabel("<b>Download Settings</b>"))
        
        # Output Directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QLineEdit()
        output_layout.addWidget(self.output_dir_input)
        layout.addLayout(output_layout)
        
        # Chunk Size
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Download Chunk Size (bytes):"))
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setMinimum(65536)  # 64 KB
        self.chunk_size_spin.setMaximum(10485760)  # 10 MB
        self.chunk_size_spin.setSingleStep(65536)
        chunk_layout.addWidget(self.chunk_size_spin)
        chunk_layout.addStretch()
        layout.addLayout(chunk_layout)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_values(self):
        """Load current configuration values into UI fields."""
        server_config = self.config.get("server", {})
        download_config = self.config.get("download", {})
        
        self.xml_url_input.setText(server_config.get("xml_url", ""))
        self.timeout_spin.setValue(server_config.get("timeout", 15))
        self.verify_ssl_check.setChecked(server_config.get("verify_ssl", False))
        self.output_dir_input.setText(download_config.get("output_directory", "pkgs"))
        self.chunk_size_spin.setValue(download_config.get("chunk_size", 1048576))
    
    def _save_config(self):
        """Save configuration to file."""
        # Validate XML URL
        if not self.xml_url_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "XML URL cannot be empty.")
            return
        
        if "{s}" not in self.xml_url_input.text():
            QMessageBox.warning(self, "Validation Error", "XML URL must contain {s} placeholder for serial number.")
            return
        
        # Validate output directory
        if not self.output_dir_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Output directory cannot be empty.")
            return
        
        # Update config dictionary
        self.config["server"]["xml_url"] = self.xml_url_input.text().strip()
        self.config["server"]["timeout"] = self.timeout_spin.value()
        self.config["server"]["verify_ssl"] = self.verify_ssl_check.isChecked()
        self.config["download"]["output_directory"] = self.output_dir_input.text().strip()
        self.config["download"]["chunk_size"] = self.chunk_size_spin.value()
        
        # Save to file
        Config.save(self.config)
        QMessageBox.information(self, "Success", "Settings saved successfully.")
        self.accept()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            Config.save(Config.DEFAULT_CONFIG)
            self.config = Config.load()
            self._load_values()
            QMessageBox.information(self, "Success", "Settings reset to defaults.")
