"""
Type validation utilities for Unified AI Platform
Auto-generated validation helpers for cross-system type safety
"""

from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel, ValidationError
import json
from datetime import datetime

T = TypeVar('T', bound=BaseModel)

class TypeValidator:
    """Utility class for validating data against Pydantic models"""
    
    @staticmethod
    def validate_json(data: str, model_class: Type[T]) -> T:
        """Validate JSON string against a Pydantic model"""
        try:
            parsed_data = json.loads(data)
            return model_class(**parsed_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation error: {e}")
    
    @staticmethod
    def validate_dict(data: Dict[str, Any], model_class: Type[T]) -> T:
        """Validate dictionary against a Pydantic model"""
        try:
            return model_class(**data)
        except ValidationError as e:
            raise ValueError(f"Validation error: {e}")
    
    @staticmethod
    def to_dict(model: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic model to dictionary with JSON-serializable values"""
        return model.model_dump(mode='json')
    
    @staticmethod
    def to_json(model: BaseModel) -> str:
        """Convert Pydantic model to JSON string"""
        return model.model_dump_json()
    
    @staticmethod
    def convert_typescript_dates(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TypeScript Date strings to Python datetime objects"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, str) and key.lower().endswith(('time', 'date', 'at')):
                try:
                    # Try to parse ISO format dates
                    converted[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    converted[key] = value
            elif isinstance(value, dict):
                converted[key] = TypeValidator.convert_typescript_dates(value)
            else:
                converted[key] = value
        return converted

# Convenience functions for common operations
def validate_cross_system_event(data: Dict[str, Any]) -> 'CrossSystemEvent':
    """Validate data as CrossSystemEvent"""
    from shared_types import CrossSystemEvent
    converted_data = TypeValidator.convert_typescript_dates(data)
    return TypeValidator.validate_dict(converted_data, CrossSystemEvent)

def validate_unified_system_status(data: Dict[str, Any]) -> 'UnifiedSystemStatus':
    """Validate data as UnifiedSystemStatus"""
    from shared_types import UnifiedSystemStatus
    converted_data = TypeValidator.convert_typescript_dates(data)
    return TypeValidator.validate_dict(converted_data, UnifiedSystemStatus)

def validate_api_response(data: Dict[str, Any]) -> 'ApiResponse':
    """Validate data as ApiResponse"""
    from shared_types import ApiResponse
    converted_data = TypeValidator.convert_typescript_dates(data)
    return TypeValidator.validate_dict(converted_data, ApiResponse)
