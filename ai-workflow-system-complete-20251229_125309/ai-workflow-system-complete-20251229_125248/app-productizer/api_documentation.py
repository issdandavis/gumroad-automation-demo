#!/usr/bin/env python3
"""
API Documentation Generator
===========================

Comprehensive API documentation system for the Self-Evolving AI Framework.
Generates interactive documentation, OpenAPI specs, and client SDKs.

TUTORIAL: API Documentation Best Practices
------------------------------------------
This module teaches you how to:
1. Document REST APIs with OpenAPI/Swagger
2. Generate interactive API explorers
3. Create client SDK documentation
4. Build API reference guides
5. Implement versioned documentation

Features:
- OpenAPI 3.0 specification generation
- Interactive API explorer (Swagger UI)
- Markdown documentation export
- Client SDK generation guides
- API versioning support
- Request/response examples
- Authentication documentation

Usage:
    python api_documentation.py generate          # Generate all docs
    python api_documentation.py openapi           # Generate OpenAPI spec
    python api_documentation.py markdown          # Generate Markdown docs
    python api_documentation.py serve             # Serve interactive docs
    python api_documentation.py validate          # Validate API spec

Demo API Keys (for testing):
    API_KEY=demo-api-key-1234567890abcdef
    API_SECRET=demo-secret-1234567890abcdef
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from functools import wraps
import inspect
