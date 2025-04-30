# dam-fastapi

A minimal Python FastAPI service to receive file uploads via POST, store them in **Cloudflare R2**, and persist metadata as **Parquet** on R2.

---

## Set Fly.io Secrets

Before deploying, configure your R2 credentials:

```bash
fly secrets set \
  R2_ENDPOINT="https://<account>.r2.cloudflarestorage.com" \
  R2_ACCESS_KEY_ID="your-access-key-id" \
  R2_SECRET_ACCESS_KEY="your-secret-access-key" \
  R2_BUCKET="your-bucket-name"
```

## Deploy to Fly.io

```
fly deploy
```


## Upload a File (Test with curl)

```
curl -X POST https://dam-fastapi.fly.dev/upload \
  -F "file=@image.jpg"
```

Expected response:

```
{"message":"Upload successful","id":"8218692a-0d5d-4547-9998-a890cd3b81b6"}
```

## Cloudflare R2 Structure

* assets/ — Uploaded files are saved here using a UUID-based name.
* metadata/assets.parquet — A Parquet file storing metadata for each uploaded file (filename, size, MIME type, R2 key, etc.).

## Query the data using Duckdb

In another folder, download the parquet file locally and query the file using SQL using Duckdb:

First create a requirements.txt file as follows:

```
# requirements.txt
duckdb
numpy
pandas
```

Then create an environment to install and use duckbd:

```
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python3 query.py
```

The results will look something like:

```
id   filename                                           r2_key     size   mime_type
0  8218692a-0d5d-4547-9998-a890cd3b81b6  image.jpg  assets/8218692a-0d5d-4547-9998-a890cd3b81b6.jpg  1257223  image/jpeg
```


## Tech stack

* FastAPI — Python web API
* boto3 — S3-compatible R2 storage access
* pandas + pyarrow — Parquet metadata writing
* Fly.io — App hosting
* Cloudflare R2 — Object storage (S3-compatible)
* duckdb - to query the parquet file using SQL