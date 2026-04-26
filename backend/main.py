import os
import base64
import re
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
from database import execute_query, execute_non_query, init_db

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/match")
async def match_face(
    file: UploadFile = File(None),
    bucket_name: str = Form(None),
    object_name: str = Form(None)
):
    if file:
        # Local upload
        contents = await file.read()
        base64_encoded = base64.b64encode(contents).decode('utf-8')
        image_data = f"data:{file.content_type};base64,{base64_encoded}"
        
        # We need to extract the raw base64 part for the API if it doesn't like the data URI prefix
        # The doc showed 'IMAGE_PATH_OR_TEXT' which can be base64 string.
        # Let's assume it expects just the base64 string or the data URI.
        # Let's try passing the base64 string.
        
        query = """
        SELECT name, image_uri, 1 - (embedding <=> google_ml.image_embedding(
            model_id => 'gemini-embedding-2',
            image => $1,
            mimetype => $2)) as similarity
        FROM face_embeddings
        ORDER BY similarity DESC
        LIMIT 5;
        """
        try:
            results = await execute_query(query, base64_encoded, file.content_type)
            return format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Matching failed: {e}")

    elif bucket_name and object_name:
        # GCS upload
        gcs_uri = f"gs://{bucket_name}/{object_name}"
        # We need to guess the mimetype or ask for it. Let's assume image/jpeg as default or try to infer from extension.
        mimetype = "image/jpeg"
        if object_name.endswith(".png"):
            mimetype = "image/png"
        
        query = """
        SELECT name, image_uri, 1 - (embedding <=> google_ml.image_embedding(
            model_id => 'gemini-embedding-2',
            image => $1,
            mimetype => $2)) as similarity
        FROM face_embeddings
        ORDER BY similarity DESC
        LIMIT 5;
        """
        try:
            results = await execute_query(query, gcs_uri, mimetype)
            return format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Matching failed: {e}")
    else:
        raise HTTPException(status_code=400, detail="Must provide either a file or GCS bucket and object name.")

def format_results(results):
    formatted = []
    for r in results:
        formatted.append({
            "name": r['name'],
            "image_uri": r['image_uri'],
            "similarity": float(r['similarity']) * 100 # Convert to percentage
        })
    return formatted

@app.post("/bulk-insert")
async def bulk_insert(bucket_name: str = Form(...), prefix: str = Form("")):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        count = 0
        for blob in blobs:
            if blob.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Extract name
                filename = os.path.basename(blob.name)
                name_without_ext = os.path.splitext(filename)[0]
                
                # Replace special characters with space
                name = re.sub(r'[-_]', ' ', name_without_ext)
                
                gcs_uri = f"gs://{bucket_name}/{blob.name}"
                mimetype = "image/jpeg"
                if blob.name.lower().endswith('.png'):
                    mimetype = "image/png"
                
                # Insert and generate embedding
                query = """
                INSERT INTO face_embeddings (name, image_uri, embedding)
                VALUES ($1, $2, google_ml.image_embedding(
                    model_id => 'gemini-embedding-2',
                    image => $2,
                    mimetype => $3))
                """
                await execute_non_query(query, name, gcs_uri, mimetype)
                count += 1
                
        return {"message": f"Successfully inserted {count} images."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk insert failed: {e}")
