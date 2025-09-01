from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import httpx
import time
import csv
import io
from . import models, schemas, database
from .metrics import calculate_metrics
from .database import get_db

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

# Sample dataset for testing
SAMPLE_DATASET = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "What is 2 + 2?", "answer": "4"},
    {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare"},
    {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
    {"question": "What year did World War II end?", "answer": "1945"},
    {"question": "What is the chemical symbol for gold?", "answer": "Au"},
    {"question": "How many continents are there?", "answer": "7"},
    {"question": "What is the square root of 64?", "answer": "8"},
    {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"question": "What is the speed of light in vacuum?", "answer": "299,792,458 meters per second"}
]

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
        questions = SAMPLE_DATASET
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
                        print(f"Calculating metrics for: '{question.expected_answer}' vs '{model_response}'")
                        metrics = calculate_metrics(question.expected_answer, model_response)
                        print(f"Metrics calculated: {metrics}")
                        
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
        
        print(f"Found {len(all_results)} results, valid metrics: BLEU={len(valid_bleu)}, ROUGE1={len(valid_rouge1)}, ROUGE2={len(valid_rouge2)}, ROUGEL={len(valid_rougel)}, Semantic={len(valid_semantic)}")
        
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
        
        print(f"Storing aggregate metrics: BLEU={db_evaluation.avg_bleu_score}, ROUGE1={db_evaluation.avg_rouge_1_score}, ROUGE2={db_evaluation.avg_rouge_2_score}, ROUGEL={db_evaluation.avg_rouge_l_score}, Semantic={db_evaluation.avg_semantic_similarity}")
        
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
