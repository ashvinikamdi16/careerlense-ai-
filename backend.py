from pathlib import Path
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.resume_parser import extract_text
from src.skill_extractor import extract_skills
from src.matcher import load_jobs, analyze_jobs
from src.ai_service import ai_resume_review

app = FastAPI(
    title="CareerLens AI API",
    description="Resume analysis, skill-gap and sample job recommendation API.",
    version="1.0.0",
)

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=30000)

class RecommendRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=30000)
    custom_description: Optional[str] = Field(default=None, max_length=12000)

class AIReviewRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=30000)

def get_jobs():
    try:
        return load_jobs(ROOT / "data" / "job_data.csv")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not load job dataset: {exc}")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CareerLens AI API", "version": "1.0.0"}

@app.get("/api/jobs")
def jobs():
    return {"count": len(get_jobs()), "jobs": get_jobs()}

@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    skills = extract_skills(request.resume_text)
    return {
        "word_count": len(request.resume_text.split()),
        "character_count": len(request.resume_text),
        "detected_skills": skills,
        "detected_skill_count": len(skills),
    }

@app.post("/api/recommend")
def recommend(request: RecommendRequest):
    skills = extract_skills(request.resume_text)
    results = analyze_jobs(
        request.resume_text,
        skills,
        get_jobs(),
        custom_description=request.custom_description or "",
    )
    return {"recommendations": results}

@app.post("/api/ai-review")
def ai_review(request: AIReviewRequest):
    skills = extract_skills(request.resume_text)
    try:
        review = ai_resume_review(request.resume_text, skills)
        return {"provider": "openai", "model": "configured model", "review": review}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        # Avoid returning provider request internals or secrets to clients.
        raise HTTPException(
            status_code=502,
            detail="AI review failed. Check your API key, model access, internet connection, and API billing.",
        )
