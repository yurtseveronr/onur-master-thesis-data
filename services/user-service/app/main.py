from fastapi import FastAPI
from app.routes.favorites_routes import router as favorites_router

app = FastAPI(title="User Favorites API")

app.include_router(favorites_router, prefix="/api", tags=["Favorites"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
