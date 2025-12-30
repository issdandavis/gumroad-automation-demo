#!/usr/bin/env tsx

/**
 * TypeScript to Python Type Generator
 * 
 * Generates Python Pydantic models from TypeScript interfaces
 * for the Unified AI Platform Bridge API
 */

import * as fs from 'fs';
import * as path from 'path';

interface TypeMapping {
  [key: string]: string;
}

const TYPE_MAPPINGS: TypeMapping = {
  'string': 'str',
  'number': 'float',
  'boolean': 'bool',
  'Date': 'datetime',
  'any': 'Any',
  'Record<string, any>': 'Dict[str, Any]',
  'Record<string, number>': 'Dict[str, float]',
  'Record<string, string>': 'Dict[str, str]',
  'Array<': 'List[',
  '[]': ']',
};

const PYTHON_IMPORTS = `"""
Generated Python types for Unified AI Platform Bridge API
Auto-generated from TypeScript definitions - do not edit manually
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field
`;

class TypeScriptToPythonConverter {
  private output: string[] = [];
  
  constructor() {
    this.output.push(PYTHON_IMPORTS);
  }

  convertTypeScriptToPython(tsContent: string): string {
    const lines = tsContent.split('\n');
    let currentInterface = '';
    let currentEnum = '';
    let braceCount = 0;
    let interfaceContent: string[] = [];
    let enumContent: string[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Skip comments and empty lines
      if (line.startsWith('//') || line.startsWith('/*') || line.startsWith('*') || line === '') {
        continue;
      }

      // Handle enum definitions
      if (line.startsWith('export enum ')) {
        currentEnum = this.extractEnumName(line);
        enumContent = [];
        braceCount = 0;
        continue;
      }

      if (currentEnum && line.includes('{')) {
        braceCount++;
        continue;
      }

      if (currentEnum && line.includes('}')) {
        braceCount--;
        if (braceCount === 0) {
          this.generatePythonEnum(currentEnum, enumContent);
          currentEnum = '';
          enumContent = [];
        }
        continue;
      }

      if (currentEnum) {
        if (line.includes('=')) {
          enumContent.push(line);
        }
        continue;
      }

      // Handle interface definitions
      if (line.startsWith('export interface ')) {
        currentInterface = this.extractInterfaceName(line);
        interfaceContent = [];
        braceCount = 0;
        continue;
      }

      if (currentInterface && line.includes('{')) {
        braceCount++;
        continue;
      }

      if (currentInterface && line.includes('}')) {
        braceCount--;
        if (braceCount === 0) {
          this.generatePythonClass(currentInterface, interfaceContent);
          currentInterface = '';
          interfaceContent = [];
        }
        continue;
      }

      if (currentInterface) {
        if (line.includes(':') && !line.includes('//')) {
          interfaceContent.push(line);
        }
        continue;
      }

      // Handle class definitions
      if (line.startsWith('export class ')) {
        this.generatePythonException(line);
        continue;
      }
    }

    return this.output.join('\n');
  }

  private extractInterfaceName(line: string): string {
    const match = line.match(/export interface (\w+)/);
    return match ? match[1] : '';
  }

  private extractEnumName(line: string): string {
    const match = line.match(/export enum (\w+)/);
    return match ? match[1] : '';
  }

  private generatePythonEnum(enumName: string, content: string[]): void {
    this.output.push(`\nclass ${enumName}(str, Enum):`);
    
    for (const line of content) {
      const match = line.match(/(\w+)\s*=\s*['"]([^'"]+)['"]/);
      if (match) {
        const [, key, value] = match;
        this.output.push(`    ${key} = "${value}"`);
      }
    }
    
    this.output.push('');
  }

  private generatePythonClass(className: string, content: string[]): void {
    this.output.push(`\nclass ${className}(BaseModel):`);
    
    if (content.length === 0) {
      this.output.push('    pass');
      this.output.push('');
      return;
    }

    for (const line of content) {
      const field = this.convertField(line);
      if (field) {
        this.output.push(`    ${field}`);
      }
    }
    
    this.output.push('');
  }

  private convertField(line: string): string | null {
    // Remove semicolon and trim
    line = line.replace(';', '').trim();
    
    if (!line.includes(':')) {
      return null;
    }

    const [fieldPart, typePart] = line.split(':', 2);
    const fieldName = fieldPart.trim();
    let typeStr = typePart.trim();

    // Handle optional fields
    const isOptional = fieldName.includes('?') || typeStr.includes('undefined');
    const cleanFieldName = fieldName.replace('?', '');
    
    // Convert TypeScript types to Python types
    const pythonType = this.convertType(typeStr);
    
    if (isOptional) {
      return `${cleanFieldName}: Optional[${pythonType}] = None`;
    } else {
      return `${cleanFieldName}: ${pythonType}`;
    }
  }

  private convertType(tsType: string): string {
    let pythonType = tsType;

    // Handle union types
    if (pythonType.includes('|')) {
      const unionTypes = pythonType.split('|').map(t => t.trim());
      const convertedTypes = unionTypes.map(t => this.convertSingleType(t));
      return `Union[${convertedTypes.join(', ')}]`;
    }

    // Handle literal types
    if (pythonType.includes("'") && pythonType.includes('|')) {
      const literalTypes = pythonType.split('|').map(t => t.trim());
      return `Literal[${literalTypes.join(', ')}]`;
    }

    return this.convertSingleType(pythonType);
  }

  private convertSingleType(tsType: string): string {
    let pythonType = tsType.trim();

    // Handle array types
    if (pythonType.endsWith('[]')) {
      const elementType = pythonType.slice(0, -2);
      return `List[${this.convertSingleType(elementType)}]`;
    }

    // Handle generic types
    if (pythonType.includes('<') && pythonType.includes('>')) {
      const baseType = pythonType.substring(0, pythonType.indexOf('<'));
      const genericPart = pythonType.substring(pythonType.indexOf('<') + 1, pythonType.lastIndexOf('>'));
      
      if (baseType === 'Record') {
        const [keyType, valueType] = genericPart.split(',').map(t => t.trim());
        return `Dict[${this.convertSingleType(keyType)}, ${this.convertSingleType(valueType)}]`;
      }
      
      if (baseType === 'Array') {
        return `List[${this.convertSingleType(genericPart)}]`;
      }
    }

    // Apply direct mappings
    for (const [tsTypePattern, pythonTypePattern] of Object.entries(TYPE_MAPPINGS)) {
      if (pythonType === tsTypePattern) {
        return pythonTypePattern;
      }
    }

    // Handle literal string types
    if (pythonType.startsWith("'") && pythonType.endsWith("'")) {
      return pythonType;
    }

    // Default: assume it's a custom class name
    return pythonType;
  }

  private generatePythonException(line: string): void {
    const match = line.match(/export class (\w+) extends (\w+)/);
    if (match) {
      const [, className, baseClass] = match;
      const pythonBaseClass = baseClass === 'Error' ? 'Exception' : baseClass;
      
      this.output.push(`\nclass ${className}(${pythonBaseClass}):`);
      this.output.push('    """Generated exception class"""');
      this.output.push('    pass');
      this.output.push('');
    }
  }
}

async function main() {
  try {
    const typesPath = path.join(__dirname, '../src/types/index.ts');
    const outputPath = path.join(__dirname, '../../app-productizer/shared_types.py');
    
    console.log('🔄 Reading TypeScript types from:', typesPath);
    const tsContent = fs.readFileSync(typesPath, 'utf-8');
    
    console.log('🔄 Converting TypeScript to Python...');
    const converter = new TypeScriptToPythonConverter();
    const pythonContent = converter.convertTypeScriptToPython(tsContent);
    
    console.log('🔄 Writing Python types to:', outputPath);
    fs.writeFileSync(outputPath, pythonContent);
    
    console.log('✅ Python types generated successfully!');
    console.log(`📄 Generated ${pythonContent.split('\n').length} lines of Python code`);
    
    // Also create a validation utility
    const validationUtilPath = path.join(__dirname, '../../app-productizer/type_validation.py');
    const validationContent = generateValidationUtility();
    fs.writeFileSync(validationUtilPath, validationContent);
    
    console.log('✅ Type validation utility created!');
    
  } catch (error) {
    console.error('❌ Error generating Python types:', error);
    process.exit(1);
  }
}

function generateValidationUtility(): string {
  return `"""
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
`;
}

if (require.main === module) {
  main();
}