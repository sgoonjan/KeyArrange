FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsndfile1 \
        build-essential \
        musescore3 \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

# MuseScore needs a display even in headless mode — xvfb provides a virtual one
ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 7860

CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & uvicorn keyarrange.api.app:app --host 0.0.0.0 --port 7860"]