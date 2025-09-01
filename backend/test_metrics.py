#!/usr/bin/env python3
"""
Test script for advanced metrics functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.metrics import MetricsCalculator

def test_metrics():
    """Test all metrics calculations."""
    calculator = MetricsCalculator()
    
    # Test data
    reference = "The quick brown fox jumps over the lazy dog"
    candidate = "A quick brown fox leaps over the lazy dog"
    
    print("Testing Advanced Metrics...")
    print(f"Reference: {reference}")
    print(f"Candidate: {candidate}")
    print("-" * 50)
    
    # Test BLEU score
    print("Testing BLEU score...")
    bleu_score = calculator.calculate_bleu_score(reference, candidate)
    if bleu_score is not None:
        print(f"✅ BLEU Score: {bleu_score}")
    else:
        print("❌ BLEU calculation failed")
    
    # Test ROUGE scores
    print("\nTesting ROUGE scores...")
    rouge_scores = calculator.calculate_rouge_scores(reference, candidate)
    if rouge_scores and any(score is not None for score in rouge_scores.values()):
        print("✅ ROUGE Scores:")
        for metric, score in rouge_scores.items():
            print(f"  {metric}: {score}")
    else:
        print("❌ ROUGE calculation failed")
    
    # Test semantic similarity
    print("\nTesting semantic similarity...")
    semantic_score = calculator.calculate_semantic_similarity(reference, candidate)
    if semantic_score is not None:
        print(f"✅ Semantic Similarity: {semantic_score}")
    else:
        print("❌ Semantic similarity calculation failed")
    
    print("\n" + "=" * 50)
    print("Metrics test completed!")

if __name__ == "__main__":
    test_metrics()
