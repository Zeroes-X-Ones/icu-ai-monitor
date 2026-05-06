# ICU AI Monitor — Phase 1

**AI-Assisted ICU Physiological Monitoring and Medical Summarizer**

A real-time ICU dashboard that simulates patient vitals, detects physiological distress, analyzes trends, and generates AI clinical summaries.

---

## Project Structure

```
icu-ai-monitor/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI application entry
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── vitals.py            # REST endpoints for vitals
│   │   │   │   ├── websockets.py        # WebSocket stream implementation
│   │   │   │   └── analysis.py          # AI analysis endpoints
│   │   ├── services/
│   │   │   ├── vitals_generator.py      # Simulates patient vitals
│   │   │   ├── vitals_service.py        # Database operations for vitals
│   │   │   ├── distress_detector.py     # Advanced distress scoring (0-100)
│   │   │   ├── trend_analysis.py        # Linear trend detection
│   │   │   ├── medical_summarizer.py    # Generates clinical summaries
│   │   │   ├── ai_engine.py             # Core AI/LLM integration
│   │   │   └── intelligence_service.py  # Orchestrates AI workflows
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── dashboard/               # Core dashboard components
    │   │   │   ├── Overview.jsx         # Main dashboard view
    │   │   │   ├── HistoryView.jsx      # Historical data table
    │   │   │   ├── IntelligencePanel.jsx# AI insights and summaries
    │   │   │   ├── AlertPanel.jsx       # Real-time alert feed
    │   │   │   └── ... (Vital views)
    │   │   ├── layout/                  # Navigation and structural elements
    │   │   ├── ui/                      # Reusable UI components
    │   │   └── charts/                  # Reusable Chart.js components
    │   ├── pages/
    │   │   └── Dashboard.jsx            # Main dashboard layout
    │   ├── services/
    │   │   └── api.js                   # WebSocket + REST client
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css                    # Tailwind CSS imports
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Quick Start

### 1. Backend Setup

```bash
cd icu-ai-monitor/backend

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
python run.py
```

Backend runs at: **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

---

### 2. Frontend Setup

```bash
cd icu-ai-monitor/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/vitals/latest` | Latest vitals + distress score |
| GET | `/api/v1/vitals/history` | Historical vital readings |
| GET | `/api/v1/vitals/session-start`| Timestamp of monitoring start |
| GET | `/api/v1/vitals/alerts` | Active medical alerts |
| GET | `/api/v1/analysis/summary` | AI-generated clinical summary |
| WS  | `/api/v1/ws/stream` | Real-time vitals stream (2s interval) |

---

## Distress Scoring Logic (Advanced 0-100 Scale)

| Vital / Condition | Value Range | Score Added | Reasons / Impact |
|-------------------|-------------|-------------|------------------|
| **SpO₂** | < 90% | +40 | Severe oxygen drop |
| | < 94% | +25 | Low oxygen |
| **Heart Rate** | > 120 bpm | +25 | High HR |
| | > 100 or < 60 bpm | +15 | Abnormal HR |
| **Respiratory Rate** | > 28 br/min | +20 | High respiratory rate |
| | > 24 br/min | +10 | Elevated respiratory rate |
| **Blood Pressure (Sys)** | > 150 mmHg | +15 | High BP |
| | > 130 mmHg | +10 | Elevated BP |
| **Trend** | Worsening | +15 | Condition worsening |
| | Improving | -10 | Condition improving |

*(Scores are accumulated and clamped between 0 and 100)*

| Score Range | Risk Level |
|-------------|------------|
| 0 – 34 | NORMAL |
| 35 – 69 | WARNING |
| 70 – 100 | CRITICAL |

---

## Frontend Deployment (Vercel)

1. Set environment variables in Vercel:
   ```
   VITE_API_URL=https://your-backend-url.com
   VITE_WS_URL=wss://your-backend-url.com
   ```
2. Set root directory to `frontend/`
3. Build command: `npm run build`
4. Output directory: `dist`

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, WebSockets, SQLAlchemy
- **Frontend**: React 18, Vite, Chart.js, react-chartjs-2, React Router
- **Styling**: Tailwind CSS, Lucide React (Icons)

---

> ⚠️ **DISCLAIMER**: This system is a Phase-1 prototype for demonstration and educational purposes only.  
> It is **NOT** intended for clinical use, medical decision-making, or patient care.
