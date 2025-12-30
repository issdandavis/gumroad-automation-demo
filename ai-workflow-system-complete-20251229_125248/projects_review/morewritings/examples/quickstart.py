"""
Quick start guide for using morewritings.
"""

# Example 1: Generate a simple scene
from morewritings.generators import SceneGenerator

generator = SceneGenerator(api_key="your-api-key")
scene = generator.generate(
    prompt="A mysterious meeting at midnight",
    title="Midnight Encounter",
    genre="mystery",
    mood="suspenseful"
)

print(f"Title: {scene.title}")
print(f"Content: {scene.content}")

# Example 2: Generate a character profile
from morewritings.generators import ProfileGenerator

profile_gen = ProfileGenerator(api_key="your-api-key")
character = profile_gen.generate(
    prompt="A wise old wizard with a secret",
    name="Merlin Shadowbrook"
)

print(f"Character: {character.name}")
print(f"Description: {character.description}")

# Example 3: Generate scenery
from morewritings.generators import SceneryGenerator

scenery_gen = SceneryGenerator(api_key="your-api-key")
location = scenery_gen.generate(
    prompt="An ancient library filled with forbidden knowledge",
    name="The Obsidian Archives",
    location_type="indoor",
    mood="mysterious"
)

print(f"Location: {location.name}")
print(f"Description: {location.description}")

# Example 4: Save to file
import json

with open("my_scene.json", "w") as f:
    json.dump(scene.model_dump(), f, indent=2, default=str)
