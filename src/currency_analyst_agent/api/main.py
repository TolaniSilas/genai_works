# src/currency_analyst_agent/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import currency


# initialize fastapi app.
app = FastAPI(
    title="Currency Analyst API",
    description="Backend service for the CrewAI-powered Currency Analyst project.",
    version="1.0.0",
)

# cors setup (allow the streamlit's frontend user interface to interact with this api).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register currency router.
app.include_router(currency.router)

# define a simple home endpoint.
@app.get("/")
def home():
    return {"message": "Welcome to Currency Analyst API!"}

# define the health check endpoint.
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Currency Analyst API is running!"}