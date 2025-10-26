"""
Setup Validation Script
Validates that the project environment is correctly configured
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils import setup_logger, load_config
from config.config_loader import ConfigLoader


def validate_directory_structure():
    """Validate that all required directories exist"""
    print("\n=== Validating Directory Structure ===")
    
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/anonymized',
        'data/metadata',
        'models/lda',
        'models/evaluation',
        'models/checkpoints',
        'visualizations/wordclouds',
        'visualizations/charts',
        'visualizations/interactive',
        'visualizations/report_figures',
        'visualizations/eda',
        'scripts',
        'logs',
        'config',
        'report/sections',
        'notebooks'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def validate_config_files():
    """Validate that all required configuration files exist"""
    print("\n=== Validating Configuration Files ===")
    
    required_files = [
        'config/config.yaml',
        'requirements.txt',
        '.env.template',
        '.gitignore'
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist


def validate_python_packages():
    """Validate that required Python packages are installed"""
    print("\n=== Validating Python Packages ===")
    
    required_packages = [
        'praw',
        'pandas',
        'numpy',
        'nltk',
        'spacy',
        'gensim',
        'vaderSentiment',
        'matplotlib',
        'seaborn',
        'wordcloud',
        'pyLDAvis',
        'sklearn',
        'yaml',
        'tqdm',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            elif package == 'sklearn':
                __import__('sklearn')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_installed = False
    
    return all_installed


def validate_nltk_data():
    """Validate that required NLTK data is downloaded"""
    print("\n=== Validating NLTK Data ===")
    
    try:
        import nltk
        
        required_data = [
            ('corpora/stopwords', 'stopwords'),
            ('tokenizers/punkt', 'punkt'),
            ('corpora/wordnet', 'wordnet'),
            ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger')
        ]
        
        all_downloaded = True
        for path, name in required_data:
            try:
                nltk.data.find(path)
                print(f"✓ {name}")
            except LookupError:
                print(f"✗ {name} - NOT DOWNLOADED")
                all_downloaded = False
        
        return all_downloaded
    except ImportError:
        print("✗ NLTK not installed")
        return False


def validate_spacy_model():
    """Validate that spaCy model is downloaded"""
    print("\n=== Validating spaCy Model ===")
    
    try:
        import spacy
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✓ en_core_web_sm")
            return True
        except OSError:
            print("✗ en_core_web_sm - NOT DOWNLOADED")
            return False
    except ImportError:
        print("✗ spaCy not installed")
        return False


def validate_reddit_credentials():
    """Validate Reddit API credentials"""
    print("\n=== Validating Reddit API Credentials ===")
    
    try:
        loader = ConfigLoader()
        loader.load()
        
        if loader.validate_reddit_credentials():
            print("✓ Reddit API credentials configured")
            return True
        else:
            print("⚠ Reddit API credentials not configured")
            print("  Please copy .env.template to .env and add your credentials")
            print("  Get credentials from: https://www.reddit.com/prefs/apps")
            return False
    except Exception as e:
        print(f"✗ Error validating credentials: {e}")
        return False


def run_validation():
    """Run all validation checks"""
    print("=" * 60)
    print("Project Setup Validation")
    print("=" * 60)
    
    results = {
        'Directory Structure': validate_directory_structure(),
        'Configuration Files': validate_config_files(),
        'Python Packages': validate_python_packages(),
        'NLTK Data': validate_nltk_data(),
        'spaCy Model': validate_spacy_model(),
        'Reddit Credentials': validate_reddit_credentials()
    }
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Setup is complete!")
    else:
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        print("\nTo install missing packages, run:")
        print("  pip install -r requirements.txt")
        print("\nTo download NLTK data, run:")
        print("  python -c \"import nltk; nltk.download(['stopwords', 'punkt', 'wordnet', 'averaged_perceptron_tagger'])\"")
        print("\nTo download spaCy model, run:")
        print("  python -m spacy download en_core_web_sm")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = run_validation()
    sys.exit(0 if success else 1)
