from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="WECC Power Grid Visualization API",
    description="API for visualizing WECC power grid data with weather impacts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.routers import auth, grid, weather, heatmap, bas, analytics, public

app.include_router(auth, prefix="/api/auth", tags=["Authentication"])
app.include_router(grid, prefix="/api/grid", tags=["Grid Components"])
app.include_router(weather, prefix="/api/weather", tags=["Weather Data"])
app.include_router(heatmap, prefix="/api/heatmap", tags=["Heatmaps"])
app.include_router(bas, prefix="/api/bas", tags=["Balancing Authorities"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])
app.include_router(public, prefix="/api/public", tags=["Public Endpoints"])

@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
