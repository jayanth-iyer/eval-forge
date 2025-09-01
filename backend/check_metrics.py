#!/usr/bin/env python3
"""
Script to check if aggregate metrics are being stored in evaluations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import sqlite3

def check_evaluation_metrics():
    """Check if evaluations have aggregate metrics stored."""
    try:
        # Connect to the database
        conn = sqlite3.connect('/Users/jayanth_iyer/Documents/codebase/eval-forge/eval_forge.db')
        cursor = conn.cursor()
        
        # Check evaluations table
        cursor.execute("""
            SELECT id, status, avg_bleu_score, avg_rouge_1_score, avg_rouge_2_score, 
                   avg_rouge_l_score, avg_semantic_similarity 
            FROM evaluations 
            ORDER BY id DESC LIMIT 5
        """)
        
        evaluations = cursor.fetchall()
        
        print("Recent Evaluations:")
        print("ID | Status | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Semantic")
        print("-" * 70)
        
        for eval_data in evaluations:
            eval_id, status, bleu, rouge1, rouge2, rougel, semantic = eval_data
            print(f"{eval_id:2} | {status:9} | {bleu or 'None':4} | {rouge1 or 'None':7} | {rouge2 or 'None':7} | {rougel or 'None':7} | {semantic or 'None':8}")
        
        # Check individual results for the latest evaluation
        if evaluations:
            latest_eval_id = evaluations[0][0]
            cursor.execute("""
                SELECT question, bleu_score, rouge_1_score, rouge_2_score, 
                       rouge_l_score, semantic_similarity 
                FROM results 
                WHERE evaluation_id = ? 
                LIMIT 3
            """, (latest_eval_id,))
            
            results = cursor.fetchall()
            
            print(f"\nIndividual Results for Evaluation {latest_eval_id}:")
            print("Question | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Semantic")
            print("-" * 70)
            
            for result in results:
                question, bleu, rouge1, rouge2, rougel, semantic = result
                question_short = question[:20] + "..." if len(question) > 20 else question
                print(f"{question_short:23} | {bleu or 'None':4} | {rouge1 or 'None':7} | {rouge2 or 'None':7} | {rougel or 'None':7} | {semantic or 'None':8}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking metrics: {e}")

if __name__ == "__main__":
    check_evaluation_metrics()
