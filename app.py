# ╔══════════════════════════════════════════════════════════════════════╗
# ║   EXAM SAMACHAR  v10.0  — Newspaper UI Edition                     ║
# ║                                                                      ║
# ║  NEW IN v10.0:                                                      ║
# ║   • 🗞 Full broadsheet newspaper masthead (horizontal title)        ║
# ║   • 🎞 Smooth marquee — all 15 major Indian competitive exams       ║
# ║   • 📂 History modal — click to preview & reopen any upload         ║
# ║   • 🗂 Tab navigation (Analysis / MCQs / Raw JSON / OCR Text)       ║
# ║   • 🎨 Playfair + Source Serif editorial typography                 ║
# ║   • 📰 Broadsheet color palette (cream, rust, deep ink)            ║
# ║   • 🔢 Numbered key points (not plain dots)                         ║
# ║   • 📊 Two-column entity layout                                     ║
# ║   • 🃏 MCQ cards with left-accent hover border                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

import io, time, json, base64, ssl, certifi, requests, os, datetime
import streamlit as st
import numpy as np
from PIL import Image
import fitz
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()



ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

try:
    import pytesseract; TESSERACT_OK = True
except ImportError:
    TESSERACT_OK = False

try:
    import easyocr; EASYOCR_OK = True
except ImportError:
    EASYOCR_OK = False

try:
    from textblob import TextBlob; TEXTBLOB_OK = True
except ImportError:
    TEXTBLOB_OK = False


# ════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Exam Samachar",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════
# CSS — Broadsheet Newspaper Editorial
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,300;1,8..60,400&family=JetBrains+Mono:wght@400;600&display=swap');

/* ══ ROOT TOKENS ══ */
:root{
  --cream:#faf7f0; --cream2:#f0ebe0; --cream3:#e8e0d0;
  --white:#ffffff;
  --ink:#1a1208; --ink2:#3d2f1a; --ink3:#8a7a6a;
  --col:#c0bab0; --col2:#a09890;
  --rust:#b5410a; --rust2:#8c3108;
  --rust-bg:#fdf0e8; --rust-bdr:rgba(181,65,10,0.2);
  --forest:#1a5c3a; --forest-bg:#eaf4ee; --forest-bdr:rgba(26,92,58,0.2);
  --navy:#14355a; --navy-bg:#e8f0f8; --navy-bdr:rgba(20,53,90,0.2);
  --gold:#c89a1a; --gold-bg:#faf3db; --gold-bdr:rgba(200,154,26,0.2);
  --sh:0 1px 4px rgba(0,0,0,0.06),0 2px 8px rgba(0,0,0,0.04);
  --sh2:0 3px 16px rgba(0,0,0,0.1),0 1px 4px rgba(0,0,0,0.06);
}

/* ══ BASE ══ */
html,body,[class*="css"]{
  font-family:'Source Serif 4',Georgia,serif !important;
  background:var(--cream) !important;
  color:var(--ink) !important;
}
.stApp{background:var(--cream) !important;}
.block-container{padding-top:0 !important; padding-left:1rem !important; padding-right:1rem !important;}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"]{
  background:var(--white) !important;
  border-right:1px solid var(--col) !important;
}
[data-testid="stSidebar"] *{color:var(--ink) !important; font-family:'Source Serif 4',serif !important;}
[data-testid="stSidebar"] .stSelectbox label{display:none;}

/* ══ SELECTBOX ══ */
[data-testid="stSelectbox"]>div>div{
  background:var(--white) !important;
  border:1px solid var(--col) !important;
  border-radius:4px !important;
  font-family:'Source Serif 4',serif !important;
}
[data-baseweb="select"]{background:var(--white) !important;}
[data-baseweb="popover"]{
  background:var(--white) !important;
  border:1px solid var(--col) !important;
  border-radius:4px !important;
  box-shadow:var(--sh2) !important;
}
[data-baseweb="menu"] li:hover{background:var(--cream2) !important;}

/* ══ BUTTONS ══ */
.stButton>button{
  background:var(--ink) !important;
  color:var(--cream) !important;
  border:none !important;
  border-bottom:3px solid var(--rust) !important;
  border-radius:4px !important;
  font-family:'Playfair Display',serif !important;
  font-weight:700 !important;
  font-size:0.88rem !important;
  padding:0.52rem 1.4rem !important;
  transition:all 0.18s !important;
  letter-spacing:0.01em !important;
}
.stButton>button:hover{background:var(--rust) !important; border-bottom-color:var(--rust2) !important;}

/* ══ METRICS ══ */
[data-testid="metric-container"]{
  background:var(--white) !important;
  border:1px solid var(--col) !important;
  border-bottom:3px solid var(--col) !important;
  border-radius:4px !important;
  padding:0.75rem 0.9rem !important;
  box-shadow:var(--sh) !important;
}
[data-testid="stMetricValue"]{
  color:var(--rust) !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:1.15rem !important;
  font-weight:600 !important;
}
[data-testid="stMetricLabel"]{
  color:var(--ink3) !important;
  font-size:0.65rem !important;
  font-family:'JetBrains Mono',monospace !important;
  text-transform:uppercase !important;
  letter-spacing:0.08em !important;
}

/* ══ EXPANDER ══ */
[data-testid="stExpander"]{
  background:var(--white) !important;
  border:1px solid var(--col) !important;
  border-radius:4px !important;
  box-shadow:var(--sh) !important;
}
[data-testid="stExpander"] summary{
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.75rem !important;
  font-weight:600 !important;
  color:var(--ink2) !important;
}

/* ══ FILE UPLOAD ══ */
[data-testid="stFileUploadDropzone"]{
  background:var(--white) !important;
  border:2px dashed var(--col2) !important;
  border-radius:6px !important;
  transition:border-color 0.18s !important;
}
[data-testid="stFileUploadDropzone"]:hover{border-color:var(--rust) !important;}

/* ══ SPINNER ══ */
.stSpinner>div{border-top-color:var(--rust) !important;}

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--cream2);}
::-webkit-scrollbar-thumb{background:var(--col);border-radius:2px;}

/* ══ TEXTAREA ══ */
.stTextArea textarea{
  background:var(--cream2) !important;
  border:1px solid var(--col) !important;
  color:var(--ink2) !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.74rem !important;
  border-radius:4px !important;
}

/* ══ TOP BAR ══ */
.topbar{
  background:var(--ink); color:var(--cream);
  padding:0 1.4rem;
  display:flex; align-items:center; justify-content:space-between;
  height:38px; border-bottom:3px solid var(--rust);
  margin:-1rem -1rem 0; /* bleed to edges */
}
.topbar-date{font-family:'JetBrains Mono',monospace;font-size:0.63rem;color:#a09888;letter-spacing:0.07em;}
.topbar-tag{font-family:'JetBrains Mono',monospace;font-size:0.63rem;color:var(--rust);
  background:rgba(181,65,10,0.15);padding:2px 8px;border-radius:2px;letter-spacing:0.06em;font-weight:600;}
.topbar-center{font-size:0.62rem;color:#a09888;font-style:italic;font-family:'Source Serif 4',serif;}

/* ══ MASTHEAD ══ */
.masthead-wrap{
  background:var(--cream); padding:1.2rem 0 0;
  border-bottom:4px double var(--col2);
  margin:0 -1rem; padding-left:1.4rem; padding-right:1.4rem;
}
.masthead-inner{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;margin-bottom:0.7rem;}
.masthead-left,.masthead-right{min-width:120px;}
.masthead-right{text-align:right;}
.mh-label{font-family:'JetBrains Mono',monospace;font-size:0.57rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.12em;}
.mh-val{font-family:'Source Serif 4',serif;font-size:0.84rem;color:var(--ink2);margin-top:1px;}
.masthead-center{text-align:center;flex:1;}
.mh-rule{display:flex;align-items:center;gap:0;margin-bottom:3px;}
.mh-line{flex:1;height:1.5px;background:var(--ink);}
.mh-diamond{width:7px;height:7px;background:var(--rust);transform:rotate(45deg);flex-shrink:0;margin:0 6px;}
.newspaper-name{
  font-family:'Playfair Display',serif;
  font-size:clamp(2rem,4vw,3.2rem);
  font-weight:900; color:var(--ink);
  line-height:1; letter-spacing:-1px; white-space:nowrap;
}
.newspaper-name span{color:var(--rust);}
.masthead-tagline{
  font-family:'Source Serif 4',serif;
  font-size:0.72rem; color:var(--ink3);
  letter-spacing:0.22em; text-transform:uppercase;
  text-align:center; padding:4px 0 5px;
  border-top:1px solid var(--col); border-bottom:1px solid var(--col);
  margin:5px 0 0.7rem;
}
.masthead-pills{display:flex;justify-content:center;gap:5px;padding-bottom:0.7rem;flex-wrap:wrap;}
.mpill{font-family:'JetBrains Mono',monospace;font-size:0.59rem;padding:2px 8px;border-radius:2px;letter-spacing:0.03em;font-weight:600;}
.mpill.rust{background:var(--rust-bg);border:1px solid var(--rust-bdr);color:var(--rust);}
.mpill.forest{background:var(--forest-bg);border:1px solid var(--forest-bdr);color:var(--forest);}
.mpill.navy{background:var(--navy-bg);border:1px solid var(--navy-bdr);color:var(--navy);}
.mpill.gold{background:var(--gold-bg);border:1px solid var(--gold-bdr);color:#8a6500;}
.mpill.ink{background:rgba(26,18,8,0.07);border:1px solid rgba(26,18,8,0.12);color:var(--ink2);}

/* ══ TICKER ══ */
.ticker-wrap{
  background:var(--ink); border-bottom:3px solid var(--rust);
  overflow:hidden; height:34px; display:flex; align-items:center;
  margin:0 -1rem;
}
.ticker-label{
  background:var(--rust); color:#fff;
  font-family:'JetBrains Mono',monospace; font-size:0.63rem; font-weight:600;
  padding:0 14px; height:100%; display:flex; align-items:center;
  white-space:nowrap; letter-spacing:0.08em; flex-shrink:0;
}
.ticker-scroll{overflow:hidden;flex:1;}
.ticker-track{
  display:inline-flex; animation:exam-scroll 42s linear infinite;
  white-space:nowrap; align-items:center; height:34px;
}
.ticker-track:hover{animation-play-state:paused;}
@keyframes exam-scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ticker-item{
  font-family:'Playfair Display',serif; font-size:0.8rem; font-weight:700;
  color:var(--cream2); white-space:nowrap; padding:0 1.4rem;
  display:flex; align-items:center; gap:6px;
}
.ticker-dot{width:4px;height:4px;border-radius:50%;background:var(--rust);flex-shrink:0;}

/* ══ SIDEBAR LABELS ══ */
.sb-lbl{
  font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:600;
  color:var(--ink3); letter-spacing:0.12em; text-transform:uppercase;
  margin:1rem 0 0.3rem; padding-bottom:4px;
  border-bottom:1px solid var(--col);
  display:flex; align-items:center; gap:6px;
}
.sb-dot{width:5px;height:5px;background:var(--rust);flex-shrink:0;}

/* ══ HISTORY ITEM ══ */
.hist-item{
  background:var(--white); border:1px solid var(--col);
  border-radius:4px; padding:0.5rem 0.65rem;
  margin-bottom:6px; cursor:pointer; transition:all 0.15s;
  display:flex; align-items:flex-start; gap:8px; position:relative;
  overflow:hidden;
}
.hist-item::before{
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:3px; background:var(--rust); opacity:0; transition:opacity 0.15s;
}
.hist-item:hover{border-color:var(--rust); box-shadow:0 2px 8px rgba(181,65,10,0.1);}
.hist-item:hover::before{opacity:1;}
.hist-thumb{
  width:38px; height:38px; border-radius:3px; background:var(--cream2);
  flex-shrink:0; display:flex; align-items:center; justify-content:center;
  border:1px solid var(--col); font-size:17px;
}
.hist-body{flex:1;min-width:0;}
.hist-name{font-size:0.74rem;font-weight:600;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.hist-meta{font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--ink3);margin-top:2px;}
.hist-tag{font-family:'JetBrains Mono',monospace;font-size:0.55rem;padding:1px 5px;border-radius:2px;font-weight:600;flex-shrink:0;}
.hist-tag.pdf{background:var(--rust-bg);border:1px solid var(--rust-bdr);color:var(--rust);}
.hist-tag.img{background:var(--navy-bg);border:1px solid var(--navy-bdr);color:var(--navy);}

/* ══ STATUS TAGS ══ */
.status-ok{display:inline-flex;align-items:center;gap:5px;background:var(--forest-bg);
  border:1px solid var(--forest-bdr);color:var(--forest);
  font-family:'JetBrains Mono',monospace;font-size:0.66rem;padding:2px 8px;border-radius:2px;font-weight:600;}
.status-warn{display:inline-flex;align-items:center;gap:5px;background:var(--rust-bg);
  border:1px solid var(--rust-bdr);color:var(--rust);
  font-family:'JetBrains Mono',monospace;font-size:0.66rem;padding:2px 8px;border-radius:2px;font-weight:600;}
.time-badge{display:inline-flex;align-items:center;gap:4px;background:var(--navy-bg);
  border:1px solid var(--navy-bdr);color:var(--navy);
  font-family:'JetBrains Mono',monospace;font-size:0.65rem;padding:2px 8px;border-radius:2px;font-weight:600;}
.time-badge.fast{background:var(--forest-bg);border-color:var(--forest-bdr);color:var(--forest);}
.time-badge.slow{background:var(--rust-bg);border-color:var(--rust-bdr);color:var(--rust);}

/* ══ PROGRESS BAR ══ */
.progress-bar-wrap{background:var(--col);border-radius:20px;height:5px;overflow:hidden;margin-bottom:0.5rem;}
.progress-bar-fill{background:var(--rust);height:100%;border-radius:20px;transition:width 0.3s ease;}

/* ══ PAGE SEPARATOR ══ */
.page-sep{display:flex;align-items:center;gap:14px;margin:2rem 0 1.4rem;}
.page-sep-line{flex:1;height:1px;background:var(--col2);}
.page-sep-label{
  font-family:'Playfair Display',serif;font-size:0.9rem;font-weight:700;
  color:var(--ink);white-space:nowrap;padding:4px 14px;
  background:var(--white);border:1px solid var(--col);border-radius:2px;
  box-shadow:var(--sh);
}
.page-sep-label span{color:var(--rust);}

/* ══ PAGE CHIPS ══ */
.page-chip{display:inline-flex;align-items:center;gap:5px;font-family:'JetBrains Mono',monospace;font-size:0.65rem;padding:2px 9px;border-radius:2px;font-weight:600;}
.page-chip.done{background:var(--forest-bg);border:1px solid var(--forest-bdr);color:var(--forest);}
.page-chip.pending{background:var(--gold-bg);border:1px solid var(--gold-bdr);color:#8a6500;}

/* ══ ARTICLE MASTHEAD CARD ══ */
.article-masthead{
  background:var(--white);border:1px solid var(--col);
  border-top:4px solid var(--ink);border-radius:0 0 6px 6px;
  padding:1.2rem 1.6rem 1rem;margin-bottom:1rem;
}
.article-kicker{
  font-family:'JetBrains Mono',monospace;font-size:0.61rem;
  color:var(--rust);text-transform:uppercase;letter-spacing:0.14em;font-weight:600;
  margin-bottom:6px;display:flex;align-items:center;gap:8px;
}
.article-kicker::after{content:'';flex:1;height:1px;background:var(--rust-bdr);}
.article-headline{
  font-family:'Playfair Display',serif;font-size:1.65rem;font-weight:900;
  color:var(--ink);line-height:1.25;margin-bottom:0.3rem;
}
.article-deck{
  font-family:'Source Serif 4',serif;font-size:0.93rem;font-style:italic;
  color:var(--ink3);margin-bottom:0.7rem;line-height:1.5;
}
.article-byline{
  display:flex;gap:7px;flex-wrap:wrap;align-items:center;
  border-top:1px solid var(--col);padding-top:0.55rem;
  font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:var(--ink3);
}
.byline-sep{color:var(--col2);}
.byline-tag{padding:1px 7px;border-radius:2px;font-weight:600;}
.byline-tag.pos{background:var(--forest-bg);color:var(--forest);border:1px solid var(--forest-bdr);}
.byline-tag.neg{background:var(--rust-bg);color:var(--rust);border:1px solid var(--rust-bdr);}
.byline-tag.neu{background:var(--gold-bg);color:#8a6500;border:1px solid var(--gold-bdr);}

/* ══ SECTION HEADS ══ */
.sec-head{
  font-family:'JetBrains Mono',monospace;font-size:0.59rem;font-weight:600;
  color:var(--rust);text-transform:uppercase;letter-spacing:0.14em;
  display:flex;align-items:center;gap:10px;margin:1.3rem 0 0.65rem;
}
.sec-head::after{content:'';flex:1;height:1px;background:var(--col);}

/* ══ TIMING CARD ══ */
.timing-card{background:var(--white);border:1px solid var(--col);border-radius:4px;padding:0.85rem 1.1rem;margin-bottom:1rem;box-shadow:var(--sh);}
.timing-row{display:flex;align-items:center;gap:10px;padding:0.28rem 0;border-bottom:1px solid var(--cream2);}
.timing-row:last-child{border-bottom:none;}
.timing-label{font-size:0.77rem;color:var(--ink3);font-family:'JetBrains Mono',monospace;min-width:170px;}
.timing-bar{flex:1;height:5px;background:var(--cream2);border-radius:3px;overflow:hidden;}
.timing-fill{height:100%;border-radius:3px;transition:width 0.5s ease;}
.timing-val{font-family:'JetBrains Mono',monospace;font-size:0.72rem;font-weight:600;color:var(--ink);min-width:36px;text-align:right;}

/* ══ SUMMARY CARD ══ */
.summary-card{
  background:var(--white);border:1px solid var(--col);
  border-left:4px solid var(--rust);border-radius:4px;
  padding:1.1rem 1.3rem;margin-bottom:1rem;
  font-family:'Source Serif 4',serif;font-size:0.91rem;
  color:var(--ink2);line-height:1.85;box-shadow:var(--sh);
}

/* ══ KEY POINTS ══ */
.kp-card{background:var(--white);border:1px solid var(--col);border-radius:4px;padding:0.65rem 1rem;margin-bottom:1rem;box-shadow:var(--sh);}
.kp-row{display:flex;gap:10px;align-items:flex-start;padding:0.45rem 0;border-bottom:1px solid var(--cream2);}
.kp-row:last-child{border-bottom:none;}
.kp-num{
  font-family:'JetBrains Mono',monospace;font-size:0.64rem;font-weight:600;
  color:var(--cream);background:var(--rust);
  width:20px;height:20px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;margin-top:2px;
}
.kp-text{font-family:'Source Serif 4',serif;font-size:0.87rem;color:var(--ink2);line-height:1.6;}

/* ══ ENTITY CARD ══ */
.ent-card{background:var(--white);border:1px solid var(--col);border-radius:4px;padding:0.75rem 1rem;box-shadow:var(--sh);}
.ent-group{margin-bottom:0.75rem;}
.ent-group:last-child{margin-bottom:0;}
.ent-label{font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px;font-weight:600;}
.ent-chips{display:flex;flex-wrap:wrap;gap:4px;}
.ent-chip{
  background:var(--cream2);border:1px solid var(--col);color:var(--ink2);
  font-family:'Source Serif 4',serif;font-size:0.78rem;padding:2px 8px;border-radius:20px;
  cursor:default;transition:all 0.14s;
}
.ent-chip:hover{background:var(--rust-bg);border-color:var(--rust-bdr);color:var(--rust);}

/* ══ SENTIMENT ══ */
.sent-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:2px;font-weight:600;font-size:0.79rem;font-family:'JetBrains Mono',monospace;}
.sent-badge.positive{background:var(--forest-bg);border:1px solid var(--forest-bdr);color:var(--forest);}
.sent-badge.negative{background:var(--rust-bg);border:1px solid var(--rust-bdr);color:var(--rust);}
.sent-badge.neutral{background:var(--gold-bg);border:1px solid var(--gold-bdr);color:#8a6500;}
.sent-reason{font-size:0.83rem;color:var(--ink3);font-style:italic;font-family:'Source Serif 4',serif;}

/* ══ NAV TABS ══ */
.nav-tabs{display:flex;gap:0;border-bottom:2px solid var(--col);margin-bottom:1.1rem;}
.nav-tab{
  font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:600;
  padding:0.48rem 1.1rem;cursor:pointer;color:var(--ink3);
  border-bottom:2px solid transparent;margin-bottom:-2px;
  transition:all 0.15s;letter-spacing:0.05em;text-transform:uppercase;
  background:none;border-top:none;border-left:none;border-right:none;
}
.nav-tab:hover{color:var(--ink2);}
.nav-tab.active{color:var(--rust);border-bottom:2px solid var(--rust);}

/* ══ MCQ ══ */
.mcq-header-card{
  background:var(--ink);color:var(--cream);
  border-radius:4px;padding:1rem 1.3rem;margin:1.4rem 0 1rem;
  display:flex;align-items:center;gap:12px;
}
.mcq-header-title{font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:900;color:var(--cream);}
.mcq-header-sub{font-family:'JetBrains Mono',monospace;font-size:0.64rem;color:#a09888;margin-top:2px;}
.mcq-count-badge{
  margin-left:auto;background:var(--rust);color:#fff;
  font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:600;
  padding:3px 10px;border-radius:2px;
}
.mcq-card{
  background:var(--white);border:1px solid var(--col);border-radius:4px;
  padding:1.1rem 1.3rem;margin-bottom:0.8rem;
  transition:all 0.18s;border-left:4px solid transparent;box-shadow:var(--sh);
}
.mcq-card:hover{border-left-color:var(--rust);box-shadow:var(--sh2);}
.mcq-q-num{
  font-family:'JetBrains Mono',monospace;font-size:0.6rem;font-weight:600;
  color:var(--rust);letter-spacing:0.1em;text-transform:uppercase;
  margin-bottom:0.4rem;display:flex;align-items:center;gap:8px;
}
.mcq-q-type{background:var(--navy-bg);border:1px solid var(--navy-bdr);color:var(--navy);font-size:0.57rem;padding:1px 6px;border-radius:2px;font-weight:600;}
.mcq-question{
  font-family:'Source Serif 4',serif;font-size:0.95rem;font-weight:600;
  color:var(--ink);line-height:1.5;margin-bottom:0.9rem;
  padding-bottom:0.8rem;border-bottom:1px solid var(--cream2);
}
.mcq-opts{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:0.75rem;}
.mcq-opt{
  background:var(--cream);border:1px solid var(--col);border-radius:3px;
  padding:0.4rem 0.7rem;font-family:'Source Serif 4',serif;font-size:0.83rem;
  color:var(--ink2);line-height:1.4;cursor:pointer;transition:all 0.12s;
}
.mcq-opt:hover{background:var(--cream2);border-color:var(--col2);}
.mcq-footer{display:flex;align-items:flex-start;gap:8px;flex-wrap:wrap;}
.mcq-ans{
  display:inline-flex;align-items:center;gap:4px;
  background:var(--forest-bg);border:1px solid var(--forest-bdr);border-radius:3px;
  padding:3px 9px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;
  color:var(--forest);font-weight:700;white-space:nowrap;
}
.mcq-exp{font-family:'Source Serif 4',serif;font-size:0.79rem;color:var(--ink3);font-style:italic;line-height:1.5;padding-top:3px;}

/* ══ UPLOAD HINT ══ */
.upload-hint{
  text-align:center;padding:3rem 1rem;background:var(--white);
  border:2px dashed var(--col2);border-radius:6px;margin-top:1rem;box-shadow:var(--sh);
  cursor:pointer;transition:all 0.18s;
}
.upload-hint:hover{border-color:var(--rust);background:var(--rust-bg);}

/* ══ HOW IT WORKS CARD ══ */
.how-card{
  background:var(--white);border:1px solid var(--col);border-radius:4px;
  padding:1.1rem;margin-bottom:0.9rem;box-shadow:var(--sh);
}
.how-title{font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:var(--rust);text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:0.5rem;}
.how-step{font-family:'Source Serif 4',serif;font-size:0.82rem;color:var(--ink3);line-height:1.7;}

/* ══ PAGE IMAGE ══ */
.page-img-wrap{border:1px solid var(--col);border-radius:4px;overflow:hidden;box-shadow:var(--sh);margin-bottom:1rem;}

/* ══ LANG NOTICE ══ */
.lang-notice{background:var(--navy-bg);border:1px solid var(--navy-bdr);border-radius:4px;padding:0.6rem 0.9rem;margin-bottom:0.9rem;font-family:'Source Serif 4',serif;font-size:0.81rem;color:var(--navy);}

/* ══ FOOTER ══ */
.app-footer{
  text-align:center;padding:1rem 0 0.5rem;margin-top:2.5rem;
  border-top:3px double var(--col2);
  font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--col2);
  letter-spacing:0.06em;
}

/* ══ HR ══ */
.hr{height:1px;background:var(--col);margin:1.1rem 0;}

/* ══ STAT PILLS ══ */
.stat-pill{background:var(--white);border:1px solid var(--col);border-radius:4px;padding:0.38rem 0.8rem;box-shadow:var(--sh);display:inline-block;}
.sp-val{font-family:'JetBrains Mono',monospace;font-size:0.96rem;color:var(--rust);font-weight:600;}
.sp-lbl{font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.06em;}

</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# CONSTANTS
# ════════════════════════════════════════════════════════════════════
BHASHINI_LANG_CODES = {
    "Hindi":"hi","Bengali":"bn","Tamil":"ta","Telugu":"te",
    "Marathi":"mr","Gujarati":"gu","Kannada":"kn","Odia":"or",
    "Punjabi":"pa","Malayalam":"ml","Assamese":"as","Urdu":"ur",
}
BHASHINI_INFERENCE_URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
ENGLISH_LIKE_LANGS = {"English","Hindi"}

MCQ_TYPES_FULL    = ["General MCQs","English Vocabulary","English Idioms & Phrases","Mixed (All Types)"]
MCQ_TYPES_LIMITED = ["General MCQs"]

EXAM_TONE_MAP = {
    "SSC ":          {"positive":0.55,"neutral":0.30,"negative":0.15},
    "Banking":          {"positive":0.50,"neutral":0.35,"negative":0.15},
    "Railway":          {"positive":0.45,"neutral":0.40,"negative":0.15},
    "Defence":          {"positive":0.60,"neutral":0.25,"negative":0.15},
    "General Knowledge":{"positive":0.40,"neutral":0.45,"negative":0.15},
    "UPSC ":  {"positive":0.35,"neutral":0.45,"negative":0.20}}


MODELS = {
    "analysis":    ["llama-3.1-8b-instant","llama-3.3-70b-versatile"],
    "vision":      ["meta-llama/llama-4-scout-17b-16e-instruct","llama-3.2-11b-vision-preview"],
    "mcq":         ["llama-3.1-8b-instant","llama-3.3-70b-versatile"],
    "translation": ["llama-3.1-8b-instant","llama-3.3-70b-versatile"],
}

# All 15 major Indian competitive exams
EXAM_NAMES = [
    "SSC","Banking","Railway","Defence","General Knowledge","UPSC"
]

EXAM_CHOICES = EXAM_NAMES  # use same list for selectbox

load_dotenv()
# ════════════════════════════════════════════════════════════════════
# GROQ CLIENT
# ════════════════════════════════════════════════════════════════════
@st.cache_resource

# Load .env


def get_groq():
    key = os.getenv("GROQ_API_KEY")   # ✅ FIXED

    if not key:
        st.error("❌ GROQ_API_KEY missing in environment")
        return None

    try:
        return Groq(api_key=key)
    except Exception as e:
        st.error(f"❌ Groq init failed: {e}")
        return None

client = get_groq()
if client is None:
    st.stop()

# ✅ Bhashini variables
BHASHINI_USER_ID = os.getenv("BHASHINI_USER_ID")
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY")



# ════════════════════════════════════════════════════════════════════
# OCR
# ════════════════════════════════════════════════════════════════════
@st.cache_resource
def _easyocr_reader():
    return easyocr.Reader(["en"], gpu=False, verbose=False) if EASYOCR_OK else None

def run_ocr(img: Image.Image):
    if TESSERACT_OK:
        try:
            t = pytesseract.image_to_string(img, config="--oem 3 --psm 6").strip()
            if len(t) > 60:
                return t, "Tesseract"
        except Exception:
            pass
    r = _easyocr_reader()
    if r:
        try:
            res = r.readtext(np.array(img), detail=0, paragraph=True)
            t = "\n".join(res).strip()
            if len(t) > 60:
                return t, "EasyOCR"
        except Exception:
            pass
    return "", "none"


# ════════════════════════════════════════════════════════════════════
# IMAGE UTIL
# ════════════════════════════════════════════════════════════════════
def optimise_img(img, max_px=1600, q=82):
    img = img.convert("RGB") if img.mode != "RGB" else img
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=q, optimize=True)
    return buf.getvalue()

def img_b64(b):
    return base64.b64encode(b).decode()


# ════════════════════════════════════════════════════════════════════
# GROQ WITH AUTO FALLBACK
# ════════════════════════════════════════════════════════════════════
def groq_fallback(messages, model_key: str, max_tokens=4096, temp=0.2):
    warns = []
    for model in MODELS.get(model_key, []):
        for attempt in range(1, 3):
            try:
                resp = client.chat.completions.create(
                    model=model, messages=messages, temperature=temp, max_tokens=max_tokens)
                return resp.choices[0].message.content.strip(), model, warns
            except Exception as e:
                err = str(e)
                warns.append(f"⚠ {model}: {err[:70]}")
                if any(k in err.lower() for k in ["rate_limit","429","quota"]):
                    break
                time.sleep(attempt)
    return None, None, warns + ["❌ All models exhausted."]

def vision_fallback(img_bytes: bytes, prompt: str):
    b64 = img_b64(img_bytes)
    warns = []
    for model in MODELS.get("vision", []):
        for attempt in range(1, 3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role":"user","content":[
                        {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}},
                        {"type":"text","text":prompt}
                    ]}],
                    temperature=0.2, max_tokens=4096)
                return resp.choices[0].message.content.strip(), model, warns
            except Exception as e:
                err = str(e)
                warns.append(f"⚠ {model}: {err[:70]}")
                if any(k in err.lower() for k in ["rate_limit","429","quota"]):
                    break
                time.sleep(attempt)
    return None, None, warns + ["❌ All vision models exhausted."]


# ════════════════════════════════════════════════════════════════════
# JSON PARSERS
# ════════════════════════════════════════════════════════════════════
def parse_obj(raw, warns):
    if not raw:
        return None
    r = raw.strip()
    if r.startswith("```"):
        r = r.split("\n",1)[-1].rsplit("```",1)[0].strip()
    try:
        return json.loads(r)
    except Exception:
        pass
    try:
        cut = r[r.find("{"):r.rfind("}")+1]
        d = json.loads(cut)
        warns.append("🔧 JSON trimmed.")
        return d
    except Exception:
        pass
    warns.append("❌ JSON parse failed.")
    return r

def parse_arr(raw, warns):
    if not raw:
        return []
    r = raw.strip()
    if r.startswith("```"):
        r = r.split("\n",1)[-1].rsplit("```",1)[0].strip()
    for fn in [json.loads, lambda x: json.loads(x[x.find("["):x.rfind("]")+1])]:
        try:
            a = fn(r)
            if isinstance(a, list):
                return a
        except Exception:
            pass
    warns.append("❌ Array parse failed.")
    return []


# ════════════════════════════════════════════════════════════════════
# STAGE 1 — OCR/VISION → JSON
# ════════════════════════════════════════════════════════════════════
_SCHEMA = """{
  "headline":    "Main headline of the article",
  "subheadline": "Sub-headline or deck line, or empty string if none",
  "date":        "Full publication date as it same from uploaded Page if you not understand you will Ask i didn't understand and fill dat e
  ",
  "category":    "Politics | Economy | Science | Sports | International | State | Health | Education | etc.",
  "summary":     "5 to 8 complete sentences covering what happened, who, where, when, why, and impact.",
  "key_points": ["Minimum 6, maximum 10 key exam-relevant facts. Each must be a complete sentence of at least 15 words."],
  "entities": {
    "people":            ["Full names of all people mentioned"],
    "locations":         ["All cities, states, countries, districts, regions mentioned"],
    "organizations":     ["All government bodies, companies, NGOs, institutions, ministries mentioned"],
    "schemes":           ["Any government scheme, programme, policy, or initiative mentioned"],
    "topics":            ["2 to 5 main topics this article covers"],
    "important_numbers": ["All numbers, statistics, budgets, percentages"],
    "important_dates":   ["All dates and time references mentioned"]
  },
  "sentiment": {"label":"Positive | Neutral | Negative","reason":"One sentence explaining sentiment"},
  "raw_ocr_text": "The complete readable text from the newspaper page"
}"""

_SYSTEM = """You are a precise newspaper content extraction engine.
ABSOLUTE RULES:
1. Return ONLY raw valid JSON — no markdown, no explanation, no preamble.
2. ONLY extract what is visible/readable in the newspaper. Do NOT invent facts.
3. If the content is clearly NOT a newspaper article, return: {"error": "not_newspaper"}
4. Do NOT generate MCQs, questions, or quiz content.
5. summary: 5-8 sentences using ONLY visible article content.
6. key_points: 6-10 factual sentences, each at least 15 words, directly from the article.
"""

def _build_analysis_prompt(text_content: str) -> str:
    return (f"{_SYSTEM}\n\nReturn exactly this JSON schema:\n{_SCHEMA}\n\n"
            f"NEWSPAPER TEXT:\n\"\"\"\n{text_content[:9000]}\n\"\"\"")

def _build_vision_prompt() -> str:
    return (f"{_SYSTEM}\n\nCarefully read every word, number, date, and name visible in this "
            f"newspaper image.\nReturn exactly this JSON schema:\n{_SCHEMA}")

def stage1_text(ocr: str):
    warns = []
    raw, model, w = groq_fallback(
        [{"role":"user","content":_build_analysis_prompt(ocr)}],
        "analysis", max_tokens=4096
    )
    warns.extend(w)
    if not raw:
        return None, model, warns + ["❌ Analysis returned nothing."]
    result = parse_obj(raw, warns)
    if isinstance(result, dict):
        if result.get("error") == "not_newspaper":
            return None, model, warns + ["⚠️ Not a newspaper page."]
        if not result.get("raw_ocr_text"):
            result["raw_ocr_text"] = ocr
    return result, model, warns

def stage1_vision(img_bytes: bytes):
    warns = []
    raw, model, w = vision_fallback(img_bytes, _build_vision_prompt())
    warns.extend(w)
    if not raw:
        return None, model, warns + ["❌ Vision returned nothing."]
    result = parse_obj(raw, warns)
    if isinstance(result, dict) and result.get("error") == "not_newspaper":
        return None, model, warns + ["⚠️ Not a newspaper page."]
    return result, model, warns


# ════════════════════════════════════════════════════════════════════
# STAGE 2 — TRANSLATE JSON
# ════════════════════════════════════════════════════════════════════
def _batch_translate(texts: list, lang: str) -> list:
    if not texts:
        return []
    numbered = "\n".join(f"{i+1}. {t}" for i,t in enumerate(texts))
    raw, _, _ = groq_fallback(
        [{"role":"user","content":
          f"Translate the following numbered English texts to {lang}.\n"
          f"Return ONLY a JSON array of translated strings in the same order. No markdown.\n\n{numbered}"}],
        "translation", max_tokens=3000
    )
    if not raw:
        return texts
    r = raw.strip()
    if r.startswith("```"):
        r = r.split("\n",1)[-1].rsplit("```",1)[0].strip()
    for fn in [json.loads, lambda x: json.loads(x[x.find("["):x.rfind("]")+1])]:
        try:
            a = fn(r)
            if isinstance(a, list) and len(a) == len(texts):
                return [str(x) for x in a]
        except Exception:
            pass
    return texts

def stage2_translate(analysis: dict, lang: str, code: str) -> dict:
    if not isinstance(analysis, dict):
        return analysis
    tr = dict(analysis)
    simple = [(f, analysis.get(f,"")) for f in ["headline","subheadline","summary"] if analysis.get(f,"")]
    if simple:
        tv = _batch_translate([v for _,v in simple], lang)
        for (f,_),v in zip(simple, tv):
            tr[f] = v
    kp = analysis.get("key_points", [])
    if kp:
        tr["key_points"] = _batch_translate(kp, lang)
    s = analysis.get("sentiment", {})
    if isinstance(s, dict) and s.get("reason"):
        tr["sentiment"] = dict(s)
        tr["sentiment"]["reason"] = _batch_translate([s["reason"]], lang)[0]
    return tr


# ════════════════════════════════════════════════════════════════════
# STAGE 3 — MCQ GENERATION
# ════════════════════════════════════════════════════════════════════
def _qrules(qtype: str) -> str:
    return {
        "General MCQs": (
            "Generate EXACTLY 10 fact-based MCQs.\n"
            "Every question must test a specific fact, date, number, name, or statement "
            "explicitly stated in the JSON above.\nquestion_type = 'MCQ'"
        ),
        "English Vocabulary": (
            "Generate EXACTLY 10 vocabulary questions.\n"
            "Pick 10 important or difficult words from the headline, summary, or key_points.\n"
            "Test meaning, synonym, antonym, or correct usage of those exact words.\nquestion_type = 'Vocabulary'"
        ),
        "English Idioms & Phrases": (
            "Generate EXACTLY 10 idiom/phrase questions.\n"
            "Each idiom must naturally relate to the topic of the article.\nquestion_type = 'Idiom/Phrase'"
        ),
        "Mixed (All Types)": (
            "Generate EXACTLY 10 questions: 4 fact MCQs + 3 vocabulary + 3 idiom/phrase.\n"
            "Set question_type correctly for each question."
        ),
    }.get(qtype, "Generate EXACTLY 10 fact-based MCQs from the JSON. question_type = 'MCQ'")

def _mcq_prompt(json_str: str, qtype: str, lang: str, exam: str) -> str:
    return f"""You are an expert {exam} competitive-exam MCQ creator.

NEWSPAPER ARTICLE JSON (your ONLY source):
{json_str}

STRICT RULES:
1. ALL facts must come from the JSON above ONLY.
2. answer field must be exactly one letter: A, B, C, or D.
3. explanation: max 25 words referencing a specific fact from the JSON.
4. Return ONLY a raw JSON array — no markdown, no text before or after.

QUESTION TYPE: {qtype}
LANGUAGE: {lang}
EXAM: {exam}

{_qrules(qtype)}

All questions, options, and explanations must be in {lang}.

RETURN FORMAT:
[
  {{
    "question_type": "MCQ",
    "question": "question in {lang}",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "explanation": "short factual note in {lang}"
  }}
]
"""

def _translate_mcqs(mcqs: list, lang: str) -> list:
    if not mcqs:
        return []
    qs   = [q.get("question","")    for q in mcqs]
    opts = [o for q in mcqs for o in q.get("options",[])]
    exps = [q.get("explanation","") for q in mcqs]
    qt   = _batch_translate(qs,   lang)
    ot   = _batch_translate(opts, lang)
    et   = _batch_translate(exps, lang)
    out  = []
    oi   = 0
    for i, q in enumerate(mcqs):
        n = len(q.get("options",[]))
        out.append({
            "question_type": q.get("question_type","MCQ"),
            "question":      qt[i] if i < len(qt) else q.get("question",""),
            "options":       ot[oi:oi+n],
            "answer":        q.get("answer",""),
            "explanation":   et[i] if i < len(et) else q.get("explanation",""),
        })
        oi += n
    return out

@st.cache_data(show_spinner=False)
def stage3_mcqs(json_str: str, qtype: str, lang: str, exam: str) -> list:
    warns = []
    if lang in ENGLISH_LIKE_LANGS:
        raw, _, w = groq_fallback(
            [{"role":"user","content":_mcq_prompt(json_str, qtype, lang, exam)}],
            "mcq", max_tokens=2800
        )
        warns.extend(w)
        return parse_arr(raw, warns)
    raw, _, w = groq_fallback(
        [{"role":"user","content":_mcq_prompt(json_str, "General MCQs", "English", exam)}],
        "mcq", max_tokens=2800
    )
    warns.extend(w)
    en = parse_arr(raw, warns)
    return _translate_mcqs(en, lang) if en else []


# ════════════════════════════════════════════════════════════════════
# SENTIMENT
# ════════════════════════════════════════════════════════════════════
def compute_sentiment(text: str, exam: str) -> dict:
    tone = EXAM_TONE_MAP.get(exam, {"positive":0.40,"neutral":0.45,"negative":0.15})
    if not text:
        return {"subjectivity":0.0,"label":"Neutral","confidence":0.0,
                "scores":{"positive":0.33,"neutral":0.34,"negative":0.33},
                "exam_weighted":tone,"keywords":[]}
    if TEXTBLOB_OK:
        b = TextBlob(text)
        pol = round(b.sentiment.polarity, 4)
        sub = round(b.sentiment.subjectivity, 4)
    else:
        pw = ["growth","progress","success","win","improve","develop","launch","boost","rise","profit","peace","secure","award","achieved","record"]
        nw = ["decline","fall","loss","fail","crisis","attack","death","crime","flood","drought","war","corrupt","accident","disaster","threat"]
        wl = text.lower().split()
        p  = sum(1 for w in wl if any(x in w for x in pw))
        n  = sum(1 for w in wl if any(x in w for x in nw))
        pol = round((p-n)/max(p+n,1),4)
        sub = 0.5
    if pol > .1:
        label="Positive"; r={"positive":min(.5+pol*.5,.95),"neutral":max(.3-pol*.1,.03),"negative":max(.2-pol*.1,.02)}
    elif pol < -.1:
        label="Negative"; r={"positive":max(.2+pol*.1,.02),"neutral":max(.3+pol*.05,.03),"negative":min(.5-pol*.5,.95)}
    else:
        label="Neutral";  r={"positive":.30,"neutral":.45,"negative":.25}
    tot    = sum(r.values())
    scores = {k:round(v/tot,4) for k,v in r.items()}
    weighted = {k:round(.6*scores[k]+.4*tone[k],4) for k in ("positive","neutral","negative")}
    seeds = ["growth","development","success","progress","launch","record","benefit","peace","award","crisis","attack","flood","fire","accident","protest","decline","death","corruption"]
    kw = list(dict.fromkeys(w for w in text.lower().split() if any(s in w for s in seeds)))[:8]
    return {"subjectivity":sub,"label":label,"confidence":round(abs(pol),4),"scores":scores,"exam_weighted":weighted,"keywords":kw}


# ════════════════════════════════════════════════════════════════════
# TIMING UTILITIES
# ════════════════════════════════════════════════════════════════════
def _speed_class(secs: float) -> str:
    if secs < 5:   return "fast"
    if secs < 15:  return ""
    return "slow"

def render_timing_card(timing: dict):
    if not timing: return
    total  = timing.get("total", 0)
    ocr_t  = timing.get("ocr",   0)
    ai_t   = timing.get("ai",    0)
    method = timing.get("method","—")
    sp = _speed_class(total)
    st.markdown(f"""
    <div class="sec-head">⏱ Response Time Breakdown</div>
    <div class="timing-card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.65rem;">
        <span style="font-family:'Playfair Display',serif;font-size:0.9rem;font-weight:700;color:var(--ink);">Total Analysis Time</span>
        <span class="time-badge {sp}">⏱ {total:.2f}s</span>
      </div>
      <div class="timing-row">
        <span class="timing-label">🔍 OCR ({method})</span>
        <div class="timing-bar"><div class="timing-fill" style="width:{min(100,(ocr_t/max(total,0.01))*100):.0f}%;background:var(--navy);"></div></div>
        <span class="timing-val">{ocr_t:.2f}s</span>
      </div>
      <div class="timing-row">
        <span class="timing-label">🤖 AI Analysis (Groq)</span>
        <div class="timing-bar"><div class="timing-fill" style="width:{min(100,(ai_t/max(total,0.01))*100):.0f}%;background:var(--rust);"></div></div>
        <span class="timing-val">{ai_t:.2f}s</span>
      </div>
      <div style="margin-top:0.55rem;font-family:'JetBrains Mono',monospace;font-size:0.63rem;color:var(--ink3);">
        Pipeline: {timing.get('pipeline','—')} &nbsp;·&nbsp; Model: {timing.get('model','—')}
      </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# UPLOAD HISTORY
# ════════════════════════════════════════════════════════════════════
def _ensure_history():
    if "upload_history" not in st.session_state:
        st.session_state["upload_history"] = []

def add_to_history(name: str, ftype: str, size_kb: float, pages: int, timestamp: str):
    _ensure_history()
    hist = st.session_state["upload_history"]
    if hist and hist[0].get("name") == name:
        return
    hist.insert(0, {"name":name,"type":ftype,"size_kb":size_kb,"pages":pages,"timestamp":timestamp})
    st.session_state["upload_history"] = hist[:20]

def render_history_panel():
    _ensure_history()
    hist = st.session_state["upload_history"]
    if not hist:
        st.markdown(
            '<div style="font-family:\'Source Serif 4\',serif;font-size:0.76rem;color:var(--ink3);'
            'text-align:center;padding:0.8rem 0;font-style:italic;">No uploads yet this session</div>',
            unsafe_allow_html=True)
        return
    for i, item in enumerate(hist):
        icon = "📄" if item["type"]=="pdf" else "🖼"
        tag_cls = "pdf" if item["type"]=="pdf" else "img"
        tag_lbl = "PDF" if item["type"]=="pdf" else "IMG"
        pg_txt  = f"{item['pages']}p · " if item["pages"]>1 else ""
        # Each history item is a clickable button (Streamlit way)
        col_hist, col_btn = st.columns([5,1])
        with col_hist:
            st.markdown(f"""<div class="hist-item">
              <div class="hist-thumb">{icon}</div>
              <div class="hist-body">
                <div class="hist-name" title="{item['name']}">{item['name']}</div>
                <div class="hist-meta">{item['timestamp']} · {pg_txt}{item['size_kb']:.0f} KB</div>
              </div>
              <span class="hist-tag {tag_cls}">{tag_lbl}</span>
            </div>""", unsafe_allow_html=True)
        with col_btn:
            if st.button("↗", key=f"hist_open_{i}", help=f"Open {item['name']}"):
                st.session_state["hist_preview_idx"] = i
                st.session_state["show_hist_modal"] = True


# ════════════════════════════════════════════════════════════════════
# HISTORY MODAL (rendered in main area)
# ════════════════════════════════════════════════════════════════════
def render_history_modal():
    """Render history preview modal if open."""
    if not st.session_state.get("show_hist_modal"):
        return
    _ensure_history()
    hist = st.session_state["upload_history"]
    idx  = st.session_state.get("hist_preview_idx", 0)
    if idx >= len(hist):
        return
    item = hist[idx]

    with st.container():
        st.markdown("""<div style="background:var(--ink);border-radius:0 0 6px 6px;
          border-top:5px solid var(--rust);padding:1.1rem 1.4rem;margin-bottom:1rem;">
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:900;
            color:var(--cream);">📂 Upload History Preview</div>
        </div>""", unsafe_allow_html=True)

        icon = "📄" if item["type"]=="pdf" else "🖼"
        pg_txt = f"{item['pages']} page{'s' if item['pages']>1 else ''}"
        st.markdown(f"""
        <div style="background:var(--white);border:1px solid var(--col);border-radius:4px;padding:1.3rem;margin-bottom:1rem;">
          <div style="font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:var(--ink);margin-bottom:0.4rem;">
            {icon} {item['name']}
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:1rem;">
            <div style="background:var(--cream2);border:1px solid var(--col);border-radius:3px;padding:0.5rem 0.8rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.57rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.1em;">Type</div>
              <div style="font-size:0.86rem;font-weight:600;color:var(--ink2);margin-top:2px;">{item['type'].upper()}</div>
            </div>
            <div style="background:var(--cream2);border:1px solid var(--col);border-radius:3px;padding:0.5rem 0.8rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.57rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.1em;">Size</div>
              <div style="font-size:0.86rem;font-weight:600;color:var(--ink2);margin-top:2px;">{item['size_kb']:.0f} KB</div>
            </div>
            <div style="background:var(--cream2);border:1px solid var(--col);border-radius:3px;padding:0.5rem 0.8rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.57rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.1em;">Pages</div>
              <div style="font-size:0.86rem;font-weight:600;color:var(--ink2);margin-top:2px;">{pg_txt}</div>
            </div>
            <div style="background:var(--cream2);border:1px solid var(--col);border-radius:3px;padding:0.5rem 0.8rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.57rem;color:var(--ink3);text-transform:uppercase;letter-spacing:0.1em;">Uploaded</div>
              <div style="font-size:0.75rem;font-weight:600;color:var(--ink2);margin-top:2px;">{item['timestamp']}</div>
            </div>
          </div>
          <div style="background:var(--cream2);border:1px dashed var(--col2);border-radius:4px;padding:2rem;text-align:center;
            font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--ink3);font-style:italic;margin-bottom:0.8rem;">
            {icon} Re-upload this file to view its analysis
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✕ Close Preview", use_container_width=True):
                st.session_state["show_hist_modal"] = False
                st.rerun()
        with c2:
            st.info("Upload the file again to restore full analysis.")


# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════
def pk(i): return f"page_{i}"

def has_s1(key):
    return (key in st.session_state and isinstance(st.session_state[key].get("analysis"), dict))

def run_stage1_silent(img: Image.Image, ocr_engine: str) -> dict:
    img_bytes = optimise_img(img)
    t0 = time.time()
    if ocr_engine == "Vision only (no OCR)":
        t_ocr_start = time.time()
        result, model, warns = stage1_vision(img_bytes)
        ocr, meth = "", "vision"
        ocr_time = time.time() - t_ocr_start
        ai_time  = 0.0
        pipeline = "Vision → JSON"
    else:
        t_ocr_start = time.time()
        ocr, meth = run_ocr(img)
        ocr_time = time.time() - t_ocr_start
        t_ai_start = time.time()
        if ocr:
            result, model, warns = stage1_text(ocr)
            pipeline = f"{meth} → Text → AI → JSON"
        else:
            result, model, warns = stage1_vision(img_bytes)
            meth = "vision"
            pipeline = "OCR failed → Vision → JSON"
        ai_time = time.time() - t_ai_start
    total_time = time.time() - t0
    timing = {"total":round(total_time,2),"ocr":round(ocr_time,2),"ai":round(ai_time,2),
              "method":meth,"pipeline":pipeline if ocr_engine!="Vision only (no OCR)" else "Vision → JSON",
              "model":model or "—"}
    return {"analysis":result,"ocr_text":ocr,"ocr_method":meth,"model_used":model,"warnings":warns,"timing":timing}


# ════════════════════════════════════════════════════════════════════
# RENDER ONE PAGE  (with tab navigation)
# ════════════════════════════════════════════════════════════════════
def render_page(key: str, exam: str, lang: str, qtype: str):
    s        = st.session_state[key]
    analysis = s["analysis"]
    ocr_text = s["ocr_text"]
    ocr_meth = s["ocr_method"]
    timing   = s.get("timing", {})

    for w in s.get("warnings", []):
        st.warning(w)
    if not isinstance(analysis, dict):
        st.error("⚠️ Analysis failed for this page.")
        return

    # Stage 2: translate
    if lang == "English":
        display = analysis
    else:
        ck = f"tr_{lang}"
        if ck not in s:
            code = BHASHINI_LANG_CODES.get(lang, "")
            with st.spinner(f"🌐 Translating to {lang} …"):
                s[ck] = stage2_translate(analysis, lang, code)
        display = s[ck]

    # Stage 3: MCQs
    is_limited = lang not in ENGLISH_LIKE_LANGS
    eff_qtype  = "General MCQs" if is_limited else qtype
    djson      = json.dumps(display, ensure_ascii=False)
    with st.spinner("📚 Generating MCQs …"):
        mcqs = stage3_mcqs(djson, eff_qtype, lang, exam)

    # Sentiment
    sent_text = ocr_text or analysis.get("raw_ocr_text","") or analysis.get("summary","")
    sent      = compute_sentiment(sent_text, exam)
    ai_s      = analysis.get("sentiment", {})
    ai_lbl    = ai_s.get("label", sent["label"]) if isinstance(ai_s,dict) else sent["label"]
    ai_rsn    = ai_s.get("reason","")             if isinstance(ai_s,dict) else ""

    # ── Article Masthead Card ──────────────────────────────────────
    head = display.get("headline", analysis.get("headline","—"))
    sub  = display.get("subheadline","")
    date = analysis.get("date","")
    cat  = analysis.get("category","")
    ll   = ai_lbl.lower()
    scls = "pos" if ll=="positive" else "neg" if ll=="negative" else "neu"
    icon_s = "●"
    t_total = timing.get("total", 0)
    t_cls   = _speed_class(t_total)
    t_label = f"⏱ {t_total:.2f}s" if t_total else ""

    st.markdown(f"""<div class="article-masthead">
      <div class="article-kicker">🗂 {cat if cat else 'Article'}</div>
      <div class="article-headline">{head}</div>
      {"<div class='article-deck'>" + sub + "</div>" if sub else ""}
      <div class="article-byline">
        {"<span>📅 " + date + "</span><span class='byline-sep'>|</span>" if date else ""}
        <span>🔤 {ocr_meth}</span><span class="byline-sep">|</span>
        <span>🌍 {lang}</span><span class="byline-sep">|</span>
        <span class="byline-tag {scls}">{icon_s} {ai_lbl}</span>
        {"<span class='byline-sep'>|</span><span class='time-badge " + t_cls + "'>" + t_label + "</span>" if t_label else ""}
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Metrics Row ────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📝 OCR Chars",  f"{len(ocr_text):,}")
    c2.metric("❓ MCQs",       str(len(mcqs)))
    c3.metric("🎯 Confidence", str(sent["confidence"]))
    c4.metric("⏱ Analysis",   f"{t_total:.1f}s" if t_total else "—")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # ── Tab Navigation (using st.tabs) ────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📰 Analysis", f"📚 MCQs ({len(mcqs)})", "🔍 Raw JSON", "📄 OCR Text"])

    with tab1:
        # Timing breakdown
        if timing:
            render_timing_card(timing)

        # Summary
        summary = display.get("summary","")
        if summary:
            st.markdown('<div class="sec-head">📰 Article Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-card">{summary}</div>', unsafe_allow_html=True)

        # Two-column layout: Key Points + Entities
        col_left, col_right = st.columns([1.5, 1])

        with col_left:
            kp = display.get("key_points", [])
            if kp:
                st.markdown('<div class="sec-head">🔑 Key Points for Exam</div>', unsafe_allow_html=True)
                rows = "".join(
                    f'<div class="kp-row">'
                    f'<div class="kp-num">{i}</div>'
                    f'<div class="kp-text">{pt}</div>'
                    f'</div>' for i, pt in enumerate(kp, 1)
                )
                st.markdown(f'<div class="kp-card">{rows}</div>', unsafe_allow_html=True)

        with col_right:
            ents = analysis.get("entities", {})
            entity_keys = [("people","👤","People"),("locations","📍","Locations"),
                           ("organizations","🏢","Organizations"),("schemes","📋","Schemes"),
                           ("topics","🏷","Topics")]
            any_ents = any(ents.get(k,[]) for k,_,_ in entity_keys)
            if any_ents:
                st.markdown('<div class="sec-head">🏷 Key Entities</div>', unsafe_allow_html=True)
                groups_html = ""
                for k, ico, lbl in entity_keys:
                    items = ents.get(k, [])
                    if not items: continue
                    chips = "".join(f'<span class="ent-chip">{it}</span>' for it in items)
                    groups_html += f'<div class="ent-group"><div class="ent-label">{ico} {lbl}</div><div class="ent-chips">{chips}</div></div>'
                # Numbers & Dates
                nums = ents.get("important_numbers", [])
                dts  = ents.get("important_dates", [])
                if nums:
                    chips = "".join(f'<span class="ent-chip">{n}</span>' for n in nums)
                    groups_html += f'<div class="ent-group"><div class="ent-label">🔢 Numbers</div><div class="ent-chips">{chips}</div></div>'
                if dts:
                    chips = "".join(f'<span class="ent-chip">{d}</span>' for d in dts)
                    groups_html += f'<div class="ent-group"><div class="ent-label">📅 Dates</div><div class="ent-chips">{chips}</div></div>'
                st.markdown(f'<div class="ent-card">{groups_html}</div>', unsafe_allow_html=True)

            # Sentiment block
            st.markdown('<div class="sec-head" style="margin-top:1rem;">📊 Sentiment</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="ent-card">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;">
                <span class="sent-badge {ll}">{icon_s} {ai_lbl}</span>
              </div>
              {"<div style='font-family:Source Serif 4,serif;font-size:0.82rem;color:var(--ink3);font-style:italic;margin-bottom:0.7rem;'>" + ai_rsn + "</div>" if ai_rsn else ""}
              <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <div class="stat-pill"><div class="sp-val">{sent['confidence']}</div><div class="sp-lbl">Confidence</div></div>
                <div class="stat-pill"><div class="sp-val">{sent['subjectivity']}</div><div class="sp-lbl">Subjectivity</div></div>
              </div>
              {"<div class='ent-chips' style='margin-top:0.6rem;'>" + "".join(f'<span class=\"ent-chip\">{w}</span>' for w in sent.get("keywords",[])) + "</div>" if sent.get("keywords") else ""}
            </div>""", unsafe_allow_html=True)

    with tab2:
        if is_limited:
            st.markdown(
                f'<div class="lang-notice">ℹ️ <strong>{lang}</strong>: Only General MCQs supported — '
                f'generated in English then translated to {lang}.</div>',
                unsafe_allow_html=True)

        st.markdown(f"""<div class="mcq-header-card">
          <span style="font-size:1.4rem;">📚</span>
          <div>
            <div class="mcq-header-title">Practice Questions</div>
            <div class="mcq-header-sub">{eff_qtype} · {lang} · {exam}</div>
          </div>
          <span class="mcq-count-badge">{len(mcqs)} Questions</span>
        </div>""", unsafe_allow_html=True)

        if not mcqs:
            st.markdown('<div style="text-align:center;padding:1.5rem;color:var(--ink3);font-style:italic;font-family:\'Source Serif 4\',serif;">No MCQs generated. Try re-analysing this page.</div>', unsafe_allow_html=True)
        else:
            for i, q in enumerate(mcqs, 1):
                opts     = q.get("options", [])
                opts_html = "".join(f'<div class="mcq-opt">{o}</div>' for o in opts)
                qt       = q.get("question_type","MCQ")
                st.markdown(f"""<div class="mcq-card">
                  <div class="mcq-q-num">Question {i:02d} <span class="mcq-q-type">{qt}</span></div>
                  <div class="mcq-question">{q.get('question','')}</div>
                  <div class="mcq-opts">{opts_html}</div>
                  <div class="mcq-footer">
                    <span class="mcq-ans">✓ {q.get('answer','')}</span>
                    <span class="mcq-exp">{q.get('explanation','')}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

    with tab3:
        st.json(analysis)
        if lang != "English" and f"tr_{lang}" in s:
            st.markdown(f'<div class="sec-head">🌐 Translated JSON ({lang})</div>', unsafe_allow_html=True)
            st.json(s[f"tr_{lang}"])
        if timing:
            st.markdown('<div class="sec-head">⏱ Timing Details</div>', unsafe_allow_html=True)
            st.json(timing)

    with tab4:
        if ocr_text:
            st.text_area(f"OCR Text ({ocr_meth})", ocr_text, height=320, key=f"ocr_ta_{key}")
        else:
            st.markdown('<div style="color:var(--ink3);font-style:italic;padding:1rem 0;font-family:\'Source Serif 4\',serif;">No OCR text (Vision mode was used).</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# BUILD TICKER HTML
# ════════════════════════════════════════════════════════════════════
def build_ticker() -> str:
    items = (EXAM_NAMES * 3)  # triple for seamless long loop
    parts = []
    for name in items:
        parts.append(f'<span class="ticker-item"><span class="ticker-dot"></span>{name}</span>')
        parts.append('<span style="color:var(--rust);padding:0 4px;font-size:0.85rem;">◆</span>')
    return "".join(parts)


# ════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Sidebar masthead
    st.markdown("""
    <div style="padding:0.8rem 0 0.5rem;">
      <div style="font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:900;color:var(--ink);line-height:1;">
        Exam <span style="color:var(--rust);">Samachar</span>
      </div>
      <div style="font-family:'Source Serif 4',serif;font-size:0.72rem;font-style:italic;color:var(--ink3);margin-top:3px;">
        An AI Decision Support System
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:var(--col2);letter-spacing:0.06em;margin-top:2px;">
    Newspaper Edition
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:var(--col);margin:0.5rem 0 0;"></div>', unsafe_allow_html=True)

    # Settings
    st.markdown('<div class="sb-lbl"><span class="sb-dot"></span>Settings</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.68rem;color:var(--ink3);margin-bottom:3px;font-family:\'JetBrains Mono\',monospace;">🌍 Language</div>', unsafe_allow_html=True)
    language_choice = st.selectbox("lang_sel", ["English"] + list(BHASHINI_LANG_CODES.keys()),
                                   key="lang", label_visibility="collapsed")

    is_limited_lang = language_choice not in ENGLISH_LIKE_LANGS
    avail_qtypes    = MCQ_TYPES_LIMITED if is_limited_lang else MCQ_TYPES_FULL

    st.markdown('<div style="font-size:0.68rem;color:var(--ink3);margin-bottom:3px;margin-top:0.6rem;font-family:\'JetBrains Mono\',monospace;">🎯 Exam Type</div>', unsafe_allow_html=True)
    exam_type = st.selectbox("exam_sel", EXAM_CHOICES, key="exam", label_visibility="collapsed")

    st.markdown('<div style="font-size:0.68rem;color:var(--ink3);margin-bottom:3px;margin-top:0.6rem;font-family:\'JetBrains Mono\',monospace;">📝 MCQ Type</div>', unsafe_allow_html=True)
    question_type = st.selectbox("qtype_sel", avail_qtypes, key="qtype", label_visibility="collapsed")

    st.markdown('<div style="font-size:0.68rem;color:var(--ink3);margin-bottom:3px;margin-top:0.6rem;font-family:\'JetBrains Mono\',monospace;">🔍 OCR Engine</div>', unsafe_allow_html=True)
    ocr_engine = st.selectbox("ocr_sel", ["Auto (Tesseract → EasyOCR)","Vision only (no OCR)"],
                               key="ocr", label_visibility="collapsed")

    if is_limited_lang:
        st.markdown(f'<div class="lang-notice" style="margin-top:6px;">ℹ️ {language_choice}: General MCQs only.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:var(--col);margin:1rem 0 0.5rem;"></div>', unsafe_allow_html=True)

    # Status
    st.markdown('<div class="sb-lbl"><span class="sb-dot"></span>System</div>', unsafe_allow_html=True)
    cols_st = st.columns(2)
    with cols_st[0]:
        if BHASHINI_API_KEY and BHASHINI_USER_ID:
            st.markdown('<span class="status-ok">✓ Bhashini</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-warn">⚠ Groq TL</span>', unsafe_allow_html=True)
    with cols_st[1]:
        st.markdown('<span class="status-ok">✓ Groq AI</span>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:var(--col);margin:0.8rem 0 0.4rem;"></div>', unsafe_allow_html=True)

    # Upload History
    st.markdown('<div class="sb-lbl"><span class="sb-dot"></span>Upload History</div>', unsafe_allow_html=True)
    render_history_panel()

    st.markdown('<div style="height:1px;background:var(--col);margin:0.6rem 0 0.4rem;"></div>', unsafe_allow_html=True)

    if st.button("🗑 Clear All & History", use_container_width=True):
        for k in [k for k in st.session_state if k.startswith("page_") or k in ("_fid","_pdf","show_hist_modal","hist_preview_idx")]:
            del st.session_state[k]
        st.session_state["upload_history"] = []
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# TOP BAR + MASTHEAD + TICKER
# ════════════════════════════════════════════════════════════════════
now = datetime.datetime.now()
date_str = now.strftime("%A, %d %B %Y")

# Top dateline bar
st.markdown(f"""<div class="topbar">
  <div class="topbar-date">{date_str} &nbsp;|&nbsp; Indore Edition</div>
  <div class="topbar-center">India's Premier Competitive Exam Intelligence Platform</div>
  <div class="topbar-tag">v10.0 ENHANCED</div>
</div>""", unsafe_allow_html=True)

# Masthead
st.markdown(f"""<div class="masthead-wrap">
  <div class="masthead-inner">
    <div class="masthead-left">
      <div class="mh-label">Established</div>
      <div class="mh-val">2026</div>
      <div class="mh-label" style="margin-top:0.5rem;">Edition</div>
      <div class="mh-val">Daily</div>
    </div>
    <div class="masthead-center">
      <div class="mh-rule"><div class="mh-line"></div><div class="mh-diamond"></div><div class="mh-line"></div></div>
      <div class="newspaper-name">Exam <span>Samachar</span></div>
      <div class="mh-rule"><div class="mh-line"></div><div class="mh-diamond"></div><div class="mh-line"></div></div>
      <div class="masthead-tagline">An AI Decision Support System </div>
    </div>
    <div class="masthead-right">
      <div class="mh-val" style="color:var(--rust);font-weight:600;">Groq AI</div>
      <div class="mh-label" style="margin-top:0.5rem;">Languages</div>
      <div class="mh-val">12 Indian</div>
    </div>
  </div>
  <div class="masthead-pills">
    <span class="mpill rust">📰 Newspaper Only</span>
    <span class="mpill navy">⏱ Response Timing</span>
    <span class="mpill forest">📊 10 MCQs/Page</span>
    <span class="mpill gold">📂 Upload History</span>
    <span class="mpill ink">🌐 Bhashini Translate</span>
  </div>
</div>""", unsafe_allow_html=True)

# Ticker
ticker_html = build_ticker()
st.markdown(f"""<div class="ticker-wrap">
  <div class="ticker-label">EXAMS ▶</div>
  <div class="ticker-scroll">
    <div class="ticker-track">{ticker_html}</div>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# HISTORY MODAL (if open, show before file upload)
# ════════════════════════════════════════════════════════════════════
render_history_modal()

# ════════════════════════════════════════════════════════════════════
# FILE UPLOAD
# ════════════════════════════════════════════════════════════════════
uploaded = st.file_uploader("", type=["jpg","jpeg","png","pdf"], label_visibility="collapsed")

if not uploaded:
    st.markdown("""<div class="upload-hint">
      <div style="font-size:2.8rem;margin-bottom:0.8rem;">📰</div>
      <div style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:700;
                  color:var(--ink);margin-bottom:0.35rem;">Upload a Newspaper Image or PDF</div>
      <div style="font-family:'Source Serif 4',serif;font-size:0.84rem;color:var(--ink3);line-height:1.6;">
        JPG · PNG · PDF &nbsp;·&nbsp; Every page analysed independently<br>
        10 MCQs per page &nbsp;·&nbsp; Response time tracked &nbsp;·&nbsp; 12 Indian Languages
      </div>
      <div style="margin-top:1rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
        <span class="mpill rust" style="font-size:0.65rem;">📰 Newspaper Only</span>
        <span class="mpill forest" style="font-size:0.65rem;">🎯 Exam-Ready MCQs</span>
        <span class="mpill navy" style="font-size:0.65rem;">🌐 Multi-Language</span>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="app-footer">Exam Samachar v10.0 · Newspaper UI Edition · Groq AI · Bhashini · Streamlit</div>', unsafe_allow_html=True)
    st.stop()

# Reset state on new file
fid = f"{uploaded.name}_{uploaded.size}"
if st.session_state.get("_fid") != fid:
    for k in [k for k in st.session_state if k.startswith("page_") or k=="_pdf"]:
        del st.session_state[k]
    st.session_state["_fid"] = fid
    st.session_state["show_hist_modal"] = False

eff_qtype = "General MCQs" if language_choice not in ENGLISH_LIKE_LANGS else question_type


# ════════════════════════════════════════════════════════════════════
# PDF FLOW
# ════════════════════════════════════════════════════════════════════
if uploaded.type == "application/pdf":
    if "_pdf" not in st.session_state:
        with st.spinner("📄 Reading PDF pages …"):
            doc   = fitz.open(stream=uploaded.read(), filetype="pdf")
            pages = [Image.open(io.BytesIO(p.get_pixmap(dpi=180).tobytes("png"))) for p in doc]
            st.session_state["_pdf"] = pages

    pages = st.session_state["_pdf"]
    total = len(pages)
    done  = sum(1 for i in range(total) if has_s1(pk(i)))

    # Add to history
    ts = now.strftime("%d %b %Y, %I:%M %p")
    add_to_history(uploaded.name, "pdf", uploaded.size/1024, total, ts)

    # Progress header
    hd_col, btn_col = st.columns([3, 1])
    with hd_col:
        pct = done/total if total else 0
        st.markdown(
            f'<div style="font-family:\'Source Serif 4\',serif;font-size:0.86rem;color:var(--ink2);margin-bottom:5px;">'
            f'<strong>{done}</strong> of <strong>{total}</strong> pages analysed</div>',
            unsafe_allow_html=True)
        st.markdown(
            f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct*100:.0f}%"></div></div>',
            unsafe_allow_html=True)
        if done == total and total > 0:
            timings = [st.session_state[pk(i)].get("timing",{}).get("total",0)
                       for i in range(total) if has_s1(pk(i))]
            avg_t = sum(timings)/len(timings) if timings else 0
            st.success(f"✅ All {total} pages complete — {total*10} MCQs ready · avg {avg_t:.1f}s/page")
    with btn_col:
        analyse_all = st.button(f"🚀 Analyse All {total} Pages", use_container_width=True)

    if analyse_all:
        pending = [i for i in range(total) if not has_s1(pk(i))]
        if pending:
            prog = st.progress(0, text="Analysing pages …")
            for step, i in enumerate(pending, 1):
                prog.progress(step/len(pending), text=f"Analysing page {i+1}/{total} …")
                st.session_state[pk(i)] = run_stage1_silent(pages[i], ocr_engine)
            prog.empty()
            st.rerun()

    for i, img in enumerate(pages):
        key = pk(i)
        # Page separator
        st.markdown(f"""<div class="page-sep">
          <div class="page-sep-line"></div>
          <div class="page-sep-label">📄 Page <span>{i+1}</span> of {total}</div>
          <div class="page-sep-line"></div>
        </div>""", unsafe_allow_html=True)

        # Status + timing
        if has_s1(key):
            t = st.session_state[key].get("timing",{}).get("total",0)
            tc = _speed_class(t)
            st.markdown(f'<span class="page-chip done">✓ Analysed</span>&nbsp;&nbsp;<span class="time-badge {tc}">⏱ {t:.2f}s</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="page-chip pending">⏳ Pending analysis</span>', unsafe_allow_html=True)

        # Page image
        st.markdown('<div class="page-img-wrap">', unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if has_s1(key):
            render_page(key, exam_type, language_choice, eff_qtype)
        else:
            pc, _ = st.columns([1, 3])
            with pc:
                if st.button(f"🚀 Analyse Page {i+1}", key=f"abtn_{i}", use_container_width=True):
                    with st.spinner(f"Analysing page {i+1} …"):
                        st.session_state[key] = run_stage1_silent(img, ocr_engine)
                    st.rerun()
            st.markdown(
                '<div style="text-align:center;padding:1rem;font-family:\'Source Serif 4\',serif;'
                'font-size:0.84rem;color:var(--ink3);font-style:italic;">Click above to analyse this page.</div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# IMAGE FLOW
# ════════════════════════════════════════════════════════════════════
else:
    img = Image.open(uploaded)
    key = pk(0)

    ts = now.strftime("%d %b %Y, %I:%M %p")
    add_to_history(uploaded.name, "image", uploaded.size/1024, 1, ts)

    img_c, ctrl_c = st.columns([2, 1])
    with img_c:
        st.markdown('<div class="page-img-wrap">', unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ctrl_c:
        st.markdown("""<div class="how-card">
          <div class="how-title">How it works</div>
          <div class="how-step">
            1. Click Analyse — OCR + AI extraction runs<br>
            2. ⏱ Response time tracked (OCR + AI split)<br>
            3. Summary, key points &amp; entities shown<br>
            4. 10 MCQs generated from this page's facts<br>
            5. Upload history saved in sidebar<br>
            6. Change language/type → MCQs refresh instantly
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🚀 Analyse", use_container_width=True, key="analyse_img"):
            with st.spinner("Analysing …"):
                st.session_state[key] = run_stage1_silent(img, ocr_engine)
            st.rerun()

        if has_s1(key):
            m = st.session_state[key].get("model_used","—")
            t = st.session_state[key].get("timing",{}).get("total",0)
            tc = _speed_class(t)
            st.markdown(f'<div class="status-ok" style="margin-top:0.5rem;">✓ Analysed · {m}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="time-badge {tc}" style="margin-top:6px;">⏱ {t:.2f}s total</div>', unsafe_allow_html=True)

    if has_s1(key):
        st.markdown('<div style="margin-top:1.2rem;"></div>', unsafe_allow_html=True)
        render_page(key, exam_type, language_choice, eff_qtype)
    else:
        st.markdown("""<div style="text-align:center;padding:2rem;
          font-family:'Source Serif 4',serif;font-size:0.9rem;color:var(--ink3);font-style:italic;
          background:var(--white);border:1px solid var(--col);border-radius:4px;margin-top:1rem;">
          Click <strong>🚀 Analyse</strong> to begin extracting content from this newspaper page.
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════
st.markdown("""<div class="app-footer">
 Newspaper UI Edition · Per-page MCQs · ⏱ Response Timing · 📂 Upload History · 🇮🇳 Bhashini · Streamlit + Groq AI
</div>""", unsafe_allow_html=True)