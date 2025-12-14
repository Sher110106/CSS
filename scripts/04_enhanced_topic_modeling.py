#!/usr/bin/env python3
"""
Module 4: Enhanced Topic Modeling - Tests 2,3,4,5 topics and selects best
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import sys
from datetime import datetime
import logging
from tqdm import tqdm

import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.models.ldamulticore import LdaMulticore

from utils import setup_logger, load_config, save_json


class EnhancedTopicModeler:
    """LDA Topic Modeling with multiple K evaluation"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize topic modeler"""
        self.config = load_config(config_path)
        self.logger = setup_logger('topic_modeling', 'logs/topic_modeling.log')
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.models_path = self.config['paths']['models']
        self.metadata_path = self.config['paths']['metadata']
        
        # Create directories
        self.lda_path = os.path.join(self.models_path, 'lda')
        self.eval_path = os.path.join(self.models_path, 'evaluation')
        os.makedirs(self.lda_path, exist_ok=True)
        os.makedirs(self.eval_path, exist_ok=True)
        
        # Data containers
        self.df = None
        self.corpus = None
        self.dictionary = None
        self.texts = None
        
        # Model evaluation
        self.topic_numbers = [2, 3, 4, 5]  # Test these topic counts
        self.models = {}
        self.coherence_scores = {}
        self.perplexity_scores = {}
        self.best_model = None
        self.best_num_topics = None
        
        self.logger.info("Enhanced Topic Modeler initialized")
        self.logger.info(f"Will test topic numbers: {self.topic_numbers}")
    
    def load_data(self):
        """Load processed data"""
        self.logger.info("Loading processed data...")
        
        try:
            df_path = os.path.join(self.processed_path, 'combined_processed.csv')
            self.df = pd.read_csv(df_path)
            
            # Parse tokens
            import ast
            self.df['tokens'] = self.df['tokens'].apply(ast.literal_eval)
            self.texts = self.df['tokens'].tolist()
            
            self.logger.info(f"Loaded {len(self.texts)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    def prepare_corpus(self):
        """Create dictionary and corpus"""
        self.logger.info("Preparing corpus...")
        
        try:
            # Create dictionary
            self.dictionary = corpora.Dictionary(self.texts)
            self.logger.info(f"Initial dictionary: {len(self.dictionary)} terms")
            
            # Filter extremes
            min_df = self.config['topic_modeling']['min_df']
            max_df = self.config['topic_modeling']['max_df']
            
            self.dictionary.filter_extremes(
                no_below=min_df,
                no_above=max_df,
                keep_n=None
            )
            
            self.logger.info(f"Filtered dictionary: {len(self.dictionary)} terms")
            
            # Create corpus
            self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
            
            # Save dictionary and corpus
            dict_path = os.path.join(self.lda_path, 'dictionary.dict')
            corpus_path = os.path.join(self.lda_path, 'corpus.mm')
            
            self.dictionary.save(dict_path)
            corpora.MmCorpus.serialize(corpus_path, self.corpus)
            
            self.logger.info(f"Saved dictionary and corpus")
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing corpus: {e}", exc_info=True)
            return False
    
    def train_lda_model(self, num_topics):
        """Train a single LDA model"""
        self.logger.info(f"\nTraining LDA model with {num_topics} topics...")
        
        try:
            # LDA parameters
            passes = self.config['topic_modeling']['passes']
            iterations = self.config['topic_modeling']['iterations']
            chunksize = self.config['topic_modeling']['chunksize']
            
            # Train model
            model = LdaMulticore(
                corpus=self.corpus,
                id2word=self.dictionary,
                num_topics=num_topics,
                passes=passes,
                iterations=iterations,
                chunksize=chunksize,
                alpha='asymmetric',
                eta='auto',
                per_word_topics=True,
                random_state=42,
                workers=3
            )
            
            self.logger.info(f"  Model trained with {num_topics} topics")
            
            # Calculate coherence
            coherence_model = CoherenceModel(
                model=model,
                texts=self.texts,
                dictionary=self.dictionary,
                coherence='c_v'
            )
            coherence_score = coherence_model.get_coherence()
            
            # Calculate perplexity
            perplexity = model.log_perplexity(self.corpus)
            
            self.logger.info(f"  Coherence (C_v): {coherence_score:.4f}")
            self.logger.info(f"  Perplexity: {perplexity:.4f}")
            
            return model, coherence_score, perplexity
            
        except Exception as e:
            self.logger.error(f"Error training model with {num_topics} topics: {e}")
            return None, None, None
    
    def train_all_models(self):
        """Train LDA models for all topic numbers"""
        self.logger.info("\n" + "="*80)
        self.logger.info("TRAINING LDA MODELS WITH DIFFERENT TOPIC NUMBERS")
        self.logger.info("="*80)
        
        results = []
        
        for num_topics in self.topic_numbers:
            model, coherence, perplexity = self.train_lda_model(num_topics)
            
            if model is not None:
                self.models[num_topics] = model
                self.coherence_scores[num_topics] = coherence
                self.perplexity_scores[num_topics] = perplexity
                
                results.append({
                    'num_topics': num_topics,
                    'coherence': coherence,
                    'perplexity': perplexity
                })
                
                # Save model
                model_path = os.path.join(self.lda_path, f'lda_model_{num_topics}_topics')
                model.save(model_path)
                self.logger.info(f"  Saved model to {model_path}")
        
        # Save comparison results
        results_df = pd.DataFrame(results)
        results_path = os.path.join(self.eval_path, 'topic_coherence_comparison.csv')
        results_df.to_csv(results_path, index=False)
        self.logger.info(f"\nSaved comparison results to {results_path}")
        
        return results_df
    
    def select_best_model(self):
        """Select best model based on coherence score"""
        self.logger.info("\n" + "="*80)
        self.logger.info("SELECTING BEST MODEL")
        self.logger.info("="*80)
        
        # Find best coherence
        best_num_topics = max(self.coherence_scores, key=self.coherence_scores.get)
        best_coherence = self.coherence_scores[best_num_topics]
        
        self.best_num_topics = best_num_topics
        self.best_model = self.models[best_num_topics]
        
        self.logger.info(f"\nBest Model: {best_num_topics} topics")
        self.logger.info(f"  Coherence Score: {best_coherence:.4f}")
        self.logger.info(f"  Perplexity: {self.perplexity_scores[best_num_topics]:.4f}")
        
        # Save best model with special name
        best_model_path = os.path.join(self.lda_path, 'lda_model_best')
        self.best_model.save(best_model_path)
        self.logger.info(f"  Saved best model to {best_model_path}")
        
        # Print all models for comparison
        self.logger.info("\nAll Models Comparison:")
        self.logger.info("-" * 60)
        self.logger.info(f"{'Topics':>8} | {'Coherence':>12} | {'Perplexity':>12}")
        self.logger.info("-" * 60)
        
        for num_topics in sorted(self.topic_numbers):
            coherence = self.coherence_scores[num_topics]
            perplexity = self.perplexity_scores[num_topics]
            marker = " ← BEST" if num_topics == best_num_topics else ""
            self.logger.info(f"{num_topics:8d} | {coherence:12.4f} | {perplexity:12.4f}{marker}")
        
        return best_num_topics
    
    def extract_topics(self):
        """Extract topic information from best model"""
        self.logger.info("\nExtracting topics from best model...")
        
        topics = []
        
        for topic_id in range(self.best_num_topics):
            # Get top words
            topic_words = self.best_model.show_topic(topic_id, topn=20)
            words = [word for word, prob in topic_words]
            probs = [float(prob) for word, prob in topic_words]  # Convert to float
            
            topic_info = {
                'topic_id': int(topic_id),
                'top_words': words,
                'word_probabilities': probs
            }
            topics.append(topic_info)
            
            self.logger.info(f"\nTopic {topic_id}:")
            self.logger.info(f"  Top 10 words: {', '.join(words[:10])}")
        
        return topics
    
    def assign_topics_to_documents(self):
        """Assign dominant topic to each document"""
        self.logger.info("\nAssigning topics to documents...")
        
        dominant_topics = []
        topic_distributions = []
        
        for doc_bow in tqdm(self.corpus, desc="Assigning topics"):
            # Get topic distribution
            doc_topics = self.best_model.get_document_topics(doc_bow)
            
            # Find dominant topic
            if doc_topics:
                dominant_topic = max(doc_topics, key=lambda x: x[1])
                dominant_topics.append(dominant_topic[0])
                
                # Store full distribution
                topic_dist = {f'topic_{i}': 0.0 for i in range(self.best_num_topics)}
                for topic_id, prob in doc_topics:
                    topic_dist[f'topic_{topic_id}'] = prob
                topic_distributions.append(topic_dist)
            else:
                dominant_topics.append(-1)
                topic_distributions.append({f'topic_{i}': 0.0 for i in range(self.best_num_topics)})
        
        # Add to dataframe
        self.df['dominant_topic'] = dominant_topics
        
        # Add topic probabilities
        topic_dist_df = pd.DataFrame(topic_distributions)
        self.df = pd.concat([self.df, topic_dist_df], axis=1)
        
        # Save
        output_path = os.path.join(self.processed_path, 'documents_with_topics.csv')
        self.df.to_csv(output_path, index=False)
        self.logger.info(f"Saved documents with topics to {output_path}")
        
        # Topic distribution summary
        topic_counts = self.df['dominant_topic'].value_counts().sort_index()
        self.logger.info("\nTopic Distribution:")
        for topic_id, count in topic_counts.items():
            pct = (count / len(self.df)) * 100
            self.logger.info(f"  Topic {topic_id}: {count:5d} docs ({pct:5.1f}%)")
        
        return topic_counts.to_dict()
    
    def generate_report(self, topics, topic_distribution):
        """Generate comprehensive report"""
        self.logger.info("\nGenerating topic modeling report...")
        
        report = {
            'model_metadata': {
                'training_date': datetime.now().isoformat(),
                'num_documents': len(self.df),
                'vocabulary_size': len(self.dictionary),
                'models_tested': self.topic_numbers,
            },
            'model_selection': {
                'best_num_topics': int(self.best_num_topics),
                'best_coherence': float(self.coherence_scores[self.best_num_topics]),
                'best_perplexity': float(self.perplexity_scores[self.best_num_topics]),
            },
            'all_models_comparison': [
                {
                    'num_topics': int(k),
                    'coherence': float(self.coherence_scores[k]),
                    'perplexity': float(self.perplexity_scores[k])
                }
                for k in sorted(self.topic_numbers)
            ],
            'topics': topics,
            'topic_distribution': {str(k): int(v) for k, v in topic_distribution.items()},
        }
        
        report_path = os.path.join(self.metadata_path, 'topic_modeling_report.json')
        save_json(report, report_path)
        self.logger.info(f"Report saved to {report_path}")
        
        return report


def main():
    """Main execution"""
    try:
        logger = setup_logger('topic_modeling_main', 'logs/topic_modeling.log')
        
        logger.info("="*80)
        logger.info("MODULE 4: ENHANCED TOPIC MODELING")
        logger.info("="*80)
        
        # Initialize modeler
        modeler = EnhancedTopicModeler()
        
        # Load and prepare data
        if not modeler.load_data():
            return 1
        
        if not modeler.prepare_corpus():
            return 1
        
        # Train models for different topic numbers
        comparison_df = modeler.train_all_models()
        
        # Select best model
        best_k = modeler.select_best_model()
        
        # Extract topics
        topics = modeler.extract_topics()
        
        # Assign topics to documents
        topic_dist = modeler.assign_topics_to_documents()
        
        # Generate report
        report = modeler.generate_report(topics, topic_dist)
        
        logger.info("\n" + "="*80)
        logger.info("✓ MODULE 4 COMPLETE: Topic Modeling")
        logger.info("="*80)
        logger.info(f"\nBest Model: {best_k} topics with coherence {modeler.coherence_scores[best_k]:.4f}")
        logger.info(f"Next step: Run sentiment analysis")
        logger.info(f"  → python scripts/05_sentiment_analysis.py")
        
        return 0
        
    except Exception as e:
        logger.error(f"Topic modeling failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
