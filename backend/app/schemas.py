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

# Synthetic Monitoring Schemas
class SyntheticTestBase(BaseModel):
    name: str
    service_name: str
    test_type: str  # api, browser, uptime
    url: str
    method: str = "GET"
    headers: Optional[str] = None
    body: Optional[str] = None
    expected_status: int = 200
    expected_response_contains: Optional[str] = None
    timeout: int = 30
    interval: int = 300
    is_active: bool = True
    auth_type: str = "none"
    auth_credentials: Optional[str] = None
    ssl_check_enabled: bool = False
    alert_thresholds: Optional[str] = None
    browser_steps: Optional[str] = None

class SyntheticTestCreate(SyntheticTestBase):
    pass

class SyntheticTest(SyntheticTestBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SyntheticExecutionBase(BaseModel):
    status: str
    response_time: float
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    dns_time: Optional[float] = None
    connect_time: Optional[float] = None
    ssl_time: Optional[float] = None
    first_byte_time: Optional[float] = None

class SyntheticExecution(SyntheticExecutionBase):
    id: int
    test_id: int
    executed_at: datetime
    
    class Config:
        from_attributes = True

class SyntheticExecutionResponse(SyntheticExecutionBase):
    id: int
    test_id: int
    executed_at: datetime

    class Config:
        from_attributes = True

class BrowserStep(BaseModel):
    action: str  # navigate, click, type, wait, screenshot
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout: int = 30

# External App Endpoint schemas
class ExternalAppEndpointBase(BaseModel):
    name: str
    endpoint_path: str
    method: str = "GET"
    description: Optional[str] = None
    headers: Optional[str] = None
    body: Optional[str] = None
    expected_status: int = 200
    expected_response_contains: Optional[str] = None
    timeout: Optional[int] = None
    is_active: bool = True

class ExternalAppEndpointCreate(ExternalAppEndpointBase):
    external_app_id: int

class ExternalAppEndpointUpdate(ExternalAppEndpointBase):
    pass

class ExternalAppEndpoint(ExternalAppEndpointBase):
    id: int
    external_app_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# External App schemas
class ExternalAppBase(BaseModel):
    name: str
    service_name: str
    base_url: str
    description: Optional[str] = None
    auth_type: str = "none"
    auth_credentials: Optional[str] = None
    timeout: int = 30
    ssl_check_enabled: bool = False
    is_active: bool = True

class ExternalAppCreate(ExternalAppBase):
    pass

class ExternalAppUpdate(ExternalAppBase):
    pass

class ExternalApp(ExternalAppBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    endpoints: List[ExternalAppEndpoint] = []

    class Config:
        from_attributes = True
