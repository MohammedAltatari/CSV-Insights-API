"""CSV Insights API - instant data profiling for CSV files."""
import io

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="CSV Insights API",
    description="Upload a CSV file and get instant data profiling insights.",
    version="1.0.0",
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def read_csv(file: UploadFile) -> pd.DataFrame:
    """Validate the uploaded file and load it into a DataFrame."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is larger than 5 MB.")
    try:
        return pd.read_csv(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse the CSV file.") from None


@app.get("/")
def root():
    return {"service": "CSV Insights API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = await read_csv(file)
    return {
        "file_name": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_types": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
        "duplicate_rows": int(df.duplicated().sum()),
    }


@app.post("/missing")
async def missing(file: UploadFile = File(...)):
    df = await read_csv(file)
    total = len(df)
    result = {}
    for col in df.columns:
        count = int(df[col].isna().sum())
        result[str(col)] = {
            "missing_count": count,
            "missing_percent": round(count / total * 100, 2) if total else 0.0,
        }
    return {"file_name": file.filename, "total_rows": total, "missing": result}


@app.post("/stats")
async def stats(file: UploadFile = File(...)):
    df = await read_csv(file)
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise HTTPException(status_code=422, detail="No numeric columns found.")
    result = {}
    for col in numeric.columns:
        s = numeric[col].dropna()
        if s.empty:
            result[str(col)] = {"count": 0}
            continue
        result[str(col)] = {
            "count": int(s.count()),
            "mean": round(float(s.mean()), 2),
            "median": round(float(s.median()), 2),
            "std": round(float(s.std()), 2) if s.count() > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
        }
    return {"file_name": file.filename, "numeric_columns": len(result), "stats": result}
