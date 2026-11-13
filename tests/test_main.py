"""Automated tests for the CSV Insights API."""
from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "sales_sample.csv"


def upload(endpoint: str, name: str = "sales_sample.csv", content: bytes | None = None):
    data = SAMPLE.read_bytes() if content is None else content
    return client.post(endpoint, files={"file": (name, data, "text/csv")})


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "CSV Insights API"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_sample():
    body = upload("/analyze").json()
    assert body["rows"] == 13
    assert body["columns"] == 8
    assert body["duplicate_rows"] == 1
    assert body["column_types"]["order_id"] == "int64"


def test_missing_sample():
    body = upload("/missing").json()
    assert body["total_rows"] == 13
    assert body["missing"]["total"] == {"missing_count": 2, "missing_percent": 15.38}
    assert body["missing"]["city"]["missing_count"] == 1
    assert body["missing"]["order_id"]["missing_count"] == 0


def test_stats_sample():
    body = upload("/stats").json()
    assert body["numeric_columns"] == 4
    total = body["stats"]["total"]
    assert total["count"] == 11
    assert total["mean"] == 22.77
    assert total["median"] == 20.0
    assert total["min"] == 3.0
    assert total["max"] == 48.0


def test_rejects_non_csv_file():
    response = upload("/analyze", name="data.txt")
    assert response.status_code == 400


def test_rejects_empty_file():
    response = upload("/analyze", content=b"")
    assert response.status_code == 400


def test_stats_without_numeric_columns():
    response = upload("/stats", content=b"name,city\nAli,Gaza\nSara,Rafah\n")
    assert response.status_code == 422
