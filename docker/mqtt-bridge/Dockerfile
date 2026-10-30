FROM python:3.11-slim
WORKDIR /app
COPY docker/mqtt-bridge/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY docker/mqtt-bridge/bridge.py /app/bridge.py
CMD ["python", "-u", "/app/bridge.py"]
