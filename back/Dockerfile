FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY back/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY back/ .

EXPOSE 8000

CMD ["uvicorn", "back.api:app", "--host", "0.0.0.0", "--port", "8000"]
