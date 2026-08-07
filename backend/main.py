from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Assistant")

@app.get("/")
def read_root():
    return {"message": "Enterprise AI Assistant backend is running"}
