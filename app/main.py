import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.db import init_db
from app.api import auth, users, tickets, categories, priorities

# KONFIGURACJA LOGOWANIA
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("/tmp/app.log"),
        logging.StreamHandler()
    ]
)

error_logger = logging.getLogger("app.error")
error_file_handler = logging.FileHandler("/tmp/app.log")
error_file_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_file_handler)

app = FastAPI(
    title="Helpdesk Backend",
    description="Helpdesk API for Azure Web App (FastAPI, MongoDB, JWT)",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    logging.info("Starting up and initializing the database.")
    try:
        await init_db()
    except Exception as e:
        error_logger.error("Błąd podczas inicjalizacji bazy danych", exc_info=True)
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_logger.error(
        f"Unhandled error: {exc}", exc_info=True, extra={"path": str(request.url)}
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(categories.router)
app.include_router(priorities.router)

if __name__ == "__main__":
    logging.info("Running in __main__ mode, starting Uvicorn server.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
