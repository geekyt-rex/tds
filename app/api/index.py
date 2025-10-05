from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from pathlib import Path
import os

# Initialize the FastAPI app
app = FastAPI()

# Enable CORS to allow POST requests from any origin.
# This is crucial for dashboard integrations.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"], # Allows POST and OPTIONS methods
    allow_headers=["*"],  # Allows all headers
)

# --- Data Loading ---
# Construct a path to the jk.json file located in the project root.
# Vercel places the root directory one level above the 'api' folder.
data_path = Path(__file__).parent.parent / 'jk.json'
df = pd.read_json(data_path)

# --- Pydantic Model for Request Body ---
# This defines the expected structure of the incoming JSON POST request.
class TelemetryRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

# --- API Endpoint ---
@app.post("/api")
def get_latency_metrics(request: TelemetryRequest):
    """
    This endpoint processes telemetry data for specified regions.
    It calculates and returns key metrics based on a latency threshold.
    """
    results = {}
    for region in request.regions:
        # Filter the DataFrame for the current region
        region_df = df[df['region'] == region]

        if not region_df.empty:
            # Calculate metrics
            avg_latency = region_df['latency_ms'].mean()
            p95_latency = region_df['latency_ms'].quantile(0.95)
            avg_uptime = region_df['uptime_percent'].mean()
            breaches = int((region_df['latency_ms'] > request.threshold_ms).sum())

            # Store results for the region
            results[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 2),
                "breaches": breaches
            }
    return results
