FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .
COPY templates/ templates/
RUN mkdir -p qr_codes data && \
    adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]