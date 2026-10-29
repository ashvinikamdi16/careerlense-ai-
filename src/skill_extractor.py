import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_PATH = ROOT / "data" / "skills.json"

def load_skill_dictionary(path=SKILLS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_skills(text: str, dictionary=None):
    dictionary = dictionary if dictionary is not None else load_skill_dictionary()
    lower = text.lower()
    found = []
    for canonical, aliases in dictionary.items():
        for term in [canonical] + aliases:
            term = term.strip()
            if not term:
                continue
            pattern = r"(?<![a-z0-9+#.])" + re.escape(term.lower()) + r"(?![a-z0-9+#.])"
            if re.search(pattern, lower):
                found.append(canonical)
                break
    return sorted(set(found), key=str.lower)

def extract_basic_details(text: str):
    email = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I)
    phone = re.search(r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = None
    for line in lines[:5]:
        if len(line) < 60 and re.fullmatch(r"[A-Za-z][A-Za-z .'-]{1,58}", line) and not re.search(
            r"resume|curriculum vitae|profile|summary|email|phone", line, re.I
        ):
            name = line
            break
    return {"name": name, "email": email.group(0) if email else None,
            "phone": phone.group(0).strip() if phone else None}
