"""Every fact shown on the profile — edit wording here, then run forge/summon.py.

Sources: your resume (Denilson_Pinto_Resume.pdf) and your public repositories,
checked against each repo's README, requirements.txt and code (2026-09-23).
Nothing here is invented; unverified claims were left out on purpose.
"""

ACRONYMS = {"AI", "ML", "LLM", "LLMS", "NLP", "UI", "UX", "IOT", "AR", "VR", "CV", "DS"}


def title_case(s: str) -> str:
    """'AI ENGINEER' → 'AI Engineer' (keeps acronyms)."""
    return " ".join(w if w.upper() in ACRONYMS else w.capitalize() for w in s.split())


PROFILE = {
    "name": "DENILSON PINTO B",
    "title": "AI ENGINEER",
    "specialties": "Machine Learning • LLMs • Generative AI",
    "headline": "AI Engineer • Machine Learning • LLMs • Generative AI",
    "summary": ("Final-year AI & Data Science undergraduate building AI applications "
                "with Python, NLP, Machine Learning and Generative AI."),
    "degree": "B.Tech Artificial Intelligence & Data Science",
    "college": "CSI College of Engineering, Ketti",
    "focus": "AI  /  ML  /  LLM  /  Generative AI",
}

MISSION = {
    "primary": "FLASHDROP",
    "primary_tags": ["FINAL YEAR PROJECT", "IN DEVELOPMENT"],
    "secondary": ["AI applications", "Machine Learning", "LLMs", "Generative AI", "Computer Vision", "Software development"],
}

FLASHDROP = {
    "concept": "Cross-platform high-speed file sharing and transfer",
    "idea": "Fast peer-to-peer / local transfer between supported devices — no cable.",
    "platforms": ["Android", "iOS", "Windows", "macOS"],
    "modules": ["FlashHub", "FlashSend", "FlashReceive", "FlashGroup", "FlashCloud", "FlashAI"],
    "example": ["Android", "Windows", "Large file", "No cable"],
    "direction": ["Flutter", "Dart", "Cross-platform architecture", "P2P / Wi-Fi transfer", "QR-based pairing"],
}

# Verified against each repo's README, requirements.txt and code. `demo` names the
# config key holding the live URL (None = no public demo). `kind` keeps TechNova
# honest: it is a web project, not an AI project.
PROJECTS = [
    dict(key="resume-analyzer", name="Smart AI Resume Analyzer Pro", repo="Smart-AI-Resume-Analyzer-Pro", title="SMART AI RESUME ANALYZER PRO", short="RESUME",
         kind="AI APPLICATION", icon="scan",
         tagline="AI-powered resume screening & career recommendation system",
         features=["ATS score & resume grade", "Skill + missing-skill detection", "Job match percentage",
                   "Career readiness score", "Section analysis & interview questions", "Radar / pie charts · PDF report"],
         tech=["Python", "Streamlit", "PyPDF2", "NumPy", "Matplotlib", "ReportLab"],
         demo="RESUME_ANALYZER_DEMO", demo_label="LIVE DEMO"),
    dict(key="cyber-detective", name="AI Cyber Detective", repo="AI-Cyber-Detective", title="AI CYBER DETECTIVE", short="CYBER",
         kind="AI SECURITY", icon="shield",
         tagline="AI-powered cyber threat investigation platform",
         features=["Phishing & fake-job scam detection", "OTP-theft & investment scams", "Lottery & tech-support scams",
                   "AI threat explanation", "Confidence score & risk level", "PDF investigation report"],
         tech=["Python", "Streamlit", "Gemini API", "Matplotlib", "ReportLab"],
         demo="CYBER_DETECTIVE_DEMO", demo_label="LIVE DEMO"),
    dict(key="interview-guide", name="AI Smart Interview Guide", repo="AI-Smart-Interview-Guide", title="AI SMART INTERVIEW GUIDE", short="INTERVIEW",
         kind="AI APPLICATION", icon="mic",
         tagline="AI-powered interview simulation platform",
         features=["Resume-based questions", "Adaptive follow-up questions", "Voice AI interviewer",
                   "Speech-to-text answers", "Gemini feedback on answers", "Dashboard & PDF report"],
         tech=["Python", "Streamlit", "Gemini API", "edge-tts", "Plotly", "ReportLab"],
         demo=None, demo_label=None),
    dict(key="ai-vision", name="AI Vision Pro", repo="AI-Vision-Pro", title="AI VISION PRO", short="VISION",
         kind="COMPUTER VISION", icon="eye",
         tagline="Image classification web app with TensorFlow & Streamlit",
         features=["Image upload (JPG / PNG)", "MobileNetV2 inference", "Top-3 predictions",
                   "Confidence visualization", "ImageNet · 1000 classes"],
         tech=["Python", "TensorFlow", "MobileNetV2", "Streamlit", "NumPy", "Pillow"],
         demo=None, demo_label=None),
    dict(key="chatbot", name="CodeOrbit Rule-Based Chatbot", repo="CodeOrbit-Rule-Based-Chatbot", title="CODEORBIT RULE-BASED CHATBOT", short="CHATBOT",
         kind="INTERNSHIP PROJECT", icon="chat",
         tagline="Rule-based chatbot · CodeOrbit AI internship project",
         features=["Interactive chat & history", "Welcome message & clear chat", "Rule-based responses",
                   "Current date & time", "Python / AI / ML / DL answers"],
         tech=["Python", "Streamlit"],
         demo=None, demo_label=None),
    dict(key="technova", name="TechNova 2K26", repo="iste.csice.edu.in", title="TECHNOVA 2K26", short="TECHNOVA",
         kind="WEB PROJECT", icon="calendar",
         tagline="National-level inter-college symposium website",
         org="ISTE Student Chapter · CSI College of Engineering, Ketti",
         features=["Event information", "Official poster", "Registration QR", "Event photographs", "College & ISTE assets"],
         tech=["HTML", "CSS", "JavaScript", "GitHub Pages"],
         demo="TECHNOVA_SITE", demo_label="LIVE SITE"),
]

SKILLS = [
    ("AI & MACHINE LEARNING", ["Machine Learning", "NLP", "Generative AI", "LLMs", "Gemini API", "NLTK", "TensorFlow", "MobileNetV2"]),
    ("DATA & ANALYTICS", ["Python", "SQL", "Pandas", "NumPy", "Power BI", "Matplotlib", "Plotly"]),
    ("APPS & TOOLING", ["Streamlit", "Git", "GitHub", "ReportLab", "PyPDF2", "Pillow"]),
]
# label → brand icon slug, or sigil:<name> for an original glyph
SKILL_ICONS = {
    "Python": "python", "Pandas": "pandas", "NumPy": "numpy", "Streamlit": "streamlit", "Git": "git", "GitHub": "github",
    "TensorFlow": "tensorflow", "Gemini API": "googlegemini", "Plotly": "plotly", "Machine Learning": "sigil:nodes",
    "NLP": "sigil:chat", "Generative AI": "sigil:spark", "LLMs": "sigil:brain", "NLTK": "sigil:book", "MobileNetV2": "sigil:layers",
    "SQL": "sigil:db", "Power BI": "sigil:chart", "Matplotlib": "sigil:chart", "ReportLab": "sigil:doc", "PyPDF2": "sigil:doc",
    "Pillow": "sigil:image", "HTML": "html5", "CSS": "css", "JavaScript": "javascript", "GitHub Pages": "sigil:globe",
    "edge-tts": "sigil:mic", "Flutter": "flutter", "Dart": "dart",
}

EXPERIENCE = [
    ("2026", "CodeOrbit", "AI Intern", "Artificial Intelligence & Data Science"),
    ("2026", "Cognifyz Technologies", "Software Development Intern", "Remote"),
    ("2026", "SaiKet Systems", "Data Science Intern", "Remote"),
]

EDUCATION = [
    ("2024 — 2027", "B.Tech Artificial Intelligence & Data Science", "CSI College of Engineering, Ketti", "FINAL YEAR"),
    ("2021 — 2024", "Diploma in Computer Engineering", "", "COMPLETED"),
]

# (certificate, issuer — or the kind of certificate when the resume names no issuer, sigil)
CERTIFICATIONS = [
    ("Prompt Engineering Certification", "Certification", "spark"),
    ("Cloud Computing Internship Certificate", "Internship certificate", "cloud"),
    ("Internship in Artificial Intelligence & Data Science", "CodeOrbit", "brain"),
    ("Internship in Software Development", "Cognifyz Technologies", "code"),
    ("Internship in Data Science", "SaiKet Systems", "chart"),
]
ISSUERS = {"CodeOrbit", "Cognifyz Technologies", "SaiKet Systems"}

TERMINAL = [
    ("whoami", ["AI Engineer"]),
    ("focus", ["AI / ML / LLM / Generative AI"]),
    ("project", ["FlashDrop"]),
    ("status", ["IN DEVELOPMENT"]),
    ("environment", ["Python / Streamlit / GitHub / Flutter"]),
]
