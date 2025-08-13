from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Form Submission API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key configuration for different sources
API_KEYS = {
    "corecrest": os.getenv("CORECREST_API_KEY"),
    "portfolio": os.getenv("PORTFOLIO_API_KEY"),
    "default": os.getenv("API_KEY"), # Fallback API key
    "test": os.getenv("TEST_API_KEY"),
    "Main Portfolio": os.getenv("MAIN_PORTFOLIO_API_KEY"),
    "QR Code Generator": os.getenv("QR_CODE_GENERATOR_API_KEY"),
    "Umwirondoro": os.getenv("UMWIRONDORO_API_KEY"),
    "Manga Scrapper": os.getenv("MANGA_SCRAPPER_API_KEY")
}

# Single notification endpoint for all sources
NOTIFICATION_ENDPOINT = "http://64.227.102.129:8000/api/v1/notifications/"

# Notification endpoint for all sources
NOTIFICATION_ENDPOINT_FOR_FORM_SUBMISSION = "http://64.227.102.129:8000/api/v1/notifications/notifications-form/"

class ContactForm(BaseModel):
    name: str
    email: str
    message: str
    subject: Optional[str] = None

class FeedbackForm(BaseModel):
    rating: int
    category: str
    feedback: str
    email: Optional[str] = None

class RegistrationForm(BaseModel):
    username: str
    email: str
    firstName: str
    lastName: str
    phoneNumber: Optional[str] = None

class GenericForm(BaseModel):
    data: Dict[str, Any]

class NotificationPayload(BaseModel):
    recipient: str
    subject: str
    body: str
    priority: int = 2
    notification_type: str = "email"
    source: str  # New field to identify the source

class FormNotificationPayload(BaseModel):
    recipient: str
    subject: str
    body: str
    body_type: Optional[str] = None
    priority: int = 2
    notification_type: str = "email"
    content_encoding: str = "plain"
    source: str

def get_api_key(source: str) -> str:
    """Get the API key for a given source"""
    api_key = API_KEYS.get(source, API_KEYS["default"])
    
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: Missing API key for source '{source}'"
        )
    
    return api_key

def format_email_body(form_type: str, form_data: Dict[str, Any]) -> str:
    """Format form data into a readable email body"""
    body = f"New {form_type} form submission:\n\n"
    for key, value in form_data.items():
        body += f"{key}: {value}\n"
    return body

@app.post("/api/submit/{form_type}")
async def submit_form(
    form_type: str,
    notification: NotificationPayload
):
    """
    Submit form data to the notification endpoint.
    
    Args:
        form_type: Type of form being submitted (e.g., 'contact', 'feedback', 'registration')
        notification: The notification payload including source
    """
    try:
        # Get API key based on source
        api_key = get_api_key(notification.source)

        # Send the notification
        response = requests.post(
            NOTIFICATION_ENDPOINT,
            json=notification.model_dump(exclude={'source'}),  # Exclude source from payload
            headers={
                "accept": "application/json",
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
        )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to send notification: {response.text}"
            )

        return {
            "status": "success",
            "message": f"{form_type} form submitted successfully from {notification.source}"
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running
    """
    return {
        "status": "ok", 
        "message": "Form submission API is running",
        "available_sources": list(API_KEYS.keys())
    } 

@app.post("/api/submit-form")
@app.post("/api/submit-form/")
async def submit_form_notification(request: Request):
    """
    Submit form notification data to the form-specific notification endpoint.
    Accepts form-encoded payload (as received) and forwards it unchanged, except:
    - Adds default content_encoding="plain" if not provided.
    - Uses `source` query parameter to resolve the API key and does not forward it.
    """
    try:
        incoming_form = await request.form()
        form_payload = dict(incoming_form)

        source = form_payload.pop("source", None)
        if not source:
            raise HTTPException(status_code=400, detail="Missing 'source' in form data")

        api_key = get_api_key(source)

        if not form_payload.get("content_encoding"):
            form_payload["content_encoding"] = "plain"

        response = requests.post(
            NOTIFICATION_ENDPOINT_FOR_FORM_SUBMISSION,
            data=form_payload,
            headers={
                "accept": "application/json",
                "x-api-key": api_key
            }
        )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to send form notification: {response.text}"
            )

        return {
            "status": "success",
            "message": f"form submitted successfully from {source}"
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send form notification: {str(e)}"
        )