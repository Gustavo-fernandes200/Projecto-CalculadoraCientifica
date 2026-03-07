# Calculadora Científica — Flet App

## Overview
A scientific calculator built with Python and the Flet framework (Flutter-based UI for Python). Features standard and scientific modes with history stored in DuckDB.

## Architecture
- **Framework**: Flet 0.82.0 (Flutter web app served via FastAPI/uvicorn)
- **UI**: Flutter web (WASM + WebSocket-based protocol)
- **Math engine**: SymPy (symbolic math) + Python math (fast path)
- **History storage**: DuckDB

## Project Structure
```
src/
  main.py        - Entry point: exports ASGI app + runs uvicorn on port 5000
  Calculadora.py - All UI components, calculator logic, history DB
src/assets/      - Static assets (favicon, icons)
pyproject.toml   - Project metadata and Python dependencies
```

## Running
- **Workflow**: `python src/main.py` on port 5000 (webview)
- The app uses WebSockets for real-time UI updates between Python backend and Flutter frontend

## Key Notes
- Flet uses binary msgpack WebSocket frames for UI protocol
- `RemoveRestrictiveHeaders` middleware strips COEP/COOP headers so the app works inside Replit's iframe-based preview
- History is stored in a DuckDB file in the app's working directory
- Deployment target: `vm` (needs persistent WebSocket connections)

## Dependencies
- flet >= 0.82.0
- sympy >= 1.14.0
- duckdb >= 1.4.4
- uvicorn (installed with flet)
