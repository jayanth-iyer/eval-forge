#!/usr/bin/env python3
"""
Script to calculate and store aggregate metrics for existing evaluations.
"""

import sqlite3

def fix_aggregate_metrics():
    """Calculate and store aggregate metrics for evaluations that are missing them."""
    try:
        conn = sqlite3.connect('/Users/jayanth_iyer/Documents/codebase/eval-forge/eval_forge.db')
        cursor = conn.cursor()
        
        # Get evaluations that are missing aggregate metrics
        cursor.execute("""
            SELECT id FROM evaluations 
            WHERE status = 'completed' 
            AND (avg_bleu_score IS NULL OR avg_rouge_1_score IS NULL)
        """)
        
        evaluations_to_fix = cursor.fetchall()
        
        for (eval_id,) in evaluations_to_fix:
            print(f"Fixing evaluation {eval_id}...")
            
            # Get all results for this evaluation
            cursor.execute("""
                SELECT bleu_score, rouge_1_score, rouge_2_score, 
                       rouge_l_score, semantic_similarity
                FROM results 
                WHERE evaluation_id = ?
            """, (eval_id,))
            
            results = cursor.fetchall()
            
            if not results:
                continue
                
            # Calculate averages (excluding None values)
            valid_bleu = [r[0] for r in results if r[0] is not None]
            valid_rouge1 = [r[1] for r in results if r[1] is not None]
            valid_rouge2 = [r[2] for r in results if r[2] is not None]
            valid_rougel = [r[3] for r in results if r[3] is not None]
            valid_semantic = [r[4] for r in results if r[4] is not None]
            
            # Calculate averages
            avg_bleu = sum(valid_bleu) / len(valid_bleu) if valid_bleu else None
            avg_rouge1 = sum(valid_rouge1) / len(valid_rouge1) if valid_rouge1 else None
            avg_rouge2 = sum(valid_rouge2) / len(valid_rouge2) if valid_rouge2 else None
            avg_rougel = sum(valid_rougel) / len(valid_rougel) if valid_rougel else None
            avg_semantic = sum(valid_semantic) / len(valid_semantic) if valid_semantic else None
            
            bleu_str = f"{avg_bleu:.4f}" if avg_bleu is not None else "None"
            rouge1_str = f"{avg_rouge1:.4f}" if avg_rouge1 is not None else "None"
            rouge2_str = f"{avg_rouge2:.4f}" if avg_rouge2 is not None else "None"
            rougel_str = f"{avg_rougel:.4f}" if avg_rougel is not None else "None"
            semantic_str = f"{avg_semantic:.4f}" if avg_semantic is not None else "None"
            
            print(f"  BLEU: {bleu_str}")
            print(f"  ROUGE-1: {rouge1_str}")  
            print(f"  ROUGE-2: {rouge2_str}")
            print(f"  ROUGE-L: {rougel_str}")
            print(f"  Semantic: {semantic_str}")
            
            print(f"  Valid counts: BLEU={len(valid_bleu)}, ROUGE1={len(valid_rouge1)}, ROUGE2={len(valid_rouge2)}, ROUGEL={len(valid_rougel)}, Semantic={len(valid_semantic)}")
            
            # Update the evaluation record
            cursor.execute("""
                UPDATE evaluations 
                SET avg_bleu_score = ?, 
                    avg_rouge_1_score = ?, 
                    avg_rouge_2_score = ?, 
                    avg_rouge_l_score = ?, 
                    avg_semantic_similarity = ?
                WHERE id = ?
            """, (avg_bleu, avg_rouge1, avg_rouge2, avg_rougel, avg_semantic, eval_id))
        
        conn.commit()
        conn.close()
        
        print(f"\nFixed {len(evaluations_to_fix)} evaluations!")
        print("Dashboard should now show the advanced metrics.")
        
    except Exception as e:
        print(f"Error fixing aggregates: {e}")

if __name__ == "__main__":
    fix_aggregate_metrics()
