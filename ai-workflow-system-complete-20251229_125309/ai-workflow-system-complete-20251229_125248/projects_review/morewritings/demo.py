#!/usr/bin/env python3
"""
Demo script showing morewritings capabilities without requiring an API key.
This uses mock data to demonstrate the tool's features.
"""

from datetime import datetime
from morewritings.models import Scene, Profile, Scenery
import json

print("=" * 70)
print("MOREWRITINGS DEMO - Showcasing Tool Capabilities")
print("=" * 70)
print()

# Demo 1: Scene Example
print("📝 EXAMPLE SCENE:")
print("-" * 70)
demo_scene = Scene(
    title="The Last Stand",
    characters=["Captain Sarah Chen", "Dr. Marcus Vale"],
    scenery="Abandoned Research Station",
    content="""The emergency lights flickered, casting eerie shadows across the 
abandoned research station. Captain Sarah Chen gripped her weapon tighter as 
footsteps echoed through the corridor.

"They're getting closer," Dr. Marcus Vale whispered, his hands trembling as 
he worked on the terminal. "Just give me two more minutes."

Sarah glanced at the sealed door behind them. "We don't have two minutes."

The sound of metal scraping against metal filled the air. Whatever was out 
there knew they were trapped. Marcus's fingers flew across the keyboard, 
sweat beading on his forehead.

"Got it!" he exclaimed. The terminal beeped, and a hidden panel slid open, 
revealing a narrow escape route.

"Move!" Sarah ordered, covering their retreat as the door began to buckle.""",
    genre="sci-fi thriller",
    mood="suspenseful",
    tags=["action", "space", "survival"]
)

print(f"Title: {demo_scene.title}")
print(f"Genre: {demo_scene.genre}")
print(f"Mood: {demo_scene.mood}")
print(f"Characters: {', '.join(demo_scene.characters)}")
print(f"Setting: {demo_scene.scenery}")
print()
print(demo_scene.content)
print()

# Demo 2: Character Profile Example
print("=" * 70)
print("👤 EXAMPLE CHARACTER PROFILE:")
print("-" * 70)
demo_profile = Profile(
    name="Elara Moonwhisper",
    description="""A enigmatic elven ranger who has walked the ancient forests 
for over three centuries. Elara possesses an uncanny ability to communicate 
with woodland creatures and read the secrets hidden in nature. Her silver hair 
and piercing amber eyes speak of her connection to the mystical realm.""",
    traits=[
        "Patient and observant",
        "Deeply connected to nature",
        "Slow to trust but fiercely loyal",
        "Expert archer and tracker",
        "Knowledgeable in ancient lore"
    ],
    background="""Born in the hidden city of Silverleaf, Elara left her home 
after witnessing the destruction of an ancient grove by human settlers. For 
the past century, she has served as a guardian of the wilderness, protecting 
the balance between civilization and nature.""",
    relationships={
        "The Elder Council": "Respectful but distant",
        "Human settlements": "Wary observer",
        "Forest spirits": "Trusted companions"
    }
)

print(f"Name: {demo_profile.name}")
print(f"\nDescription:")
print(demo_profile.description)
print(f"\nTraits:")
for trait in demo_profile.traits:
    print(f"  • {trait}")
print(f"\nBackground:")
print(demo_profile.background)
print(f"\nRelationships:")
for entity, relationship in demo_profile.relationships.items():
    print(f"  • {entity}: {relationship}")
print()

# Demo 3: Scenery Example
print("=" * 70)
print("🏞️  EXAMPLE SCENERY:")
print("-" * 70)
demo_scenery = Scenery(
    name="The Crimson Archives",
    location_type="indoor - library",
    description="""Towering shelves of dark mahogany stretch toward a vaulted 
ceiling lost in shadows. Thousands of ancient tomes, their spines bound in 
leather and emblazoned with gold, line the walls. Crimson velvet curtains 
filter the light from tall, arched windows, casting everything in a warm, 
blood-red glow.

The air is thick with the scent of old paper, leather, and something else—
something older and indefinable. A spiral staircase of wrought iron winds 
upward to a second level, where more shelves disappear into the darkness.

In the center of the room sits a massive reading table of polished obsidian, 
surrounded by high-backed chairs. Candelabras provide flickering light, their 
flames dancing in an imperceptible breeze. The silence here is absolute, 
broken only by the occasional whisper of turning pages—though no one else 
appears to be present.""",
    mood="mysterious and scholarly",
    time_of_day="late evening",
    details=[
        "Ancient tomes with gold embossing",
        "Crimson velvet curtains",
        "Obsidian reading table",
        "Wrought iron spiral staircase",
        "Flickering candelabras"
    ]
)

print(f"Location: {demo_scenery.name}")
print(f"Type: {demo_scenery.location_type}")
print(f"Mood: {demo_scenery.mood}")
print(f"Time: {demo_scenery.time_of_day}")
print()
print(demo_scenery.description)
print(f"\nNotable Details:")
for detail in demo_scenery.details:
    print(f"  • {detail}")
print()

# Demo 4: Show JSON export capability
print("=" * 70)
print("💾 JSON EXPORT EXAMPLE:")
print("-" * 70)
print("All generated content can be saved as JSON for later use:")
print()
print(json.dumps(demo_scene.model_dump(), indent=2, default=str)[:500] + "...")
print()

# Demo 5: Show how to use the tool
print("=" * 70)
print("🚀 HOW TO USE MOREWRITINGS:")
print("-" * 70)
print("""
To generate your own content with AI:

1. Set your OpenAI API key:
   export OPENAI_API_KEY="your-key-here"

2. Generate a scene:
   morewritings generate-scene "Your prompt here" --genre fantasy

3. Generate a character:
   morewritings generate-profile "Your character description" --name "Name"

4. Generate scenery:
   morewritings generate-scenery "Your location description" --mood eerie

5. Batch generate from a file:
   morewritings batch-generate examples/batch_example.yaml

See README.md and QUICKSTART.md for full documentation!
""")

print("=" * 70)
print("✨ These examples show what morewritings can create for you!")
print("=" * 70)
