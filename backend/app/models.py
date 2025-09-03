from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

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

# Synthetic Monitoring Models
class SyntheticTest(Base):
    __tablename__ = "synthetic_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    service_name = Column(String, index=True)  # Friendly name for external app
    test_type = Column(String)  # api, browser, uptime
    url = Column(String)
    method = Column(String, default="GET")  # GET, POST, PUT, DELETE
    headers = Column(Text, nullable=True)  # JSON string
    body = Column(Text, nullable=True)  # JSON string
    expected_status = Column(Integer, default=200)
    expected_response_contains = Column(String, nullable=True)
    timeout = Column(Integer, default=30)  # seconds
    interval = Column(Integer, default=300)  # seconds (5 minutes default)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    
    # Authentication
    auth_type = Column(String, default="none")  # none, api_key, bearer_token
    auth_credentials = Column(Text, nullable=True)  # Encrypted storage
    
    # SSL and advanced monitoring
    ssl_check_enabled = Column(Boolean, default=False)
    alert_thresholds = Column(Text, nullable=True)  # JSON config for alerting
    
    # Browser automation specific
    browser_steps = Column(Text, nullable=True)  # JSON string of steps
    
    executions = relationship("SyntheticExecution", back_populates="test")

class SyntheticExecution(Base):
    __tablename__ = "synthetic_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("synthetic_tests.id"))
    status = Column(String)  # success, failure, timeout
    response_time = Column(Float)  # in milliseconds
    status_code = Column(Integer)
    details = Column(Text)  # JSON string with additional details
    executed_at = Column(DateTime)
    
    test = relationship("SyntheticTest", back_populates="executions")

class ExternalApp(Base):
    __tablename__ = "external_apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    service_name = Column(String)
    base_url = Column(String)
    description = Column(Text)
    auth_type = Column(String, default="none")  # none, api_key, bearer_token
    auth_credentials = Column(Text)  # JSON string with auth details
    health_endpoint = Column(String, default="/health")
    timeout = Column(Integer, default=30)
    ssl_check_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
