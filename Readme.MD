# 📰 Newse Samachar (An AI Driven decision Support System) v8.1

AI-powered newspaper analyser for competitive exam preparation.  
OCR → AI extraction → Sentiment → 10 MCQs per page · 12 Indian languages.

## 🚀 Deploy on Streamlit Cloud (Free)

1. **Fork / push this repo to GitHub**

2. **Go to** [share.streamlit.io](https://share.streamlit.io) → *New app* → select your repo → `app.py`

3

   ```
   Get a free Groq key at [console.groq.com](https://console.groq.com)

4. Click **Deploy** — done!

> `packages.txt` installs Tesseract OCR automatically on Streamlit Cloud.

---

## 💻 Run Locally

```bash
pip install -r requirements.txt

# Set your key in the environment (no secrets.toml needed)
set GROQ_API_KEY=gsk_your_key_here        # Windows
export GROQ_API_KEY=gsk_your_key_here     # Mac/Linux

streamlit run app.py
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| Input | JPG, PNG, PDF (multi-page) |
| OCR | Tesseract → EasyOCR → Vision fallback |
| AI Models | Groq (Llama 3.1 / 3.3 / Llama 4) |
| Languages | English + 12 Indian languages via Bhashini |
| MCQ types | General, Vocabulary, Idioms, Mixed |
| Exam targets | SSC, Banking, Railway, Defence, UPSC, GK |
| MCQs per page | 10 questions with answers & explanations |

## 🔑 Key Fixes in v8.1

- Removed accidental nested `render_page()` definition that caused `NameError: some_list`
- Fixed `StreamlitDuplicateElementKey` — chart keys are now `chart_donut_page_N` / `chart_bar_page_N`
- API keys loaded from Streamlit secrets → env variable → fallback (no `secrets.toml` required for local dev)
