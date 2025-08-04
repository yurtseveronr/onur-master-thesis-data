# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=us-east-1
ENV SERIES_CAMPAIGN_ARN="arn:aws:personalize:us-east-1:708778582346:campaign/tv-series-campaign"
ENV MOVIES_CAMPAIGN_ARN="arn:aws:personalize:us-east-1:708778582346:campaign/movies-campaign"
ENV SERIES_DATASET_ARN="arn:aws:personalize:us-east-1:708778582346:dataset/tv_series-dataset-group"
ENV MOVIES_DATASET_ARN="arn:aws:personalize:us-east-1:708778582346:dataset/movies-dataset-group"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000



# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]