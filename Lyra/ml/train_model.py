import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# -----------------------------
# STEP 1: Create Synthetic Dataset
# -----------------------------

np.random.seed(42)

data_size = 500

# Features
avg_complexity = np.random.randint(1, 20, data_size)
nested_loops = np.random.randint(0, 5, data_size)
risk_count = np.random.randint(0, 5, data_size)
edge_cases = np.random.randint(0, 5, data_size)
lines_of_code = np.random.randint(5, 300, data_size)

# Rule to generate labels
labels = []

for i in range(data_size):
    score = (
        avg_complexity[i] * 0.3 +
        nested_loops[i] * 0.2 +
        risk_count[i] * 0.3 +
        edge_cases[i] * 0.1 +
        (lines_of_code[i] / 100) * 0.1
    )

    if score < 3:
        labels.append("Optimized")
    elif score < 6:
        labels.append("Moderate")
    elif score < 9:
        labels.append("Complex")
    else:
        labels.append("Risky")

# Create DataFrame
df = pd.DataFrame({
    "avg_complexity": avg_complexity,
    "nested_loops": nested_loops,
    "risk_count": risk_count,
    "edge_cases": edge_cases,
    "lines_of_code": lines_of_code,
    "label": labels
})

# -----------------------------
# STEP 2: Train Model
# -----------------------------

X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"Model trained successfully! Accuracy: {accuracy:.2f}")

# -----------------------------
# STEP 3: Save Model
# -----------------------------

joblib.dump(model, "ml/quality_model.pkl")
print("Model saved as quality_model.pkl")
