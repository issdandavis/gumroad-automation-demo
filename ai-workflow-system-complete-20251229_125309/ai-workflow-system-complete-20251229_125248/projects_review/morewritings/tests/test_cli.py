"""
Tests for CLI commands (mocked).
"""
import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from morewritings.cli import cli
from morewritings.models import Scene, Profile, Scenery


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_generators():
    """Mock all generators."""
    with patch('morewritings.cli.SceneGenerator') as scene_gen, \
         patch('morewritings.cli.ProfileGenerator') as profile_gen, \
         patch('morewritings.cli.SceneryGenerator') as scenery_gen:
        
        # Mock scene generator
        scene_instance = MagicMock()
        scene_instance.generate.return_value = Scene(
            title="Test Scene",
            content="Test content",
            characters=["Alice"],
            genre="test"
        )
        scene_gen.return_value = scene_instance
        
        # Mock profile generator
        profile_instance = MagicMock()
        profile_instance.generate.return_value = Profile(
            name="Test Character",
            description="Test description"
        )
        profile_gen.return_value = profile_instance
        
        # Mock scenery generator
        scenery_instance = MagicMock()
        scenery_instance.generate.return_value = Scenery(
            name="Test Location",
            location_type="outdoor",
            description="Test description"
        )
        scenery_gen.return_value = scenery_instance
        
        yield {
            'scene': scene_instance,
            'profile': profile_instance,
            'scenery': scenery_instance
        }


def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_generate_scene_basic(runner, mock_generators):
    """Test basic scene generation."""
    result = runner.invoke(cli, [
        'generate-scene',
        'Test prompt',
        '--api-key', 'test-key'
    ])
    assert result.exit_code == 0
    assert 'SCENE:' in result.output
    assert 'Test content' in result.output


def test_generate_scene_with_options(runner, mock_generators):
    """Test scene generation with options."""
    result = runner.invoke(cli, [
        'generate-scene',
        'Test prompt',
        '--title', 'My Scene',
        '--characters', 'Alice',
        '--characters', 'Bob',
        '--genre', 'fantasy',
        '--api-key', 'test-key'
    ])
    assert result.exit_code == 0
    mock_generators['scene'].generate.assert_called_once()


def test_generate_profile(runner, mock_generators):
    """Test profile generation."""
    result = runner.invoke(cli, [
        'generate-profile',
        'Test prompt',
        '--name', 'Test Character',
        '--api-key', 'test-key'
    ])
    assert result.exit_code == 0
    assert 'CHARACTER PROFILE:' in result.output


def test_generate_scenery(runner, mock_generators):
    """Test scenery generation."""
    result = runner.invoke(cli, [
        'generate-scenery',
        'Test prompt',
        '--name', 'Test Location',
        '--type', 'outdoor',
        '--api-key', 'test-key'
    ])
    assert result.exit_code == 0
    assert 'SCENERY:' in result.output


def test_generate_scene_with_output(runner, mock_generators, tmp_path):
    """Test scene generation with file output."""
    output_file = tmp_path / "scene.json"
    result = runner.invoke(cli, [
        'generate-scene',
        'Test prompt',
        '--output', str(output_file),
        '--api-key', 'test-key'
    ])
    assert result.exit_code == 0
    assert output_file.exists()
    
    # Verify JSON content
    with open(output_file) as f:
        data = json.load(f)
        assert data['title'] == 'Test Scene'
        assert data['content'] == 'Test content'
