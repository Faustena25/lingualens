<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=40&pause=1000&color=1F3864&center=true&vCenter=true&width=600&lines=LinguaLens+%F0%9F%94%8D;Multilingual+Sentiment+AI;For+700M+Indian+Voices" alt="LinguaLens" />

<br/>

# 🔍 LinguaLens
### An Explainable and Bias-Aware Multilingual Sentiment Analysis Web Platform for Indian Code-Switched Text

<br/>

> *"For 700 million Indians who express themselves in Tanglish, Hinglish, Tenglish, and Manglish every day —*
> *LinguaLens is the first system that actually understands what they are saying."*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Google Colab](https://img.shields.io/badge/Google_Colab-T4_GPU-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=black)](https://colab.research.google.com)
[![License](https://img.shields.io/badge/License-MIT-28a745?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In_Development-dc3545?style=for-the-badge)]()

<br/>

</div>

---

## 🌍 The Problem No One Is Talking About

Every day, **700 million Indians** express their opinions online. But they do not write in pure Tamil or pure Hindi. They write like this:

```
"dei this phone battery romba worst da bro"        → Tanglish
"yaar ye product bahut bakwaas hai"                → Hinglish  
"bro ee movie chala boring gaa undi"               → Tenglish
"mone ee phone okke mosham aayirunnu"              → Manglish
```

And every major sentiment tool — **Google NLP, AWS Comprehend, IBM Watson, VADER** — reads these as broken English and gives you completely wrong results.

Words like **romba** (very), **bakwaas** (terrible), **adipoli** (awesome), and **baagundi** (good) — the words that carry all the emotion — get silently thrown away.

**LinguaLens fixes that.**

---

## ✨ What Makes LinguaLens Different

<div align="center">

| Capability | Google NLP | AWS Comprehend | VADER | **LinguaLens** |
|:---|:---:|:---:|:---:|:---:|
| Reads Tanglish correctly | ❌ | ❌ | ❌ | ✅ |
| Reads Hinglish correctly | ❌ | ❌ | ❌ | ✅ |
| Reads Tenglish correctly | ❌ | ❌ | ❌ | ✅ |
| Reads Manglish correctly | ❌ | ❌ | ❌ | ✅ |
| YouTube auto-fetch | ❌ | ❌ | ❌ | ✅ |
| Explains predictions (SHAP) | ❌ | ❌ | ❌ | ✅ |
| Bias audit across languages | ❌ | ❌ | ❌ | ✅ |
| Free and open source | ❌ | ❌ | ✅ | ✅ |

</div>

---

## 🎯 Features

<table>
<tr>
<td width="50%">

### 🎬 YouTube Auto-Analysis
Paste any YouTube video link. LinguaLens automatically fetches all comments via the YouTube Data API v3 and analyses every single one. No copy-paste. No manual work.

</td>
<td width="50%">

### 📄 Universal CSV Upload
Scraped reviews from Amazon, Flipkart, Instagram, Facebook, Twitter? Upload as CSV. LinguaLens analyses any platform's data.

</td>
</tr>
<tr>
<td width="50%">

### 🤖 Multilingual AI Model
XLM-RoBERTa — fine-tuned on Indian code-switched benchmark datasets — classifies every comment as **Positive**, **Negative**, or **Neutral** with a confidence score.

</td>
<td width="50%">

### 😊 Emotion Detection
Beyond positive/negative — LinguaLens detects **Joy**, **Anger**, **Sadness**, **Fear**, and **Surprise** in every comment using distilroberta-base.

</td>
</tr>
<tr>
<td width="50%">

### 💡 SHAP Explainability
Not a black box. LinguaLens shows you **exactly which words** drove each sentiment prediction — colour-coded, word by word.

```
"romba worst da"
 ^^^^^^ ^^^^^ 
  -0.89  -0.74   → Negative drivers
```

</td>
<td width="50%">

### ⚖️ Bias Audit Panel
LinguaLens checks whether it treats all Indian language groups **fairly** — computing differential F1 scores for Tamil, Hindi, Telugu, and Malayalam comments separately. If the gap exceeds 10%, it raises a fairness warning.

</td>
</tr>
<tr>
<td width="50%">

### 📊 Interactive Dashboard
Chart.js visualisations — sentiment donut chart, emotion radar chart, language distribution bar chart — all updating in real time from live API data.

</td>
<td width="50%">

### 📜 Analysis History
Every analysis is saved to SQLite. Browse, search, filter by sentiment or platform, and delete records. Full history at your fingertips.

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│          Browser · Bootstrap 5 · Vanilla JS · Chart.js         │
│   ┌────────────────────┐        ┌──────────────────────────┐   │
│   │   YouTube URL      │        │   CSV File Upload        │   │
│   │   (Auto-fetch)     │        │   (Any Platform)         │   │
│   └──────────┬─────────┘        └────────────┬─────────────┘   │
└──────────────┼──────────────────────────────-┼─────────────────┘
               │         HTTP POST/GET          │
               └────────────────┬──────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                     FLASK REST API                              │
│     POST /api/analyze · GET /api/history · DELETE /api/history  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   SOURCE DETECTOR     │
                    │   YouTube · Instagram │
                    │   Facebook · CSV      │
                    └───────────┬───────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      NLP PIPELINE                               │
│                                                                 │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │ Preprocessing│  │  XLM-RoBERTa     │  │ distilroberta     │  │
│  │ Emoji→Text  │  │  Sentiment:      │  │ Emotion:          │  │
│  │ URL Removal │  │  Pos/Neg/Neutral │  │ Joy/Anger/Sadness │  │
│  │ Script Detect│  │  + Confidence    │  │ Fear/Surprise     │  │
│  │ Lang Tagging │  └──────────────────┘  └───────────────────┘  │
│  └─────────────┘                                                │
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │  SHAP Explainability    │  │  Bias Audit                  │  │
│  │  Token-level attribution│  │  F1 per language group       │  │
│  │  Word-level highlights  │  │  Fairness flag if gap > 10%  │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     SQLite DB         │
                    │  analyses · comments  │
                    │  sentiment_details    │
                    └───────────────────────┘
```

---

## 🗣️ Languages Supported

<div align="center">

| Language Pair | Name | Speakers | Example |
|:---|:---:|:---:|:---|
| Tamil + English | **Tanglish** | 80M+ | *"romba super da bro climax"* |
| Hindi + English | **Hinglish** | 500M+ | *"yaar bahut acha tha yeh movie"* |
| Telugu + English | **Tenglish** | 85M+ | *"bro chala boring gaa undi story"* |
| Malayalam + English | **Manglish** | 35M+ | *"adipoli aayirunnu bro ee movie"* |

</div>

---

## 🗃️ Datasets Used

| Dataset | Language | Size | Source |
|:---|:---:|:---:|:---:|
| [SemEval-2020 Task 9](https://github.com/kmi-linguistics/SemEval-2020-Task-9) | Hinglish | 14,000 tweets | GitHub / CodaLab |
| [TamilMixSentiment](https://huggingface.co/datasets/community-datasets/tamilmixsentiment) | Tanglish | 15,744 comments | HuggingFace / Kaggle |
| [DravidianCodeMix](https://github.com/bharathichezhiyan/DravidianCodeMix-Dataset) | Manglish + Tenglish | 20,000+ comments | GitHub / Zenodo |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|:---|:---|
| **AI Model** | XLM-RoBERTa (sentiment) · distilroberta-base (emotion) |
| **Explainability** | SHAP (SHapley Additive exPlanations) |
| **Backend** | Python 3.10 · Flask 3.x · Flask-CORS |
| **Frontend** | HTML5 · CSS3 · Bootstrap 5 · Chart.js · Vanilla JS |
| **Database** | SQLite3 |
| **Data** | Pandas · NumPy · langdetect · emoji |
| **ML** | PyTorch · HuggingFace Transformers · scikit-learn |
| **YouTube** | google-api-python-client (YouTube Data API v3) |
| **Development** | Google Colab T4 GPU · VS Code · pyngrok |

</div>

---

## 📁 Project Structure

```
lingualens/
│
├── 📂 backend/
│   ├── app.py                  ← Flask REST API
│   ├── scraper.py              ← YouTube API + CSV reader
│   ├── preprocess.py           ← Text cleaning + language detection
│   ├── model.py                ← XLM-RoBERTa + emotion model
│   ├── explainer.py            ← SHAP integration
│   ├── bias_audit.py           ← Differential F1 computation
│   └── requirements.txt
│
├── 📂 frontend/
│   ├── templates/
│   │   ├── index.html          ← Home page (URL input + CSV upload)
│   │   ├── results.html        ← Results dashboard
│   │   └── history.html        ← Analysis history
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── main.js
│           ├── results.js
│           └── history.js
│
├── 📂 database/
│   └── schema.sql              ← SQLite schema
│
├── 📂 data/
│   └── datasets/               ← SemEval, TamilMixSentiment, DravidianCodeMix
│
├── 📂 notebooks/
│   └── LinguaLens_Main.ipynb   ← Google Colab development notebook
│
├── 📂 docs/
│   └── report/                 ← Project documentation
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.10+
Google Cloud Console account (for YouTube API key)
Google Colab account (for GPU inference)
```

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/lingualens.git
cd lingualens
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Set Up YouTube API Key
```bash
# Go to console.cloud.google.com
# Enable YouTube Data API v3
# Create API key and save it

export YOUTUBE_API_KEY="your_api_key_here"
```

### 4. Run on Google Colab (Recommended — Free GPU)
```python
# Open notebooks/LinguaLens_Main.ipynb in Google Colab
# Set runtime to T4 GPU
# Run all cells
# Copy the ngrok URL and open in browser
```

### 5. Run Locally (No GPU)
```bash
python backend/app.py
# Open http://localhost:5000
```

---

## 📊 Expected Accuracy

| Language Pair | Expected F1 | Training Data |
|:---|:---:|:---:|
| Hinglish | 75 – 82% | 14,000 samples |
| Tanglish | 68 – 75% | 15,744 samples |
| Manglish | 62 – 70% | ~8,000 samples |
| Tenglish | 58 – 67% | ~6,000 samples |

> **Note:** Lower accuracy for Manglish and Tenglish is a known limitation due to limited labelled training data — a documented gap in Indian NLP research. The bias audit panel makes this visible and auditable.

---

## 👥 Team

<div align="center">

| | Name | Role | Register No. |
|:---:|:---|:---|:---:|
| 👩‍💻 | **Faustena S** | Backend · AI · NLP Pipeline · SHAP · Bias Audit · Flask API | 2548313 |
| 👨‍💻 | **Vishwa Karthick S** | Frontend · UI/UX · Database · Chart.js · Documentation | 2548342 |

**Guide:** Dr. Gayathry S Warrier
**Institution:** CHRIST (Deemed to be University), Bangalore Yeshwanthpur Campus
**Programme:** Master of Data Science
**Academic Year:** 2026 – 2027

</div>

---

## 📚 References

1. Patwa, P. et al. (2020). *SemEval-2020 Task 9: Sentiment Analysis of Code-Mixed Tweets.* SemEval-2020.
2. Chakravarthi, B. R. et al. (2020). *Corpus Creation for Sentiment Analysis in Code-Mixed Tamil-English Text.* WILDRE-5.
3. Conneau, A. et al. (2020). *Unsupervised Cross-lingual Representation Learning at Scale.* ACL 2020.
4. Lundberg, S. M. & Lee, S. I. (2017). *A Unified Approach to Interpreting Model Predictions.* NeurIPS 2017.
5. Suryawanshi, S. et al. (2020). *DravidianCodeMix: Sentiment Analysis for Dravidian Languages.* WILDRE-5.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for 700 million Indian voices that deserve to be understood.**

<br/>

*LinguaLens · CHRIST (Deemed to be University) · 2026*

<br/>

⭐ **If this project helped you, please give it a star!** ⭐

</div>
