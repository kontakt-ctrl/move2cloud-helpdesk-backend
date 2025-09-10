import uvicorn
from fastapi import FastAPI
from app.core.db import init_db
from app.api import auth, users, tickets, categories, priorities

app = FastAPI(
    title="Helpdesk Backend",
    description="Helpdesk API for Azure Web App (FastAPI, MongoDB, JWT)",
    version="1.0.0"
)

@app.on_event("startup")
async def on_startup():
    await init_db()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(categories.router)
app.include_router(priorities.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)