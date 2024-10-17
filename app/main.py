from fastapi import FastAPI
from app.api.routes import router
from app.config import settings
import logging

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(
        "\033[93mPlease set up the .env file using .env.example as a reference before running the program.\033[0m"
    )

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
