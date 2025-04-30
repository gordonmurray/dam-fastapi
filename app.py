from fastapi import FastAPI, UploadFile, File
import boto3, uuid, os
import pandas as pd
from io import BytesIO

app = FastAPI()

# R2 client setup
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv("R2_ENDPOINT"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
)

BUCKET = os.getenv("R2_BUCKET")
METADATA_KEY = "metadata/assets.parquet"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    object_key = f"assets/{file_id}{file_ext}"

    # Upload raw file to R2
    s3.put_object(
        Bucket=BUCKET,
        Key=object_key,
        Body=file_bytes,
        ContentType=file.content_type
    )

    # Build metadata
    metadata = pd.DataFrame([{
        "id": file_id,
        "filename": file.filename,
        "r2_key": object_key,
        "size": len(file_bytes),
        "mime_type": file.content_type
    }])

    # Download existing metadata (if it exists)
    try:
        existing_obj = s3.get_object(Bucket=BUCKET, Key=METADATA_KEY)
        existing_df = pd.read_parquet(BytesIO(existing_obj['Body'].read()))
        combined_df = pd.concat([existing_df, metadata], ignore_index=True)
    except s3.exceptions.NoSuchKey:
        combined_df = metadata

    # Save new metadata
    buffer = BytesIO()
    combined_df.to_parquet(buffer, engine="pyarrow", index=False)
    buffer.seek(0)

    s3.put_object(
        Bucket=BUCKET,
        Key=METADATA_KEY,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream"
    )

    return {"message": "Upload successful", "id": file_id}
