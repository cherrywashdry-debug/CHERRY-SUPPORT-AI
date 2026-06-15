FROM python:3.12-slim



WORKDIR /app



ENV PYTHONUNBUFFERED=1

ENV PORT=8080



COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



COPY *.py ./

COPY quick_replies_seed.json quick_reply_buttons_seed.json quick_reply_images_seed.json staff_users_seed.json ./

RUN mkdir -p data



CMD ["python", "-u", "app.py"]

