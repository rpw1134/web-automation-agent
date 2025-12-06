"""
Unit tests for the Executor class.

Tests the parsing and execution of function calls.
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from agent_backend.classes.Executor import Executor
from agent_backend.types.llm import ParsedFunction
from agent_backend.types.tool import ToolResponse


class TestExecutorParseFunctions:
    """Tests for Executor._parse_functions method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor instance for testing."""
        return Executor(env_key="test-key")

    def test_parse_single_function_string_args(self, executor):
        """Test parsing a single function with string arguments."""
        # Arrange
        function_calls = ["go_to_url(url=https://github.com)"]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], ParsedFunction)
        assert result[0].function.__name__ == "go_to_url"
        assert result[0].arguments == {"url": "https://github.com"}

    def test_parse_function_with_multiple_string_args(self, executor):
        """Test parsing a function with multiple string arguments."""
        # Arrange
        page_id = uuid4()
        function_calls = [f"type_text(page_id={page_id},selector=#username,text=testuser)"]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 1
        assert result[0].function.__name__ == "type_text"
        assert len(result[0].arguments) == 3
        assert isinstance(result[0].arguments["page_id"], UUID)
        assert result[0].arguments["page_id"] == page_id
        assert result[0].arguments["selector"] == "#username"
        assert result[0].arguments["text"] == "testuser"

    def test_parse_function_with_uuid_arg(self, executor):
        """Test parsing a function with UUID argument."""
        # Arrange
        page_id = uuid4()
        function_calls = [f"click(page_id={page_id},selector=#button)"]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 1
        assert result[0].function.__name__ == "click"
        assert len(result[0].arguments) == 2
        assert isinstance(result[0].arguments["page_id"], UUID)
        assert result[0].arguments["page_id"] == page_id
        assert result[0].arguments["selector"] == "#button"

    def test_parse_function_with_integer_args(self, executor):
        """Test parsing a function with integer arguments."""
        # Arrange
        page_id = uuid4()
        function_calls = [f"scroll(page_id={page_id},x=0,y=500)"]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 1
        assert result[0].function.__name__ == "scroll"
        assert isinstance(result[0].arguments["page_id"], UUID)
        assert result[0].arguments["page_id"] == page_id
        assert result[0].arguments["x"] == 0
        assert result[0].arguments["y"] == 500
        assert isinstance(result[0].arguments["x"], int)
        assert isinstance(result[0].arguments["y"], int)

    def test_parse_multiple_functions(self, executor):
        """Test parsing multiple function calls."""
        # Arrange
        page_id = uuid4()
        function_calls = [
            "go_to_url(url=https://github.com)",
            f"scroll(page_id={page_id},x=0,y=100)"
        ]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 2
        assert result[0].function.__name__ == "go_to_url"
        assert result[1].function.__name__ == "scroll"

    def test_parse_function_unknown_function_name(self, executor):
        """Test parsing with unknown function name raises ValueError."""
        # Arrange
        function_calls = ["unknown_function(arg1,arg2)"]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            executor._parse_functions(function_calls)
        assert "Function unknown_function not found" in str(exc_info.value)

    def test_parse_function_with_whitespace(self, executor):
        """Test parsing handles whitespace in arguments."""
        # Arrange
        page_id = uuid4()
        function_calls = [f"type_text( page_id = {page_id} , selector = #username , text = testuser )"]

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert len(result) == 1
        # Arguments should be stripped of whitespace
        assert isinstance(result[0].arguments["page_id"], UUID)
        assert result[0].arguments["selector"] == "#username"
        assert result[0].arguments["text"] == "testuser"

    def test_parse_function_empty_list(self, executor):
        """Test parsing empty function list returns empty result."""
        # Arrange
        function_calls = []

        # Act
        result = executor._parse_functions(function_calls)

        # Assert
        assert result == []


class TestExecutorExecuteFunction:
    """Tests for Executor._execute_function method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor instance for testing."""
        return Executor(env_key="test-key")

    @pytest.mark.asyncio
    async def test_execute_function_success(self, executor):
        """Test executing a function that succeeds."""
        # Arrange
        mock_function = AsyncMock(return_value=ToolResponse(
            success=True,
            content="Function executed successfully"
        ))
        parsed_function = ParsedFunction(
            function=mock_function,
            arguments={"arg1": "value1", "arg2": "value2"}
        )

        # Act
        result = await executor._execute_function(parsed_function)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert result.content == "Function executed successfully"
        mock_function.assert_called_once_with(arg1="value1", arg2="value2")

    @pytest.mark.asyncio
    async def test_execute_function_failure(self, executor):
        """Test executing a function that fails."""
        # Arrange
        mock_function = AsyncMock(return_value=ToolResponse(
            success=False,
            content="ERROR: Function failed"
        ))
        parsed_function = ParsedFunction(
            function=mock_function,
            arguments={"arg1": "value1"}
        )

        # Act
        result = await executor._execute_function(parsed_function)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "ERROR" in result.content
        mock_function.assert_called_once_with(arg1="value1")

    @pytest.mark.asyncio
    async def test_execute_function_no_args(self, executor):
        """Test executing a function with no arguments."""
        # Arrange
        mock_function = AsyncMock(return_value=ToolResponse(
            success=True,
            content="No args function"
        ))
        parsed_function = ParsedFunction(
            function=mock_function,
            arguments={}
        )

        # Act
        result = await executor._execute_function(parsed_function)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        mock_function.assert_called_once_with()


class TestExecutorExecuteRequest:
    """Tests for Executor.execute_request method."""

    @pytest.fixture
    def executor(self):
        """Create an Executor instance for testing."""
        return Executor(env_key="test-key")

    @pytest.mark.asyncio
    @patch('agent_backend.classes.Executor.Executor._parse_functions')
    @patch('agent_backend.classes.Executor.Executor._execute_function')
    async def test_execute_request_single_success(
        self, mock_execute_function, mock_parse_functions, executor
    ):
        """Test executing a single successful function call."""
        # Arrange
        mock_function = AsyncMock()
        mock_parse_functions.return_value = [
            ParsedFunction(function=mock_function, arguments={"url": "https://github.com"})
        ]
        mock_execute_function.return_value = ToolResponse(
            success=True,
            content="Success"
        )

        # Act
        result = await executor.execute_request(["go_to_url(url=https://github.com)"])

        # Assert
        assert len(result) == 1
        assert result[0].success is True
        assert result[0].content == "Success"
        mock_parse_functions.assert_called_once()
        mock_execute_function.assert_called_once()

    @pytest.mark.asyncio
    @patch('agent_backend.classes.Executor.Executor._parse_functions')
    @patch('agent_backend.classes.Executor.Executor._execute_function')
    async def test_execute_request_multiple_success(
        self, mock_execute_function, mock_parse_functions, executor
    ):
        """Test executing multiple successful function calls."""
        # Arrange
        mock_function1 = AsyncMock()
        mock_function2 = AsyncMock()
        page_id = uuid4()
        mock_parse_functions.return_value = [
            ParsedFunction(function=mock_function1, arguments={"url": "https://github.com"}),
            ParsedFunction(function=mock_function2, arguments={"page_id": page_id, "x": 0, "y": 100})
        ]
        mock_execute_function.side_effect = [
            ToolResponse(success=True, content="First success"),
            ToolResponse(success=True, content="Second success")
        ]

        # Act
        result = await executor.execute_request([
            "go_to_url(url=https://github.com)",
            f"scroll(page_id={page_id},x=0,y=100)"
        ])

        # Assert
        assert len(result) == 2
        assert result[0].success is True
        assert result[0].content == "First success"
        assert result[1].success is True
        assert result[1].content == "Second success"
        assert mock_execute_function.call_count == 2

    @pytest.mark.asyncio
    @patch('agent_backend.classes.Executor.Executor._parse_functions')
    @patch('agent_backend.classes.Executor.Executor._execute_function')
    async def test_execute_request_stops_on_failure(
        self, mock_execute_function, mock_parse_functions, executor
    ):
        """Test that execution stops when a function fails."""
        # Arrange
        mock_function1 = AsyncMock()
        mock_function2 = AsyncMock()
        mock_function3 = AsyncMock()
        page_id = uuid4()
        mock_parse_functions.return_value = [
            ParsedFunction(function=mock_function1, arguments={"url": "https://github.com"}),
            ParsedFunction(function=mock_function2, arguments={"page_id": page_id, "selector": "#missing-button"}),
            ParsedFunction(function=mock_function3, arguments={"page_id": page_id, "selector": "#username", "text": "test"})
        ]
        mock_execute_function.side_effect = [
            ToolResponse(success=True, content="First success"),
            ToolResponse(success=False, content="ERROR: Second failed"),
            # Third should not be executed
        ]

        # Act
        result = await executor.execute_request([
            "go_to_url(url=https://github.com)",
            f"click(page_id={page_id},selector=#missing-button)",
            f"type_text(page_id={page_id},selector=#username,text=test)"
        ])

        # Assert
        assert len(result) == 2  # Only first two executed
        assert result[0].success is True
        assert result[1].success is False
        assert "ERROR" in result[1].content
        # Should only call execute_function twice (stops after failure)
        assert mock_execute_function.call_count == 2

    @pytest.mark.asyncio
    @patch('agent_backend.classes.Executor.Executor._parse_functions')
    async def test_execute_request_empty_list(
        self, mock_parse_functions, executor
    ):
        """Test executing empty function list."""
        # Arrange
        mock_parse_functions.return_value = []

        # Act
        result = await executor.execute_request([])

        # Assert
        assert result == []
        mock_parse_functions.assert_called_once_with([])

    @pytest.mark.asyncio
    @patch('agent_backend.classes.Executor.Executor._parse_functions')
    async def test_execute_request_parse_error_propagates(
        self, mock_parse_functions, executor
    ):
        """Test that parsing errors propagate correctly."""
        # Arrange
        mock_parse_functions.side_effect = ValueError("Unknown function")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await executor.execute_request(["unknown_func(arg)"])
        assert "Unknown function" in str(exc_info.value)
