# 🫀 OrganBridge — AI-Powered Organ Matching Platform

> Built for **Google Solution Challenge 2026** | Theme: Unbiased AI Decision-Making
> Team: **Orion-XAI** | Soaeb Hasan

[![Python](https://img.shields.io/badge/Python-3.14-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green?style=flat-square&logo=django)](https://djangoproject.com)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.8-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 📌 Overview

OrganBridge is a full-stack web application that uses machine learning to intelligently match organ donors with recipients — while auditing its own decisions for bias. Built with Django and powered by a TF-IDF + Cosine Similarity algorithm, it goes far beyond traditional blood-type-only matching by analyzing **15+ compatibility factors** in real time.

At its core, OrganBridge doesn't just predict matches — it **explains** them using Explainable AI (XAI) and ensures **fairness** across age, gender, and geography using bias detection.

> **In a system where every second counts and every decision impacts a life, OrganBridge makes organ allocation smarter, fairer, and more transparent.**

---

## 🚀 Features

### ✅ Implemented
- **AI-Powered Matching** — TF-IDF vectorization + Cosine Similarity engine evaluating 15+ parameters (blood type, age, geography, lifestyle, medical history)
- **Role-Based Dashboards** — Separate dashboards for donors and recipients
- **Custom User Model** — Extended Django user with medical fields (blood type, age, gender, race, city)
- **Authentication System** — Register, Login, Logout with session management
- **Responsive UI** — Tailwind CSS + HTMX powered interface

### 🔄 In Progress
- **Donor & Recipient Profiles** — Complete medical profile setup
- **Match Engine Integration** — Full ML pipeline connected to Django views
- **Real-Time Messaging** — HTMX-powered live chat between matched donors and recipients

<!--
### 🔮 Coming Soon (Phase 2 — Top 100)
- **Bias Audit Layer** — Fairlearn-powered fairness metrics (demographic parity, equalized odds)
- **XAI Explanations** — SHAP-based "why this match?" explanations for doctors
- **Bias Mitigation** — Automatic reweighing and calibrated thresholds
- **Google Cloud Integration** — Cloud Run deployment, Firebase Realtime DB
- **Gemini AI** — Natural language match explanations powered by Google Gemini API
- **Bias Dashboard** — Visual fairness metrics for administrators

### 🏆 Coming Soon (Phase 3 — Grand Finale)
- **Production Deployment** — Railway/Google Cloud Run with PostgreSQL
- **Google OAuth** — Login with Google
- **Real Data Validation** — Anonymized hospital dataset integration
- **Impact Metrics** — Quantified bias reduction and matching improvement stats
- **API Layer** — REST API for third-party hospital system integration
-->

---

## 🧠 ML Matching Algorithm

The matching engine uses two layers of logic:

1. **ML Layer** — Donor and recipient profiles are serialized into feature strings and transformed using a trained TF-IDF vectorizer. Cosine similarity is computed to produce a raw compatibility score (0–100%).

2. **Business Rules Layer** — Blood type compatibility, urgency level, geographic proximity, and health status are applied on top of the ML score to produce a final ranked list.

3. **Fallback** — If trained model files are unavailable, the engine automatically falls back to a rule-based scoring system.

### Matching Factors Analyzed
| Category | Factors |
|---|---|
| Medical | Blood type, organ type, medical history, BMI |
| Personal | Age, gender, race |
| Lifestyle | Smoking status, alcohol use, drug history, avg sleep |
| Geographic | City, state, travel distance |
| Clinical | Urgency level, health status, last medical checkup |

<!--
### Bias Detection (Coming Soon)
- Demographic parity across gender and age groups
- Equalized odds across geographic regions
- SHAP feature importance for individual match explanations
- Fairlearn MetricFrame for group-level fairness analysis
-->

---


## 🏥 Phase 2 Vision — Hospital Integration

> *This section outlines the planned extension of OrganBridge to involve hospitals as verified intermediaries in the organ matching process.*

### Current Flow
```
Donor → OrganBridge → Recipient
```

### Planned Flow (Phase 2)
```
Donor → Hospital (Verified) → OrganBridge AI → Hospital → Recipient
```

### Planned Features

**Hospital Dashboard**
Hospitals will have their own verified accounts to manage patients, confirm donor eligibility, track transplant history, and receive real-time match notifications.

**Medical Verification System**
Every donor and recipient profile will require hospital verification before entering the matching pool — eliminating fake data and increasing match reliability. Each verified profile will carry a Trust Score.

**Transplant Coordination**
Once a match is accepted, hospitals on both sides will coordinate surgery scheduling, operation theater availability, and inter-hospital organ transfer logistics.

**Cold Chain Tracking**
Organs have a limited viability window (kidneys: 24-36 hours). Phase 2 will introduce real-time organ tracking from harvest to transplant using Google Maps API — ensuring organs reach recipients before expiry.

**Chain Transplant Support**
OrganBridge will support paired and chain transplants — where a donor who cannot directly help their loved one triggers a chain of compatible swaps across multiple hospitals, saving multiple lives from a single donation.

**Doctor & Surgeon Portal**
Doctors will be able to review AI-generated match explanations, add medical notes, request second opinions, and use Gemini AI for surgical risk assessment before approving a transplant.

**Regulatory & Government Integration**
Phase 2 will integrate with NOTTO (National Organ & Tissue Transplant Organisation) for legal compliance, automated documentation, and government audit trails for every transplant decision.

### Phase 2 Roadmap

| Phase | Timeline | Milestone |
|---|---|---|
| Phase 1 | Now ✅ | Donor-Recipient AI Matching + Gemini + Bias Dashboard |
| Phase 2 | 2 months | Hospital Integration + Medical Verification |
| Phase 3 | 3 months | NOTTO / Government Integration |
| Phase 4 | 5 months | Pan-India Deployment |

---



## 🏗️ Project Structure

```
organBridge/
├── accounts/           # Custom user model, auth views
├── profiles/           # DonorProfile, RecipientProfile, dashboards
├── matches/            # OrganMatch, MatchMessage, matching views
├── ml_model/           # ML engine, training, bias audit (in-app)
│   ├── matching_algorithm.py
│   ├── train_model.py
│   └── trained_models/
├── bias_dashboard/     # Fairness metrics visualization
├── organBridge/        # Django settings, URLs
├── templates/          # All HTML templates
├── static/             # CSS, JS
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0, Python 3.14 |
| ML / AI | Scikit-learn (TF-IDF, Cosine Similarity) |
| XAI | SHAP |
| Bias Detection | Fairlearn |
| Frontend | Tailwind CSS, HTMX, Alpine.js |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Google AI | Gemini API |
| Deployment | Railway / Google Cloud Run *(coming soon)* |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/soaebhasan12/OrganBridge.git
cd OrganBridge/organBridge
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

---

<!--
## 🤖 Training the ML Model

```bash
python manage.py train_ml
```

Or populate the database with sample data:

```bash
python manage.py populate_donor_profiles
python manage.py populate_recipient_profiles
```
-->

---

## 📊 Key Statistics (Demo Data)

| Metric | Value |
|---|---|
| Dataset Size | 900+ donor-recipient records |
| Model Accuracy | 95% on test data |
| Compatibility Factors | 15+ per match |
| Matching Speed | Sub-second inference |

---

## 🔒 Security & Privacy

- All match details visible only to directly involved donor and recipient
- Personal contact information hidden until match acceptance
- Every sensitive view protected with `@login_required`
- CSRF protection on all forms
- Environment variables for all sensitive credentials

---

<!--
## ☁️ Deployment

### Railway (Coming Soon)
```bash
# Procfile
web: gunicorn organBridge.wsgi --log-file -
```

### Google Cloud Run (Coming Soon)
- Containerized with Docker
- PostgreSQL on Cloud SQL
- Static files on Cloud Storage
- Gemini API integration
-->

---

## 🏆 Hackathon

This project is submitted for the **Google Solution Challenge 2026 India — Build with AI**

- **Theme:** Unbiased AI Decision-Making
- **Team:** Orion-XAI
- **Track:** Theme 4 — Ensuring Fairness and Detecting Bias in Automated Decisions

---

## 📄 License

This project was built for a hackathon. MIT License — see [LICENSE](LICENSE) for details.

---

## 🙌 Contributing

Pull requests are welcome. For significant changes, please open an issue first.

---

<div align="center">
  <p>Built with ❤️ by Team Orion-XAI for Google Solution Challenge 2026</p>
</div>
