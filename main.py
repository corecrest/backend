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
        notification: The notification payload
    """
    try:
        # Get environment variables
        notification_endpoint = os.getenv("NOTIFICATION_ENDPOINT", "http://64.227.102.129:8000/api/v1/notifications/")
        api_key = os.getenv("API_KEY")

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: Missing API key"
            )

        # Send the notification
        response = requests.post(
            notification_endpoint,
            json=notification.model_dump(),
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
            "message": f"{form_type} form submitted successfully"
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
    return {"status": "ok", "message": "Form submission API is running"} 