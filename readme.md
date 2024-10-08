# Image Processing Service

A FastAPI-based service for compressing product images .
The service accepts CSV files containing product information and image URLs, processes the images, and provides access to the processed results.

## Development Environment

This project is developed and tested on Windows Subsystem for Linux (WSL2) with Ubuntu. For

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/image-processing-service.git
cd image-processing-service
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start PostgreSQL and create the database:

```bash
# Using psql
psql -U postgres
CREATE DATABASE "spyne-local";
```

6. Start Redis server:

```bash
# On Linux/macOS
redis-server

# On Windows
# Start Redis using Windows Subsystem for Linux (WSL) or Docker
```

## Running the Application

1. Start the FastAPI application:

```bash
fastapi dev main.py
```

2. Start Celery worker:

```bash
# In a new terminal
celery -A app.celery_app worker --loglevel=INFO
```

## Usage

### 1. Prepare CSV File

Create a CSV file with the following structure:

```csv
Serial Number,Product Name,Input Image URL,
1001,Product A,http://example.com/image1.jpg,http://example.com/image2.jpg
1002,Product B,http://example.com/image3.jpg
```

### 2. Upload CSV

```bash
curl -X POST \
  http://localhost:8000/upload \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@products.csv'
```

### 3. Check Status

```bash
curl -X GET \
  http://localhost:8000/status/{request_id}
```

### 4. Access Processed Images

Processed images will be available at:

```
http://localhost:8000/images/{filename}
```
