FROM python:3.10-slim

# 1. Mag-install ng system dependencies (kasama ang build tools para sa insightface)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    ffmpeg \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. I-copy ang requirements
COPY requirements.txt .

# 3. I-install ang dependencies nang paisa-isa (ito ang susi para hindi mag-conflict)
# Unahin ang build tools at tamang NumPy version
RUN pip install --no-cache-dir --upgrade pip setuptools wheel cython numpy==1.26.4

# I-install ang insightface (ito ang nagbibigay ng ArcFace)
RUN pip install --no-cache-dir insightface==0.7.3

# I-install ang iba pang requirements (FastAPI, uvicorn, atbp.)
RUN pip install --no-cache-dir -r requirements.txt

# 4. I-copy ang main.py
COPY main.py .

EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
