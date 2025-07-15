"""
Authentication router for Gmail OAuth2 integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from typing import Dict, Optional
import os
from urllib.parse import urlencode

from services import GmailService

router = APIRouter()

# Store for demo purposes - in production use proper session management
auth_state = {"authenticated": False, "gmail_service": None}


@router.get("/status")
async def auth_status() -> Dict[str, bool]:
    """Check authentication status."""
    return {"authenticated": auth_state["authenticated"]}


@router.get("/login")
async def login():
    """Initiate Gmail OAuth2 login."""
    try:
        # Check for credentials file
        if not os.path.exists('credentials.json'):
            raise HTTPException(
                status_code=500,
                detail="credentials.json not found. Please set up Google OAuth2 credentials."
            )
        
        gmail_service = GmailService()
        
        # In a real app, this would redirect to Google OAuth
        # For demo, we'll simulate the process
        if gmail_service.authenticate():
            auth_state["authenticated"] = True
            auth_state["gmail_service"] = gmail_service
            return {"message": "Authentication successful", "authenticated": True}
        else:
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@router.post("/logout")
async def logout():
    """Logout user."""
    auth_state["authenticated"] = False
    auth_state["gmail_service"] = None
    return {"message": "Logged out successfully", "authenticated": False}


@router.get("/emails")
async def get_emails(max_results: int = 10):
    """Get emails from authenticated user's Gmail."""
    if not auth_state["authenticated"] or not auth_state["gmail_service"]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        gmail_service = auth_state["gmail_service"]
        messages = gmail_service.get_inbox_messages(max_results=max_results)
        
        # Extract email info
        emails = []
        for message in messages:
            email_info = gmail_service.extract_message_info(message)
            emails.append(email_info)
        
        return {"emails": emails, "count": len(emails)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching emails: {str(e)}")