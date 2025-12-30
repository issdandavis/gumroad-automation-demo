# Quick Start Guide

Welcome to Morewritings! This guide will help you get started quickly.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/issdandavis/morewritings.git
   cd morewritings
   ```

2. **Install the package:**
   ```bash
   pip install -e .
   ```

3. **Set up your API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file (see `examples/.env.example`)

## Basic Usage

### Generate a Scene

The simplest way to generate a scene:

```bash
morewritings generate-scene "A mysterious stranger arrives in a small town at midnight"
```

With more options:

```bash
morewritings generate-scene "A heated argument between two old friends" \
    --title "Breaking Point" \
    --characters Alice \
    --characters Bob \
    --genre drama \
    --mood tense
```

### Generate a Character Profile

```bash
morewritings generate-profile "A brave knight with a secret fear of horses" \
    --name "Sir Galahad"
```

### Generate Scenery

```bash
morewritings generate-scenery "A dark forest with ancient trees and mysterious fog" \
    --name "The Whispering Woods" \
    --type outdoor \
    --mood eerie \
    --time midnight
```

### Save Output to File

Add `-o` or `--output` to save as JSON:

```bash
morewritings generate-scene "A space battle near a dying star" \
    --genre sci-fi \
    --output my_scenes/space_battle.json
```

### Batch Generation

Create multiple items at once using a YAML file:

```bash
morewritings batch-generate examples/batch_example.yaml --output-dir my_content
```

## Examples

Check the `examples/` directory for:
- `batch_example.yaml` - Sample batch file with scenes, profiles, and scenery
- `quickstart.py` - Python API usage examples
- `.env.example` - Environment configuration template

## Tips

1. **Be Specific**: The more detailed your prompt, the better the results
2. **Use Parameters**: Genre, mood, and character names help guide the AI
3. **Iterate**: Generate multiple versions and pick the best
4. **Combine**: Use scenery and profiles together when generating scenes
5. **Batch Process**: Use YAML files for generating multiple related items

## Common Commands

```bash
# Get help
morewritings --help
morewritings generate-scene --help

# Check version
morewritings --version

# Generate with custom API key
morewritings generate-scene "prompt" --api-key sk-xxx

# Save to specific location
morewritings generate-profile "prompt" -o profiles/character.json
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [templates/scene_templates.yaml](templates/scene_templates.yaml) for prompt ideas
- Try the [quickstart.py](examples/quickstart.py) Python examples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute

## Need Help?

- Open an issue on GitHub
- Check the documentation in README.md
- See examples in the `examples/` directory

Happy writing! 🎭📝
