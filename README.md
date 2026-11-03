# MP2 REST API

A FastAPI application that wraps the MP1 data pipeline in a REST API. Clients upload a CSV (`POST /upload`), which is stored in memory with an integer ID; retrieve stored rows with an optional `limit` (`GET /datasets/{id}`); and validate and clean a stored dataset by sending a JSON configuration to `POST /datasets/{id}/process`, which returns the number of rows removed by validation plus a cleaning report and replaces the stored data with the processed result. `GET /health` reports status and version. Middleware assigns every request an `X-Request-ID` and logs method, path, status, and duration at INFO/WARNING/ERROR by status class. Pydantic models define the request/response schemas, errors map to 400/404/422 responses, and pytest tests using `TestClient` cover the upload → process → retrieve workflow.

## Run

```bash
python -m venv venv && source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload   # docs at http://127.0.0.1:8000/docs
python -m pytest tests -v
```
