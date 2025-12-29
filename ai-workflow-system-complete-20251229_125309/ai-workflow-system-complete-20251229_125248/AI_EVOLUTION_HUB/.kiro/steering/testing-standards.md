---
inclusion: fileMatch
fileMatchPattern: "**/*.{test,spec}.py"
---

# Testing Standards: AI Evolution Hub

## Organization

- Co-locate: `mutation.py` → `test_mutation.py`
- Property tests: `test_properties.py` for system-wide properties
- Integration tests: `tests/integration/` directory

## Structure

```python
class TestMutationEngine:
    """Test suite for MutationEngine class."""
    
    def test_apply_mutation_success(self):
        """Should apply valid mutation and update fitness score."""
        # Arrange
        engine = MutationEngine()
        mutation = Mutation(type="communication_enhancement", ...)
        
        # Act
        result = engine.apply_mutation(mutation)
        
        # Assert
        assert result.success is True
        assert result.fitness_delta > 0
```

## Principles

- **Unit**: Isolated functions/classes with mocked dependencies
- **Property**: Universal properties tested with hypothesis
- **Integration**: Component interactions with LocalStack
- **E2E**: Complete evolution workflows
- **Coverage**: Minimum 85% for core evolution components

## Property-Based Testing

- Use hypothesis for generating test data
- Test invariants: fitness scores, generation counters, rollback completeness
- Test round-trip properties: serialize/deserialize, mutation/rollback
- Minimum 100 iterations per property test

## AWS Testing

- LocalStack for DynamoDB and S3 integration tests
- Moto for Lambda and API Gateway mocking
- Real AWS services only for final E2E validation
- Document MCP server usage in integration tests