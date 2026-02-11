# ml/quality_model.py

from pathlib import Path

import joblib
import numpy as np


_MODEL = None
_MODEL_PATH = Path(__file__).resolve().parent / "quality_model.pkl"


def _load_model():
    global _MODEL
    if _MODEL is None and _MODEL_PATH.exists():
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def _extract_features(result, code_input):
    complexity_list = result.get("complexity") or []
    avg_complexity = float(np.mean([c for (_, c) in complexity_list])) if complexity_list else 0.0
    nested_loops = int(result.get("nested_loops") or 0)
    risk_count = len(result.get("risks") or [])
    edge_cases = len(result.get("edge_cases") or [])
    lines_of_code = len(code_input.splitlines())
    return np.array([avg_complexity, nested_loops, risk_count, edge_cases, lines_of_code], dtype=float)


def _fallback_rule(result, code_input):
    time_complexity = (result.get("time_complexity") or "O(n)").lower()
    nested_depth = int(result.get("nested_loops") or 0)
    risk_count = len(result.get("risks") or [])
    edge_cases = len(result.get("edge_cases") or [])
    loc = len(code_input.splitlines())

    score = 0

    if "n^3" in time_complexity or "n3" in time_complexity:
        score += 3
    elif "n^2" in time_complexity or "n2" in time_complexity:
        score += 2
    elif "log" in time_complexity:
        score += 0
    else:
        # Treat O(n) as neutral when nesting is shallow and risks are empty
        score += 0 if nested_depth <= 1 and risk_count == 0 else 1

    if nested_depth >= 3:
        score += 2
    elif nested_depth == 2:
        score += 1

    if risk_count >= 3:
        score += 2
    elif risk_count == 2:
        score += 1

    if edge_cases >= 2:
        score += 1

    # Only penalize size if there are signals of risk/nesting; avoid punishing verbose but simple code
    if nested_depth >= 2 or risk_count > 0:
        if loc > 150:
            score += 2
        elif loc > 80:
            score += 1

    # Force a minimum severity for obvious heavy patterns
    if ("n^2" in time_complexity or "n2" in time_complexity) and nested_depth >= 2:
        score = max(score, 4)

    if score <= 1:
        return "Optimized"
    elif score <= 3:
        return "Moderate"
    elif score <= 5:
        return "Complex"
    else:
        return "High Risk"


def predict_quality(result, code_input):
    model = _load_model()
    label_map = {"Risky": "High Risk", "High Risk": "High Risk"}
    severity_rank = {"Optimized": 0, "Moderate": 1, "Complex": 2, "High Risk": 3}

    rule_label = _fallback_rule(result, code_input)
    best_label = rule_label

    if model is not None:
        try:
            features = _extract_features(result, code_input)
            prediction = model.predict([features])[0]
            ml_label = label_map.get(prediction, prediction)

            # Always return the worst (highest severity) between ML and rule heuristics
            if severity_rank.get(ml_label, 0) > severity_rank.get(best_label, 0):
                best_label = ml_label
        except Exception as exc:
            print("ML Prediction Error:", exc)

    return best_label
