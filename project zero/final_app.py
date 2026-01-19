# -----------------------------
# Module Imports
# -----------------------------
import io
import os
import re
import json
import math
import time
import hashlib
import zipfile
import datetime as dt
import subprocess
import multiprocessing
from typing import List, Optional, Dict, Any, Tuple, Generator, cast

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, String, Integer, Float, Boolean, DateTime, Text, asc, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session, Mapped, mapped_column

# Required for Streamlit frontend
import streamlit as st
import requests

# -----------------------------
# Third-party optional imports
# -----------------------------
# These blocks handle cases where third-party libraries (like androguard) might not be installed.
# They define placeholder classes to prevent ImportErrors.
try:
    from androguard.core.bytecodes.apk import APK  # type: ignore
    ANDROGUARD_AVAILABLE = True
except ImportError:
    ANDROGUARD_AVAILABLE = False
    class APK:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def get_app_name(self): pass
        def get_package(self): pass
        def get_permissions(self): pass
        def get_activities(self): pass
        def get_receivers(self): pass
        def get_services(self): pass
        def get_providers(self): pass
        def get_signature_names(self): pass

try:
    from apkutils2 import APK as APKU  # type: ignore
    APKUTILS_AVAILABLE = True
except ImportError:
    APKUTILS_AVAILABLE = False
    class APKU:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def get_manifest(self): pass
        def get_app_name(self): pass
        def get_package_name(self): pass

try:
    from rapidfuzz import fuzz  # type: ignore
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    class fuzz:  # type: ignore
        @staticmethod
        def ratio(s1, s2): return 0

try:
    import joblib  # type: ignore
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    class joblib:  # type_ignore
        @staticmethod
        def load(path): return None


# -----------------------------
# BACKEND: Setup
# This section sets up the database, file directories, and core constants for the FastAPI backend.
# -----------------------------
DATA_DIR = os.path.abspath("data")
UPLOAD_DIR = os.path.abspath(os.path.join("storage", "uploads"))
MODEL_DIR = os.path.abspath("models")
MAX_UPLOAD_SIZE = 100 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/vnd.android.package-archive", "application/octet-stream"}

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_URL = f"sqlite:///{os.path.join(DATA_DIR, 'app.db')}"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# -----------------------------
# BACKEND: Models (SQLAlchemy 2.0 typing)
# These classes define the database schema using SQLAlchemy 2.0's Mapped syntax.
# Pylance uses these type hints to ensure data integrity in the code.
# -----------------------------
class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    sha256: Mapped[str] = mapped_column(String, unique=True, index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    verdict: Mapped[str] = mapped_column(String)
    score: Mapped[float] = mapped_column(Float)
    reasons: Mapped[str] = mapped_column(Text)
    features: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class BankRef(Base):
    __tablename__ = "banks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    package: Mapped[str] = mapped_column(String, index=True)
    official: Mapped[bool] = mapped_column(Boolean, default=True)


Base.metadata.create_all(bind=engine)


# Seed database with known banks. This ensures the application has initial data to work with.
with SessionLocal() as s:
    if s.query(BankRef).count() == 0:
        seed = [
            ("SBI YONO", "com.sbi.lotusintouch"),
            ("HDFC Bank MobileBanking", "com.snapwork.hdfc"),
            ("ICICI iMobile Pay", "com.csam.icici.bank.imobile"),
            ("Axis Mobile", "com.axis.mobile"),
            ("Paytm", "net.one97.paytm"),
            ("PhonePe", "com.phonepe.app"),
            ("Google Pay", "com.google.android.apps.nbu.paisa.user"),
        ]
        for n, p in seed:
            s.add(BankRef(name=n, package=p, official=True))
        s.commit()


# -----------------------------
# BACKEND: Pydantic Models
# These classes define the data structures for API requests and responses.
# FastAPI uses them for data validation and serialization.
# -----------------------------
class Reason(BaseModel):
    code: str
    detail: str


class AnalysisResult(BaseModel):
    sha256: str
    filename: str
    size_bytes: int
    score: float
    verdict: str
    reasons: List[Reason]
    features: Dict[str, Any]
    created_at: dt.datetime


class BankIn(BaseModel):
    name: str
    package: str
    official: bool = True


class BankOut(BankIn):
    id: int


# -----------------------------
# BACKEND: FastAPI setup
# This initializes the FastAPI application and configures CORS.
# -----------------------------
app = FastAPI(title="Fake Banking APK Detector – Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# BACKEND: Utils
# Helper functions for database session, hashing, and feature analysis.
# -----------------------------
def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sha256_bytes(b: bytes) -> str:
    """Calculates the SHA256 hash of a byte string."""
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()

DANGEROUS_PERMS = {
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.QUERY_ALL_PACKAGES",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.PACKAGE_USAGE_STATS",
}

SUSPICIOUS_TLDS = {
    ".top", ".xyz", ".info", ".click", ".shop", ".live", ".ru", ".cn", ".su", ".biz",
}

URL_REGEX = re.compile(r"https?://[\w.-/:?=&%#]+", re.IGNORECASE)

def extract_with_androguard(apk_bytes: bytes) -> Dict[str, Any]:
    """Extracts features from an APK using androguard."""
    fp = io.BytesIO(apk_bytes)
    a = APK(fp)
    out: Dict[str, Any] = {
        "app_name": a.get_app_name(),
        "package": a.get_package(),
        "permissions": sorted(list(set(a.get_permissions() or []))),
        "activities": a.get_activities() or [],
        "receivers": a.get_receivers() or [],
        "services": a.get_services() or [],
        "providers": a.get_providers() or [],
        "files": [],
        "urls": [],
        "certificates": [str(x) for x in (a.get_signature_names() or [])],
    }
    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
        file_names = z.namelist()
        out["files"] = file_names
        urls: List[str] = []
        for name in file_names:
            if name.endswith((".dex", ".arsc", ".xml", ".txt", ".json", ".js")):
                try:
                    data = z.read(name)
                    urls.extend([u for u in URL_REGEX.findall(data.decode("utf-8", errors="ignore"))])
                except Exception:
                    pass
        out["urls"] = sorted(list(set(urls)))
    return out


def extract_with_apkutils(apk_bytes: bytes) -> Dict[str, Any]:
    """Extracts features from an APK using apkutils2."""
    fp = io.BytesIO(apk_bytes)
    apk = APKU(fp)
    manifest = apk.get_manifest() or {}
    permissions = sorted(list({p["name"] for p in manifest.get("uses-permission", []) if "name" in p}))
    app_label = apk.get_app_name()
    pkg = apk.get_package_name()
    out: Dict[str, Any] = {
        "app_name": app_label,
        "package": pkg,
        "permissions": permissions,
        "activities": [],
        "receivers": [],
        "services": [],
        "providers": [],
        "files": [],
        "urls": [],
        "certificates": [],
    }
    with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
        file_names = z.namelist()
        out["files"] = file_names
        urls: List[str] = []
        for name in file_names:
            if name.endswith((".dex", ".arsc", ".xml", ".txt", ".json", ".js")):
                try:
                    data = z.read(name)
                    urls.extend([u for u in URL_REGEX.findall(data.decode("utf-8", errors="ignore"))])
                except Exception:
                    pass
        out["urls"] = sorted(list(set(urls)))
    return out


def extract_features(apk_bytes: bytes) -> Dict[str, Any]:
    """Attempts to extract features using available libraries, with a fallback for basic info."""
    if ANDROGUARD_AVAILABLE:
        try:
            return extract_with_androguard(apk_bytes)
        except Exception:
            pass
    if APKUTILS_AVAILABLE:
        try:
            return extract_with_apkutils(apk_bytes)
        except Exception:
            pass
    features: Dict[str, Any] = {
        "app_name": None,
        "package": None,
        "permissions": [],
        "activities": [],
        "receivers": [],
        "services": [],
        "providers": [],
        "files": [],
        "urls": [],
        "certificates": [],
    }
    try:
        with zipfile.ZipFile(io.BytesIO(apk_bytes)) as z:
            file_names = z.namelist()
            features["files"] = file_names
            urls: List[str] = []
            for name in file_names:
                if name.endswith((".dex", ".arsc", ".xml", ".txt", ".json", ".js")):
                    try:
                        data = z.read(name)
                        urls.extend([u for u in URL_REGEX.findall(data.decode("utf-8", errors="ignore"))])
                    except Exception:
                        pass
            features["urls"] = sorted(list(set(urls)))
    except Exception:
        pass
    return features


def tld_score(urls: List[str]) -> int:
    """Calculates a score based on suspicious top-level domains in URLs."""
    score = 0
    for u in urls:
        for tld in SUSPICIOUS_TLDS:
            if u.lower().endswith(tld) or ("." + tld.strip(".")) in u.lower().split("/")[2]:
                score += 2
                break
    return score


def name_similarity_score(app_name: Optional[str], known: List[str]) -> float:
    """Calculates app name similarity to a list of known names."""
    if not app_name or not known:
        return 0.0
    if RAPIDFUZZ_AVAILABLE:
        best = max(fuzz.ratio(app_name, k) for k in known)
        return float(best)
    app_lower = app_name.lower()
    best = 0
    for k in known:
        k_lower = k.lower()
        common = len(set(app_lower.split()) & set(k_lower.split()))
        best = max(best, common / max(len(k_lower.split()), 1) * 100)
    return float(best)


def compute_heuristic_score(
    features: Dict[str, Any],
    bank_names: List[str],
    bank_packages: List[str]
) -> Tuple[float, List[Reason]]:
    """Applies a set of heuristic rules to determine a risk score."""
    score = 0.0
    reasons: List[Reason] = []
    perms = set(features.get("permissions") or [])
    bad_perms = perms & DANGEROUS_PERMS
    if bad_perms:
        add = min(40, 5 * len(bad_perms))
        score += add
        reasons.append(Reason(code="dangerous_permissions", detail=f"Requests {len(bad_perms)} dangerous permissions: {', '.join(bad_perms)} (+{add})"))
    urls = features.get("urls") or []
    if urls:
        add = min(20, 2 * len(urls))
        score += add
        reasons.append(Reason(code="embedded_urls", detail=f"Contains {len(urls)} embedded URL(s) in resources (+{add})"))
        s_tld = tld_score(urls)
        if s_tld:
            score += s_tld
            reasons.append(Reason(code="suspicious_tlds", detail=f"URLs include suspicious TLDs (+{s_tld})"))
    app_name = features.get("app_name")
    pkg = features.get("package") or ""
    if pkg and any(pkg.startswith(k.split(".")[0]) for k in bank_packages) and app_name:
        sim = name_similarity_score(app_name, bank_names)
        if sim < 60:
            score += 15
            reasons.append(Reason(code="pkg_name_mismatch", detail=f"Bank-like package prefix but name similarity low ({sim:.1f}) (+15)"))
    if "android.permission.BIND_ACCESSIBILITY_SERVICE" in perms:
        score += 15
        reasons.append(Reason(code="accessibility", detail="Requests Accessibility Service (used in overlay/credential theft) (+15)"))
    if "android.permission.SYSTEM_ALERT_WINDOW" in perms:
        score += 10
        reasons.append(Reason(code="overlay", detail="Can draw over other apps (overlay attacks) (+10)"))
    sms_perms = {"android.permission.READ_SMS", "android.permission.RECEIVE_SMS", "android.permission.SEND_SMS"}
    if perms & sms_perms:
        score += 10
        reasons.append(Reason(code="otp_capture", detail="Requests SMS permissions (OTP capture risk) (+10)"))
    score = max(0.0, min(100.0, score))
    if score >= 70:
        verdict = "MALICIOUS"
    elif score >= 40:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"
    sim = name_similarity_score(app_name, bank_names) if app_name else 0.0
    reasons.insert(0, Reason(code="name_similarity", detail=f"App name similarity to official bank apps: {sim:.1f}/100"))
    return score, reasons


def model_predict_probability(features: Dict[str, Any]) -> Optional[float]:
    """Uses a machine learning model to predict a malicious probability."""
    if not JOBLIB_AVAILABLE:
        return None
    model_path = os.path.join(MODEL_DIR, "model.joblib")
    if not os.path.exists(model_path):
        return None
    try:
        model = joblib.load(model_path)
    except Exception:
        return None
    perms = set(features.get("permissions") or [])
    vec = [
        len(perms & DANGEROUS_PERMS),
        len(features.get("urls") or []),
        1 if "android.permission.BIND_ACCESSIBILITY_SERVICE" in perms else 0,
        1 if "android.permission.SYSTEM_ALERT_WINDOW" in perms else 0,
    ]
    try:
        if hasattr(model, "predict_proba"):
            proba = float(model.predict_proba([vec])[0][1])  # type: ignore
        else:
            d = float(model.decision_function([vec])[0])  # type: ignore
            proba = 1.0 / (1.0 + math.exp(-d))
        return proba
    except Exception:
        return None


# -----------------------------
# BACKEND: Routes
# These are the API endpoints for the FastAPI backend.
# The Streamlit frontend sends requests to these endpoints.
# -----------------------------
@app.get("/health")
def health():
    """Health check endpoint to ensure the backend is running."""
    return {"ok": True, "androguard": ANDROGUARD_AVAILABLE, "apkutils": APKUTILS_AVAILABLE}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_apk(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Analyzes an uploaded APK file and returns a security report."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        zipfile.ZipFile(io.BytesIO(content)).testzip()
    except Exception:
        raise HTTPException(status_code=400, detail="File is not a valid APK/ZIP archive")

    digest = sha256_bytes(content)
    existing = db.query(Report).filter(Report.sha256 == digest).first()
    if existing:
        existing = cast(Report, existing)
        return AnalysisResult(
            sha256=existing.sha256,
            filename=existing.filename,
            size_bytes=existing.size_bytes,
            score=existing.score,
            verdict=existing.verdict,
            reasons=[Reason(**r) for r in json.loads(existing.reasons)],
            features=json.loads(existing.features),
            created_at=existing.created_at,
        )

    features = extract_features(content)
    banks = db.query(BankRef).filter(BankRef.official == True).all()
    bank_names = [b.name for b in banks]
    bank_packages = [b.package for b in banks]

    h_score, reasons = compute_heuristic_score(features, bank_names, bank_packages)
    proba = model_predict_probability(features)
    if proba is not None:
        ml_score = float(proba * 100)
        reasons.append(Reason(code="ml_probability", detail=f"ML model risk probability: {ml_score:.1f}/100"))
        score = 0.7 * ml_score + 0.3 * h_score
    else:
        score = h_score

    verdict = "SAFE"
    if score >= 70:
        verdict = "MALICIOUS"
    elif score >= 40:
        verdict = "SUSPICIOUS"

    safe_name = os.path.basename(file.filename or f"upload_{int(time.time())}.apk")
    out_path = os.path.join(UPLOAD_DIR, f"{digest}.apk")
    with open(out_path, "wb") as f:
        f.write(content)

    report = Report(
        filename=safe_name,
        sha256=digest,
        size_bytes=len(content),
        verdict=verdict,
        score=float(score),
        reasons=json.dumps([r.dict() for r in reasons]),
        features=json.dumps(features),
        created_at=dt.datetime.utcnow(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return AnalysisResult(**report.dict())


@app.get("/reports", response_model=List[AnalysisResult])
def list_reports(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """Retrieves a list of recent analysis reports."""
    rows = db.query(Report).order_by(desc(Report.created_at)).limit(limit).all()
    out: List[AnalysisResult] = []
    for r in cast(List[Report], rows):
        data = r.__dict__
        data["reasons"] = [Reason(**x) for x in json.loads(data["reasons"])]
        data["features"] = json.loads(data["features"])
        out.append(AnalysisResult(**data))
    return out


@app.get("/reports/{report_id}", response_model=AnalysisResult)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Retrieves a single report by its ID."""
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    r = cast(Report, r)
    data = r.__dict__
    data["reasons"] = [Reason(**x) for x in json.loads(data["reasons"])]
    data["features"] = json.loads(data["features"])
    return AnalysisResult(**data)


@app.get("/reports/sha/{sha256}", response_model=AnalysisResult)
def get_report_by_sha(sha256: str, db: Session = Depends(get_db)):
    """Retrieves a single report by its SHA256 hash."""
    r = db.query(Report).filter(Report.sha256 == sha256).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    r = cast(Report, r)
    data = r.__dict__
    data["reasons"] = [Reason(**x) for x in json.loads(data["reasons"])]
    data["features"] = json.loads(data["features"])
    return AnalysisResult(**data)


@app.get("/banks", response_model=List[BankOut])
def list_banks(db: Session = Depends(get_db)):
    """Lists all official bank references in the database."""
    rows = db.query(BankRef).order_by(asc(BankRef.name)).all()
    return [BankOut(id=r.id, name=r.name, package=r.package, official=r.official) for r in cast(List[BankRef], rows)]


@app.post("/banks", response_model=BankOut)
def add_bank(bank: BankIn, db: Session = Depends(get_db)):
    """Adds a new bank reference to the database."""
    row = BankRef(name=bank.name, package=bank.package, official=bank.official)
    db.add(row)
    db.commit()
    db.refresh(row)
    row = cast(BankRef, row)
    return BankOut(id=row.id, name=row.name, package=row.package, official=row.official)


@app.delete("/banks/{bank_id}")
def delete_bank(bank_id: int, db: Session = Depends(get_db)):
    """Deletes a bank reference by its ID."""
    row = db.query(BankRef).filter(BankRef.id == bank_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Bank not found")
    db.delete(row)
    db.commit()
    return {"deleted": bank_id}


# -----------------------------
# FRONTEND: Streamlit App
# This section defines the entire Streamlit frontend application.
# It uses the `requests` library to communicate with the FastAPI backend.
# -----------------------------
def run_streamlit_app():
    # This URL connects the frontend to the FastAPI backend running in a separate process.
    BACKEND_URL = "http://127.0.0.1:8000"
    
    st.set_page_config(
        page_title="Fake Banking App Detector",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    def display_analysis_result(result):
        """Displays the formatted analysis result."""
        st.header(f"Analysis Report for '{result['filename']}'")
        st.metric("SHA256 Hash", result['sha256'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Verdict", result['verdict'])
        col2.metric("Score", f"{result['score']:.2f}")
        col3.metric("Size", f"{result['size_bytes'] / 1024 / 1024:.2f} MB")

        st.subheader("Reasons for Verdict")
        with st.expander("Show Details"):
            for reason in result['reasons']:
                st.markdown(f"- **{reason['code'].replace('_', ' ').title()}**: {reason['detail']}")

        st.subheader("Extracted Features")
        with st.expander("Show Raw Data"):
            st.json(result['features'])

        st.subheader("Features Summary")
        with st.expander("Show Summary"):
            features = result['features']
            st.markdown(f"- **App Name**: {features['app_name']}")
            st.markdown(f"- **Package Name**: {features['package']}")
            st.markdown(f"- **Permissions**: {len(features['permissions'])} permissions found.")
            st.markdown(f"- **URLs**: {len(features['urls'])} URLs found.")
            st.markdown(f"- **Activities**: {len(features['activities'])} activities found.")
            st.markdown(f"- **Services**: {len(features['services'])} services found.")

    st.title("Fake Banking App Detector")
    st.markdown("Use this tool to analyze an APK file and detect if it is a fake banking application.")
    
    # Tabs for the main UI sections
    tab1, tab2, tab3 = st.tabs(["Analyze APK", "Recent Reports", "Manage Banks"])

    with tab1:
        # UI for file upload and analysis
        st.subheader("Upload an APK file")
        uploaded_file = st.file_uploader("Choose an APK file", type=['apk'])

        if uploaded_file is not None:
            with st.spinner("Analyzing APK... This may take a moment."):
                files = {'file': uploaded_file.getvalue()}
                try:
                    # Connects to the /analyze endpoint of the FastAPI backend
                    response = requests.post(f"{BACKEND_URL}/analyze", files=files, timeout=60)
                    if response.status_code == 200:
                        analysis_result = response.json()
                        display_analysis_result(analysis_result)
                    else:
                        st.error(f"Error analyzing file: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend. Please check if the FastAPI server is running at {BACKEND_URL}.")
                    st.exception(e)

    with tab2:
        # UI to view recent reports
        st.subheader("Recent Analysis Reports")
        if st.button("Refresh Reports"):
            st.session_state.reports_data = None
        
        if 'reports_data' not in st.session_state or st.session_state.reports_data is None:
            try:
                # Connects to the /reports endpoint of the FastAPI backend
                response = requests.get(f"{BACKEND_URL}/reports")
                if response.status_code == 200:
                    st.session_state.reports_data = response.json()
                else:
                    st.error(f"Error fetching reports: {response.text}")
                    st.session_state.reports_data = []
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the backend at {BACKEND_URL}.")
                st.session_state.reports_data = []

        if st.session_state.reports_data:
            df = st.session_state.reports_data
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No reports found.")

    with tab3:
        # UI to manage bank references
        st.subheader("Official Bank References")
        
        try:
            # Connects to the /banks endpoint of the FastAPI backend
            banks_response = requests.get(f"{BACKEND_URL}/banks")
            if banks_response.status_code == 200:
                banks = banks_response.json()
                st.write("Currently Tracked Banks:")
                if banks:
                    st.dataframe(banks, use_container_width=True)
                else:
                    st.info("No banks in the database.")
            else:
                st.error(f"Error fetching banks: {banks_response.text}")
        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend to fetch bank list.")

        st.markdown("---")
        st.subheader("Add a New Bank Reference")
        with st.form("add_bank_form"):
            new_name = st.text_input("Bank Name", placeholder="e.g., Bank of America")
            new_package = st.text_input("Package Name", placeholder="e.g., com.bofa.app")
            new_official = st.checkbox("Is Official?", value=True)
            submit_button = st.form_submit_button(label="Add Bank")

        if submit_button:
            if not new_name or not new_package:
                st.warning("Please fill in both name and package.")
            else:
                bank_data = {"name": new_name, "package": new_package, "official": new_official}
                try:
                    # Connects to the /banks POST endpoint of the FastAPI backend
                    response = requests.post(f"{BACKEND_URL}/banks", json=bank_data)
                    if response.status_code == 200:
                        st.success("Bank added successfully!")
                        st.rerun()  # The corrected line to refresh the page
                    else:
                        st.error(f"Failed to add bank: {response.text}")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend to add bank.")


def run_fastapi_server():
    """Starts the Uvicorn server for the FastAPI backend."""
    import uvicorn
    uvicorn.run("final_app:app", host="127.0.0.1", port=8000, log_level="info", reload=False)


if __name__ == "__main__":
    if multiprocessing.current_process().name == 'MainProcess':
        # This part of the code serves as a launcher to run both applications simultaneously.
        # It creates a temporary file to launch the Streamlit app.
        streamlit_script_content = """
import streamlit as st
import requests
import json
from final_app import run_streamlit_app

if __name__ == '__main__':
    run_streamlit_app()
"""
        with open("streamlit_launcher.py", "w") as f:
            f.write(streamlit_script_content)

        # Start the FastAPI process in a new thread
        fastapi_proc = multiprocessing.Process(target=run_fastapi_server)
        fastapi_proc.start()

        # Start the Streamlit process via a subprocess call
        streamlit_proc = subprocess.Popen(["streamlit", "run", "streamlit_launcher.py"])
        
        try:
            # Keep the main process alive until a KeyboardInterrupt (Ctrl+C)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down servers...")
        finally:
            fastapi_proc.terminate()
            streamlit_proc.terminate()
            os.remove("streamlit_launcher.py")
