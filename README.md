# SmartAds — Multilingual AI Advertising Platform for SMEs

SmartAds is an open-source web platform that lets small business owners produce
professional logos, posters, and video advertisements with voiceover using
product descriptions written in **Roman Urdu, Hindi, or English** — no design
skills or English fluency required.

> Developed as a Final Year Project at FAST-NUCES Chiniot-Faisalabad Campus.  
> Associated research paper submitted to *SoftwareX* (Elsevier).

---

## Features

| Module | Description |
|--------|-------------|
| **Role-based team access** | Owner creates sub-users and assigns only the features each needs |
| **Prompt normalization** | Gemini rewrites informal Roman Urdu/Hindi text into structured English cinematic prompts |
| **Logo & poster generation** | Imagen 4 generates brand visuals (1:1 logos, 3:4 posters) |
| **Video ads with voiceover** | Veo 3.1 produces 16:9 video ads with narration generated natively |
| **Caption generation** | Ready-to-post social media copy, auto-generated |
| **Social uploader & scheduler** | Publishes and schedules posts to connected social accounts |
| **Sentiment analysis** | Hybrid RoBERTa + likes-count engine labels feedback as positive / neutral / negative |
| **Analytics dashboard** | Tracks per-post sentiment trends over time with adjustable thresholds |

---

## Tech Stack

**Backend**
- Python 3.10+
- Flask (main REST API)
- FastAPI (sentiment microservice)
- PyTorch + HuggingFace Transformers (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
- MongoDB Atlas (metadata)
- Cloudinary (generated media storage)

**Frontend**
- React 18+ with Vite
- Tailwind CSS
- Google OAuth 2.0 + JWT authentication

**AI Services (Google Cloud)**
- Gemini — prompt normalization and caption generation
- Imagen 4 — logo and poster generation
- Veo 3.1 — video ad generation with native voiceover

---

## Prerequisites

- Python >= 3.10
- Node.js >= 18
- A Google Cloud account with Gemini, Imagen 4, and Veo 3.1 APIs enabled
- MongoDB Atlas connection string
- Cloudinary account credentials

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Javeria530/SmartAdsforSMEs.git
cd SmartAdsforSMEs
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

### 4. Environment variables

Create a `.env` file in the `backend/` directory:

```env
GOOGLE_API_KEY=your_google_cloud_api_key
MONGODB_URI=your_mongodb_atlas_connection_string
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
JWT_SECRET=your_jwt_secret_key
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
```

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:5000
VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id
```

---

## Running the Application

### Start the Flask REST API

```bash
cd backend
flask run --port 5000
```

### Start the Sentiment microservice (FastAPI)

```bash
cd backend
uvicorn sentiment_service:app --port 8000
```

### Start the React frontend

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`.

---

## Running Tests

The project includes a pytest/Vitest suite of 22 automated tests covering
authentication, the sentiment pipeline (thresholds, interpolation, weight
normalisation, batch error isolation, CSV processing), and the main React views.

### Backend tests

```bash
cd backend
pytest tests/ -v
```

### Frontend tests

```bash
cd frontend
npm run test
```

All 22 tests pass in the released version.

---

## Project Structure

```
SmartAdsforSMEs/
├── backend/
│   ├── app.py                  # Flask main application
│   ├── sentiment_service.py    # FastAPI sentiment microservice
│   ├── services/               # Adapter classes for each AI module
│   │   ├── gemini_service.py
│   │   ├── imagen_service.py
│   │   ├── veo_service.py
│   │   └── sentiment_adapter.py
│   ├── controllers/            # Flask route controllers
│   ├── models/                 # MongoDB data models
│   ├── tests/                  # pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.js              # Single API module (all endpoints)
│   │   ├── views/              # Five main view components
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Sentiment Scoring

The two-signal sentiment scorer fuses a RoBERTa text classifier with a
likes-count engagement heuristic:

```
s = α·sₜ + (1−α)·sₗ     α = 0.75 (default)
```

Where `sₜ ∈ [−1, 1]` is the text signal and `sₗ ∈ [0, 1]` is the engagement
signal. Both `α` and the likes thresholds (θ_L, θ_H) are configurable from
the analytics dashboard without touching code.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file
for details.

---

## Authors

- **Javeria Iqbal** — [nakhalsheikh4@gmail.com](mailto:nakhalsheikh4@gmail.com)  
  Department of Computer Science, FAST-NUCES Chiniot-Faisalabad
- **Dr. Anwar Shah** (Supervisor)  
  Department of AI and Data Science, FAST-NUCES Chiniot-Faisalabad
---

## Citation

If you use SmartAds in your research, please cite:

```
Iqbal, J., Shah, A. (2026). SmartAds: a multilingual AI advertising platform
for small and medium-sized enterprises. SoftwareX. Elsevier.
```

---

## Support

For questions or issues, contact: nakhalsheikh4@gmail.com
