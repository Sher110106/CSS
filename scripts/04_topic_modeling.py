"""
Module 4: Topic Modeling using Latent Dirichlet Allocation (LDA)
Trains LDA models with different topic numbers and selects the best model
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from tqdm import tqdm

import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.models.ldamulticore import LdaMulticore

from utils import setup_logger, load_config, save_json


class TopicModeler:
    """LDA Topic Modeling"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize topic modeler"""
        self.config = load_config(config_path)
        self.logger = setup_logger(
            'topic_modeling',
            'logs/topic_modeling.log'
        )
        
        # Paths
        self.processed_path = self.config['paths']['processed_data']
        self.models_path = self.config['paths']['models']
        self.metadata_path = self.config['paths']['metadata']
        
        # Create model directories
        self.lda_path = os.path.join(self.models_path, 'lda')
        self.eval_path = os.path.join(self.models_path, 'evaluation')
        os.makedirs(self.lda_path, exist_ok=True)
        os.makedirs(self.eval_path, exist_ok=True)
        
        # Data containers
        self.df = None
        self.corpus = None
        self.dictionary = None
        self.texts = None
        self.models = {}
        self.coherence_scores = {}
        self.best_model = None
        self.best_num_topics = None
        
        self.logger.info("Topic Modeler initialized")
    
    def load_data(self):
        """Load processed data and corpus"""
        self.logger.info("Loading processed data...")
        
        try:
            # Load processed dataframe
            df_path = os.path.join(self.processed_path, 'combined_processed.csv')
            self.df = pd.read_csv(df_path)
            
            # Parse tokens column
            import ast
            self.df['tokens'] = self.df['tokens'].apply(ast.literal_eval)
            
            # Extract token lists
            self.texts = self.df['tokens'].tolist()
            
            self.logger.info(f"Loaded {len(self.texts)} documents")
            self.logger.info(f"Sample text: {self.texts[0][:10]}...")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            return False
    
    def prepare_corpus(self):
        """Create Gensim dictionary and corpus"""
        self.logger.info("Preparing corpus for LDA...")
        
        try:
            # Create dictionary
            self.dictionary = corpora.Dictionary(self.texts)
            
            self.logger.info(f"Initial dictionary size: {len(self.dictionary)}")
            
            # Filter extremes
            min_df = self.config['topic_modeling']['min_df']
            max_df = self.config['topic_modeling']['max_df']
            
            self.dictionary.filter_extremes(
                no_below=min_df,  # Remove words appearing in < min_df documents
                no_above=max_df,   # Remove words appearing in > max_df fraction
                keep_n=None        # Keep all remaining words
            )
            
            self.logger.info(f"Filtered dictionary size: {len(self.dictionary)}")
            
            # Create corpus (bag of words)
            self.corpus = [self.dictionary.doc2bow(text) for text in tqdm(
                self.texts, 
                desc="Creating corpus"
            )]
            
            self.logger.info(f"Corpus created with {len(self.corpus)} documents")
            
            # Save dictionary and corpus
            dict_path = os.path.join(self.lda_path, 'dictionary.dict')
            corpus_path = os.path.join(self.lda_path, 'corpus.pkl')
            
            self.dictionary.save(dict_path)
            with open(corpus_path, 'wb') as f:
                pickle.dump(self.corpus, f)
            
            self.logger.info("Dictionary and corpus saved")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing corpus: {e}", exc_info=True)
            return False
    
    def train_lda_model(self, num_topics):
        """Train LDA model with specified number of topics"""
        self.logger.info(f"Training LDA model with {num_topics} topics...")
        
        try:
            # Get parameters from config
            passes = self.config['topic_modeling']['passes']
            iterations = self.config['topic_modeling']['iterations']
            chunksize = self.config['topic_modeling']['chunksize']
            alpha = self.config['topic_modeling']['alpha']
            eta = self.config['topic_modeling']['eta']
            
            # Train model
            model = LdaModel(
                corpus=self.corpus,
                id2word=self.dictionary,
                num_topics=num_topics,
                random_state=42,
                chunksize=chunksize,
                passes=passes,
                iterations=iterations,
                alpha=alpha,
                eta=eta,
                per_word_topics=True,
                minimum_probability=0.0
            )
            
            self.logger.info(f"Model with {num_topics} topics trained")
            
            return model
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}", exc_info=True)
            return None
    
    def calculate_coherence(self, model, num_topics):
        """Calculate coherence score for model"""
        self.logger.info(f"Calculating coherence for {num_topics} topics...")
        
        try:
            coherence_model = CoherenceModel(
                model=model,
                texts=self.texts,
                dictionary=self.dictionary,
                coherence='c_v'
            )
            
            coherence_score = coherence_model.get_coherence()
            
            self.logger.info(f"Coherence score ({num_topics} topics): {coherence_score:.4f}")
            
            return coherence_score
            
        except Exception as e:
            self.logger.error(f"Error calculating coherence: {e}", exc_info=True)
            return 0.0
    
    def optimize_topic_number(self):
        """Train models with different numbers of topics and compare"""
        self.logger.info("Optimizing number of topics...")
        
        topic_range = self.config['topic_modeling']['num_topics_range']
        
        results = []
        
        for num_topics in topic_range:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Testing {num_topics} topics")
            self.logger.info(f"{'='*60}")
            
            # Train model
            model = self.train_lda_model(num_topics)
            
            if model is None:
                continue
            
            # Calculate coherence
            coherence = self.calculate_coherence(model, num_topics)
            
            # Calculate perplexity
            perplexity = model.log_perplexity(self.corpus)
            
            # Store results
            self.models[num_topics] = model
            self.coherence_scores[num_topics] = coherence
            
            results.append({
                'num_topics': num_topics,
                'coherence_score': coherence,
                'perplexity': perplexity
            })
            
            self.logger.info(f"Results for {num_topics} topics:")
            self.logger.info(f"  Coherence: {coherence:.4f}")
            self.logger.info(f"  Perplexity: {perplexity:.4f}")
        
        # Select best model (highest coherence)
        best_result = max(results, key=lambda x: x['coherence_score'])
        self.best_num_topics = best_result['num_topics']
        self.best_model = self.models[self.best_num_topics]
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Best model: {self.best_num_topics} topics")
        self.logger.info(f"Best coherence: {best_result['coherence_score']:.4f}")
        self.logger.info(f"{'='*60}\n")
        
        # Save comparison
        comparison_df = pd.DataFrame(results)
        comparison_path = os.path.join(self.eval_path, 'topic_coherence_comparison.csv')
        comparison_df.to_csv(comparison_path, index=False)
        
        self.logger.info(f"Comparison saved to {comparison_path}")
        
        return results
    
    def extract_topics(self, model, num_topics):
        """Extract topic information"""
        self.logger.info(f"Extracting topics for {num_topics}-topic model...")
        
        topics_info = []
        
        for topic_id in range(num_topics):
            # Get top words
            top_words = model.show_topic(topic_id, topn=20)
            
            # Format words
            words = [word for word, prob in top_words]
            probs = [float(prob) for word, prob in top_words]  # Convert to native Python float
            
            # Create topic label from top 3 words
            topic_label = f"Topic {topic_id}: {', '.join(words[:3])}"
            
            topic_info = {
                'topic_id': int(topic_id),  # Convert to native Python int
                'topic_label': topic_label,
                'top_words': words,
                'word_probabilities': probs,
                'top_10_words': ', '.join(words[:10])
            }
            
            topics_info.append(topic_info)
            
            self.logger.info(f"{topic_label}")
            self.logger.info(f"  Words: {', '.join(words[:10])}")
        
        return topics_info
    
    def assign_topics_to_documents(self, model, num_topics):
        """Assign dominant topic to each document"""
        self.logger.info("Assigning topics to documents...")
        
        try:
            dominant_topics = []
            topic_distributions = []
            
            for doc_bow in tqdm(self.corpus, desc="Assigning topics"):
                # Get topic distribution for document
                topic_dist = model.get_document_topics(doc_bow, minimum_probability=0.0)
                
                # Convert to dict for easy access
                topic_probs = {topic_id: prob for topic_id, prob in topic_dist}
                
                # Find dominant topic
                dominant_topic = max(topic_probs.items(), key=lambda x: x[1])
                
                dominant_topics.append(dominant_topic[0])
                topic_distributions.append(list(topic_probs.values()))
            
            # Add to dataframe
            self.df['dominant_topic'] = dominant_topics
            self.df['topic_probability'] = [max(dist) for dist in topic_distributions]
            
            # Add full topic distribution
            for topic_id in range(num_topics):
                self.df[f'topic_{topic_id}_prob'] = [dist[topic_id] for dist in topic_distributions]
            
            # Calculate topic prevalence
            topic_counts = self.df['dominant_topic'].value_counts().sort_index()
            
            self.logger.info("\nTopic Distribution:")
            for topic_id, count in topic_counts.items():
                percentage = (count / len(self.df)) * 100
                self.logger.info(f"  Topic {topic_id}: {count} docs ({percentage:.1f}%)")
            
            # Save documents with topics
            output_path = os.path.join(self.processed_path, 'documents_with_topics.csv')
            self.df.to_csv(output_path, index=False)
            
            self.logger.info(f"Documents with topics saved to {output_path}")
            
            # Convert to native Python types for JSON serialization
            return {int(k): int(v) for k, v in topic_counts.to_dict().items()}
            
        except Exception as e:
            self.logger.error(f"Error assigning topics: {e}", exc_info=True)
            return {}
    
    def save_best_model(self):
        """Save the best model"""
        self.logger.info(f"Saving best model ({self.best_num_topics} topics)...")
        
        try:
            model_path = os.path.join(
                self.lda_path, 
                f'lda_model_{self.best_num_topics}_topics.model'
            )
            self.best_model.save(model_path)
            
            # Also save as "best" for easy loading
            best_path = os.path.join(self.lda_path, 'lda_model_best.model')
            self.best_model.save(best_path)
            
            self.logger.info(f"Model saved to {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {e}", exc_info=True)
    
    def generate_topic_report(self):
        """Generate comprehensive topic modeling report"""
        self.logger.info("Generating topic modeling report...")
        
        try:
            # Extract topics for best model
            topics_info = self.extract_topics(self.best_model, self.best_num_topics)
            
            # Assign topics to documents
            topic_distribution = self.assign_topics_to_documents(
                self.best_model, 
                self.best_num_topics
            )
            
            # Create report
            report = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'best_num_topics': self.best_num_topics,
                    'best_coherence_score': self.coherence_scores[self.best_num_topics],
                    'total_documents': len(self.df),
                    'vocabulary_size': len(self.dictionary)
                },
                'model_parameters': {
                    'passes': self.config['topic_modeling']['passes'],
                    'iterations': self.config['topic_modeling']['iterations'],
                    'min_df': self.config['topic_modeling']['min_df'],
                    'max_df': self.config['topic_modeling']['max_df'],
                    'alpha': self.config['topic_modeling']['alpha'],
                    'eta': self.config['topic_modeling']['eta']
                },
                'coherence_comparison': {
                    str(k): v for k, v in self.coherence_scores.items()
                },
                'topics': topics_info,
                'topic_distribution': topic_distribution,
                'topic_interpretations': self._interpret_topics(topics_info)
            }
            
            # Save report
            report_path = os.path.join(self.metadata_path, 'topic_modeling_report.json')
            save_json(report, report_path)
            
            self.logger.info(f"Report saved to {report_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}", exc_info=True)
            return {}
    
    def _interpret_topics(self, topics_info):
        """Manually interpret topics based on top words"""
        interpretations = []
        
        for topic in topics_info:
            words = topic['top_words'][:10]
            
            # Simple heuristic interpretation
            if 'weight' in words and 'lose' in words:
                interpretation = "Weight Loss Experiences"
            elif 'side' in words and 'effect' in words:
                interpretation = "Side Effects and Concerns"
            elif 'food' in words or 'eat' in words or 'calorie' in words:
                interpretation = "Diet and Eating Habits"
            elif 'dose' in words or 'take' in words:
                interpretation = "Medication Dosage and Usage"
            elif 'doctor' in words or 'insurance' in words:
                interpretation = "Medical Consultation and Access"
            elif 'blood' in words and 'sugar' in words:
                interpretation = "Blood Sugar and Diabetes"
            elif 'feel' in words or 'help' in words:
                interpretation = "Patient Experiences and Effects"
            else:
                interpretation = "General Discussion"
            
            interpretations.append({
                'topic_id': topic['topic_id'],
                'interpretation': interpretation,
                'top_words': ', '.join(words)
            })
        
        return interpretations


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("MODULE 4: TOPIC MODELING WITH LDA")
    print("="*60 + "\n")
    
    # Initialize
    modeler = TopicModeler()
    
    # Load data
    print("Step 1: Loading data...")
    if not modeler.load_data():
        print("ERROR: Failed to load data")
        return
    
    # Prepare corpus
    print("\nStep 2: Preparing corpus...")
    if not modeler.prepare_corpus():
        print("ERROR: Failed to prepare corpus")
        return
    
    # Optimize topic number
    print("\nStep 3: Training models and optimizing topic number...")
    print("This may take several minutes...\n")
    results = modeler.optimize_topic_number()
    
    # Save best model
    print("\nStep 4: Saving best model...")
    modeler.save_best_model()
    
    # Generate report
    print("\nStep 5: Generating comprehensive report...")
    report = modeler.generate_topic_report()
    
    # Print summary
    print("\n" + "="*60)
    print("TOPIC MODELING COMPLETE!")
    print("="*60)
    print(f"\nBest Model: {modeler.best_num_topics} topics")
    print(f"Coherence Score: {modeler.coherence_scores[modeler.best_num_topics]:.4f}")
    print(f"\nTopics Identified:")
    
    for topic in report['topics']:
        print(f"\n{topic['topic_label']}")
        print(f"  Top words: {topic['top_10_words']}")
    
    print(f"\nFiles saved:")
    print(f"  - Model: models/lda/lda_model_best.model")
    print(f"  - Documents with topics: data/processed/documents_with_topics.csv")
    print(f"  - Report: data/metadata/topic_modeling_report.json")
    print(f"  - Coherence comparison: models/evaluation/topic_coherence_comparison.csv")
    
    print("\n✓ Module 4: Topic Modeling - COMPLETE\n")


if __name__ == "__main__":
    main()
