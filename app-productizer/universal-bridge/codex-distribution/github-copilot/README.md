# Universal Language Codex - GitHub Copilot Integration

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
