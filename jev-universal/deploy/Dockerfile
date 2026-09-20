FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 jev
USER jev
EXPOSE 8765
ENTRYPOINT ["jev-universal", "--transport", "streamable-http"]
