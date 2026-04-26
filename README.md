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

## New Additions

*   **Containerization**: The backend is packaged in a Docker container for easy deployment.
*   **Infrastructure as Code**: Terraform scripts are provided to deploy all necessary infrastructure (VPC, AlloyDB, Cloud Run).
*   **Automation**: A deployment script (`deploy.sh`) automates the build and deployment process.

## Prerequisites

*   An active Google Cloud project.
*   Google Cloud SDK (`gcloud`) installed and authenticated.
*   Terraform installed.
*   Python 3.x (for local testing).

## Installation & Deployment Guide

### Local Testing

#### 1. Configure Environment Variables
Set the following environment variables to allow the backend to connect to your existing AlloyDB instance:

```bash
export DB_HOST="YOUR_ALLOYDB_IP"
export DB_USER="postgres"
export DB_PASSWORD="YOUR_PASSWORD"
export DB_NAME="face-recognition-db"
```

#### 2. Install Backend Dependencies
Navigate to the `backend` directory and install the required Python packages:

```bash
cd backend
python3 -m pip install -r requirements.txt
```

#### 3. Run the Backend
```bash
python3 -m uvicorn main:app --reload
```

#### 4. Access the Frontend
Open `frontend/index.html` in your browser.

---

### Cloud Deployment (Terraform & Cloud Run)

#### 1. Configure `config.env`
Open the `config.env` file in the project root and set your project ID, preferred region, and a secure password for AlloyDB:

```env
PROJECT_ID=your-project-id
REGION=us-central1
DB_PASSWORD=your-secure-password
```

#### 2. Run the Deployment Script
Execute the deployment script to build the container image and deploy the infrastructure:

```bash
chmod +x deploy.sh
./deploy.sh
```

*Note: This script uses Cloud Build to build the image and Terraform to deploy. Ensure you have the necessary permissions in your GCP project.*

#### 3. Access the Application
The script will output the Cloud Run URL. Open `frontend/index.html` in your browser; it will be automatically updated to use the new Cloud Run URL.

## License

[Specify License if applicable]
