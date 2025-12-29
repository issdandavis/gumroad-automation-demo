"""
Command-line interface for morewritings.
"""
import click
import json
import os
import yaml
from pathlib import Path
from typing import Optional
from ..generators import SceneGenerator, ProfileGenerator, SceneryGenerator
from ..models import Scene, Profile, Scenery


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Morewritings - AI-powered creative writing tool for scenes, profiles, and scenery."""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--title", default="Generated Scene", help="Title for the scene")
@click.option("--characters", multiple=True, help="Characters in the scene")
@click.option("--scenery", help="Setting/scenery for the scene")
@click.option("--genre", help="Genre of the scene")
@click.option("--mood", help="Mood/tone of the scene")
@click.option("--output", "-o", help="Output file path (JSON)")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def generate_scene(
    prompt: str,
    title: str,
    characters: tuple,
    scenery: Optional[str],
    genre: Optional[str],
    mood: Optional[str],
    output: Optional[str],
    api_key: Optional[str]
):
    """Generate a scene using AI.
    
    Example:
        morewritings generate-scene "A tense negotiation in a dimly lit room" \\
            --characters Alice --characters Bob --genre thriller --mood suspenseful
    """
    try:
        generator = SceneGenerator(api_key=api_key)
        scene = generator.generate(
            prompt=prompt,
            title=title,
            characters=list(characters),
            scenery=scenery,
            genre=genre,
            mood=mood
        )
        
        # Output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(scene.model_dump(), f, indent=2, default=str)
            click.echo(f"Scene saved to {output}")
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"SCENE: {scene.title}")
            click.echo(f"{'='*60}\n")
            if scene.characters:
                click.echo(f"Characters: {', '.join(scene.characters)}")
            if scene.genre:
                click.echo(f"Genre: {scene.genre}")
            if scene.mood:
                click.echo(f"Mood: {scene.mood}")
            click.echo(f"\n{scene.content}\n")
            click.echo(f"{'='*60}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("prompt")
@click.option("--name", help="Character name")
@click.option("--output", "-o", help="Output file path (JSON)")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def generate_profile(
    prompt: str,
    name: Optional[str],
    output: Optional[str],
    api_key: Optional[str]
):
    """Generate a character profile using AI.
    
    Example:
        morewritings generate-profile "A retired detective with a mysterious past" \\
            --name "John Rivers"
    """
    try:
        generator = ProfileGenerator(api_key=api_key)
        profile = generator.generate(prompt=prompt, name=name)
        
        # Output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(profile.model_dump(), f, indent=2, default=str)
            click.echo(f"Profile saved to {output}")
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"CHARACTER PROFILE: {profile.name}")
            click.echo(f"{'='*60}\n")
            click.echo(profile.description)
            click.echo(f"\n{'='*60}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("prompt")
@click.option("--name", help="Location name")
@click.option("--type", "location_type", help="Location type (indoor/outdoor/fantasy/sci-fi)")
@click.option("--mood", help="Mood/atmosphere")
@click.option("--time", "time_of_day", help="Time of day")
@click.option("--weather", help="Weather conditions")
@click.option("--output", "-o", help="Output file path (JSON)")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def generate_scenery(
    prompt: str,
    name: Optional[str],
    location_type: Optional[str],
    mood: Optional[str],
    time_of_day: Optional[str],
    weather: Optional[str],
    output: Optional[str],
    api_key: Optional[str]
):
    """Generate scenery/setting description using AI.
    
    Example:
        morewritings generate-scenery "An abandoned lighthouse on a rocky coast" \\
            --name "Blackstone Lighthouse" --mood eerie --time dusk
    """
    try:
        generator = SceneryGenerator(api_key=api_key)
        scenery = generator.generate(
            prompt=prompt,
            name=name,
            location_type=location_type,
            mood=mood,
            time_of_day=time_of_day,
            weather=weather
        )
        
        # Output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(scenery.model_dump(), f, indent=2, default=str)
            click.echo(f"Scenery saved to {output}")
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"SCENERY: {scenery.name}")
            click.echo(f"{'='*60}")
            if scenery.location_type:
                click.echo(f"Type: {scenery.location_type}")
            if scenery.mood:
                click.echo(f"Mood: {scenery.mood}")
            if scenery.time_of_day:
                click.echo(f"Time: {scenery.time_of_day}")
            if scenery.weather:
                click.echo(f"Weather: {scenery.weather}")
            click.echo(f"\n{scenery.description}\n")
            click.echo(f"{'='*60}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("batch_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", default="generated_scenes", help="Output directory")
@click.option("--api-key", envvar="OPENAI_API_KEY", help="OpenAI API key")
def batch_generate(batch_file: str, output_dir: str, api_key: Optional[str]):
    """Generate multiple items from a batch file (YAML/JSON).
    
    The batch file should contain a list of generation requests with type and parameters.
    
    Example batch file (YAML):
        - type: scene
          prompt: "A mysterious encounter in a forest"
          title: "Forest Meeting"
          genre: fantasy
        - type: profile
          prompt: "A wise old wizard"
          name: "Merlin"
    """
    try:
        # Load batch file
        with open(batch_file) as f:
            if batch_file.endswith('.json'):
                requests = json.load(f)
            else:
                requests = yaml.safe_load(f)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process each request
        generators = {
            "scene": SceneGenerator(api_key=api_key),
            "profile": ProfileGenerator(api_key=api_key),
            "scenery": SceneryGenerator(api_key=api_key)
        }
        
        results = []
        for i, req in enumerate(requests, 1):
            req_type = req.pop("type")
            prompt = req.pop("prompt")
            
            click.echo(f"Generating {req_type} {i}/{len(requests)}...")
            
            generator = generators.get(req_type)
            if not generator:
                click.echo(f"Unknown type: {req_type}", err=True)
                continue
            
            result = generator.generate(prompt=prompt, **req)
            
            # Save result
            filename = f"{req_type}_{i:03d}.json"
            with open(output_path / filename, 'w') as f:
                json.dump(result.model_dump(), f, indent=2, default=str)
            
            results.append({"type": req_type, "file": filename})
            click.echo(f"  Saved to {filename}")
        
        click.echo(f"\nGenerated {len(results)} items in {output_dir}/")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
