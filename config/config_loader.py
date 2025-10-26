"""
Configuration Loader Utility
Loads configuration from YAML and environment variables
"""

import yaml
import os
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Configuration loader that merges YAML config with environment variables"""
    
    def __init__(self, config_path="config/config.yaml", env_path=".env"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to YAML configuration file
            env_path: Path to .env file
        """
        self.config_path = config_path
        self.env_path = env_path
        self.config = None
        
    def load(self):
        """
        Load configuration from YAML and merge with environment variables
        
        Returns:
            dict: Complete configuration
        """
        load_dotenv(self.env_path)
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self._load_reddit_credentials()
        self._resolve_paths()
        
        return self.config
    
    def _load_reddit_credentials(self):
        """Load Reddit API credentials from environment variables"""
        reddit_config = self.config.get('reddit', {})
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')
        
        if client_id:
            reddit_config['client_id'] = client_id
        if client_secret:
            reddit_config['client_secret'] = client_secret
        if user_agent:
            reddit_config['user_agent'] = user_agent
            
        self.config['reddit'] = reddit_config
    
    def _resolve_paths(self):
        """Convert relative paths to absolute paths"""
        base_path = Path.cwd()
        
        if 'paths' in self.config:
            for key, path in self.config['paths'].items():
                if not Path(path).is_absolute():
                    self.config['paths'][key] = str(base_path / path)
    
    def get(self, key, default=None):
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        if self.config is None:
            self.load()
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate_reddit_credentials(self):
        """
        Validate Reddit API credentials are present
        
        Returns:
            bool: True if valid, False otherwise
        """
        if self.config is None:
            self.load()
        
        reddit = self.config.get('reddit', {})
        
        required = ['client_id', 'client_secret', 'user_agent']
        for field in required:
            value = reddit.get(field, '')
            if not value or value.startswith('YOUR_') or value.startswith('your_'):
                return False
        
        return True
    
    def get_reddit_config(self):
        """
        Get Reddit API configuration
        
        Returns:
            dict: Reddit configuration
        """
        if self.config is None:
            self.load()
        
        return self.config.get('reddit', {})


def load_config(config_path="config/config.yaml", env_path=".env"):
    """
    Convenience function to load configuration
    
    Args:
        config_path: Path to YAML configuration file
        env_path: Path to .env file
    
    Returns:
        dict: Complete configuration
    """
    loader = ConfigLoader(config_path, env_path)
    return loader.load()
