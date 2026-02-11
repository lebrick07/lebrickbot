from fastapi import FastAPI
from datetime import datetime
import os
import uvicorn

app = FastAPI(title="{{CUSTOMER_NAME}} API")

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "Hello from {{CUSTOMER_NAME}}!",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    uvicorn.run(app, host="0.0.0.0", port=port)
