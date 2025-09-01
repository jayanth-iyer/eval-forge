from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    type: str
    endpoint: str
    model_name: str

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    status: str
    
    class Config:
        from_attributes = True

class EvaluationBase(BaseModel):
    name: str
    model_id: int
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9

class EvaluationCreate(EvaluationBase):
    pass

class Evaluation(EvaluationBase):
    id: int
    status: str
    total_questions: int
    accuracy: Optional[float] = None
    correct_answers: int
    incorrect_answers: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_name: Optional[str] = None
    
    # Advanced metrics
    avg_bleu_score: Optional[float] = None
    avg_rouge_1_score: Optional[float] = None
    avg_rouge_2_score: Optional[float] = None
    avg_rouge_l_score: Optional[float] = None
    avg_semantic_similarity: Optional[float] = None
    avg_response_time: Optional[float] = None
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question: str
    expected_answer: str

class Question(QuestionBase):
    id: int
    evaluation_id: int
    
    class Config:
        from_attributes = True

class ResultBase(BaseModel):
    question: str
    expected_answer: str
    model_response: str
    is_correct: bool
    response_time: int

class Result(ResultBase):
    id: int
    evaluation_id: int
    
    # Advanced metrics
    bleu_score: Optional[float] = None
    rouge_1_score: Optional[float] = None
    rouge_2_score: Optional[float] = None
    rouge_l_score: Optional[float] = None
    semantic_similarity: Optional[float] = None
    
    class Config:
        from_attributes = True
