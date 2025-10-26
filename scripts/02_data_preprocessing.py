"""
Data Preprocessing Pipeline
Cleans and prepares text data for analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from datetime import datetime
import logging
from tqdm import tqdm
import pickle
from utils import (
    setup_logger, 
    load_dataframe, 
    save_dataframe, 
    save_json,
    clean_text as util_clean_text,
    calculate_basic_stats
)
from config.config_loader import ConfigLoader

# Ensure tqdm works with pandas
tqdm.pandas()


class TextPreprocessor:
    """Text preprocessing pipeline for Reddit data"""
    
    def __init__(self, config):
        """
        Initialize preprocessing tools
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = setup_logger(
            'data_preprocessing',
            f'logs/data_preprocessing_{datetime.now():%Y%m%d_%H%M%S}.log'
        )
        
        # Load preprocessing config
        self.preproc_config = config['preprocessing']
        self.min_word_length = self.preproc_config['min_word_length']
        self.max_word_length = self.preproc_config['max_word_length']
        self.min_post_length = self.preproc_config['min_post_length']
        
        # Initialize NLP tools
        self.logger.info("Loading NLP models...")
        self._initialize_nlp_tools()
        self.logger.info("NLP models loaded successfully")
    
    def _initialize_nlp_tools(self):
        """Initialize spaCy and NLTK resources"""
        try:
            # Load spaCy model
            self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
            
            # Load NLTK stopwords
            self.stop_words = set(stopwords.words('english'))
            
            # Add custom stopwords
            custom_stops = self.preproc_config.get('custom_stopwords', [])
            self.stop_words.update(custom_stops)
            
            # Medical terms to preserve
            self.medical_terms = {
                'ozempic', 'wegovy', 'semaglutide', 'rybelsus',
                'glp1', 'glp-1', 'diabetes', 'diabetic',
                'insulin', 'glucose', 'weight', 'loss',
                'nausea', 'vomit', 'constipation', 'diarrhea',
                'injection', 'dose', 'dosage', 'mg', 'medication'
            }
            
            # Lemmatizer
            self.lemmatizer = WordNetLemmatizer()
            
        except Exception as e:
            self.logger.error(f"Error initializing NLP tools: {e}")
            raise
    
    def clean_text(self, text):
        """
        Clean individual text
        
        Args:
            text: Input text
        
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Use utility function for basic cleaning
        text = util_clean_text(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize_and_lemmatize(self, text):
        """
        Tokenize and lemmatize text using spaCy
        
        Args:
            text: Input text
        
        Returns:
            list: List of lemmatized tokens
        """
        if not text:
            return []
        
        try:
            doc = self.nlp(text)
            
            tokens = []
            for token in doc:
                # Skip if not alphabetic (unless it's a medical term with numbers)
                if not token.is_alpha:
                    # Check if it's a medical term like "glp1" or dosages
                    if token.text.lower() in self.medical_terms:
                        tokens.append(token.text.lower())
                    continue
                
                # Get lemma
                lemma = token.lemma_.lower()
                
                # Skip stopwords (unless medical term)
                if lemma in self.stop_words and lemma not in self.medical_terms:
                    continue
                
                # Check length
                if len(lemma) < self.min_word_length or len(lemma) > self.max_word_length:
                    continue
                
                tokens.append(lemma)
            
            return tokens
        
        except Exception as e:
            self.logger.warning(f"Error tokenizing text: {e}")
            return []
    
    def preprocess_document(self, text):
        """
        Full preprocessing pipeline for single document
        
        Args:
            text: Input text
        
        Returns:
            tuple: (cleaned_text, tokens)
        """
        # Clean text
        cleaned = self.clean_text(text)
        
        if not cleaned:
            return "", []
        
        # Tokenize and lemmatize
        tokens = self.tokenize_and_lemmatize(cleaned)
        
        # Rejoin tokens for cleaned text
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text, tokens
    
    def preprocess_dataframe(self, df, text_column='text'):
        """
        Process entire dataframe
        
        Args:
            df: Input DataFrame
            text_column: Name of text column
        
        Returns:
            DataFrame: Processed DataFrame
        """
        self.logger.info(f"Preprocessing {len(df)} documents...")
        
        # Create text column if combining multiple fields
        if text_column == 'text' and text_column not in df.columns:
            # For posts, combine title and selftext
            if 'title' in df.columns and 'selftext' in df.columns:
                df['text'] = df['title'].fillna('') + ' ' + df['selftext'].fillna('')
            # For comments, use body
            elif 'body' in df.columns:
                df['text'] = df['body'].fillna('')
            else:
                raise ValueError("No text column found")
        
        # Apply preprocessing
        results = df[text_column].progress_apply(self.preprocess_document)
        
        # Split results
        df['cleaned_text'] = results.apply(lambda x: x[0])
        df['tokens'] = results.apply(lambda x: x[1])
        df['token_count'] = df['tokens'].apply(len)
        
        # Filter out very short documents
        original_count = len(df)
        df = df[df['token_count'] >= self.min_post_length].copy()
        filtered_count = original_count - len(df)
        
        self.logger.info(f"Filtered {filtered_count} short documents (< {self.min_post_length} tokens)")
        self.logger.info(f"Remaining documents: {len(df)}")
        
        return df
    
    def create_corpus(self, df):
        """
        Create corpus for topic modeling
        
        Args:
            df: DataFrame with tokens column
        
        Returns:
            list: List of token lists
        """
        corpus = df['tokens'].tolist()
        self.logger.info(f"Created corpus with {len(corpus)} documents")
        return corpus


def combine_posts_and_comments(posts_df, comments_df):
    """
    Combine posts and comments into single dataset
    
    Args:
        posts_df: Posts DataFrame
        comments_df: Comments DataFrame
    
    Returns:
        DataFrame: Combined DataFrame
    """
    # Prepare posts
    posts_df['text'] = posts_df['title'].fillna('') + ' ' + posts_df['selftext'].fillna('')
    posts_df['doc_type'] = 'post'
    posts_df['doc_id'] = posts_df['post_id']
    
    # Prepare comments
    comments_df['text'] = comments_df['body'].fillna('')
    comments_df['doc_type'] = 'comment'
    comments_df['doc_id'] = comments_df['comment_id']
    
    # Select common columns
    common_cols = ['doc_id', 'doc_type', 'text', 'author', 'score', 'created_utc']
    
    # Add subreddit for posts, get from post_id for comments
    posts_subset = posts_df[common_cols + ['subreddit']].copy()
    
    # For comments, we'll add subreddit later if needed
    comments_subset = comments_df[common_cols].copy()
    comments_subset['subreddit'] = None
    
    # Combine
    combined = pd.concat([posts_subset, comments_subset], ignore_index=True)
    
    return combined


def generate_preprocessing_report(original_df, processed_df, corpus, output_path):
    """
    Generate preprocessing report
    
    Args:
        original_df: Original DataFrame
        processed_df: Processed DataFrame
        corpus: Token corpus
        output_path: Output file path
    """
    # Calculate statistics
    all_tokens = [token for doc in corpus for token in doc]
    vocabulary = set(all_tokens)
    
    report = {
        'preprocessing_timestamp': datetime.now().isoformat(),
        'original_document_count': int(len(original_df)),
        'processed_document_count': int(len(processed_df)),
        'documents_filtered': int(len(original_df) - len(processed_df)),
        'token_statistics': {
            'total_tokens': int(len(all_tokens)),
            'unique_tokens': int(len(vocabulary)),
            'avg_tokens_per_doc': float(processed_df['token_count'].mean()),
            'median_tokens_per_doc': float(processed_df['token_count'].median()),
            'min_tokens': int(processed_df['token_count'].min()),
            'max_tokens': int(processed_df['token_count'].max())
        },
        'most_common_tokens': {k: int(v) for k, v in pd.Series(all_tokens).value_counts().head(50).to_dict().items()},
        'document_length_distribution': {
            'short (10-25 tokens)': int(len(processed_df[processed_df['token_count'].between(10, 25)])),
            'medium (26-100 tokens)': int(len(processed_df[processed_df['token_count'].between(26, 100)])),
            'long (100+ tokens)': int(len(processed_df[processed_df['token_count'] > 100]))
        }
    }
    
    save_json(report, output_path)
    
    return report


def validate_preprocessing(df):
    """
    Validate preprocessed data
    
    Args:
        df: Processed DataFrame
    
    Returns:
        bool: True if valid
    """
    print("\n" + "="*60)
    print("PREPROCESSING VALIDATION")
    print("="*60)
    
    # Check cleaned_text column
    if 'cleaned_text' in df.columns:
        print(f"✓ Cleaned text column present")
    else:
        print(f"✗ Missing cleaned_text column")
        return False
    
    # Check tokens column
    if 'tokens' in df.columns:
        print(f"✓ Tokens column present")
    else:
        print(f"✗ Missing tokens column")
        return False
    
    # Check no URLs remain
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls_found = df['cleaned_text'].str.contains(url_pattern, regex=True).sum()
    if urls_found == 0:
        print(f"✓ No URLs in cleaned text")
    else:
        print(f"⚠ Found {urls_found} documents with URLs")
    
    # Check token counts
    avg_tokens = df['token_count'].mean()
    if avg_tokens > 5:
        print(f"✓ Average tokens per document: {avg_tokens:.1f}")
    else:
        print(f"✗ Low average token count: {avg_tokens:.1f}")
    
    # Check no empty documents
    empty_docs = (df['token_count'] == 0).sum()
    if empty_docs == 0:
        print(f"✓ No empty documents")
    else:
        print(f"✗ Found {empty_docs} empty documents")
    
    # Check vocabulary size
    all_tokens = [token for tokens in df['tokens'] for token in tokens]
    vocab_size = len(set(all_tokens))
    if vocab_size > 100:
        print(f"✓ Vocabulary size: {vocab_size:,} unique tokens")
    else:
        print(f"⚠ Small vocabulary: {vocab_size}")
    
    print("="*60)
    
    return True


def main():
    """Main execution function"""
    try:
        # Load configuration
        loader = ConfigLoader()
        config = loader.load()
        
        logger = setup_logger(
            'preprocessing_main',
            f'logs/preprocessing_main_{datetime.now():%Y%m%d_%H%M%S}.log'
        )
        
        logger.info("="*60)
        logger.info("Starting Data Preprocessing")
        logger.info("="*60)
        
        # Load raw data
        logger.info("Loading raw data...")
        posts_df = load_dataframe('data/raw/posts.csv')
        comments_df = load_dataframe('data/raw/comments.csv')
        
        logger.info(f"Loaded {len(posts_df)} posts and {len(comments_df)} comments")
        
        # Initialize preprocessor
        preprocessor = TextPreprocessor(config)
        
        # Process posts
        logger.info("\nProcessing posts...")
        posts_df['text'] = posts_df['title'].fillna('') + ' ' + posts_df['selftext'].fillna('')
        posts_processed = preprocessor.preprocess_dataframe(posts_df.copy(), 'text')
        
        # Process comments
        logger.info("\nProcessing comments...")
        comments_df['text'] = comments_df['body'].fillna('')
        comments_processed = preprocessor.preprocess_dataframe(comments_df.copy(), 'text')
        
        # Combine datasets
        logger.info("\nCombining posts and comments...")
        
        # Add document type
        posts_processed['doc_type'] = 'post'
        posts_processed['doc_id'] = posts_processed['post_id']
        comments_processed['doc_type'] = 'comment'
        comments_processed['doc_id'] = comments_processed['comment_id']
        
        # Select columns to keep (without subreddit first)
        keep_cols = ['doc_id', 'doc_type', 'author', 'score', 'created_utc', 
                     'text', 'cleaned_text', 'tokens', 'token_count']
        
        posts_keep = posts_processed[keep_cols].copy()
        comments_keep = comments_processed[keep_cols].copy()
        
        # Add subreddit column
        if 'subreddit' in posts_processed.columns:
            posts_keep['subreddit'] = posts_processed['subreddit']
        else:
            posts_keep['subreddit'] = None
        
        # Comments don't have subreddit directly
        comments_keep['subreddit'] = None
        
        # Combine
        combined_processed = pd.concat([posts_keep, comments_keep], ignore_index=True)
        
        logger.info(f"Combined dataset: {len(combined_processed)} documents")
        
        # Save processed data
        logger.info("\nSaving processed data...")
        save_dataframe(posts_processed, 'data/processed/posts_processed.csv')
        save_dataframe(comments_processed, 'data/processed/comments_processed.csv')
        save_dataframe(combined_processed, 'data/processed/combined_processed.csv')
        
        logger.info("Saved processed dataframes")
        
        # Create corpus
        logger.info("\nCreating corpus for topic modeling...")
        corpus = preprocessor.create_corpus(combined_processed)
        
        # Save corpus
        with open('data/processed/corpus.pkl', 'wb') as f:
            pickle.dump(corpus, f)
        
        logger.info(f"Saved corpus: {len(corpus)} documents")
        
        # Generate preprocessing report
        logger.info("\nGenerating preprocessing report...")
        report = generate_preprocessing_report(
            pd.concat([posts_df, comments_df], ignore_index=True),
            combined_processed,
            corpus,
            'data/metadata/preprocessing_report.json'
        )
        
        # Log summary
        logger.info("\n" + "="*60)
        logger.info("Preprocessing Summary")
        logger.info("="*60)
        logger.info(f"Original documents: {report['original_document_count']:,}")
        logger.info(f"Processed documents: {report['processed_document_count']:,}")
        logger.info(f"Filtered out: {report['documents_filtered']:,}")
        logger.info(f"Total tokens: {report['token_statistics']['total_tokens']:,}")
        logger.info(f"Vocabulary size: {report['token_statistics']['unique_tokens']:,}")
        logger.info(f"Avg tokens/doc: {report['token_statistics']['avg_tokens_per_doc']:.1f}")
        logger.info("="*60)
        
        # Validate
        success = validate_preprocessing(combined_processed)
        
        if success:
            print("\n✓ MODULE 2 COMPLETE: Data preprocessing successful!")
            logger.info("✓ MODULE 2 COMPLETE")
        else:
            print("\n⚠ Preprocessing complete but validation has warnings")
            logger.warning("Preprocessing validation has warnings")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        print(traceback.format_exc())
        if 'logger' in locals():
            logger.error(f"Preprocessing failed: {e}")
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
