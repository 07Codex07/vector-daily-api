from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re

from .database import init_db, add_subscriber, get_all_subscribers, remove_subscriber, is_subscribed

app = FastAPI(title="Vector Daily Newsletter API")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run database setup on startup
@app.on_event("startup")
def startup_event():
    init_db()

# -------- Email validation --------
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def validate_email(email: str):
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status_code=400, detail="Invalid email format")

# -------- Request Model --------
class SubscribeRequest(BaseModel):
    email: str


# =========================================================
# POST /subscribe
# =========================================================
@app.post("/subscribe")
def subscribe_user(request: SubscribeRequest):
    validate_email(request.email)

    try:
        add_subscriber(request.email)
        return {"message": f"✅ {request.email} subscribed successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# POST /unsubscribe
# =========================================================
@app.post("/unsubscribe")
def unsubscribe_user(request: SubscribeRequest):
    validate_email(request.email)

    if not is_subscribed(request.email):
        raise HTTPException(status_code=404, detail="Email not found")

    try:
        remove_subscriber(request.email)
        return {"message": f"❎ {request.email} unsubscribed successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# GET /unsubscribe (for email footer links)
# Example link: https://your-domain.com/unsubscribe?email=user@gmail.com
# =========================================================
@app.get("/unsubscribe")
def unsubscribe_from_link(email: str):
    validate_email(email)

    if not is_subscribed(email):
        return {"message": "Email already unsubscribed or not found"}

    remove_subscriber(email)
    return {"message": f"{email} unsubscribed successfully!"}


# =========================================================
# /subscribers
# =========================================================
@app.get("/subscribers")
def get_subscribers():
    subscribers = get_all_subscribers()
    return {"subscribers": subscribers}

# =========================================================
# Root
# =========================================================
@app.get("/")
def root():
    return {"message": "Welcome to The Vector Daily Newsletter API!"}
