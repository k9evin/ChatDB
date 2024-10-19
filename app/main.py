from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
import logging

app = FastAPI()

# Allow Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(
        "\033[93mPlease set up the .env file using .env.example as a reference before running the program.\033[0m"
    )

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
