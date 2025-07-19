# ================================
# Dockerfile for Django Healthcare System Backend
# ================================

# 1. Base Image
FROM python:3.10-slim

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set Work Directory
WORKDIR /app

# 4. Install System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy Project Files
COPY . /app/

# 7. Run Collect Static (Optional for production)
RUN python manage.py collectstatic --noinput || true

# 8. Expose Port
EXPOSE 8000

# 9. Start the Application
CMD ["gunicorn", "healthcare_system_backend.wsgi:application", "--bind", "0.0.0.0:8000"]