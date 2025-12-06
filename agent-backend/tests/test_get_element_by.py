"""
Unit tests for the get_element_by function.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from agent_backend.tools.playwright_functions import get_element_by, get_element_by_tool
from agent_backend.types.tool import ToolResponse


class TestGetElementBy:
    """Tests for get_element_by function."""

    @pytest.mark.asyncio
    async def test_invalid_query_by_value(self):
        """Test that invalid query_by values return an error."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#button"
        invalid_query_by = "invalid"

        # Act
        result = await get_element_by(context_id, page_id, query, invalid_query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "Invalid query_by value" in result.content
        assert "invalid" in result.content

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_css_query_success(self, mock_get_page):
        """Test querying by CSS selector successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#login-button"
        query_by = "css"

        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_page.locator.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 1 element(s)" in result.content
        assert "css='#login-button'" in result.content
        mock_page.locator.assert_called_once_with(query)

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_label_query_success(self, mock_get_page):
        """Test querying by label successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "Username"
        query_by = "label"

        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_page.get_by_label.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 1 element(s)" in result.content
        mock_page.get_by_label.assert_called_once_with(query)

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_text_query_success(self, mock_get_page):
        """Test querying by text successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "Login"
        query_by = "text"

        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=2)
        mock_page.get_by_text.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 2 element(s)" in result.content
        mock_page.get_by_text.assert_called_once_with(query)

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_element_not_found(self, mock_get_page):
        """Test when no elements match the query."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#nonexistent"
        query_by = "css"

        mock_page = MagicMock()
        mock_locator = MagicMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "No element found" in result.content

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_timeout_error(self, mock_get_page):
        """Test handling of timeout errors."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#button"
        query_by = "css"

        mock_get_page.side_effect = TimeoutError("Page timeout")

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "Request timed out" in result.content

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_unexpected_error(self, mock_get_page):
        """Test handling of unexpected errors."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#button"
        query_by = "css"

        mock_get_page.side_effect = Exception("Unexpected error")

        # Act
        result = await get_element_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "Unexpected error" in result.content


class TestGetElementByTool:
    """Tests for get_element_by_tool definition."""

    def test_tool_definition(self):
        """Test that the tool is properly defined."""
        assert get_element_by_tool.name == "get_element_by"
        assert get_element_by_tool.type == "function"
        assert "page_id" in get_element_by_tool.parameters.properties
        assert "query" in get_element_by_tool.parameters.properties
        assert "query_by" in get_element_by_tool.parameters.properties
        assert get_element_by_tool.parameters.required == ["page_id", "query", "query_by"]

    def test_tool_registered_in_dictionaries(self):
        """Test that the tool is registered in the function mappings."""
        from agent_backend.tools.playwright_functions import (
            playwright_function_names_to_functions,
            playwright_function_names_to_tools
        )

        assert "get_element_by" in playwright_function_names_to_functions
        assert "get_element_by" in playwright_function_names_to_tools
        assert playwright_function_names_to_functions["get_element_by"] == get_element_by
        assert playwright_function_names_to_tools["get_element_by"] == get_element_by_tool
