# CareerLens AI — Resume Analyzer, Skill Gap & Job Recommendation

A Windows-friendly Streamlit college project with an optional FastAPI backend and optional OpenAI-powered resume review.

## 1. Start the app (Windows)
1. Extract this ZIP.
2. Open the folder that directly contains `app.py`, `requirements.txt`, and `RUN_PROJECT.bat`.
3. Double-click **`RUN_PROJECT.bat`**. It creates `.venv`, installs dependencies, and starts Streamlit. The first install needs internet and may take a few minutes.
4. Open `http://localhost:8501` in your browser.
5. To stop the app, focus the terminal and press `Ctrl+C`.

If double-clicking does not work, use PowerShell from the project folder:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --default-timeout=120 --retries 5 -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
This avoids PowerShell activation-policy problems.

## 2. Configure your OpenAI API key (optional)
The app runs without an API key using its built-in rule-based analysis and sample data. The AI review button requires your own OpenAI API key and account access/billing.

1. In the project folder, make a copy of `.env.example` named exactly `.env`.
2. Open `.env` in Notepad and replace `put_your_real_api_key_here` with your API key:
   ```env
   OPENAI_API_KEY=your_real_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Save `.env` and restart the app.
4. Open **Resume Improvement** and click **Generate AI resume review**.

Do not paste your API key into chat, screenshots, source code, or public repositories. The `.env` file is ignored by Git. API usage may cost money depending on your provider account and model. Never use a key belonging to someone else.

## 3. Start the REST backend (optional)
Start `RUN_PROJECT.bat` once to create the environment and install packages. Then run `RUN_BACKEND.bat` in another terminal. The API listens locally at `http://127.0.0.1:8000`.
Interactive API documentation: `http://127.0.0.1:8000/docs`.

Endpoints:
- `GET /api/health` — health check
- `GET /api/jobs` — sample job dataset
- `POST /api/analyze` — skill extraction and resume text counts
- `POST /api/recommend` — job recommendations
- `POST /api/ai-review` — OpenAI-backed review; requires `.env` API key

Example request body for `/api/analyze`:
```json
{"resume_text": "Python, SQL, pandas, machine learning, and a data analytics project."}
```

Example PowerShell call:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/analyze `
  -ContentType "application/json" `
  -Body '{"resume_text":"Python, SQL, pandas and machine learning"}'
```

## Features
- Home dashboard
- PDF/DOCX resume parsing
- Dictionary-based skill extraction and basic contact-detail detection
- Skill gap analysis and recommendations from a local sample job dataset
- TF-IDF similarity ranking
- Rule-based resume checklist and optional AI review
- FastAPI backend with API documentation
- Light/Dark mode and distinct light-mode page themes
- CSV and Markdown downloads

## Project structure
```text
app.py
backend.py
requirements.txt
.env.example
RUN_PROJECT.bat
RUN_BACKEND.bat
src/
  ai_service.py
  resume_parser.py
  skill_extractor.py
  matcher.py
data/
  skills.json
  job_data.csv
tests/
sample_data/
docs/
```

## Four-member work division (suggested)
- Member 1: resume parsing and skill extraction
- Member 2: skill-gap and matching logic
- Member 3: job recommendation logic and sample dataset
- Member 4: UI, API integration, testing, report, diagrams and presentation

## Limitations and responsible use
- Job records are sample data, not live vacancies.
- Skill extraction is dictionary-based and can miss synonyms.
- Scanned/image-only PDFs need OCR, not included.
- Match scores are demo comparisons, not hiring probabilities.
- AI review requires an API key, internet access, model availability and provider billing where applicable.
- Resume text is sent to the configured AI provider when you request AI review. Use a sample/redacted resume if you do not want to share personal data with that provider.
- Verify all suggestions. Do not invent skills, education, or achievements.

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
