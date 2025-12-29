# Contributing to Morewritings

Thank you for your interest in contributing to Morewritings!

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`pytest`)
5. **Format code** (`black morewritings/ tests/`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/morewritings.git
cd morewritings

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black morewritings/ tests/

# Check linting
flake8 morewritings/ tests/
```

## Guidelines

- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style (use `black` for formatting)
- Keep pull requests focused on a single feature/fix

## Reporting Bugs

Please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)

## Feature Requests

We welcome feature requests! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- Any implementation ideas you have

## Code of Conduct

Be respectful and constructive in all interactions.

## Questions?

Feel free to open an issue for any questions about contributing!
