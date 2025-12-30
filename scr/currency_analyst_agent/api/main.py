import fastapi



@app.get("/")
def home():
    return {"message": "Welcome to Currency Analyst API!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "uptime": "running"}
