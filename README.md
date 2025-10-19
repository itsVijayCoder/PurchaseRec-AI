# PurchaseRec-AI

A Flask-based API for purchase recommendations.

## Project Overview

This application provides purchase recommendation capabilities through several endpoints:
- Authentication (login, register)
- Data ingestion
- Data analysis and recommendations

## Technologies Used

- Python with Flask (APIFlask)
- MongoDB for data storage
- Redis for caching
- OpenAI integration for analysis

## Prerequisites

- Docker and Docker Compose

## Getting Started

### Environment Setup

1. Clone this repository.
2. Create a `.env` file based on the `.env.example` file:
   ```bash
   cp .env.example .env
   ```
3. Update the `.env` file with your specific configurations.

### Running with Docker

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. The API will be available at http://localhost:8080

3. Check the health endpoint at http://localhost:8080/health

### Running without Docker

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure MongoDB and Redis are running.
4. Configure the environment variables.
5. Run the application:
   ```bash
   python app.py
   ```

## Google Vision OCR

- Purpose: Adds a fallback OCR when a PDF page has no extractable text (scanned PDFs).
- Setup:
  - Enable the Vision API in your Google Cloud project and create a service account with sufficient permissions (e.g., `roles/Cloud Vision API User`).
  - Download the service account key JSON and place it in the project root (e.g., `google-vision-key.json`).
  - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS`:
    - Docker: `GOOGLE_APPLICATION_CREDENTIALS=/app/google-vision-key.json` (repo is mounted at `/app`).
    - Local: `GOOGLE_APPLICATION_CREDENTIALS=./google-vision-key.json`.
- Dependencies: `google-cloud-vision` is included in `requirements.txt`.
- Behavior:
  - Uses `pdfplumber` for native text extraction.
  - If a page returns empty text, renders the page via `pypdfium2` and runs Google Vision `document_text_detection`.
  - Aggregates text across all pages seamlessly.

## API Endpoints

- `/api/v1/` - Authentication endpoints
- `/api/v1/analyse` - Analysis endpoints
- `/api/v1/ingest` - Data ingestion endpoints
- `/health` - Health check endpoint

## Stopping the Application

To stop the Docker containers:
```bash
docker-compose down
```

To stop and remove volumes:
```bash
docker-compose down -v
```