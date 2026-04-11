FROM python:3.12-slim

WORKDIR /app

# Build context must be the project root:
#   docker build -f web/Dockerfile -t regula-assess-web .
COPY scripts/ /app/scripts/
COPY web/ /app/web/

RUN pip install --no-cache-dir flask

WORKDIR /app/web

EXPOSE 5000

CMD ["python", "app.py"]
