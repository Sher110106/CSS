"""
Utility Functions for Semaglutide Reddit Analysis
Helper functions for logging, data I/O, text cleaning, and validation
"""

import logging
import os
import json
import yaml
import pandas as pd
import re
import hashlib
from datetime import datetime
from pathlib import Path


def setup_logger(name, log_file, level=logging.INFO):
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
    
    Returns:
        logger: Configured logger instance
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config(config_path="config/config.yaml"):
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
    
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise FileNotFoundError(f"Config file not found: {config_path}. Error: {e}")


def save_dataframe(df, filepath, format='csv'):
    """
    Save dataframe to file
    
    Args:
        df: Pandas DataFrame
        filepath: Output file path
        format: File format (csv, json, excel)
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'json':
        df.to_json(filepath, orient='records', indent=2)
    elif format == 'excel':
        df.to_excel(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_dataframe(filepath):
    """
    Load dataframe from file
    
    Args:
        filepath: Input file path
    
    Returns:
        DataFrame: Loaded dataframe
    """
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.json'):
        return pd.read_json(filepath)
    elif filepath.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def save_json(data, filepath):
    """
    Save data to JSON file
    
    Args:
        data: Data to save (dict or list)
        filepath: Output file path
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(filepath):
    """
    Load data from JSON file
    
    Args:
        filepath: Input file path
    
    Returns:
        Data from JSON file
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def remove_urls(text):
    """
    Remove URLs from text
    
    Args:
        text: Input text
    
    Returns:
        str: Text with URLs removed
    """
    if not isinstance(text, str):
        return ""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub('', text)


def remove_emojis(text):
    """
    Remove emojis from text
    
    Args:
        text: Input text
    
    Returns:
        str: Text with emojis removed
    """
    if not isinstance(text, str):
        return ""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def remove_usernames(text):
    """
    Remove Reddit usernames from text
    
    Args:
        text: Input text
    
    Returns:
        str: Text with usernames removed
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'u/\w+', '', text)
    text = re.sub(r'@\w+', '', text)
    return text


def clean_text(text):
    """
    Comprehensive text cleaning
    
    Args:
        text: Input text
    
    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    text = remove_urls(text)
    text = remove_emojis(text)
    text = remove_usernames(text)
    text = re.sub(r'\[deleted\]', '', text)
    text = re.sub(r'\[removed\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s\.\,\!\?\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def anonymize_text(text):
    """
    Anonymize text by removing identifiable information
    
    Args:
        text: Input text
    
    Returns:
        str: Anonymized text
    """
    text = remove_usernames(text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    return text


def hash_username(username):
    """
    Hash username for anonymization
    
    Args:
        username: Username string
    
    Returns:
        str: Hashed username
    """
    if not isinstance(username, str):
        return "anonymous"
    return hashlib.sha256(username.encode()).hexdigest()[:16]


def calculate_basic_stats(data):
    """
    Calculate basic statistics for dataset
    
    Args:
        data: DataFrame or dict
    
    Returns:
        dict: Statistics dictionary
    """
    if isinstance(data, pd.DataFrame):
        stats = {
            'total_records': len(data),
            'columns': list(data.columns),
            'missing_values': data.isnull().sum().to_dict(),
            'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024**2
        }
    else:
        stats = {
            'type': str(type(data)),
            'length': len(data) if hasattr(data, '__len__') else None
        }
    
    return stats


def export_summary_stats(stats, filepath):
    """
    Export statistics to JSON file
    
    Args:
        stats: Statistics dictionary
        filepath: Output file path
    """
    stats['generated_at'] = datetime.now().isoformat()
    save_json(stats, filepath)


def validate_dataframe(df, required_columns):
    """
    Validate dataframe has required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
    
    Returns:
        bool: True if valid
    
    Raises:
        ValueError: If validation fails
    """
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return True


def check_data_quality(df):
    """
    Check data quality and return report
    
    Args:
        df: DataFrame to check
    
    Returns:
        dict: Quality report
    """
    report = {
        'total_records': len(df),
        'duplicate_records': df.duplicated().sum(),
        'missing_values_by_column': df.isnull().sum().to_dict(),
        'total_missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'dtypes': df.dtypes.astype(str).to_dict()
    }
    
    return report


def ensure_directories_exist(config):
    """
    Ensure all required directories exist
    
    Args:
        config: Configuration dictionary
    """
    paths = config.get('paths', {})
    for path in paths.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    
    Path('logs').mkdir(exist_ok=True)
