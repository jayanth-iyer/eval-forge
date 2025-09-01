from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # ollama, openai, etc.
    endpoint = Column(String)
    model_name = Column(String)
    status = Column(String, default="unknown")  # unknown, connected, error, testing
    
    evaluations = relationship("Evaluation", back_populates="model")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    status = Column(String, default="draft")  # draft, running, completed, failed
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=512)
    top_p = Column(Float, default=0.9)
    total_questions = Column(Integer, default=0)
    accuracy = Column(Float, nullable=True)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    created_at = Column(DateTime)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Advanced metrics aggregates
    avg_bleu_score = Column(Float, nullable=True)
    avg_rouge_1_score = Column(Float, nullable=True)
    avg_rouge_2_score = Column(Float, nullable=True)
    avg_rouge_l_score = Column(Float, nullable=True)
    avg_semantic_similarity = Column(Float, nullable=True)
    avg_response_time = Column(Float, nullable=True)
    
    model = relationship("Model", back_populates="evaluations")
    questions = relationship("Question", back_populates="evaluation")
    results = relationship("Result", back_populates="evaluation")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    question = Column(Text)
    expected_answer = Column(Text)
    
    evaluation = relationship("Evaluation", back_populates="questions")

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    question = Column(Text)
    expected_answer = Column(Text)
    model_response = Column(Text)
    is_correct = Column(Boolean)
    response_time = Column(Integer)  # in milliseconds
    
    # Advanced metrics
    bleu_score = Column(Float, nullable=True)
    rouge_1_score = Column(Float, nullable=True)
    rouge_2_score = Column(Float, nullable=True)
    rouge_l_score = Column(Float, nullable=True)
    semantic_similarity = Column(Float, nullable=True)
    
    evaluation = relationship("Evaluation", back_populates="results")
