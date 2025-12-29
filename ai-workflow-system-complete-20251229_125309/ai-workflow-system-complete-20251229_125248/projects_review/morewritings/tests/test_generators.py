"""
Tests for generators (mocked).
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from morewritings.generators import SceneGenerator, ProfileGenerator, SceneryGenerator
from morewritings.models import Scene, Profile, Scenery


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('morewritings.generators.OpenAI') as mock:
        client = MagicMock()
        mock.return_value = client
        
        # Mock response
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "Generated content"
        client.chat.completions.create.return_value = response
        
        yield client


def test_scene_generator_initialization(mock_openai_client):
    """Test SceneGenerator initialization."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = SceneGenerator()
        assert generator.api_key == 'test-key'


def test_scene_generator_missing_api_key():
    """Test SceneGenerator raises error without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key required"):
            SceneGenerator()


def test_scene_generation(mock_openai_client):
    """Test scene generation."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = SceneGenerator()
        scene = generator.generate(
            prompt="Test prompt",
            title="Test Scene",
            characters=["Alice", "Bob"],
            genre="fantasy"
        )
        
        assert isinstance(scene, Scene)
        assert scene.title == "Test Scene"
        assert scene.characters == ["Alice", "Bob"]
        assert scene.genre == "fantasy"
        assert scene.content == "Generated content"


def test_profile_generation(mock_openai_client):
    """Test profile generation."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = ProfileGenerator()
        profile = generator.generate(
            prompt="Test prompt",
            name="Test Character"
        )
        
        assert isinstance(profile, Profile)
        assert profile.name == "Test Character"
        assert profile.description == "Generated content"


def test_scenery_generation(mock_openai_client):
    """Test scenery generation."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        generator = SceneryGenerator()
        scenery = generator.generate(
            prompt="Test prompt",
            name="Test Location",
            location_type="outdoor",
            mood="peaceful"
        )
        
        assert isinstance(scenery, Scenery)
        assert scenery.name == "Test Location"
        assert scenery.location_type == "outdoor"
        assert scenery.mood == "peaceful"
        assert scenery.description == "Generated content"
