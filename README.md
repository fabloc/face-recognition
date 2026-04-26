# Face Matching Application

This application demonstrates face matching capabilities using Google Cloud's AlloyDB and Vertex AI. It leverages the native integration of AlloyDB with Vertex AI to generate and compare embeddings using the `gemini-embedding-2` model.

## Features

*   **Image Upload**: Upload images from your local machine or specify a GCS bucket location.
*   **Face Matching**: Compare the uploaded image against stored reference images using vector similarity search.
*   **Bulk Insert**: Automatically fetch and index all images from a specified GCS bucket, replacing special characters in filenames with spaces to use as names.

## Architecture

*   **Frontend**: A simple and modern HTML/JS interface.
*   **Backend**: FastAPI application handling requests and interacting with the database.
*   **Database**: AlloyDB for PostgreSQL storing image references and embeddings.
*   **AI Model**: `gemini-embedding-2` (multimodal embedding model) accessed natively via AlloyDB.

## Prerequisites

*   An active Google Cloud project.
*   An AlloyDB cluster with the `google_ml_integration` extension enabled.
*   A database named `face-recognition-db` (or as configured).
*   Python 3.x installed.

## Installation Guide

### 1. Clone or Download the Project

If you haven't already, clone or download this repository to your local machine.

### 2. Set Up the Database

Ensure your AlloyDB instance is running and you have created the necessary table. The backend will attempt to create the table automatically on startup if it has permissions.

The expected schema is:
```sql
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    image_uri TEXT,
    embedding vector(3072)
);
```

### 3. Configure Environment Variables

Set the following environment variables to allow the backend to connect to your AlloyDB instance:

```bash
export DB_HOST="YOUR_ALLOYDB_IP"
export DB_USER="postgres"
export DB_PASSWORD="YOUR_PASSWORD"
export DB_NAME="face-recognition-db"
```

### 4. Install Backend Dependencies

Navigate to the `backend` directory and install the required Python packages:

```bash
cd backend
python3 -m pip install -r requirements.txt
```

## Running the Application

### 1. Start the Backend

From the `backend` directory, start the FastAPI server using Uvicorn:

```bash
python3 -m uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`.

### 2. Access the Frontend

Open the `frontend/index.html` file directly in your web browser. It is configured to communicate with the backend running at `http://localhost:8000`.

## License

[Specify License if applicable]
