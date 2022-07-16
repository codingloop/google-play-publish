FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

RUN pip install --target=/app/src -r requirements.txt
RUN apt-get update && apt-get install -y gnupg
RUN apt-get install -y ca-certificates wget

FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app/src
ENV PYTHONPATH /app/src
CMD ["/app/src/main.py"]