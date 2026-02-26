# Calculadora Científica

A scientific calculator web application built with Python and the Flet UI framework.

## Project Overview

A multi-mode scientific calculator supporting:
- Standard mode
- Scientific mode
- Graphing mode
- Programmer mode
- Date mode

## Tech Stack

- **Language**: Python 3.10
- **UI Framework**: Flet (v0.81.0) — runs as a web app
- **Math Engine**: SymPy (symbolic computation)

## Project Structure

```
src/
  main.py          - Application entry point, launches Flet web server on port 5000
  Calculadora.py   - Calculator logic, configuration, and UI components
  assets/
    icon.png
    splash_android.png
```

## Running the App

The app runs via the "Start application" workflow:
```
python src/main.py
```

This starts a Flet web server on `0.0.0.0:5000`.

## Deployment

Configured for VM deployment:
- Run command: `python src/main.py`
- The app maintains persistent WebSocket connections (required by Flet)
