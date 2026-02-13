import pandas as pd
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, r2_score

# Define base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "dataset")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Create output directory
os.makedirs(MODELS_DIR, exist_ok=True)

# Load dataset
data_path = os.path.join(DATA_DIR, "winequality-red.csv")
data = pd.read_csv(data_path, sep=';')

# Features and target
X = data.drop("quality", axis=1)
y = data["quality"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)


# Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Model 
model = Lasso(alpha=0.1)

# Train model
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Print metrics (required)
print(f"MSE: {mse}")
print(f"R2 Score: {r2}")

# Save model
model_path = os.path.join(MODELS_DIR, "model.pkl")
joblib.dump(model, model_path)

# Save results to app/artifacts/metrics.json as per Lab 6 requirements
# artifacts are expected to be in app/artifacts relative to the workspace root
# Since we run from root, we can specify the path directly
ARTIFACTS_DIR = os.path.join(BASE_DIR, "app", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

results = {
    "accuracy": r2  # Lab 6 instructions call it "accuracy", using R2 as proxy or just calling it accuracy
}

# Note: The instructions mention "Read Accuracy - Extract accuracy value". 
# Common regression metrics are MSE/R2. "Accuracy" usually implies classification. 
# However, this is a regression problem (wine quality). 
# I will save R2 as "accuracy" to satisfy the pipeline stage "Read Accuracy" which likely expects a key named "accuracy" or similar.
# Or I can save both. Let's save "accuracy": r2 to be safe for the "Read Accuracy" stage compatibility.

results_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
with open(results_path, "w") as f:
    json.dump(results, f, indent=4)
