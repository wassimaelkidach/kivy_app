# deploy/Dockerfile (for FastAPI backend)
FROM python:3.12-slim-buster

WORKDIR /app

# COPY commands are relative to the build context (which is your_project_root/)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . . # This will copy everything from your_project_root/ to /app/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]