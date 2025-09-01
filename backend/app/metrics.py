"""
Advanced metrics calculation module for LLM evaluation.
Provides BLEU, ROUGE, and semantic similarity scoring with robust error handling.
"""

import logging
from typing import Optional, Dict, Any
import re
import warnings

# Suppress warnings from transformers and other libraries
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculate advanced metrics for LLM evaluation with graceful error handling."""
    
    def __init__(self):
        self._nltk_initialized = False
        self._rouge_scorer = None
        self._sentence_model = None
        
    def _init_nltk(self):
        """Initialize NLTK with error handling."""
        if self._nltk_initialized:
            return True
            
        try:
            import nltk
            # Download required NLTK data if not present
            required_data = ['punkt', 'punkt_tab']
            
            for data_name in required_data:
                try:
                    if data_name == 'punkt':
                        nltk.data.find('tokenizers/punkt')
                    elif data_name == 'punkt_tab':
                        nltk.data.find('tokenizers/punkt_tab')
                except LookupError:
                    logger.info(f"Downloading NLTK {data_name} data...")
                    nltk.download(data_name, quiet=True)
            
            self._nltk_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize NLTK: {e}")
            return False
    
    def _init_rouge(self):
        """Initialize ROUGE scorer with error handling."""
        if self._rouge_scorer is not None:
            return True
            
        try:
            from rouge_score import rouge_scorer
            self._rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ROUGE scorer: {e}")
            return False
    
    def _init_sentence_model(self):
        """Initialize sentence transformer model with error handling."""
        if self._sentence_model is not None:
            return True
            
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model for better performance
            self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            return True
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
            return False
    
    def calculate_bleu_score(self, reference: str, candidate: str) -> Optional[float]:
        """
        Calculate BLEU score between reference and candidate text.
        
        Args:
            reference: Expected/reference text
            candidate: Model-generated text
            
        Returns:
            BLEU score (0.0-1.0) or None if calculation fails
        """
        try:
            if not self._init_nltk():
                return None
            
            from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
            from nltk.tokenize import word_tokenize
            
            # Tokenize texts
            reference_tokens = [word_tokenize(reference.lower())]
            candidate_tokens = word_tokenize(candidate.lower())
            
            # Use smoothing to avoid division by zero and compatibility issues
            smoothie = SmoothingFunction().method4
            
            # Calculate BLEU score with smoothing
            score = sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smoothie)
            
            return round(score, 4)
            
        except Exception as e:
            logger.error(f"BLEU calculation failed: {e}")
            return None
    
    def calculate_rouge_scores(self, reference: str, candidate: str) -> Dict[str, Optional[float]]:
        """
        Calculate ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L).
        
        Args:
            reference: Expected/reference text
            candidate: Model-generated text
            
        Returns:
            Dictionary with rouge1, rouge2, rougeL scores or None for failed calculations
        """
        try:
            if not self._init_rouge():
                return {"rouge1": None, "rouge2": None, "rougeL": None}
            
            scores = self._rouge_scorer.score(reference, candidate)
            
            return {
                "rouge1": round(scores['rouge1'].fmeasure, 4),
                "rouge2": round(scores['rouge2'].fmeasure, 4),
                "rougeL": round(scores['rougeL'].fmeasure, 4)
            }
            
        except Exception as e:
            logger.error(f"ROUGE calculation failed: {e}")
            return {"rouge1": None, "rouge2": None, "rougeL": None}
    
    def calculate_semantic_similarity(self, reference: str, candidate: str) -> Optional[float]:
        """
        Calculate semantic similarity using sentence embeddings.
        
        Args:
            reference: Expected/reference text
            candidate: Model-generated text
            
        Returns:
            Cosine similarity score (0.0-1.0) or None if calculation fails
        """
        try:
            if not self._init_sentence_model():
                return None
            
            import numpy as np
            
            # Generate embeddings
            embeddings = self._sentence_model.encode([reference, candidate])
            
            # Calculate cosine similarity manually (avoiding scikit-learn)
            def cosine_similarity_manual(a, b):
                dot_product = np.dot(a, b)
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
            
            similarity = cosine_similarity_manual(embeddings[0], embeddings[1])
            
            # Ensure score is between 0 and 1
            similarity = max(0.0, min(1.0, similarity))
            
            return round(float(similarity), 4)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return None
    
    def calculate_all_metrics(self, reference: str, candidate: str) -> Dict[str, Any]:
        """
        Calculate all available metrics for a reference-candidate pair.
        
        Args:
            reference: Expected/reference text
            candidate: Model-generated text
            
        Returns:
            Dictionary containing all calculated metrics
        """
        # Input validation
        if not reference or not candidate:
            return self._get_empty_metrics()
        
        # Clean inputs
        reference = self._clean_text(reference)
        candidate = self._clean_text(candidate)
        
        if not reference or not candidate:
            return self._get_empty_metrics()
        
        metrics = {}
        
        # Calculate BLEU score
        metrics['bleu_score'] = self.calculate_bleu_score(reference, candidate)
        
        # Calculate ROUGE scores
        rouge_scores = self.calculate_rouge_scores(reference, candidate)
        metrics.update(rouge_scores)
        
        # Calculate semantic similarity
        metrics['semantic_similarity'] = self.calculate_semantic_similarity(reference, candidate)
        
        return metrics
    
    def _tokenize_text(self, text: str) -> list:
        """Tokenize text into words with basic preprocessing."""
        try:
            if not self._init_nltk():
                # Fallback to simple tokenization
                return text.lower().split()
            
            import nltk
            tokens = nltk.word_tokenize(text.lower())
            # Filter out punctuation
            return [token for token in tokens if token.isalnum()]
            
        except Exception:
            # Fallback to simple tokenization
            return text.lower().split()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            'bleu_score': None,
            'rouge1': None,
            'rouge2': None,
            'rougeL': None,
            'semantic_similarity': None
        }


# Global instance for reuse
metrics_calculator = MetricsCalculator()


def calculate_metrics(reference: str, candidate: str) -> Dict[str, Any]:
    """
    Convenience function to calculate all metrics.
    
    Args:
        reference: Expected/reference text
        candidate: Model-generated text
        
    Returns:
        Dictionary containing all calculated metrics
    """
    return metrics_calculator.calculate_all_metrics(reference, candidate)
