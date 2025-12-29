"""
Data models for profiles, scenes, and scenery.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class Profile(BaseModel):
    """Character or entity profile."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    name: str
    description: str
    traits: List[str] = Field(default_factory=list)
    background: Optional[str] = None
    relationships: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class Scenery(BaseModel):
    """Setting or environment description."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    name: str
    location_type: str  # e.g., "indoor", "outdoor", "fantasy", "sci-fi"
    description: str
    mood: Optional[str] = None
    time_of_day: Optional[str] = None
    weather: Optional[str] = None
    details: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Scene(BaseModel):
    """A complete scene with characters, setting, and narrative."""
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    title: str
    characters: List[str] = Field(default_factory=list)
    scenery: Optional[str] = None
    content: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationRequest(BaseModel):
    """Request for AI-generated content."""
    type: str  # "scene", "profile", "scenery"
    prompt: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
