from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
import logging

app = FastAPI()

# Allow Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
    )
    logging.info(
        "\033[93mPlease set up the .env file using .env.example as a reference before running the program.\033[0m"
    )

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug, 
        reload_dirs=["app"], 
        reload_excludes=["*/__pycache__/*"],
    )
