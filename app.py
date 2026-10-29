from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.resume_parser import extract_text
from src.skill_extractor import extract_skills, extract_basic_details
from src.matcher import load_jobs, analyze_jobs
from src.ai_service import ai_resume_review

st.set_page_config(
    page_title="CareerLens AI | Resume Intelligence",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- App state ----------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""

PAGES = [
    "Home",
    "Resume Analysis",
    "Skill Gap Analysis",
    "Job Recommendations",
    "Resume Improvement",
    "About & Team",
]
PAGE_META = {
    "Home": {"icon": "🧭", "eyebrow": "CAREER INTELLIGENCE", "title": "Find your next career move", "light": "#eef4ff", "accent": "#3157d5"},
    "Resume Analysis": {"icon": "📄", "eyebrow": "PROFILE INTELLIGENCE", "title": "Understand your resume", "light": "#effaf5", "accent": "#16795b"},
    "Skill Gap Analysis": {"icon": "🎯", "eyebrow": "SKILL INTELLIGENCE", "title": "Turn gaps into a growth plan", "light": "#fff6e9", "accent": "#b86b12"},
    "Job Recommendations": {"icon": "💼", "eyebrow": "OPPORTUNITY INTELLIGENCE", "title": "Explore roles that fit you", "light": "#f4efff", "accent": "#7042b8"},
    "Resume Improvement": {"icon": "✨", "eyebrow": "RESUME STUDIO", "title": "Make your resume stronger", "light": "#fff0f4", "accent": "#b83f69"},
    "About & Team": {"icon": "🧩", "eyebrow": "PROJECT BLUEPRINT", "title": "Built to make career planning clearer", "light": "#edf8fa", "accent": "#167b8a"},
}

def apply_theme(page_name):
    meta = PAGE_META[page_name]
    dark = st.session_state.theme_mode == "Dark"
    if dark:
        bg = "#111827"
        panel = "#1f2937"
        text = "#f3f4f6"
        muted = "#b7c1d1"
        border = "#374151"
        sidebar = "#0b1220"
        accent = "#9bb6ff"
    else:
        bg = meta["light"]
        panel = "#ffffff"
        text = "#172033"
        muted = "#58657a"
        border = "#dce3ee"
        sidebar = "#ffffff"
        accent = meta["accent"]
    css = f"""
    <style>
    :root {{ color-scheme: {'dark' if dark else 'light'}; }}
    [data-testid="stAppViewContainer"] {{ background: {bg}; color: {text}; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ background: {sidebar}; border-right: 1px solid {border}; }}
    [data-testid="stSidebar"] * {{ color: {text}; }}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1250px; }}
    h1, h2, h3, h4, p, label, li {{ color: {text}; }}
    .muted, .subtle {{ color: {muted} !important; }}
    .hero {{
      background: linear-gradient(135deg, {panel} 0%, {bg} 100%);
      border: 1px solid {border}; border-radius: 24px; padding: 28px 30px;
      margin: 4px 0 22px 0; box-shadow: 0 8px 30px rgba(20,30,60,0.06);
    }}
    .eyebrow {{ font-size: 0.75rem; font-weight: 800; letter-spacing: .15em; color: {accent}; margin-bottom: 8px; }}
    .hero-title {{ font-size: clamp(1.8rem, 4vw, 2.7rem); line-height: 1.13; font-weight: 850; margin: 0 0 10px 0; color: {text}; }}
    .hero-copy {{ color: {muted}; font-size: 1.02rem; max-width: 800px; margin: 0; }}
    .panel {{
      background: {panel}; border: 1px solid {border}; border-radius: 18px;
      padding: 18px 20px; box-shadow: 0 4px 18px rgba(20,30,60,0.035); height: 100%;
    }}
    .panel-label {{ color: {muted}; font-size: .82rem; font-weight: 650; }}
    .panel-value {{ color: {text}; font-size: 1.8rem; font-weight: 800; margin-top: 5px; }}
    .pill {{ display:inline-block; padding:5px 10px; border-radius:999px; font-size:.78rem; font-weight:750; background:{bg}; border:1px solid {border}; color:{accent}; }}
    .step-number {{ display:inline-flex; align-items:center; justify-content:center; width:32px; height:32px; border-radius:10px; background:{bg}; color:{accent}; font-weight:850; margin-right:8px; }}
    div[data-testid="stMetric"] {{ background:{panel}; border:1px solid {border}; padding:14px 16px; border-radius:16px; }}
    div[data-testid="stFileUploader"] {{ background:{panel}; border:1px dashed {border}; border-radius:16px; padding:12px; }}
    .stButton > button, .stDownloadButton > button {{ border-radius: 11px; font-weight: 700; min-height: 2.7rem; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid {border}; border-radius: 12px; overflow: hidden; }}
    .footer {{ color:{muted}; font-size:.8rem; padding-top:20px; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def hero(page_name, description):
    meta = PAGE_META[page_name]
    st.markdown(
        f"""<div class="hero">
        <div class="eyebrow">{meta['icon']} &nbsp; {meta['eyebrow']}</div>
        <div class="hero-title">{meta['title']}</div>
        <p class="hero-copy">{description}</p>
        </div>""",
        unsafe_allow_html=True,
    )

def panel(label, value, detail=""):
    st.markdown(
        f"""<div class="panel">
        <div class="panel-label">{label}</div>
        <div class="panel-value">{value}</div>
        <div class="subtle" style="font-size:.82rem;margin-top:4px">{detail}</div>
        </div>""",
        unsafe_allow_html=True,
    )

# Sidebar controls
with st.sidebar:
    st.markdown("## 🧭 CareerLens AI")
    st.caption("Resume intelligence workspace")
    st.markdown("---")
    st.session_state.theme_mode = st.radio(
        "Appearance",
        ["Light", "Dark"],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        horizontal=True,
        help="Light mode uses a distinct soft background on each page. Dark mode uses a consistent low-glare palette.",
    )
    st.markdown("### Workspace")
    chosen = st.radio(
        "Navigate",
        PAGES,
        index=PAGES.index(st.session_state.active_page),
        format_func=lambda p: f"{PAGE_META[p]['icon']}  {p}",
        label_visibility="collapsed",
    )
    st.session_state.active_page = chosen
    st.markdown("---")
    if st.session_state.resume_text:
        st.success(f"Resume ready: {st.session_state.resume_filename}")
        st.caption(f"{len(st.session_state.resume_skills)} skills detected")
    else:
        st.info("Upload a resume in Resume Analysis to unlock personalized results.")
    st.markdown("---")
    st.caption("College project prototype • Sample job data")

page = st.session_state.active_page
apply_theme(page)

# Load dataset safely
try:
    jobs = load_jobs(ROOT / "data" / "job_data.csv")
except Exception as e:
    jobs = []
    st.error(f"Could not load the job dataset: {e}")

if page == "Home":
    hero("Home", "A polished workspace to explore resume strengths, skill gaps and potential job roles — all in one place.")
    c1, c2, c3 = st.columns(3)
    with c1: panel("SUPPORTED RESUME FORMATS", "PDF + DOCX", "Text-based documents")
    with c2: panel("SAMPLE JOB ROLES", str(len(jobs)), "Editable CSV dataset")
    with c3: panel("ANALYSIS FLOW", "4 steps", "Upload → Extract → Compare → Improve")
    st.markdown("### Your career workflow")
    steps = st.columns(4)
    workflow = [
        ("01", "Upload", "Add a PDF or DOCX resume."),
        ("02", "Analyze", "Extract contact details and known skills."),
        ("03", "Compare", "Review matched and missing role skills."),
        ("04", "Improve", "Explore roles and practical next steps."),
    ]
    for col, (num, title, copy) in zip(steps, workflow):
        with col:
            st.markdown(f'<div class="panel"><span class="step-number">{num}</span><b>{title}</b><p class="subtle">{copy}</p></div>', unsafe_allow_html=True)
    st.markdown("### What makes this useful?")
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="panel"><h3>🔎 Explainable results</h3><p class="subtle">The system shows which skills matched and which skills are missing, rather than returning only a score.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><h3>🎨 Designed for clarity</h3><p class="subtle">Choose Light or Dark appearance from the sidebar. Each page has its own light-mode accent and background.</p></div>', unsafe_allow_html=True)
    st.info("Start with **Resume Analysis** in the sidebar. Job recommendations use a local sample dataset, not live vacancies.")

elif page == "Resume Analysis":
    hero(page, "Upload a resume to extract readable text, identify known skills and create the analysis used by the other pages.")
    uploaded = st.file_uploader("Choose a resume", type=["pdf", "docx"], help="Text-based PDF and DOCX files are supported.")
    if uploaded:
        try:
            resume_text = extract_text(uploaded.getvalue(), uploaded.name)
            if not resume_text.strip():
                st.error("No readable text found. Scanned PDFs need OCR, which is not included in this version.")
            else:
                skills = extract_skills(resume_text)
                details = extract_basic_details(resume_text)
                st.session_state.resume_text = resume_text
                st.session_state.resume_skills = skills
                st.session_state.resume_filename = uploaded.name
                st.success("Resume processed. Other pages can now use this analysis.")
                m1, m2, m3 = st.columns(3)
                m1.metric("Skills detected", len(skills))
                m2.metric("Words extracted", len(resume_text.split()))
                m3.metric("Format", uploaded.name.rsplit(".", 1)[-1].upper())
                st.markdown("### Profile snapshot")
                d1, d2, d3 = st.columns(3)
                with d1: panel("NAME (HEURISTIC)", details["name"] or "Not detected", "Check manually for accuracy")
                with d2: panel("EMAIL", details["email"] or "Not found", "Extracted from text")
                with d3: panel("PHONE", details["phone"] or "Not found", "Extracted from text")
                st.markdown("### Skills found")
                if skills:
                    st.write(" ".join([f"`{s}`" for s in skills]))
                else:
                    st.warning("No known skills were detected. Add aliases to data/skills.json if the resume uses different wording.")
                with st.expander("Preview extracted resume text"):
                    st.text_area("Extracted text", resume_text, height=250)
        except Exception as e:
            st.error(f"Resume could not be processed: {e}")
    elif st.session_state.resume_text:
        st.success(f"Current session has an analyzed resume: {st.session_state.resume_filename}")
        st.write("Upload another file above to replace the current analysis.")
        st.write("Detected skills:", ", ".join(st.session_state.resume_skills) or "None")
    else:
        st.markdown('<div class="panel"><h3>Before you upload</h3><p class="subtle">Use a text-based PDF or DOCX. Scanned image-only PDFs are not supported in this build.</p></div>', unsafe_allow_html=True)

elif page == "Skill Gap Analysis":
    hero(page, "Choose a target job role and see the skills you already have, the skills listed as requirements, and the gaps to prioritize.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first on the Resume Analysis page.")
    elif not jobs:
        st.error("No job dataset is available.")
    else:
        results = analyze_jobs(st.session_state.resume_text, st.session_state.resume_skills, jobs)
        role = st.selectbox("Target job role", [r["title"] for r in results])
        item = next(r for r in results if r["title"] == role)
        x, y, z = st.columns(3)
        x.metric("Skill match", f"{item['skill_match_pct']:.0f}%")
        y.metric("Matched skills", len(item["matched_skills"]))
        z.metric("Skills to consider", len(item["missing_skills"]))
        st.progress(int(item["skill_match_pct"]), text=f"{item['skill_match_pct']:.0f}% of the role's listed skills matched")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="panel"><h3>✅ Skills matched</h3>', unsafe_allow_html=True)
            if item["matched_skills"]:
                for s in item["matched_skills"]: st.write(f"✓ {s}")
            else: st.write("No overlap found in the sample requirement list.")
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="panel"><h3>📚 Skills to learn</h3>', unsafe_allow_html=True)
            if item["missing_skills"]:
                for s in item["missing_skills"]: st.write(f"＋ {s}")
            else: st.write("No missing skills from this sample list.")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("### Suggested action plan")
        if item["missing_skills"]:
            first = item["missing_skills"][0]
            st.write(f"1. Start with **{first}** and learn the fundamentals.")
            st.write("2. Build a small project that demonstrates the skill.")
            st.write("3. Add the project to your resume only after you have completed it.")
        else:
            st.write("Review the job description carefully and strengthen your portfolio with relevant projects.")
        st.caption("Skill match is a comparison against this demo dataset; it is not a hiring probability.")

elif page == "Job Recommendations":
    hero(page, "Compare your resume with sample job roles. Ranking uses skill coverage and text similarity to help you explore possible directions.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first on the Resume Analysis page.")
    elif not jobs:
        st.error("No job dataset is available.")
    else:
        custom_desc = st.text_area("Optional: paste a specific job description", height=130, placeholder="Paste the job description here to compare resume text with it.")
        results = analyze_jobs(st.session_state.resume_text, st.session_state.resume_skills, jobs, custom_description=custom_desc)
        rows = []
        for i, r in enumerate(results, 1):
            rows.append({
                "Rank": i,
                "Job role": r["title"],
                "Skill match": f"{r['skill_match_pct']:.1f}%",
                "Text similarity": f"{r['text_similarity_pct']:.1f}%",
                "Combined score": f"{r['combined_score']:.1f}%",
                "Missing skills": ", ".join(r["missing_skills"]) or "None from sample list",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown("### Recommendation details")
        chosen_role = st.selectbox("Inspect a recommendation", [r["title"] for r in results])
        selected = next(r for r in results if r["title"] == chosen_role)
        st.markdown(f'<div class="panel"><div class="eyebrow">RECOMMENDED ROLE</div><h2>{selected["title"]}</h2><p class="subtle">{selected["description"]}</p></div>', unsafe_allow_html=True)
        q1, q2 = st.columns(2)
        with q1: panel("SKILL MATCH", f'{selected["skill_match_pct"]:.1f}%', "Based on listed required skills")
        with q2: panel("TEXT SIMILARITY", f'{selected["text_similarity_pct"]:.1f}%', "TF-IDF cosine similarity")
        st.write("**Matched:**", ", ".join(selected["matched_skills"]) or "None")
        st.write("**Missing:**", ", ".join(selected["missing_skills"]) or "None from sample list")
        st.download_button("⬇ Download recommendations CSV", pd.DataFrame(rows).to_csv(index=False).encode("utf-8"), "job_recommendations.csv", "text/csv")
        st.caption("The job list is sample data, not live vacancies. Scores support exploration and do not guarantee suitability or hiring.")

elif page == "Resume Improvement":
    hero(page, "Use simple, transparent checks to identify areas worth reviewing before you send your resume to an employer.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first on the Resume Analysis page.")
    else:
        txt = st.session_state.resume_text
        lower = txt.lower()
        tips = []
        if len(txt.split()) < 120:
            tips.append(("Add relevant detail", "The extracted resume text looks short. Consider relevant projects, coursework, internships and achievements."))
        if "project" not in lower:
            tips.append(("Add a projects section", "Describe what you built, your individual contribution, tools used and the outcome."))
        if not any(x in lower for x in ["education", "b.tech", "bachelor", "degree"]):
            tips.append(("Clarify education", "Use a clearly labeled Education section with degree, institution and dates."))
        if not any(x in lower for x in ["github", "portfolio"]):
            tips.append(("Add a portfolio link", "If you have one, include a GitHub or portfolio link with relevant work."))
        if not tips:
            tips.append(("Tailor each application", "Use concise bullets and include measurable outcomes only when you can support the numbers."))
        st.markdown("### Your review checklist")
        for i, (title, detail) in enumerate(tips, 1):
            st.markdown(f'<div class="panel" style="margin-bottom:12px"><span class="step-number">{i:02}</span><b>{title}</b><p class="subtle">{detail}</p></div>', unsafe_allow_html=True)
        st.markdown("### Download your summary")
        summary = pd.DataFrame([{
            "resume_file": st.session_state.resume_filename,
            "detected_skills": ", ".join(st.session_state.resume_skills),
            "word_count": len(txt.split()),
            "suggestions": " | ".join(t[0] for t in tips),
        }])
        st.download_button("⬇ Download resume review summary", summary.to_csv(index=False).encode("utf-8"), "resume_review_summary.csv", "text/csv")
        st.markdown("### 🤖 Optional AI-powered review")
        st.write("Connect your own OpenAI API key using the local `.env` file to generate tailored feedback.")
        if st.button("Generate AI resume review", type="primary", key="generate_ai_review"):
            with st.spinner("Reviewing resume with the configured AI model..."):
                try:
                    ai_review = ai_resume_review(txt, st.session_state.resume_skills)
                    st.session_state["career_ai_review"] = ai_review
                except Exception as exc:
                    st.error(str(exc))
        if st.session_state.get("career_ai_review"):
            st.markdown(st.session_state["career_ai_review"])
            st.download_button(
                "⬇ Download AI review",
                st.session_state["career_ai_review"].encode("utf-8"),
                "ai_resume_review.md",
                "text/markdown",
            )
        st.caption("AI feedback is optional and requires your own API key. Verify every suggestion and never add invented achievements.")
        st.caption("These are basic rule-based suggestions, not a substitute for a professional resume review.")

elif page == "About & Team":
    hero(page, "A transparent, student-friendly prototype that demonstrates document processing, explainable matching and interface design.")
    st.markdown("### Project overview")
    st.write("**AI-Based Resume Analyzer, Skill Gap Analysis & Job Recommendation System**")
    st.write("The application extracts text from PDF/DOCX resumes, detects skills from a configurable dictionary, compares those skills with a sample job dataset, and ranks roles using skill coverage and TF-IDF text similarity.")
    st.markdown("### Team work division")
    cols = st.columns(4)
    team = [
        ("01", "Resume Analysis", "PDF/DOCX parsing, basic details and skill extraction."),
        ("02", "Skill Gap", "Matched skills, missing skills and coverage formula."),
        ("03", "Job Recommendation", "Job dataset, TF-IDF similarity and ranked roles."),
        ("04", "UI & Quality", "Dashboard integration, testing, report, diagrams and PPT."),
    ]
    for col, (num, title, desc) in zip(cols, team):
        with col:
            st.markdown(f'<div class="panel"><span class="step-number">{num}</span><h3>{title}</h3><p class="subtle">{desc}</p></div>', unsafe_allow_html=True)
    st.markdown("### Technology stack")
    st.write("Python · Streamlit · PyMuPDF · python-docx · Pandas · scikit-learn · CSV/JSON")
    st.markdown("### Limitations and responsible use")
    st.markdown("""
    - Sample job records are static and are not live vacancies.
    - Skill detection depends on the dictionary in `data/skills.json`.
    - Scanned PDFs require OCR, not included in this version.
    - The match score is not a hiring probability or guarantee of suitability.
    - Basic name and phone detection may be inaccurate; verify results manually.
    - Do not upload sensitive personal information to a public deployment.
    """)
st.markdown('<div class="footer">CareerLens AI • Educational prototype • Verify all extracted details before using them in real applications.</div>', unsafe_allow_html=True)
