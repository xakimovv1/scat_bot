FROM python:3.11-slim

WORKDIR /app

COPY scat_bot/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY scat_bot/ .

CMD ["python", "app.py"]
