#!/usr/bin/env python3
"""
Codex Distribution System
Packages and distributes the Universal Language Codex to all AI systems
"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class CodexDistributor:
    """
    Distributes the Universal Language Codex to multiple AI systems
    Creates packages for different AI platforms and integration methods
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.distribution_path = self.base_path / "codex-distribution"
        self.distribution_path.mkdir(exist_ok=True)
        
    def create_master_codex_package(self) -> Dict[str, Any]:
        """Create the master codex package with all languages"""
        
        # Import our lexicon systems
        try:
            from integrated_lexicon import IntegratedLexicon, LanguageType
            lexicon = IntegratedLexicon()
        except ImportError:
            print("❌ Could not import lexicon - creating basic package")
            return self._create_basic_package()
        
        # Create comprehensive codex
        master_codex = {
            "metadata": {
                "name": "Universal Language Codex",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Complete translation system for 6 programming languages + 6 Sacred Tongues",
                "total_languages": 12,
                "creator": "App Productizer Universal Bridge System"
            },
            
            "programming_languages": {
                "python": self._extract_language_data(lexicon, LanguageType.PYTHON),
                "javascript": self._extract_language_data(lexicon, LanguageType.JAVASCRIPT),
                "go": self._extract_language_data(lexicon, LanguageType.GO),
                "rust": self._extract_language_data(lexicon, LanguageType.RUST),
                "csharp": self._extract_language_data(lexicon, LanguageType.CSHARP),
                "java": self._extract_language_data(lexicon, LanguageType.JAVA)
            },
            
            "sacred_tongues": {
                "koraelin": self._extract_language_data(lexicon, LanguageType.KORAELIN),
                "avali": self._extract_language_data(lexicon, LanguageType.AVALI),
                "runethic": self._extract_language_data(lexicon, LanguageType.RUNETHIC),
                "cassisivadan": self._extract_language_data(lexicon, LanguageType.CASSISIVADAN),
                "umbroth": self._extract_language_data(lexicon, LanguageType.UMBROTH),
                "draumric": self._extract_language_data(lexicon, LanguageType.DRAUMRIC)
            },
            
            "universal_constructs": [
                {
                    "concept": construct.concept,
                    "description": construct.description,
                    "programming_usage": construct.programming_usage,
                    "magical_usage": construct.magical_usage,
                    "translations": {
                        # Programming Languages
                        "python": construct.python,
                        "javascript": construct.javascript,
                        "go": construct.go,
                        "rust": construct.rust,
                        "csharp": construct.csharp,
                        "java": construct.java,
                        # Sacred Tongues
                        "koraelin": construct.koraelin,
                        "avali": construct.avali,
                        "runethic": construct.runethic,
                        "cassisivadan": construct.cassisivadan,
                        "umbroth": construct.umbroth,
                        "draumric": construct.draumric
                    }
                }
                for construct in lexicon.constructs
            ],
            
            "concept_bridges": lexicon.concept_bridges,
            "programming_patterns": lexicon.programming_patterns,
            "sacred_patterns": lexicon.sacred_patterns,
            
            "usage_instructions": {
                "for_ai_systems": "Import this codex to enable universal language translation",
                "for_developers": "Use the constructs to translate between any two languages",
                "for_magical_systems": "Sacred Tongues enable spell-to-code conversion",
                "integration_guide": "See integration examples for your specific AI platform"
            }
        }
        
        return master_codex
    
    def _extract_language_data(self, lexicon, language_type: LanguageType) -> Dict[str, Any]:
        """Extract language-specific data from lexicon"""
        
        language_data = {
            "name": language_type.value,
            "type": "programming" if language_type.value in ["python", "javascript", "go", "rust", "csharp", "java"] else "sacred",
            "constructs": {},
            "patterns": {},
            "examples": []
        }
        
        # Extract constructs for this language
        for construct in lexicon.constructs:
            lang_value = getattr(construct, language_type.value)
            language_data["constructs"][construct.concept] = {
                "syntax": lang_value,
                "description": construct.description,
                "usage": construct.programming_usage if language_data["type"] == "programming" else construct.magical_usage
            }
        
        # Add language-specific patterns
        if language_data["type"] == "programming":
            patterns = lexicon.programming_patterns.get("syntax_patterns", {}).get(language_type.value, {})
            language_data["patterns"] = patterns
        else:
            patterns = lexicon.sacred_patterns.get("magical_particles", {}).get(language_type.value, {})
            language_data["patterns"] = patterns
        
        return language_data
    
    def _create_basic_package(self) -> Dict[str, Any]:
        """Create basic package if lexicon import fails"""
        
        return {
            "metadata": {
                "name": "Basic Universal Codex",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Basic language translation system",
                "status": "Limited - full lexicon not available"
            },
            "note": "Full codex requires integrated_lexicon.py to be available"
        }
    
    def create_ai_platform_packages(self, master_codex: Dict[str, Any]) -> Dict[str, str]:
        """Create platform-specific packages for different AI systems"""
        
        packages = {}
        
        # 1. GitHub Copilot / VS Code Extension Package
        packages["github_copilot"] = self._create_github_copilot_package(master_codex)
        
        # 2. OpenAI API / ChatGPT Package
        packages["openai_api"] = self._create_openai_package(master_codex)
        
        # 3. Claude API Package
        packages["claude_api"] = self._create_claude_package(master_codex)
        
        # 4. Perplexity API Package
        packages["perplexity_api"] = self._create_perplexity_package(master_codex)
        
        # 5. Universal JSON Package (for any AI)
        packages["universal_json"] = self._create_universal_package(master_codex)
        
        # 6. Python Module Package
        packages["python_module"] = self._create_python_module_package(master_codex)
        
        # 7. JavaScript/Node.js Package
        packages["javascript_module"] = self._create_javascript_package(master_codex)
        
        return packages
    
    def _create_github_copilot_package(self, codex: Dict[str, Any]) -> str:
        """Create package for GitHub Copilot integration"""
        
        package_dir = self.distribution_path / "github-copilot"
        package_dir.mkdir(exist_ok=True)
        
        # Create VS Code extension format
        copilot_package = {
            "name": "universal-language-codex",
            "displayName": "Universal Language Codex",
            "description": "12-language translation system for programming and Sacred Tongues",
            "version": "1.0.0",
            "codex_data": codex,
            "integration_instructions": {
                "setup": "Install as VS Code extension or import JSON data",
                "usage": "Access codex.universal_constructs for translations",
                "example": "codex.programming_languages.python.constructs.function_spell"
            }
        }
        
        package_file = package_dir / "github-copilot-codex.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(copilot_package, f, indent=2, ensure_ascii=False)
        
        # Create README
        readme_content = """# Universal Language Codex - GitHub Copilot Integration

## Installation
1. Save `github-copilot-codex.json` to your project
2. Import in your code: `const codex = require('./github-copilot-codex.json')`

## Usage
```javascript
// Translate Python function to Kor'aelin spell
const pythonFunc = codex.programming_languages.python.constructs.function_spell.syntax;
const koraelinSpell = codex.sacred_tongues.koraelin.constructs.function_spell.syntax;
```

## Features
- 6 Programming Languages: Python, JavaScript, Go, Rust, C#, Java
- 6 Sacred Tongues: Kor'aelin, Avali, Runethic, Cassisivadan, Umbroth, Draumric
- Universal construct translation
- Code to Spell conversion
"""
        
        with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return str(package_file)
    
    def _create_openai_package(self, codex: Dict[str, Any]) -> str:
        """Create package for OpenAI API integration"""
        
        package_dir = self.distribution_path / "openai-api"
        package_dir.mkdir(exist_ok=True)
        
        # Create OpenAI-specific format with system prompts
        openai_package = {
            "system_prompt": """You are an AI with access to the Universal Language Codex, enabling translation between 12 languages:

Programming Languages: Python, JavaScript, Go, Rust, C#, Java
Sacred Tongues: Kor'aelin (binding), Avali (diplomatic), Runethic (ancient), Cassisivadan (inventive), Umbroth (shadow), Draumric (forge)

You can translate any programming concept to any other language, including fictional magical languages. Use the codex data below for accurate translations.""",
            
            "codex_data": codex,
            
            "example_prompts": [
                "Translate this Python function to Kor'aelin spell format",
                "Convert this JavaScript code to Draumric forge-tongue",
                "Transform this Runethic binding spell to Go code",
                "Show me the Sacred Tongue equivalent of this programming concept"
            ],
            
            "integration_guide": {
                "method": "Include this JSON in your system prompt or as context",
                "usage": "Reference codex_data.universal_constructs for translations",
                "api_call": "Pass codex as context in your OpenAI API calls"
            }
        }
        
        package_file = package_dir / "openai-codex.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(openai_package, f, indent=2, ensure_ascii=False)
        
        return str(package_file)
    
    def _create_claude_package(self, codex: Dict[str, Any]) -> str:
        """Create package for Claude API integration"""
        
        package_dir = self.distribution_path / "claude-api"
        package_dir.mkdir(exist_ok=True)
        
        claude_package = {
            "claude_system_message": """I have access to the Universal Language Codex containing 12 languages (6 programming + 6 Sacred Tongues). I can translate between any of these languages using the universal constructs system. The Sacred Tongues are fictional constructed languages with magical properties.""",
            
            "codex_data": codex,
            
            "claude_specific_features": {
                "long_context": "Full codex can be included in Claude's large context window",
                "reasoning": "Claude can explain translation reasoning and cultural context",
                "safety": "Claude will warn about dangerous magical constructs (e.g., Runethic reality-breaking spells)"
            }
        }
        
        package_file = package_dir / "claude-codex.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(claude_package, f, indent=2, ensure_ascii=False)
        
        return str(package_file)
    
    def _create_perplexity_package(self, codex: Dict[str, Any]) -> str:
        """Create package for Perplexity API integration"""
        
        package_dir = self.distribution_path / "perplexity-api"
        package_dir.mkdir(exist_ok=True)
        
        perplexity_package = {
            "perplexity_context": "Universal Language Codex for real-time translation between programming languages and fictional Sacred Tongues",
            "codex_data": codex,
            "search_enhancement": "Use codex for translating user queries into multiple language formats for better search results"
        }
        
        package_file = package_dir / "perplexity-codex.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(perplexity_package, f, indent=2, ensure_ascii=False)
        
        return str(package_file)
    
    def _create_universal_package(self, codex: Dict[str, Any]) -> str:
        """Create universal JSON package for any AI system"""
        
        package_file = self.distribution_path / "universal-codex.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(codex, f, indent=2, ensure_ascii=False)
        
        return str(package_file)
    
    def _create_python_module_package(self, codex: Dict[str, Any]) -> str:
        """Create Python module package"""
        
        package_dir = self.distribution_path / "python-module"
        package_dir.mkdir(exist_ok=True)
        
        # Create Python module
        python_module = f'''"""
Universal Language Codex - Python Module
Auto-generated from Universal Bridge System
"""

import json
from typing import Dict, List, Any, Optional

CODEX_DATA = {json.dumps(codex, indent=4)}

class UniversalTranslator:
    """Universal language translator using the codex"""
    
    def __init__(self):
        self.codex = CODEX_DATA
    
    def translate(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Translate text between any two languages"""
        
        # Find matching construct
        for construct in self.codex["universal_constructs"]:
            if construct["translations"][from_lang] == text:
                return construct["translations"][to_lang]
        
        return None
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a specific language"""
        
        if language in self.codex["programming_languages"]:
            return self.codex["programming_languages"][language]
        elif language in self.codex["sacred_tongues"]:
            return self.codex["sacred_tongues"][language]
        
        return {{}}
    
    def list_languages(self) -> List[str]:
        """List all available languages"""
        
        prog_langs = list(self.codex["programming_languages"].keys())
        sacred_langs = list(self.codex["sacred_tongues"].keys())
        return prog_langs + sacred_langs

# Create global translator instance
translator = UniversalTranslator()

# Convenience functions
def translate(text: str, from_lang: str, to_lang: str) -> Optional[str]:
    return translator.translate(text, from_lang, to_lang)

def get_languages() -> List[str]:
    return translator.list_languages()
'''
        
        with open(package_dir / "universal_codex.py", 'w', encoding='utf-8') as f:
            f.write(python_module)
        
        return str(package_dir / "universal_codex.py")
    
    def _create_javascript_package(self, codex: Dict[str, Any]) -> str:
        """Create JavaScript/Node.js package"""
        
        package_dir = self.distribution_path / "javascript-module"
        package_dir.mkdir(exist_ok=True)
        
        # Create JavaScript module
        js_module = f'''/**
 * Universal Language Codex - JavaScript Module
 * Auto-generated from Universal Bridge System
 */

const CODEX_DATA = {json.dumps(codex, indent=2)};

class UniversalTranslator {{
    constructor() {{
        this.codex = CODEX_DATA;
    }}
    
    translate(text, fromLang, toLang) {{
        // Find matching construct
        for (const construct of this.codex.universal_constructs) {{
            if (construct.translations[fromLang] === text) {{
                return construct.translations[toLang];
            }}
        }}
        return null;
    }}
    
    getLanguageInfo(language) {{
        if (this.codex.programming_languages[language]) {{
            return this.codex.programming_languages[language];
        }}
        if (this.codex.sacred_tongues[language]) {{
            return this.codex.sacred_tongues[language];
        }}
        return {{}};
    }}
    
    listLanguages() {{
        const progLangs = Object.keys(this.codex.programming_languages);
        const sacredLangs = Object.keys(this.codex.sacred_tongues);
        return [...progLangs, ...sacredLangs];
    }}
}}

// Create global translator instance
const translator = new UniversalTranslator();

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {{
    // Node.js
    module.exports = {{ UniversalTranslator, translator, CODEX_DATA }};
}} else if (typeof window !== 'undefined') {{
    // Browser
    window.UniversalTranslator = UniversalTranslator;
    window.universalTranslator = translator;
}}
'''
        
        with open(package_dir / "universal-codex.js", 'w', encoding='utf-8') as f:
            f.write(js_module)
        
        return str(package_dir / "universal-codex.js")
    
    def create_distribution_zip(self, packages: Dict[str, str]) -> str:
        """Create a complete distribution ZIP file"""
        
        zip_path = self.distribution_path / f"universal-codex-distribution-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all package files
            for platform, package_path in packages.items():
                if os.path.isfile(package_path):
                    zipf.write(package_path, f"{platform}/{os.path.basename(package_path)}")
                elif os.path.isdir(package_path):
                    # Add directory contents
                    for root, dirs, files in os.walk(package_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, self.distribution_path)
                            zipf.write(file_path, arc_path)
            
            # Add master README
            readme_content = self._create_master_readme()
            zipf.writestr("README.md", readme_content)
            
            # Add installation guide
            install_guide = self._create_installation_guide()
            zipf.writestr("INSTALLATION_GUIDE.md", install_guide)
        
        return str(zip_path)
    
    def _create_master_readme(self) -> str:
        """Create master README for the distribution"""
        
        return """# Universal Language Codex Distribution

## Overview
Complete translation system for 12 languages:
- **6 Programming Languages**: Python, JavaScript, Go, Rust, C#, Java
- **6 Sacred Tongues**: Kor'aelin, Avali, Runethic, Cassisivadan, Umbroth, Draumric

## What's Included
- `github-copilot/` - GitHub Copilot/VS Code integration
- `openai-api/` - OpenAI API integration
- `claude-api/` - Claude API integration  
- `perplexity-api/` - Perplexity API integration
- `python-module/` - Python module for direct import
- `javascript-module/` - JavaScript/Node.js module
- `universal-codex.json` - Universal JSON format

## Quick Start
1. Choose your AI platform directory
2. Follow the README in that directory
3. Import the codex data into your AI system
4. Start translating between any two languages!

## Features
- Programming to Programming translation
- Programming to Sacred Tongue translation  
- Sacred Tongue to Sacred Tongue translation
- Universal construct system
- Magical resonance analysis
- Cultural and emotional context

## Example Usage
```python
# Python
from universal_codex import translate
result = translate("def hello():", "python", "koraelin")
# Returns: "Thul'ael nav'sil" (Kor'aelin binding spell)
```

```javascript
// JavaScript
const { translate } = require('./universal-codex');
const result = translate("function hello() {", "javascript", "draumric");
// Returns: "Grondrak'tharn form" (Draumric forge creation)
```

## Support
Created by the App Productizer Universal Bridge System
For updates and support, check the original repository.
"""
    
    def _create_installation_guide(self) -> str:
        """Create installation guide"""
        
        return """# Installation Guide - Universal Language Codex

## For Different AI Platforms

### GitHub Copilot / VS Code
1. Copy `github-copilot/github-copilot-codex.json` to your project
2. In VS Code, create a new file and import:
   ```javascript
   const codex = require('./github-copilot-codex.json');
   ```
3. Access translations: `codex.codex_data.universal_constructs`

### OpenAI API / ChatGPT
1. Use `openai-api/openai-codex.json` as system context
2. Include in your API calls:
   ```python
   import json
   with open('openai-codex.json') as f:
       codex = json.load(f)
   
   # Add to system prompt
   system_prompt = codex['system_prompt']
   ```

### Claude API
1. Load `claude-api/claude-codex.json`
2. Include codex data in your Claude conversations
3. Claude can handle the full context due to large context window

### Perplexity API
1. Use `perplexity-api/perplexity-codex.json`
2. Include as context for enhanced search and translation

### Python Projects
1. Copy `python-module/universal_codex.py` to your project
2. Import and use:
   ```python
   from universal_codex import translate, get_languages
   
   # Translate between any languages
   result = translate("print('hello')", "python", "koraelin")
   
   # List all available languages
   languages = get_languages()
   ```

### JavaScript/Node.js Projects
1. Copy `javascript-module/universal-codex.js` to your project
2. Import and use:
   ```javascript
   const { translator } = require('./universal-codex');
   
   // Translate between any languages
   const result = translator.translate("console.log('hello')", "javascript", "avali");
   
   // List all available languages
   const languages = translator.listLanguages();
   ```

### Universal JSON (Any Platform)
1. Use `universal-codex.json` for any system that can read JSON
2. Parse the JSON and access:
   - `programming_languages` - Programming language data
   - `sacred_tongues` - Sacred Tongue data
   - `universal_constructs` - Translation mappings
   - `concept_bridges` - Cross-domain concept mapping

## Troubleshooting
- **Import errors**: Ensure file paths are correct
- **Translation not found**: Check if the exact text exists in constructs
- **Sacred Tongue warnings**: Some constructs have magical warnings (e.g., Runethic)

## Advanced Usage
- Combine with AI Neural Spine for learning and adaptation
- Use Universal Bridge for multi-language communication
- Extend with your own language constructs
"""

def main():
    """Main distribution function"""
    
    print("📦 UNIVERSAL CODEX DISTRIBUTION SYSTEM")
    print("=" * 60)
    print("Creating packages for all AI platforms...")
    print()
    
    distributor = CodexDistributor()
    
    # Step 1: Create master codex
    print("🔧 Step 1: Creating master codex package...")
    master_codex = distributor.create_master_codex_package()
    print(f"   ✅ Master codex created with {len(master_codex.get('universal_constructs', []))} constructs")
    
    # Step 2: Create platform packages
    print("\n📱 Step 2: Creating platform-specific packages...")
    packages = distributor.create_ai_platform_packages(master_codex)
    
    for platform, package_path in packages.items():
        print(f"   ✅ {platform}: {package_path}")
    
    # Step 3: Create distribution ZIP
    print("\n📦 Step 3: Creating distribution ZIP...")
    zip_path = distributor.create_distribution_zip(packages)
    print(f"   ✅ Distribution ZIP: {zip_path}")
    
    # Step 4: Summary
    print("\n🎉 DISTRIBUTION COMPLETE!")
    print("=" * 60)
    print(f"📁 Distribution folder: {distributor.distribution_path}")
    print(f"📦 Complete package: {zip_path}")
    print()
    print("🤖 AI PLATFORMS SUPPORTED:")
    print("   ✅ GitHub Copilot / VS Code")
    print("   ✅ OpenAI API / ChatGPT")
    print("   ✅ Claude API")
    print("   ✅ Perplexity API")
    print("   ✅ Python modules")
    print("   ✅ JavaScript/Node.js")
    print("   ✅ Universal JSON (any platform)")
    print()
    print("🌍 LANGUAGES INCLUDED:")
    print("   📱 Programming: Python, JavaScript, Go, Rust, C#, Java")
    print("   ✨ Sacred Tongues: Kor'aelin, Avali, Runethic, Cassisivadan, Umbroth, Draumric")
    print()
    print("🚀 READY TO DISTRIBUTE TO ALL YOUR AI SYSTEMS!")
    
    return zip_path

if __name__ == '__main__':
    main()