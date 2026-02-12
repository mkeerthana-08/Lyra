# Lyra - Cognitive Code Intelligence

Lyra is a Flask web app for code analysis and lightweight execution. It estimates time/space complexity, detects risks and edge cases, and surfaces strategy insights. A small ML model adds a quality label for Python code.

## Features

- Code analysis: cyclomatic complexity (Python), nested loop depth, time/space estimates.
- Risk and edge-case heuristics.
- Strategy detection and optimization suggestions.
- Built-in code execution for Python, Java, C, C++, and JavaScript.
- Chat assistant powered by Google Gemini API.

## How It Works (High-Level Steps)

1. User selects a language and submits code in the web UI.
2. The backend runs analysis in `analyzers/` and optional execution in `executor/`.
3. Results are rendered in the UI (complexity, risks, strategy, ML quality).
4. The chat widget calls `/chat` to generate responses from Gemini.

## Tech Stack

- Backend: Flask
- Frontend: HTML/CSS/JS
- Analysis: Radon, custom heuristics
- ML: scikit-learn + joblib
- Execution: subprocess + temp files

## Project Structure

```
Lyra/  
│
├── app.py
├── main.py
├── complexity_analyzer.py
├── requirements.txt
│
├── analyzers/
│   ├── __init__.py
│   ├── alignment_engine.py
│   ├── complexity_engine.py
│   ├── generic_engine.py
│   ├── risk_engine.py
│   └── strategy_engine.py
│
├── executor/
│   ├── code_runner.py
│   ├── java_executor.py
│   ├── c_executor.py
│   ├── cpp_executor.py
│   └── js_executor.py
│
├── ml/
│   ├── quality_model.py
│   └── train_model.py
│
├── static/
│   ├── style.css
│   ├── animations.css
│   ├── chatbot.js
│   └── code-executor.js
│
├── templates/
│   └── index.html
│
└── sample_codes/
    └── example1.py

```

## Setup

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` or set variables in your shell:

- `GEMINI_API_KEY` (required for chat)
- `GEMINI_MODEL` (optional, default: `gemini-2.5-flash`)

### 4) Run the app

```bash
python app.py
```

Open https://lyra-yylx.onrender.com/ in your browser.

## Code Execution Requirements

The `/execute` endpoint uses local compilers/runtimes. Install them and ensure they are in PATH.

- Python: bundled with your environment
- Java: JDK (`java` + `javac`)
- C: `gcc`
- C++: `g++`
- JavaScript: Node.js (`node`)

On Windows, MSYS2 UCRT64 works for C/C++:

```
C:\msys64\ucrt64\bin
```

## API Endpoints

- `GET /` - UI
- `POST /` - Analyze code and render results
- `POST /execute` - Run code (Python/Java/C/C++/JS)
- `POST /chat` - Chat assistant (Gemini)

## ML Quality Model

The ML model is stored at `ml/quality_model.pkl`. If you want to retrain:

```bash
python ml/train_model.py
```

## Notes

- Python analysis uses AST + Radon for cyclomatic complexity.
- Non-Python languages use heuristic analysis in `analyzers/generic_engine.py`.
- Execution is time-limited to reduce runaway code.

