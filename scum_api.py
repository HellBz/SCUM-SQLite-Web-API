from fastapi import FastAPI, HTTPException, Query, Body, Header
from fastapi.responses import ORJSONResponse
import sqlite3
import re
import os
import time
import datetime

# === Basic configuration ===
# Just set the folder where your SCUM.db is located
SCUM_PATH = r"D:\SERVER\SCUM\SCUM\Saved\SaveFiles"

# Automatically build paths
DB_PATH = os.path.join(SCUM_PATH, "SCUM.db")
LOG_DIR = os.path.join(SCUM_PATH, "Logs")
LOG_FILE = os.path.join(LOG_DIR, "api_log.txt")

# Ensure that the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Define multiple API keys and their labels (for tracking)
API_KEYS = {
    "supersecret123": "internal",
    "AquariiNyx": "AquariiNyx",
    "dashboardKey": "dashboard",
}

# === Initialize FastAPI ===
app = FastAPI(
    title="SCUM SQLite API",
    version="1.4.1",
    description="Simple JSON API to query SCUM.db (read-only, safe mode, multi-key logging)",
    default_response_class=ORJSONResponse
)


# === Utility functions ===

def run_query(sql: str, params: tuple = (), retries: int = 3, delay: float = 0.5):
    """
    Execute a read-only SQL query and return results as list of dicts.
    Automatically retries if the database is temporarily locked.
    """
    last_exception = None
    for attempt in range(retries):
        try:
            # Open SQLite in read-only mode (safe for live servers)
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(sql, params)
            rows = cur.fetchall()
            conn.close()

            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                # Wait and retry if the DB is busy
                time.sleep(delay * (attempt + 1))
                last_exception = e
                continue
            else:
                raise HTTPException(status_code=400, detail=f"SQLite error: {str(e)}")

    # If all retries fail, raise an exception
    raise HTTPException(status_code=503, detail=f"Database is locked: {str(last_exception)}")


def is_select_query(sql: str) -> bool:
    """Allow only SELECT queries for safety."""
    return bool(re.match(r'^\s*SELECT\b', sql, re.IGNORECASE))


def check_api_key(x_api_key: str) -> str:
    """Validate API key and return its label (for logging)."""
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")
    return API_KEYS[x_api_key]


def log_query(sql: str, key_label: str):
    """Write query and API key info to SCUM's LOGS folder."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {key_label} ran: {sql}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# === Endpoints ===

@app.get("/query")
def query_get(
    sql: str = Query(..., description="SQL SELECT query"),
    x_api_key: str = Header(None, description="API Key for authentication")
):
    """Run a read-only SELECT query via GET."""
    key_label = check_api_key(x_api_key)
    if not is_select_query(sql):
        raise HTTPException(status_code=403, detail="Only SELECT queries are allowed.")

    result = run_query(sql)
    log_query(sql, key_label)

    return {"rows": result, "count": len(result), "api_key": key_label}


@app.post("/query")
def query_post(
    body: dict = Body(..., example={"query": "SELECT * FROM user LIMIT 10"}),
    x_api_key: str = Header(None, description="API Key for authentication")
):
    """Run a read-only SELECT query via POST with JSON body."""
    key_label = check_api_key(x_api_key)
    sql = body.get("query", "")
    if not sql:
        raise HTTPException(status_code=400, detail="Missing 'query' field in JSON.")
    if not is_select_query(sql):
        raise HTTPException(status_code=403, detail="Only SELECT queries are allowed.")

    result = run_query(sql)
    log_query(sql, key_label)

    return {"rows": result, "count": len(result), "api_key": key_label}


# === Health check endpoint ===

@app.get("/ping")
def ping(x_api_key: str = Header(None)):
    """Health check — minimal when anonymous, detailed when API key is valid."""
    info = {
        "status": "ok",
        "db_exists": os.path.exists(DB_PATH)
    }

    # Add more info only if valid API key is provided
    if x_api_key and x_api_key in API_KEYS:
        key_label = API_KEYS[x_api_key]
        info.update({
            "db_path": DB_PATH,
            "log_dir_exists": os.path.exists(LOG_DIR),
            "keys_available": list(API_KEYS.values()),
            "requested_by": key_label
        })

    return info
