import json
import os
from pathlib import Path

class Config:
    """Configuration manager for PKG Fetcher."""
    
    CONFIG_FILE = "config.json"
    DEFAULT_CONFIG = {
        "server": {
            "xml_url": "",
            "timeout": 15,
            "verify_ssl": False
        },
        "download": {
            "chunk_size": 1048576,  # 1 MB
            "output_directory": "pkgs"
        }
    }
    
    @classmethod
    def load(cls):
        """Load configuration from config.json or use defaults."""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}. Using defaults.")
                return cls.DEFAULT_CONFIG
        else:
            # Create default config file
            cls.save(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG
    
    @classmethod
    def save(cls, config_data):
        """Save configuration to config.json."""
        try:
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            print(f"Error saving config file: {e}")
    
    @classmethod
    def get_xml_url(cls, config=None):
        """Get the XML URL template from config."""
        if config is None:
            config = cls.load()
        return config["server"]["xml_url"]
    
    @classmethod
    def get_timeout(cls, config=None):
        """Get the request timeout from config."""
        if config is None:
            config = cls.load()
        return config["server"]["timeout"]
    
    @classmethod
    def get_verify_ssl(cls, config=None):
        """Get SSL verification setting from config."""
        if config is None:
            config = cls.load()
        return config["server"]["verify_ssl"]
    
    @classmethod
    def get_chunk_size(cls, config=None):
        """Get download chunk size from config."""
        if config is None:
            config = cls.load()
        return config["download"]["chunk_size"]
    
    @classmethod
    def get_output_directory(cls, config=None):
        """Get output directory from config."""
        if config is None:
            config = cls.load()
        return config["download"]["output_directory"]
