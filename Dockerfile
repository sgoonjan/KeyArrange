FROM python:3.11-slim

# ffmpeg for audio I/O, libsndfile for soundfile, git for demucs model download
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsndfile1 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only torch first
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch torchvision torchaudio

# Install Python deps first so Docker layer cache is reused on code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn python-multipart

COPY . .
RUN pip install --no-cache-dir -e .

# Hugging Face Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "keyarrange.api.app:app", "--host", "0.0.0.0", "--port", "7860"]
