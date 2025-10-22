FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=dreamOtp.settings \
    PORT=8000

EXPOSE 8000

CMD python manage.py migrate &&  python manage.py runserver 0.0.0.0:$PORT
