FROM python:3.10-slim
WORKDIR /app
COPY bot.py db.py /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends libsecret-1-dev && rm -rf /var/lib/apt/lists/*
CMD ["python", "bot.py"]
