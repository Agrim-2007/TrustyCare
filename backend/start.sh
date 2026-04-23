#!/usr/bin/env bash
# Start script for Render deployment

# Build the FAISS index (downloads models and creates the vectorstore)
echo "Building FAISS index..."
python rag/ingest.py

# Start the Uvicorn server
echo "Starting Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
