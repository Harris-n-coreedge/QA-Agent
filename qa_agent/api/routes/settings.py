"""
Settings management endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

router = APIRouter()

class SettingsModel(BaseModel):
    apiKeys: Optional[Dict[str, str]] = None
    browserSettings: Optional[Dict[str, Any]] = None
    testSettings: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None

# In-memory settings storage (in production, use database)
settings_store = {
    "apiKeys": {
        "openai": "",
        "anthropic": "",
        "google": ""
    },
    "browserSettings": {
        "stealth": True,
        "headless": True,
        "timeout": 30
    },
    "testSettings": {
        "maxRetries": 3,
        "waitTime": 5,
        "screenshotOnFailure": True
    },
    "notifications": {
        "email": "",
        "enabled": False
    }
}

@router.get("/settings")
async def get_settings():
    """Get current settings."""
    return settings_store

@router.post("/settings")
async def update_settings(settings: SettingsModel):
    """Update settings."""
    try:
        # Update settings store with new values
        if settings.apiKeys:
            settings_store["apiKeys"].update(settings.apiKeys)
        if settings.browserSettings:
            settings_store["browserSettings"].update(settings.browserSettings)
        if settings.testSettings:
            settings_store["testSettings"].update(settings.testSettings)
        if settings.notifications:
            settings_store["notifications"].update(settings.notifications)
        
        return {"message": "Settings updated successfully", "settings": settings_store}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@router.get("/settings/reset")
async def reset_settings():
    """Reset settings to defaults."""
    global settings_store
    settings_store = {
        "apiKeys": {
            "openai": "",
            "anthropic": "",
            "google": ""
        },
        "browserSettings": {
            "stealth": True,
            "headless": True,
            "timeout": 30
        },
        "testSettings": {
            "maxRetries": 3,
            "waitTime": 5,
            "screenshotOnFailure": True
        },
        "notifications": {
            "email": "",
            "enabled": False
        }
    }
    return {"message": "Settings reset to defaults", "settings": settings_store}

