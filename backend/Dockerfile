FROM python:3.13-alpine

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv pip install -e . --system

RUN chmod +x entrypoint.sh