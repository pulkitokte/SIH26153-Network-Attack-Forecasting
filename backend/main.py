from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.inference.multihorizon_gru_inference import MultiHorizonGRUInference


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "multihorizon_gru.pt"
TEST_SEQUENCE_PATH = BASE_DIR / "ml" / "processed" / "multihorizon_X_test.npy"

DEMO_TEST_INDEX = 1691
DEMO_WINDOW_ID = 17909
DEMO_EPISODE_ID = 20


app = FastAPI(title="SIH26153 Network Attack Forecasting API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/demo-sequence")
def demo_sequence():
    if not TEST_SEQUENCE_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Verified test sequence file was not found.",
        )

    try:
        test_sequences = np.load(TEST_SEQUENCE_PATH, allow_pickle=False)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load test sequence file: {exc}",
        ) from exc

    if test_sequences.ndim != 3:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected test tensor dimensions: {test_sequences.shape}",
        )

    if DEMO_TEST_INDEX >= len(test_sequences):
        raise HTTPException(
            status_code=500,
            detail=f"Demo test index {DEMO_TEST_INDEX} is outside the test tensor.",
        )

    sequence = test_sequences[DEMO_TEST_INDEX]

    if sequence.shape != (100, 68):
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected demo sequence shape: {sequence.shape}",
        )

    if not np.isfinite(sequence).all():
        raise HTTPException(
            status_code=500,
            detail="Demo sequence contains NaN or infinite values.",
        )

    return {
        "source": "CICIDS2017 held-out TEST sequence",
        "mode": "offline_demo",
        "window_id": DEMO_WINDOW_ID,
        "episode_id": DEMO_EPISODE_ID,
        "test_index": DEMO_TEST_INDEX,
        "observation_start_position": 38790,
        "observation_end_position": 38889,
        "observation_length": 100,
        "sequence": sequence.tolist(),
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