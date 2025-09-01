"""
Question bank loader for randomized sample datasets.
"""

import os
import re
import random
from typing import List, Dict

def parse_markdown_questions(file_path: str) -> List[Dict[str, str]]:
    """Parse questions from a markdown file."""
    questions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all question blocks using regex
        question_pattern = r'## Question \d+\n\*\*Question:\*\* (.*?)\n\*\*Answer:\*\* (.*?)(?=\n\n|\n## |\Z)'
        matches = re.findall(question_pattern, content, re.DOTALL)
        
        for question_text, answer_text in matches:
            questions.append({
                "question": question_text.strip(),
                "answer": answer_text.strip()
            })
    
    except Exception:
        return []
    
    return questions

def load_question_bank() -> List[Dict[str, str]]:
    """Load all questions from the question bank directory."""
    question_bank_dir = os.path.join(os.path.dirname(__file__), '..', 'question-bank')
    all_questions = []
    
    if not os.path.exists(question_bank_dir):
        return []
    
    # Load questions from all markdown files
    for filename in os.listdir(question_bank_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(question_bank_dir, filename)
            subject_questions = parse_markdown_questions(file_path)
            all_questions.extend(subject_questions)
    return all_questions

def get_random_sample_dataset(num_questions: int = 10) -> List[Dict[str, str]]:
    """Get a random sample of questions from the question bank."""
    all_questions = load_question_bank()
    
    if len(all_questions) < num_questions:
        return all_questions
    
    # Randomly select questions
    selected_questions = random.sample(all_questions, num_questions)
    return selected_questions
