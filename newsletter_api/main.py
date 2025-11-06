from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .database import init_db, add_subscriber, get_all_subscribers

app = FastAPI(title="Vector Daily Newsletter API")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Run database setup on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Schema for incoming email requests
class SubscribeRequest(BaseModel):
    email: str

@app.post("/subscribe")
def subscribe_user(request: SubscribeRequest):
    try:
        add_subscriber(request.email)
        return {"message": f"✅ {request.email} subscribed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscribers")
def get_subscribers():
    subscribers = get_all_subscribers()
    return {"subscribers": subscribers}

@app.get("/")
def root():
    return {"message": "Welcome to The Vector Daily Newsletter API!"}
