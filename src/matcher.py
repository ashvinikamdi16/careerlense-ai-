import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_jobs(path):
    df = pd.read_csv(path).fillna("")
    required = {"title", "required_skills", "description"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Job dataset is missing columns: {', '.join(sorted(missing))}")
    return df.to_dict(orient="records")

def compare_job(resume_text, resume_skills, job, custom_description=""):
    required = [s.strip() for s in str(job.get("required_skills", "")).split("|") if s.strip()]
    user = {s.casefold() for s in resume_skills}
    matched = [s for s in required if s.casefold() in user]
    missing = [s for s in required if s.casefold() not in user]
    skill_pct = len(matched) / len(required) * 100 if required else 0.0
    job_text = custom_description.strip() or f"{job.get('title', '')} {job.get('description', '')} {' '.join(required)}"
    try:
        vectors = TfidfVectorizer(stop_words="english").fit_transform([resume_text, job_text])
        similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100)
    except ValueError:
        similarity = 0.0
    combined = 0.8 * skill_pct + 0.2 * similarity
    return {
        "title": str(job.get("title", "Untitled role")),
        "description": str(job.get("description", "")),
        "required_skills": required,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_pct": round(skill_pct, 1),
        "text_similarity_pct": round(similarity, 1),
        "combined_score": round(combined, 1),
    }

def analyze_jobs(resume_text, resume_skills, jobs, custom_description=""):
    rows = [compare_job(resume_text, resume_skills, job, custom_description) for job in jobs]
    return sorted(rows, key=lambda row: (row["combined_score"], row["skill_match_pct"]), reverse=True)
