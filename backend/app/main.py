from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import httpx
import time
import csv
import io
import asyncio
from . import models, schemas, database
from .metrics import calculate_metrics
from .database import get_db
from .question_bank import get_random_sample_dataset
from .synthetic_monitoring import synthetic_service
from .scheduler import scheduler

app = FastAPI(title="Eval Forge API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Startup event to start scheduler
@app.on_event("startup")
async def startup_event():
    await scheduler.start()

# Shutdown event to stop scheduler
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop()


@app.get("/")
async def root():
    return {"message": "Eval Forge API"}

# Models endpoints
@app.get("/api/models", response_model=List[schemas.Model])
def get_models(db: Session = Depends(get_db)):
    return db.query(models.Model).all()

@app.post("/api/models", response_model=schemas.Model)
def create_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    db_model = models.Model(**model.dict(), status="unknown")
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

@app.delete("/api/models/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    db.delete(db_model)
    db.commit()
    return {"message": "Model deleted"}

@app.get("/api/models/{model_id}/test")
async def test_model_connection(model_id: int, db: Session = Depends(get_db)):
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Update status to testing
    db_model.status = "testing"
    db.commit()
    
    try:
        if db_model.type == "ollama":
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{db_model.endpoint}/api/tags")
                if response.status_code == 200:
                    tags = response.json()
                    available_models = tags.get("models", [])
                    model_names = [model["name"] for model in available_models]
                    
                    # Check for exact match first
                    if db_model.model_name in model_names:
                        db_model.status = "connected"
                    else:
                        # Check for partial match (e.g., "llama3.2" matches "llama3.2:latest")
                        partial_match = any(
                            name.startswith(db_model.model_name + ":") or 
                            name == db_model.model_name
                            for name in model_names
                        )
                        if partial_match:
                            db_model.status = "connected"
                        else:
                            db_model.status = "error"
                else:
                    db_model.status = "error"
        else:
            db_model.status = "error"
    except httpx.TimeoutException:
        db_model.status = "error"
    except httpx.ConnectError:
        db_model.status = "error"
    except Exception:
        db_model.status = "error"
    
    db.commit()
    db.refresh(db_model)
    return db_model

# Evaluations endpoints
@app.get("/api/evaluations", response_model=List[schemas.Evaluation])
def get_evaluations(db: Session = Depends(get_db)):
    evaluations = db.query(models.Evaluation).all()
    for eval in evaluations:
        if eval.model:
            eval.model_name = eval.model.name
    return evaluations

@app.post("/api/evaluations", response_model=schemas.Evaluation)
async def create_evaluation(
    name: str = Form(...),
    model_id: int = Form(...),
    use_sample: bool = Form(False),
    temperature: float = Form(0.7),
    max_tokens: int = Form(512),
    top_p: float = Form(0.9),
    dataset_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Verify model exists
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Create evaluation
    db_evaluation = models.Evaluation(
        name=name,
        model_id=model_id,
        status="draft",
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        created_at=datetime.utcnow()
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    # Handle dataset
    questions = []
    if use_sample:
        questions = get_random_sample_dataset(10)
    elif dataset_file:
        content = await dataset_file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        questions = [{"question": row["question"], "answer": row["answer"]} for row in csv_reader]
    
    # Store questions
    for q in questions:
        db_question = models.Question(
            evaluation_id=db_evaluation.id,
            question=q["question"],
            expected_answer=q["answer"]
        )
        db.add(db_question)
    
    db_evaluation.total_questions = len(questions)
    db.commit()
    db.refresh(db_evaluation)
    db_evaluation.model_name = db_model.name
    return db_evaluation

@app.post("/api/evaluations/{evaluation_id}/run")
async def run_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    db_evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    db_evaluation.status = "running"
    db_evaluation.started_at = datetime.utcnow()
    db.commit()
    
    try:
        # Get model and questions
        db_model = db_evaluation.model
        questions = db.query(models.Question).filter(models.Question.evaluation_id == evaluation_id).all()
        
        correct_count = 0
        total_count = len(questions)
        
        for question in questions:
            start_time = time.time()
            
            try:
                # Call Ollama API
                async with httpx.AsyncClient() as client:
                    payload = {
                        "model": db_model.model_name,
                        "prompt": question.question,
                        "stream": False,
                        "options": {
                            "temperature": db_evaluation.temperature,
                            "num_predict": db_evaluation.max_tokens,
                            "top_p": db_evaluation.top_p
                        }
                    }
                    
                    response = await client.post(
                        f"{db_model.endpoint}/api/generate",
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        model_response = result.get("response", "").strip()
                        
                        # Simple accuracy check (case-insensitive contains)
                        is_correct = question.expected_answer.lower() in model_response.lower()
                        if is_correct:
                            correct_count += 1
                        
                        # Calculate advanced metrics

                        metrics = calculate_metrics(question.expected_answer, model_response)
                        #print(f"Metrics calculated: {metrics}")
                        
                        # Store result with advanced metrics
                        db_result = models.Result(
                            evaluation_id=evaluation_id,
                            question=question.question,
                            expected_answer=question.expected_answer,
                            model_response=model_response,
                            is_correct=is_correct,
                            response_time=int((time.time() - start_time) * 1000),
                            bleu_score=metrics.get('bleu_score'),
                            rouge_1_score=metrics.get('rouge1'),
                            rouge_2_score=metrics.get('rouge2'),
                            rouge_l_score=metrics.get('rougeL'),
                            semantic_similarity=metrics.get('semantic_similarity')
                        )
                        db.add(db_result)
                    else:
                        # Store error result
                        db_result = models.Result(
                            evaluation_id=evaluation_id,
                            question=question.question,
                            expected_answer=question.expected_answer,
                            model_response="Error: Failed to get response",
                            is_correct=False,
                            response_time=int((time.time() - start_time) * 1000)
                        )
                        db.add(db_result)
                        
            except Exception as e:
                # Store error result
                db_result = models.Result(
                    evaluation_id=evaluation_id,
                    question=question.question,
                    expected_answer=question.expected_answer,
                    model_response=f"Error: {str(e)}",
                    is_correct=False,
                    response_time=int((time.time() - start_time) * 1000)
                )
                db.add(db_result)
        
        # Calculate aggregate metrics from all results
        all_results = db.query(models.Result).filter(models.Result.evaluation_id == evaluation_id).all()
        
        # Calculate averages for advanced metrics (excluding None values)
        valid_bleu = [r.bleu_score for r in all_results if r.bleu_score is not None]
        valid_rouge1 = [r.rouge_1_score for r in all_results if r.rouge_1_score is not None]
        valid_rouge2 = [r.rouge_2_score for r in all_results if r.rouge_2_score is not None]
        valid_rougel = [r.rouge_l_score for r in all_results if r.rouge_l_score is not None]
        valid_semantic = [r.semantic_similarity for r in all_results if r.semantic_similarity is not None]
        valid_response_times = [r.response_time for r in all_results if r.response_time is not None]
        
        
        # Update evaluation with results and aggregate metrics
        db_evaluation.status = "completed"
        db_evaluation.completed_at = datetime.utcnow()
        db_evaluation.accuracy = correct_count / total_count if total_count > 0 else 0
        db_evaluation.correct_answers = correct_count
        db_evaluation.incorrect_answers = total_count - correct_count
        
        # Store aggregate advanced metrics
        db_evaluation.avg_bleu_score = sum(valid_bleu) / len(valid_bleu) if valid_bleu else None
        db_evaluation.avg_rouge_1_score = sum(valid_rouge1) / len(valid_rouge1) if valid_rouge1 else None
        db_evaluation.avg_rouge_2_score = sum(valid_rouge2) / len(valid_rouge2) if valid_rouge2 else None
        db_evaluation.avg_rouge_l_score = sum(valid_rougel) / len(valid_rougel) if valid_rougel else None
        db_evaluation.avg_semantic_similarity = sum(valid_semantic) / len(valid_semantic) if valid_semantic else None
        db_evaluation.avg_response_time = sum(valid_response_times) / len(valid_response_times) if valid_response_times else None
        
        
        db.commit()
        
    except Exception as e:
        db_evaluation.status = "failed"
        db_evaluation.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
    
    return {"message": "Evaluation completed"}

# Results endpoints
@app.get("/api/results")
def get_results(db: Session = Depends(get_db)):
    evaluations = db.query(models.Evaluation).filter(models.Evaluation.status == "completed").all()
    results = []
    for eval in evaluations:
        results.append({
            "id": eval.id,
            "evaluation_id": eval.id,
            "evaluation_name": eval.name,
            "model_name": eval.model.name,
            "completed_at": eval.completed_at,
            "accuracy": eval.accuracy,
            "total_questions": eval.total_questions
        })
    return results

@app.get("/api/results/{evaluation_id}")
def get_evaluation_results(evaluation_id: int, db: Session = Depends(get_db)):
    db_evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    results = db.query(models.Result).filter(models.Result.evaluation_id == evaluation_id).all()
    
    return {
        "evaluation_name": db_evaluation.name,
        "model_name": db_evaluation.model.name,
        "accuracy": db_evaluation.accuracy,
        "correct_answers": db_evaluation.correct_answers,
        "incorrect_answers": db_evaluation.incorrect_answers,
        "total_questions": db_evaluation.total_questions,
        "questions": [
            {
                "question": r.question,
                "expected_answer": r.expected_answer,
                "model_response": r.model_response,
                "is_correct": r.is_correct,
                "response_time": r.response_time
            }
            for r in results
        ]
    }

@app.delete("/api/results/{evaluation_id}")
def delete_evaluation_results(evaluation_id: int, db: Session = Depends(get_db)):
    db_evaluation = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Delete results and questions
    db.query(models.Result).filter(models.Result.evaluation_id == evaluation_id).delete()
    db.query(models.Question).filter(models.Question.evaluation_id == evaluation_id).delete()
    db.delete(db_evaluation)
    db.commit()
    
    return {"message": "Evaluation and results deleted"}

# Synthetic Monitoring endpoints
@app.get("/api/synthetic-tests", response_model=List[schemas.SyntheticTest])
def get_synthetic_tests(db: Session = Depends(get_db)):
    return db.query(models.SyntheticTest).filter(models.SyntheticTest.id == models.SyntheticTest.id).all()

@app.post("/api/synthetic-tests", response_model=schemas.SyntheticTest)
async def create_synthetic_test(test: schemas.SyntheticTestCreate, db: Session = Depends(get_db)):
    db_test = models.SyntheticTest(**test.dict(), created_at=datetime.now())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    
    # Schedule the test if it's active
    if db_test.is_active:
        scheduler.schedule_test(db_test)
    
    return db_test

@app.get("/api/synthetic-tests/{test_id}", response_model=schemas.SyntheticTest)
def get_synthetic_test(test_id: int, db: Session = Depends(get_db)):
    db_test = db.query(models.SyntheticTest).filter(models.SyntheticTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Synthetic test not found")
    return db_test

@app.put("/api/synthetic-tests/{test_id}", response_model=schemas.SyntheticTest)
async def update_synthetic_test(test_id: int, test: schemas.SyntheticTestCreate, db: Session = Depends(get_db)):
    db_test = db.query(models.SyntheticTest).filter(models.SyntheticTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Synthetic test not found")
    
    # Store old active state
    was_active = db_test.is_active
    
    for key, value in test.dict().items():
        setattr(db_test, key, value)
    
    db.commit()
    db.refresh(db_test)
    
    # Update scheduling based on changes
    if db_test.is_active and not was_active:
        # Test was activated, schedule it
        scheduler.schedule_test(db_test)
    elif not db_test.is_active and was_active:
        # Test was deactivated, unschedule it
        scheduler.unschedule_test(test_id)
    elif db_test.is_active:
        # Test is still active, reschedule with potential new interval
        scheduler.schedule_test(db_test)
    
    return db_test

@app.delete("/api/synthetic-tests/{test_id}")
async def delete_synthetic_test(test_id: int, db: Session = Depends(get_db)):
    db_test = db.query(models.SyntheticTest).filter(models.SyntheticTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Synthetic test not found")
    
    # Unschedule the test
    scheduler.unschedule_test(test_id)
    
    # Delete executions first
    db.query(models.SyntheticExecution).filter(models.SyntheticExecution.test_id == test_id).delete()
    db.delete(db_test)
    db.commit()
    
    return {"message": "Synthetic test deleted"}

@app.post("/api/synthetic-tests/{test_id}/execute")
async def execute_synthetic_test(test_id: int, db: Session = Depends(get_db)):
    db_test = db.query(models.SyntheticTest).filter(models.SyntheticTest.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Synthetic test not found")
    
    execution = await synthetic_service.execute_test(db_test, db)
    return execution

@app.get("/api/synthetic-tests/{test_id}/executions", response_model=List[schemas.SyntheticExecution])
def get_test_executions(test_id: int, limit: int = 50, db: Session = Depends(get_db)):
    executions = db.query(models.SyntheticExecution)\
        .filter(models.SyntheticExecution.test_id == test_id)\
        .order_by(models.SyntheticExecution.executed_at.desc())\
        .limit(limit)\
        .all()
    return executions

@app.get("/api/synthetic-executions", response_model=List[schemas.SyntheticExecution])
def get_all_executions(limit: int = 100, db: Session = Depends(get_db)):
    executions = db.query(models.SyntheticExecution)\
        .order_by(models.SyntheticExecution.executed_at.desc())\
        .limit(limit)\
        .all()
    return executions

@app.get("/api/synthetic-monitoring/metrics")
async def get_monitoring_metrics(db: Session = Depends(get_db)):
    try:
        # Get metrics for each test type
        uptime_metrics = synthetic_service.get_monitoring_metrics(db, "uptime")
        api_metrics = synthetic_service.get_monitoring_metrics(db, "api")
        browser_metrics = synthetic_service.get_monitoring_metrics(db, "browser")
        
        return {
            "uptime": uptime_metrics,
            "api": api_metrics,
            "browser": browser_metrics
        }
    except Exception as e:
        logger.error(f"Error getting monitoring metrics: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong while fetching metrics")

# External Apps endpoints
@app.get("/api/external-apps", response_model=List[schemas.ExternalApp])
def get_external_apps(db: Session = Depends(get_db)):
    return db.query(models.ExternalApp).all()

@app.post("/api/external-apps", response_model=schemas.ExternalApp)
def create_external_app(app: schemas.ExternalAppCreate, db: Session = Depends(get_db)):
    db_app = models.ExternalApp(**app.dict(), created_at=datetime.now())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.get("/api/external-apps/{app_id}", response_model=schemas.ExternalApp)
def get_external_app(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.ExternalApp).filter(models.ExternalApp.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="External app not found")
    return db_app

@app.put("/api/external-apps/{app_id}", response_model=schemas.ExternalApp)
def update_external_app(app_id: int, app: schemas.ExternalAppUpdate, db: Session = Depends(get_db)):
    db_app = db.query(models.ExternalApp).filter(models.ExternalApp.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="External app not found")
    
    for key, value in app.dict().items():
        setattr(db_app, key, value)
    
    db_app.updated_at = datetime.now()
    db.commit()
    db.refresh(db_app)
    return db_app

@app.delete("/api/external-apps/{app_id}")
def delete_external_app(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.ExternalApp).filter(models.ExternalApp.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="External app not found")
    
    db.delete(db_app)
    db.commit()
    
    return {"message": "External app deleted"}

# External App Endpoints endpoints
@app.get("/api/external-apps/{app_id}/endpoints", response_model=List[schemas.ExternalAppEndpoint])
def get_external_app_endpoints(app_id: int, db: Session = Depends(get_db)):
    db_app = db.query(models.ExternalApp).filter(models.ExternalApp.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="External app not found")
    return db.query(models.ExternalAppEndpoint).filter(models.ExternalAppEndpoint.external_app_id == app_id).all()

@app.post("/api/external-apps/{app_id}/endpoints", response_model=schemas.ExternalAppEndpoint)
def create_external_app_endpoint(app_id: int, endpoint: schemas.ExternalAppEndpointCreate, db: Session = Depends(get_db)):
    db_app = db.query(models.ExternalApp).filter(models.ExternalApp.id == app_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="External app not found")
    
    endpoint_data = endpoint.dict()
    endpoint_data['external_app_id'] = app_id
    db_endpoint = models.ExternalAppEndpoint(**endpoint_data, created_at=datetime.now())
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

@app.get("/api/external-app-endpoints/{endpoint_id}", response_model=schemas.ExternalAppEndpoint)
def get_external_app_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.ExternalAppEndpoint).filter(models.ExternalAppEndpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="External app endpoint not found")
    return db_endpoint

@app.put("/api/external-app-endpoints/{endpoint_id}", response_model=schemas.ExternalAppEndpoint)
def update_external_app_endpoint(endpoint_id: int, endpoint: schemas.ExternalAppEndpointUpdate, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.ExternalAppEndpoint).filter(models.ExternalAppEndpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="External app endpoint not found")
    
    for key, value in endpoint.dict(exclude_unset=True).items():
        setattr(db_endpoint, key, value)
    
    db_endpoint.updated_at = datetime.now()
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

@app.delete("/api/external-app-endpoints/{endpoint_id}")
def delete_external_app_endpoint(endpoint_id: int, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.ExternalAppEndpoint).filter(models.ExternalAppEndpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="External app endpoint not found")
    
    db.delete(db_endpoint)
    db.commit()
    
    return {"message": "External app endpoint deleted"}
