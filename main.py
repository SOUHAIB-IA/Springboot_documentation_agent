import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from src.api.routes import router as api_router

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AI Documentation Agent API",
    description="An API to automatically generate documentation for a Spring Boot project.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api", tags=["Agent"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)