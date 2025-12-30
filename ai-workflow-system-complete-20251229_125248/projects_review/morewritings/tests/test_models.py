"""
Tests for data models.
"""
import pytest
from datetime import datetime
from morewritings.models import Profile, Scenery, Scene, GenerationRequest


def test_profile_creation():
    """Test creating a profile."""
    profile = Profile(
        name="Test Character",
        description="A test character",
        traits=["brave", "clever"],
        background="Born in a small village"
    )
    assert profile.name == "Test Character"
    assert len(profile.traits) == 2
    assert profile.background == "Born in a small village"
    assert isinstance(profile.created_at, datetime)


def test_scenery_creation():
    """Test creating scenery."""
    scenery = Scenery(
        name="Dark Forest",
        location_type="outdoor",
        description="A mysterious forest",
        mood="eerie",
        time_of_day="night"
    )
    assert scenery.name == "Dark Forest"
    assert scenery.location_type == "outdoor"
    assert scenery.mood == "eerie"
    assert isinstance(scenery.created_at, datetime)


def test_scene_creation():
    """Test creating a scene."""
    scene = Scene(
        title="The Meeting",
        characters=["Alice", "Bob"],
        scenery="Coffee Shop",
        content="They met at dawn...",
        genre="drama",
        mood="tense"
    )
    assert scene.title == "The Meeting"
    assert len(scene.characters) == 2
    assert scene.genre == "drama"
    assert isinstance(scene.created_at, datetime)


def test_generation_request():
    """Test creating a generation request."""
    request = GenerationRequest(
        type="scene",
        prompt="Generate a scene",
        model="gpt-4",
        temperature=0.7
    )
    assert request.type == "scene"
    assert request.prompt == "Generate a scene"
    assert request.temperature == 0.7
    assert request.max_tokens == 2000  # default


def test_profile_serialization():
    """Test profile can be serialized to dict."""
    profile = Profile(
        name="Test",
        description="Test description"
    )
    data = profile.model_dump()
    assert data["name"] == "Test"
    assert data["description"] == "Test description"
    assert "created_at" in data
