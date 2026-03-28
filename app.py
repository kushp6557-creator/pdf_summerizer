import os
import streamlit as st
import PyPDF2
import re
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root, "api.env")
load_dotenv(dotenv_path)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "sshleifer/distilbart-cnn-12-6"

st.set_page_config(
    page_title="Luminary PDF Summarizer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap');

:root {
  --bg:          #0a0b0e;
  --bg-card:     #111318;
  --bg-lift:     #181c24;
  --border:      #1f2330;
  --border-hi:   #2e3447;
  --text:        #e8eaf0;
  --text-soft:   #6b7285;
  --text-dim:    #3d4355;
  --accent:      #7c6af7;
  --accent-lt:   #a89bfa;
  --accent-glow: rgba(124,106,247,.18);
  --cyan:        #3ecfcf;
  --cyan-dim:    rgba(62,207,207,.12);
  --gold:        #e8b96a;
  --gold-dim:    rgba(232,185,106,.1);
  --radius:      14px;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.8rem 2.2rem 5rem !important; max-width: 980px !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 99px; }

/* Hero */
.hero { display:flex; align-items:center; gap:1.2rem; margin-bottom:2.4rem; animation:fadeUp .6s cubic-bezier(.22,1,.36,1) both; }
.hero-icon {
  width:58px; height:58px; border-radius:16px;
  background: linear-gradient(135deg, #7c6af7 0%, #5b4fcf 100%);
  display:flex; align-items:center; justify-content:center; font-size:24px; flex-shrink:0;
  box-shadow: 0 0 0 1px rgba(124,106,247,.4), 0 8px 30px rgba(124,106,247,.35);
}
.hero-text h1 {
  font-family:'Syne',sans-serif !important; font-size:2rem !important; font-weight:700 !important;
  letter-spacing:-.5px; margin:0 0 .2rem !important;
  background:linear-gradient(90deg,#e8eaf0 0%,#a89bfa 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hero-text p { font-size:.9rem; color:var(--text-soft); margin:0; letter-spacing:.01em; }

.divider {
  height:1px; margin:0 0 2.6rem;
  background:linear-gradient(90deg,transparent,var(--accent),var(--cyan),transparent);
  opacity:.3; animation:fadeIn .8s .25s ease both;
}

/* Upload */
[data-testid="stFileUploadDropzone"] {
  border:1.5px dashed var(--border-hi) !important;
  border-radius:var(--radius) !important;
  background:var(--bg-card) !important;
  padding:2.8rem !important;
  transition:background .3s,border-color .3s;
}
[data-testid="stFileUploadDropzone"]:hover {
  background:var(--bg-lift) !important;
  border-color:var(--accent) !important;
  box-shadow:0 0 0 3px var(--accent-glow);
}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] small { color:var(--text-soft) !important; font-size:.88rem !important; }
[data-testid="stFileUploadDropzone"] button {
  background:var(--bg-lift) !important; color:var(--accent-lt) !important;
  border:1px solid var(--border-hi) !important; border-radius:8px !important;
  font-family:'Inter',sans-serif !important; font-size:.82rem !important;
}

/* Stat cards */
.stat-row { display:flex; gap:14px; margin:1.8rem 0; flex-wrap:wrap; }
.stat-card {
  flex:1; min-width:130px; background:var(--bg-card); border:1px solid var(--border);
  border-radius:var(--radius); padding:1.1rem 1.3rem; position:relative; overflow:hidden;
  animation:scaleIn .45s cubic-bezier(.22,1,.36,1) both;
}
.stat-card::after {
  content:''; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent,var(--accent-lt),transparent); opacity:.2;
}
.stat-card .label { font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; color:var(--text-soft); margin-bottom:.4rem; font-weight:500; }
.stat-card .value {
  font-family:'Syne',sans-serif; font-size:1.7rem; font-weight:700; line-height:1;
  background:linear-gradient(135deg,#e8eaf0,#a89bfa);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.stat-card:nth-child(1){animation-delay:.06s}
.stat-card:nth-child(2){animation-delay:.14s}
.stat-card:nth-child(3){animation-delay:.22s}

/* Summary card */
.summary-card {
  background:var(--bg-card); border-radius:var(--radius); border:1px solid var(--border);
  padding:1.8rem 2rem; position:relative; overflow:hidden;
  animation:fadeUp .5s .1s cubic-bezier(.22,1,.36,1) both;
}
.summary-card::before {
  content:''; position:absolute; top:0; left:0; width:3px; height:100%;
  background:linear-gradient(180deg,var(--accent) 0%,var(--cyan) 100%);
}
.summary-card::after {
  content:''; position:absolute; top:-60px; right:-60px; width:200px; height:200px;
  border-radius:50%; background:var(--accent-glow); filter:blur(40px); pointer-events:none;
}
.summary-card h3 {
  font-family:'Syne',sans-serif !important; font-size:.9rem !important; font-weight:600 !important;
  margin:0 0 1rem !important; color:var(--accent-lt) !important;
  text-transform:uppercase; letter-spacing:.1em;
}
.summary-card p { line-height:1.85; color:var(--text); font-size:.95rem; margin:0; }

/* Preview */
.preview-card {
  background:var(--bg-card); border-radius:var(--radius); padding:1.3rem 1.6rem;
  font-size:.85rem; line-height:1.75; color:var(--text-soft); border:1px solid var(--border);
  max-height:210px; overflow-y:auto; animation:fadeUp .4s ease both;
}

/* Badges */
.badge { display:inline-flex; align-items:center; gap:5px; padding:4px 11px; border-radius:20px; font-size:.72rem; font-weight:500; margin-right:6px; letter-spacing:.02em; }
.badge-accent { background:rgba(124,106,247,.15); color:var(--accent-lt); border:1px solid rgba(124,106,247,.25); }
.badge-cyan   { background:var(--cyan-dim);       color:var(--cyan);      border:1px solid rgba(62,207,207,.2); }
.badge-gold   { background:var(--gold-dim);       color:var(--gold);      border:1px solid rgba(232,185,106,.2); }
.badge-muted  { background:var(--bg-lift);        color:var(--text-soft); border:1px solid var(--border); }

/* Download button */
.stDownloadButton>button {
  background:linear-gradient(135deg,#7c6af7 0%,#5b4fcf 100%) !important;
  color:#fff !important; border:none !important; border-radius:10px !important;
  padding:.6rem 1.5rem !important; font-family:'Inter',sans-serif !important;
  font-weight:500 !important; font-size:.88rem !important;
  box-shadow:0 4px 20px rgba(124,106,247,.35) !important;
  transition:opacity .2s,box-shadow .2s,transform .15s !important;
}
.stDownloadButton>button:hover { opacity:.9; box-shadow:0 6px 28px rgba(124,106,247,.5) !important; transform:translateY(-1px); }

/* Spinner & progress */
.stSpinner>div { border-top-color:var(--accent) !important; }
.stProgress>div { background:var(--bg-lift) !important; border-radius:99px !important; height:5px !important; }
.stProgress>div>div { background:linear-gradient(90deg,var(--accent),var(--cyan)) !important; border-radius:99px !important; }

/* Alerts & expander */
[data-testid="stAlert"] { border-radius:var(--radius) !important; font-size:.88rem !important; background:var(--bg-card) !important; border:1px solid var(--border-hi) !important; }
[data-testid="stExpander"] { border:1px solid var(--border) !important; border-radius:var(--radius) !important; background:var(--bg-card) !important; }
[data-testid="stExpander"] summary { color:var(--text-soft) !important; font-size:.88rem !important; }

/* Sidebar */
[data-testid="stSidebar"] { background:var(--bg-card) !important; border-right:1px solid var(--border) !important; }

/* Labels & misc */
.section-label { font-size:.7rem; text-transform:uppercase; letter-spacing:.12em; color:var(--text-dim); font-weight:500; margin-bottom:.7rem; }
hr { border:none !important; border-top:1px solid var(--border) !important; margin:1.8rem 0 !important; }
.idle-wrap { text-align:center; padding:4rem 0 2rem; animation:fadeIn .9s ease both; }
.idle-icon {
  width:72px; height:72px; border-radius:20px; border:1px solid var(--border-hi);
  background:var(--bg-card); display:inline-flex; align-items:center; justify-content:center;
  font-size:30px; margin-bottom:1rem;
}
.idle-text { color:var(--text-dim); font-size:.88rem; }

@keyframes fadeUp  { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn  { from{opacity:0} to{opacity:1} }
@keyframes scaleIn { from{opacity:0;transform:scale(.88)} to{opacity:1;transform:scale(1)} }
</style>
""", unsafe_allow_html=True)




# ─── Helpers ────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_remote_client():
    if not HF_API_TOKEN:
        return None
    try:
        from huggingface_hub import InferenceClient
        return InferenceClient(token=HF_API_TOKEN)
    except Exception:
        return None

@st.cache_resource
def load_local_model():
    if load_remote_client() is not None:
        return None
    try:
        from transformers import pipeline
        return pipeline("text-generation", model=HF_MODEL)
    except Exception:
        return None

def extract_text(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
    except Exception as e:
        raise ValueError(f"Unable to read PDF: {e}")
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        except:
            continue
    return text

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, chunk_size=800):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_text(text, progress_bar=None):
    if not text.strip():
        return ""
    remote_client = load_remote_client()
    summarizer    = load_local_model()
    chunks        = chunk_text(text)
    summary_parts = []

    def summarize_chunk_remote(chunk):
        prompt = f"Summarize the following text in plain text without markdown formatting:\n\n{chunk}"
        response = remote_client.summarization(prompt, model=HF_MODEL, clean_up_tokenization_spaces=True)
        if hasattr(response, "summary_text"): return response.summary_text
        if isinstance(response, dict): return response.get("generated_text") or response.get("summary_text") or ""
        elif isinstance(response, str): return response
        elif isinstance(response, list): return response[0] if response else ""
        return ""

    def summarize_chunk_local(chunk):
        prompt = f"Summarize the following text in plain text without markdown formatting:\n\n{chunk}"
        result = summarizer(prompt, max_new_tokens=120, do_sample=False, num_return_sequences=1)
        return result[0] if isinstance(result, list) else result

    use_remote = remote_client is not None
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        try:
            if use_remote:
                parsed = summarize_chunk_remote(chunk)
            else:
                if not summarizer:
                    st.warning("No model available. Please set HF_API_TOKEN.")
                    return ""
                parsed = summarize_chunk_local(chunk)
            if parsed:
                if isinstance(parsed, dict):
                    parsed = parsed.get("generated_text") or parsed.get("summary_text") or ""
                if isinstance(parsed, str) and parsed.lower().startswith("summarize:"):
                    parsed = parsed[len("summarize:"):].strip()
                if parsed:
                    summary_parts.append(parsed.strip())
        except Exception as e:
            st.warning(f"Chunk {i+1} skipped: {e}")
        if progress_bar:
            progress_bar.progress((i + 1) / total)

    return " ".join(summary_parts).strip()



# ─── UI ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">✦</div>
  <div class="hero-text">
    <h1>PDF Summarizer</h1>
    <p>Drop any PDF — receive a concise, professional plain-text summary.</p>
  </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

remote_client = load_remote_client()
api_label = "✦ Remote API active" if remote_client else "⚐ Local model"
api_cls   = "badge-accent" if remote_client else "badge-gold"
token_mark = "✔" if HF_API_TOKEN else "✘"

st.markdown(
    f'<span class="badge {api_cls}">{api_label}</span>'
    f'<span class="badge badge-muted">{HF_MODEL}</span>'
    f'<span class="badge badge-cyan">Token {token_mark}</span>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<p class="section-label">Upload document</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload PDF", 
    type=["pdf"], 
    label_visibility="collapsed"
)

if uploaded_file is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    size_kb = uploaded_file.size / 1024
    st.markdown(
        f'<span class="badge badge-accent">📄 {uploaded_file.name}</span>'
        f'<span class="badge badge-muted">{size_kb:.1f} KB</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("Reading PDF…"):
        try:
            text = extract_text(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
            text = ""

    if not text.strip():
        st.error("No readable text found. Please upload a text-based PDF.")
    else:
        cleaned = clean_text(text)
        words   = len(cleaned.split())
        chars   = len(cleaned)
        chunks  = len(chunk_text(cleaned))

        st.markdown(
            f"""<div class="stat-row">
              <div class="stat-card"><div class="label">Characters</div><div class="value">{chars:,}</div></div>
              <div class="stat-card"><div class="label">Words</div><div class="value">{words:,}</div></div>
              <div class="stat-card"><div class="label">Chunks</div><div class="value">{chunks}</div></div>
            </div>""",
            unsafe_allow_html=True,
        )

        with st.expander("Preview extracted text"):
            st.markdown(
                f'<div class="preview-card">{cleaned[:2500]}{"…" if chars > 2500 else ""}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        progress_bar = st.progress(0, text="Summarising…")
        summary = summarize_text(cleaned, progress_bar)
        progress_bar.empty()

        if not summary:
            st.warning("Could not generate a summary. Check your API token or model setup.")
        else:
            st.success("Summary ready")
            st.markdown(
                f'<div class="summary-card"><h3>✦ &nbsp;Summary</h3><p>{summary}</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            dl_col, tip_col = st.columns([1, 3])
            with dl_col:
                st.download_button(
                    label="⬇  Download summary",
                    data=summary,
                    file_name=f"summary_{uploaded_file.name.replace('.pdf','')}.txt",
                    mime="text/plain",
                )
            with tip_col:
                st.markdown(
                    '<p style="font-size:.82rem;color:#3d4355;margin-top:.65rem;">'
                    'Tip: text-based PDFs yield the sharpest results.</p>',
                    unsafe_allow_html=True,
                )
else:
    st.markdown("""
    <div class="idle-wrap">
      <div class="idle-icon">📄</div>
      <p class="idle-text">No file selected yet</p>
    </div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings & Tips")
    st.markdown("---")
    st.markdown(
        "**API Token**  \n"
        f"{'✅ Loaded — remote inference active.' if HF_API_TOKEN else '❌ Not set — using local fallback.'}"
    )
    st.markdown(f"**Model**  \n`{HF_MODEL}`")
    st.markdown("---")
    st.markdown(
        "**Usage tips**\n"
        "- Keep uploads ≤ 200 MB\n"
        "- Text-based PDFs extract best\n"
        "- Add `HF_API_TOKEN` to `api.env` for remote inference\n"
        "- Longer docs take more time — be patient!"
    )
    