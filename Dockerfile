FROM python:3.12-slim



WORKDIR /app



ENV PYTHONUNBUFFERED=1

ENV PORT=8080



COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



COPY app.py quick_replies.py reply_store.py reply_defaults.py quick_replies_seed.json ./

RUN mkdir -p data



CMD ["python", "-u", "app.py"]

