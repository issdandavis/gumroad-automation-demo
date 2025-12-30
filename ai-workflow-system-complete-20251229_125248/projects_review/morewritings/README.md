# Morewritings

AI-powered creative writing tool for generating scenes, character profiles, and scenery descriptions.

## Overview

Morewritings is a command-line tool that leverages OpenAI's GPT models to help writers create:
- **Scenes**: Complete narrative scenes with characters, settings, and dialogue
- **Character Profiles**: Detailed character backgrounds, traits, and motivations
- **Scenery**: Vivid environmental and setting descriptions

## Features

- 🎭 **Scene Generation**: Create complete scenes with customizable parameters (genre, mood, characters)
- 👥 **Character Profiles**: Generate detailed character backgrounds and personalities
- 🏞️ **Scenery Descriptions**: Craft immersive settings and environments
- 📦 **Batch Processing**: Generate multiple items from YAML/JSON configuration files
- 💾 **Export Support**: Save generated content as JSON for later use
- 🎨 **Customizable**: Control tone, genre, mood, and other creative parameters

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Install from source

```bash
git clone https://github.com/issdandavis/morewritings.git
cd morewritings
pip install -e .
```

### Install dependencies only

```bash
pip install -r requirements.txt
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in your project directory:

```bash
cp examples/.env.example .env
# Edit .env and add your API key
```

## Usage

### Generate a Scene

```bash
morewritings generate-scene "A tense negotiation in a dimly lit room" \
    --title "The Deal" \
    --characters Alice \
    --characters Bob \
    --genre thriller \
    --mood suspenseful
```

### Generate a Character Profile

```bash
morewritings generate-profile "A retired detective with a mysterious past" \
    --name "John Rivers"
```

### Generate Scenery

```bash
morewritings generate-scenery "An abandoned lighthouse on a rocky coast" \
    --name "Blackstone Lighthouse" \
    --type outdoor \
    --mood eerie \
    --time dusk \
    --weather stormy
```

### Save Output to File

Add `--output` or `-o` to save results as JSON:

```bash
morewritings generate-scene "A magical duel in an ancient library" \
    --output scenes/magical_duel.json \
    --genre fantasy
```

### Batch Generation

Create multiple items from a YAML configuration file:

```bash
morewritings batch-generate examples/batch_example.yaml \
    --output-dir my_generated_content
```

Example batch file (`batch.yaml`):

```yaml
- type: scene
  prompt: "Two rivals must work together"
  title: "Unlikely Alliance"
  genre: adventure
  
- type: profile
  prompt: "A brilliant inventor"
  name: "Dr. Elena Watts"
  
- type: scenery
  prompt: "A futuristic floating city"
  name: "Skyreach"
  location_type: sci-fi
```

## Command Reference

### `generate-scene`

Generate a narrative scene.

**Options:**
- `--title TEXT`: Scene title (default: "Generated Scene")
- `--characters TEXT`: Characters in the scene (can specify multiple)
- `--scenery TEXT`: Setting/location for the scene
- `--genre TEXT`: Genre (e.g., fantasy, sci-fi, thriller, drama)
- `--mood TEXT`: Mood/tone (e.g., suspenseful, melancholic, joyful)
- `--output, -o PATH`: Save to JSON file
- `--api-key TEXT`: OpenAI API key (or set OPENAI_API_KEY env var)

### `generate-profile`

Generate a character profile.

**Options:**
- `--name TEXT`: Character name
- `--output, -o PATH`: Save to JSON file
- `--api-key TEXT`: OpenAI API key

### `generate-scenery`

Generate scenery/setting description.

**Options:**
- `--name TEXT`: Location name
- `--type TEXT`: Location type (indoor, outdoor, fantasy, sci-fi)
- `--mood TEXT`: Atmosphere/mood
- `--time TEXT`: Time of day
- `--weather TEXT`: Weather conditions
- `--output, -o PATH`: Save to JSON file
- `--api-key TEXT`: OpenAI API key

### `batch-generate`

Generate multiple items from a batch file.

**Arguments:**
- `BATCH_FILE`: Path to YAML or JSON batch file

**Options:**
- `--output-dir, -o PATH`: Output directory (default: "generated_scenes")
- `--api-key TEXT`: OpenAI API key

## Project Structure

```
morewritings/
├── morewritings/          # Main package
│   ├── __init__.py
│   ├── models/            # Data models (Scene, Profile, Scenery)
│   ├── generators/        # AI generation logic
│   └── cli/              # Command-line interface
├── tests/                 # Test suite
├── templates/             # Prompt templates
├── examples/              # Example files and configurations
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=morewritings --cov-report=html
```

### Code formatting

```bash
black morewritings/ tests/
```

### Linting

```bash
flake8 morewritings/ tests/
```

## Examples

See the `examples/` directory for:
- `batch_example.yaml`: Sample batch generation file
- `.env.example`: Environment configuration template
- Template files in `templates/`: Reusable prompt templates

## Use Cases

- **Writers**: Generate scene ideas, develop characters, create settings
- **Game Masters**: Create NPCs, locations, and encounters for RPG campaigns
- **Storytellers**: Build narrative elements for stories and worlds
- **Creative Teams**: Rapidly prototype story concepts and scenarios
- **Education**: Teach creative writing and narrative structure

## Limitations

- Requires internet connection for AI generation
- API usage incurs costs based on OpenAI pricing
- Generated content should be reviewed and edited
- Quality depends on prompt clarity and specificity

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Roadmap

Future enhancements planned:
- [ ] Support for multiple AI providers (Anthropic, local models)
- [ ] Interactive mode with conversation-based refinement
- [ ] Export to various formats (Markdown, PDF, DOCX)
- [ ] Template library and community sharing
- [ ] Character relationship graphs
- [ ] Story arc planning tools
- [ ] Integration with writing software (Scrivener, etc.)
- [ ] Web interface option 
