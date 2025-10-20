# SCUM SQLite API

A lightweight FastAPI-based REST API to safely query the **SCUM.db** file from a running SCUM server.  
Designed for read-only access with multiple API keys, logging, and safe SQLite connection handling.

---

## 🚀 Features

- 🔒 **Read-only** access (no DB modifications)
- 🧠 **Multi-API key support** with labels (for tracking)
- 🪵 **Query logging** (writes to `Logs/api_log.txt`)
- ⚡ **Automatic retry** on locked databases
- 📂 **Configurable SCUM path** — works directly in your `Saved\SaveFiles` folder
- 🩺 `/ping` endpoint for health checks (anonym or authenticated)
- 🧰 **Self-contained setup** — just FastAPI, Uvicorn, and ORJSON

---

## 📦 Installation

Clone or copy the files into your SCUM `SaveFiles` directory:

```
D:\SERVER\SCUM\SCUM\Saved\SaveFiles\
```

Then run the startup script:

```bash
start_api.bat
```

The script will:
- Verify your Python installation  
- Install all required dependencies  
- Launch the FastAPI server (on port `8000` by default)

---

## 🧩 Example Usage

### Query via GET:
```bash
curl -X GET "http://localhost:8000/query?sql=SELECT+*+FROM+players+LIMIT+5" ^
     -H "x-api-key: AquariiNyx"
```

### Query via POST:
```bash
curl -X POST "http://localhost:8000/query" ^
     -H "Content-Type: application/json" ^
     -H "x-api-key: AquariiNyx" ^
     -d "{\"query\": \"SELECT * FROM players LIMIT 5\"}"
```

### Health Check:
```bash
curl -X GET "http://localhost:8000/ping"
```

Authenticated version (more info):
```bash
curl -X GET "http://localhost:8000/ping" -H "x-api-key: AquariiNyx"
```

---

## 🧾 Configuration

Inside `scum_api.py`:

```python
SCUM_PATH = r"D:\SERVER\SCUM\SCUM\Saved\SaveFiles"
API_KEYS = {
    "supersecret123": "internal",
    "AquariiNyx": "AquariiNyx",
    "dashboardKey": "dashboard",
}
```

You can change the SCUM folder path and API keys as needed.  
Logs are automatically created in `Logs/api_log.txt`.

---

## 🧠 Notes

- This API uses SQLite’s `mode=ro` (read-only) connection string,  
  ensuring no modification of the live `SCUM.db`.
- Each query is executed in a fresh connection and closed immediately.
- Logs contain only executed queries and their associated API key labels.
- `/ping` requests are **not logged** to avoid spam from health checks.

---

## 📜 License

MIT License © 2025 [Stefan Kögl (HellBz)](https://github.com/HellBz)

---

## ❤️ Credits

Developed by **Stefan Kögl (HellBz)**  
with support from **Synthia** 🤖
