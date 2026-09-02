from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml.inference.multihorizon_gru_inference import MultiHorizonGRUInference


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "multihorizon_gru.pt"

app = FastAPI(title="SIH26153 Network Attack Forecasting API")

model = MultiHorizonGRUInference(str(MODEL_PATH))


class PredictRequest(BaseModel):
    sequence: list[list[float]] = Field(
        ...,
        description="Exactly 100 consecutive flow rows with exactly 68 features each.",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model-status")
def model_status():
    return {
        "loaded": True,
        "model": type(model.model).__name__,
        "horizons": model.horizons,
        "thresholds": model.thresholds,
    }


@app.post("/predict")
def predict(request: PredictRequest):
    rows = len(request.sequence)

    if rows != 100:
        raise HTTPException(
            status_code=422,
            detail=f"Expected exactly 100 rows, got {rows}",
        )

    for index, row in enumerate(request.sequence):
        if len(row) != 68:
            raise HTTPException(
                status_code=422,
                detail=f"Row {index} must contain exactly 68 features, got {len(row)}",
            )

    try:
        return model.predict(request.sequence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc