FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

RUN pip install --target=/app/src -r requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app/src
ENV PYTHONPATH /app/src
CMD ["python main.py"]