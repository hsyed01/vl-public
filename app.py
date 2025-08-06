
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Podcast Ad Listener Predictor API"}

@app.post("/will-listen-to")
def predict_gradient_boosting():
    pass
