from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models
from .routers import emi, leads, appointments, funds, sip, chat
from dotenv import load_dotenv
load_dotenv()


# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Bot Backend",
    description="EMI + Mutual Fund + Lead + SIP",
    version="0.1.0",
)

# CORS (adjust origins when you build frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emi.router)
app.include_router(leads.router)
app.include_router(appointments.router)
app.include_router(funds.router)
app.include_router(sip.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "Finance Bot Backend is running"}

import requests

@app.on_event("startup")
def warm_llm():
    try:
        requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": "warmup"}],
                "stream": False
            },
            timeout=5
        )
    except:
        pass

