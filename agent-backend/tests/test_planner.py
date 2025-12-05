"""
Unit tests for the Planner class.

Tests the _parse_plan method which parses LLM responses into structured plan objects.
"""

import pytest
import json
from agent_backend.classes.Planner import Planner
from agent_backend.types.llm import PlanResponse, PlanResponseError


class TestPlannerParsePlan:
    """Tests for Planner._parse_plan method."""

    @pytest.fixture
    def planner(self):
        """Create a Planner instance for testing."""
        return Planner(api_key="test-key")

    def test_parse_plan_valid_json(self, planner):
        """Test parsing a valid plan JSON response."""
        # Arrange
        plan_json = json.dumps({
            "plan": "Navigate to GitHub homepage",
            "function_calls": ["go_to_url(https://github.com)"]
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "Navigate to GitHub homepage"
        assert result.function_calls == ["go_to_url(https://github.com)"]
        assert result.done is False

    def test_parse_plan_with_multiple_function_calls(self, planner):
        """Test parsing a plan with multiple function calls."""
        # Arrange
        plan_json = json.dumps({
            "plan": "Click button and type text",
            "function_calls": [
                "click(#submit)",
                "type_text(#username,testuser)"
            ]
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "Click button and type text"
        assert len(result.function_calls) == 2
        assert result.function_calls[0] == "click(#submit)"
        assert result.function_calls[1] == "type_text(#username,testuser)"
        assert result.done is False

    def test_parse_plan_done_status(self, planner):
        """Test parsing a plan with 'done' status."""
        # Arrange
        plan_json = json.dumps({
            "plan": "done",
            "function_calls": []
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "done"
        assert result.function_calls == []
        assert result.done is True

    def test_parse_plan_done_case_insensitive(self, planner):
        """Test that 'done' detection is case-insensitive."""
        # Arrange
        plan_json = json.dumps({
            "plan": "DONE",
            "function_calls": []
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.done is True

    def test_parse_plan_empty_function_calls(self, planner):
        """Test parsing a plan with no function calls."""
        # Arrange
        plan_json = json.dumps({
            "plan": "Just thinking, no actions needed",
            "function_calls": []
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "Just thinking, no actions needed"
        assert result.function_calls == []
        assert result.done is False

    def test_parse_plan_missing_fields(self, planner):
        """Test parsing a plan with missing optional fields."""
        # Arrange
        plan_json = json.dumps({
            "plan": "Simple plan"
            # No function_calls field
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "Simple plan"
        assert result.function_calls == []  # Should default to empty list

    def test_parse_plan_invalid_json(self, planner):
        """Test parsing invalid JSON returns PlanResponseError."""
        # Arrange
        invalid_json = "This is not valid JSON {{"

        # Act
        result = planner._parse_plan(invalid_json)

        # Assert
        assert isinstance(result, PlanResponseError)
        assert "Failed to parse plan JSON" in result.error

    def test_parse_plan_none_input(self, planner):
        """Test parsing None input returns PlanResponseError."""
        # Act
        result = planner._parse_plan(None)

        # Assert
        assert isinstance(result, PlanResponseError)
        assert "Failed to parse plan JSON" in result.error

    def test_parse_plan_empty_string(self, planner):
        """Test parsing empty string returns PlanResponseError."""
        # Act
        result = planner._parse_plan("")

        # Assert
        assert isinstance(result, PlanResponseError)
        assert "Failed to parse plan JSON" in result.error

    def test_parse_plan_malformed_json(self, planner):
        """Test parsing malformed JSON returns PlanResponseError."""
        # Arrange
        malformed_json = '{"plan": "test", "function_calls": [unclosed array'

        # Act
        result = planner._parse_plan(malformed_json)

        # Assert
        assert isinstance(result, PlanResponseError)
        assert "Failed to parse plan JSON" in result.error

    def test_parse_plan_json_with_extra_fields(self, planner):
        """Test parsing JSON with extra fields (should ignore them)."""
        # Arrange
        plan_json = json.dumps({
            "plan": "Test plan",
            "function_calls": ["go_to_url(https://example.com)"],
            "extra_field": "should be ignored",
            "another_field": 123
        })

        # Act
        result = planner._parse_plan(plan_json)

        # Assert
        assert isinstance(result, PlanResponse)
        assert result.plan == "Test plan"
        assert result.function_calls == ["go_to_url(https://example.com)"]
        assert result.done is False
