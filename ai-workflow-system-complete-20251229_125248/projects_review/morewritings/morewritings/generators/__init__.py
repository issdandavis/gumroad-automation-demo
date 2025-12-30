"""
AI-powered content generators for scenes, profiles, and scenery.
"""
import os
from typing import Optional, Dict, Any
from openai import OpenAI
from ..models import Scene, Profile, Scenery, GenerationRequest


class AIGenerator:
    """Base class for AI-powered content generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key)
    
    def _generate(self, request: GenerationRequest) -> str:
        """Generate content using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(request.type)},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {str(e)}")
    
    def _get_system_prompt(self, content_type: str) -> str:
        """Get system prompt based on content type."""
        prompts = {
            "scene": "You are a creative writing assistant specializing in crafting vivid, engaging scenes. Focus on sensory details, character interactions, and compelling narrative.",
            "profile": "You are a character development expert. Create detailed, believable character profiles with rich backgrounds, motivations, and unique traits.",
            "scenery": "You are an expert at describing settings and environments. Create immersive, atmospheric descriptions that bring locations to life."
        }
        return prompts.get(content_type, "You are a helpful creative writing assistant.")


class SceneGenerator(AIGenerator):
    """Generate scenes with AI assistance."""
    
    def generate(
        self,
        prompt: str,
        characters: Optional[list] = None,
        scenery: Optional[str] = None,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        **kwargs
    ) -> Scene:
        """Generate a scene based on the prompt and parameters."""
        # Build enhanced prompt
        enhanced_prompt = prompt
        if characters:
            enhanced_prompt += f"\n\nCharacters involved: {', '.join(characters)}"
        if scenery:
            enhanced_prompt += f"\nSetting: {scenery}"
        if genre:
            enhanced_prompt += f"\nGenre: {genre}"
        if mood:
            enhanced_prompt += f"\nMood/Tone: {mood}"
        
        # Create request
        request = GenerationRequest(
            type="scene",
            prompt=enhanced_prompt,
            parameters=kwargs
        )
        
        # Generate content
        content = self._generate(request)
        
        # Create scene object
        return Scene(
            title=kwargs.get("title", "Generated Scene"),
            characters=characters or [],
            scenery=scenery,
            content=content,
            genre=genre,
            mood=mood,
            tags=kwargs.get("tags", [])
        )


class ProfileGenerator(AIGenerator):
    """Generate character profiles with AI assistance."""
    
    def generate(
        self,
        prompt: str,
        name: Optional[str] = None,
        **kwargs
    ) -> Profile:
        """Generate a character profile based on the prompt."""
        # Build enhanced prompt
        enhanced_prompt = f"Create a detailed character profile.\n\n{prompt}"
        if name:
            enhanced_prompt += f"\n\nCharacter name: {name}"
        
        # Create request
        request = GenerationRequest(
            type="profile",
            prompt=enhanced_prompt,
            parameters=kwargs
        )
        
        # Generate content
        content = self._generate(request)
        
        # Parse the generated content (simplified - in production, use structured output)
        return Profile(
            name=name or "Unnamed Character",
            description=content,
            traits=kwargs.get("traits", []),
            background=kwargs.get("background")
        )


class SceneryGenerator(AIGenerator):
    """Generate scenery/setting descriptions with AI assistance."""
    
    def generate(
        self,
        prompt: str,
        name: Optional[str] = None,
        location_type: Optional[str] = None,
        **kwargs
    ) -> Scenery:
        """Generate scenery based on the prompt."""
        # Build enhanced prompt
        enhanced_prompt = f"Describe a setting/location.\n\n{prompt}"
        if location_type:
            enhanced_prompt += f"\n\nType: {location_type}"
        if kwargs.get("mood"):
            enhanced_prompt += f"\nMood: {kwargs['mood']}"
        if kwargs.get("time_of_day"):
            enhanced_prompt += f"\nTime: {kwargs['time_of_day']}"
        
        # Create request
        request = GenerationRequest(
            type="scenery",
            prompt=enhanced_prompt,
            parameters=kwargs
        )
        
        # Generate content
        content = self._generate(request)
        
        # Create scenery object
        return Scenery(
            name=name or "Unnamed Location",
            location_type=location_type or "general",
            description=content,
            mood=kwargs.get("mood"),
            time_of_day=kwargs.get("time_of_day"),
            weather=kwargs.get("weather")
        )
