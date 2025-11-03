FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Copy requirements to container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (including /app folder)
COPY app /app/app

# Avoid buffering logs
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

