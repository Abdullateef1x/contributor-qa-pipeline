# 🚀 Contributor QA Pipeline

> A full-stack quality assurance system for AI training data, inspired by the real-world workflows used by AI data infrastructure companies like Hub.xyz.

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-Strict-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Supabase](https://img.shields.io/badge/Supabase-Hosted_DB-green)
![Cloudflare\_R2](https://img.shields.io/badge/Cloudflare-R2-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![Tests](https://img.shields.io/badge/Tests-13%20Passing-success)

🌐 **Live Demo:** https://your-vercel-url.vercel.app

📖 **API Docs:** https://your-railway-url.up.railway.app/docs

---

## 🎯 Project Overview

AI companies rely on massive contributor networks to collect audio, image, and video data.

Before this data can be used for model training, it must pass multiple quality checks:

* Is the file valid?
* Is it corrupted?
* Does it meet minimum quality requirements?
* Should it be flagged for human review?
* Is it suitable for AI training?

This project simulates that workflow.

Contributors upload files through the API, automated validation runs asynchronously, AI-powered quality analysis evaluates submissions, and results are surfaced through a dashboard.

---

## ⚙️ How the Pipeline Works

```text
Contributor Upload
        │
        ▼
Cloudflare R2 Storage
        │
        ▼
Background QA Processing
        │
        ├── File Validation
        ├── Quality Scoring
        ├── AI Analysis (Groq)
        │
        ▼
PostgreSQL (Supabase)
        │
        ▼
Dashboard + Analytics
```

### Step-by-Step

1️⃣ Contributor uploads an image, audio, or video file

2️⃣ File is stored in Cloudflare R2 (S3-compatible storage)

3️⃣ Background task starts automatically

4️⃣ Validation pipeline runs:

* File size validation
* MIME type validation
* Corruption detection
* Quality scoring

5️⃣ Groq LLM performs AI-powered assessment

6️⃣ Results are written to PostgreSQL

7️⃣ Dashboard updates automatically

---

## 📸 Screenshots

### Dashboard Overview

*Add screenshot here*

### Submission Detail

*Add screenshot here*

### Contributor Management

*Add screenshot here*

---

# 🏗️ Architecture

```text
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard
│   │   ├── Upload
│   │   ├── Contributors
│   │   └── Submissions
│   └── lib/
│       └── api.ts

backend/
├── app/
│   ├── routes/
│   │   ├── contributors.py
│   │   └── submissions.py
│   ├── services/
│   │   ├── qa.py
│   │   └── storage.py
│   ├── models/
│   └── db/
└── tests/
```

---

# 🛠️ Tech Stack

| Layer            | Technology                        |
| ---------------- | --------------------------------- |
| Backend          | FastAPI, Python, SQLAlchemy Async |
| Database         | PostgreSQL (Supabase)             |
| Storage          | Cloudflare R2                     |
| AI Analysis      | Groq Llama 3.1                    |
| Frontend         | React, TypeScript, Tailwind CSS   |
| Charts           | Recharts                          |
| State Management | TanStack Query                    |
| Testing          | Pytest                            |
| Deployment       | Railway + Vercel                  |

---

# 🚀 Getting Started

## Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest tests/ -v
```

### Current Coverage

✅ File validation

✅ Corrupt file detection

✅ QA score calculation

✅ Boundary condition testing

✅ API behavior

✅ Image validation

✅ Audio validation

**13 automated tests currently passing**

---

# 📊 Quality Scoring

| Score  | Status  |
| ------ | ------- |
| 0      | Invalid |
| 20     | Corrupt |
| 50-79  | Flagged |
| 80-100 | Passed  |

---

# 🤖 AI Analysis

The system uses:

```text
Groq
└── llama-3.1-8b-instant
```

The LLM evaluates:

* AI training suitability
* Quality concerns
* Potential issues
* PASS / FLAG / REJECT recommendation

### Why Groq?

⚡ Extremely low latency

⚡ Cost-effective

⚡ Suitable for high-volume pipelines

---

# 📡 API Endpoints

## Contributors

| Method | Endpoint               |
| ------ | ---------------------- |
| POST   | /api/contributors      |
| GET    | /api/contributors      |
| GET    | /api/contributors/{id} |

---

## Submissions

| Method | Endpoint                        |
| ------ | ------------------------------- |
| POST   | /api/submissions/upload         |
| GET    | /api/submissions                |
| GET    | /api/submissions/{id}           |
| GET    | /api/submissions/stats/overview |

---

# 🚢 Deployment

## Backend (Railway)

1. Connect GitHub repository
2. Set root directory to:

```text
backend
```

3. Add environment variables
4. Deploy

---

## Frontend (Vercel)

1. Connect GitHub repository
2. Set root directory:

```text
frontend
```

3. Configure API URL
4. Deploy

---

# 🎯 Design Decisions

## Why FastAPI BackgroundTasks Instead of Celery?

For MVP-scale workloads, BackgroundTasks provide:

✅ Lower operational complexity

✅ No Redis dependency

✅ Faster iteration

The architecture isolates processing logic, making migration to Celery straightforward when queue guarantees become necessary.

---

## Why Async SQLAlchemy?

File processing is heavily I/O-bound:

* Storage uploads
* Database operations
* LLM requests

Async operations prevent request blocking and improve throughput.

---

## Why Supabase Session Pooler?

The session pooler:

✅ Handles connection limits

✅ Improves reliability

✅ Matches production deployment patterns

---

## Why Cloudflare R2?

✅ S3-compatible

✅ No egress fees

✅ Easy migration path

✅ Local storage fallback

---

## Why Groq?

AI quality assessment should not become the bottleneck.

Groq provides:

⚡ Fast inference

⚡ Low latency

⚡ Cost efficiency

---

# 📈 Evaluation & Instrumentation

Each submission tracks:

* Processing time
* QA score
* Pass/Fail status
* AI recommendation

Metrics are aggregated into:

* Pass rate
* Average score
* Average processing time

This forms the foundation of an evaluation loop used to continuously monitor data quality.

---

# 🔮 Future Improvements

### Infrastructure

* Replace BackgroundTasks with Celery + Redis
* Add retry queues
* Add dead-letter queues

### Realtime

* Replace polling with WebSockets
* Live dashboard updates

### Analytics

* Contributor reputation scoring
* Quality drift detection
* Historical performance trends

### Storage

* Lifecycle policies
* Automated archival

### Observability

* OpenTelemetry tracing
* Queue monitoring
* Processing latency dashboards

---

# 👨‍💻 Author

**Abdullateef Alao**

🔗 GitHub: https://github.com/Abdullateef1x

🔗 LinkedIn: https://www.linkedin.com/in/abdullateef-alao-89926b31b/

📧 Email: [alaokeny05@gmail.com](mailto:alaokeny05@gmail.com)

---

⭐ If you found this project interesting, consider starring the repository.
