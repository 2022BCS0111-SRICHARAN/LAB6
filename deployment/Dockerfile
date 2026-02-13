FROM python:3.10-slim

WORKDIR /app

# Copy requirements from deployment folder
COPY deployment/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code from deployment/app
COPY deployment/app/ app/

# Copy trained model from models directory
COPY models/model.pkl app/model.pkl

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
