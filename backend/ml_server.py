"""FastAPI server to manage and serve the sentiment model.

Endpoints:
- GET  /status           -> model status
- POST /load            -> { "model_dir": "models/roberta-sentiment" }
- POST /unload          -> unload model from memory
- POST /predict         -> { "text": "..." }

Run with: `uvicorn ml_server:app --host 0.0.0.0 --port 8001`
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Sentiment ML Server")

try:
    from services.sentiment_service import init as svc_init, unload as svc_unload, status as svc_status, predict as svc_predict
except Exception:
    svc_init = svc_unload = svc_status = svc_predict = None


class LoadRequest(BaseModel):
    model_dir: Optional[str] = "models/roberta-sentiment"


class PredictRequest(BaseModel):
    text: str


@app.get("/status")
def status():
    if svc_status is None:
        return {"available": False, "message": "sentiment_service unavailable"}
    return svc_status()


@app.post("/load")
def load_model(req: LoadRequest):
    if svc_init is None:
        raise HTTPException(status_code=500, detail="sentiment_service not available")
    try:
        svc_init(req.model_dir)
        return {"loaded": True, "model_dir": req.model_dir}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unload")
def unload_model():
    if svc_unload is None:
        raise HTTPException(status_code=500, detail="sentiment_service not available")
    svc_unload()
    return {"unloaded": True}


@app.post("/predict")
def predict(req: PredictRequest):
    if svc_predict is None:
        raise HTTPException(status_code=500, detail="sentiment_service not available")
    try:
        label, score = svc_predict(req.text)
        return {"label": label, "score": score}
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""FastAPI server to manage the sentiment model lifecycle and inference.

Endpoints:
- `GET /status` -> returns model status
- `POST /load` -> loads model from provided `model_dir` (json body: {"model_dir": "..."})
- `POST /unload` -> unloads model
- `POST /predict` -> body: {"text": "..."} -> returns {label, score}

Run with: `uvicorn ml_server:app --host 0.0.0.0 --port 9000`
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services import sentiment_service


class LoadRequest(BaseModel):
    model_dir: str


class PredictRequest(BaseModel):
    text: str


app = FastAPI(title="Sentiment Model Server")


@app.get("/status")
def get_status():
    return sentiment_service.status()


@app.post("/load")
def load_model(req: LoadRequest):
    try:
        sentiment_service.init(req.model_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return sentiment_service.status()


@app.post("/unload")
def unload_model():
    sentiment_service.unload()
    return sentiment_service.status()


@app.post("/predict")
def predict(req: PredictRequest):
    try:
        label, score = sentiment_service.predict(req.text)
        return {"label": label, "score": score}
    except ImportError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
