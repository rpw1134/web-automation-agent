"""
Unit tests for the get_visible_elements_by function.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from agent_backend.tools.playwright_functions import get_visible_elements_by, get_visible_elements_by_tool
from agent_backend.types.tool import ToolResponse


class TestGetVisibleElementsBy:
    """Tests for get_visible_elements_by function."""

    @pytest.mark.asyncio
    async def test_invalid_query_by_value(self):
        """Test that invalid query_by values return an error."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#button"
        invalid_query_by = "invalid"

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, invalid_query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "Invalid query_by value" in result.content
        assert "invalid" in result.content

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.create_new_locators_for_page')
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_css_query_success(self, mock_get_page, mock_create_locators):
        """Test querying by CSS selector successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#login-button"
        query_by = "css"

        mock_element = MagicMock()
        mock_element.is_visible = AsyncMock(return_value=True)

        mock_locator = MagicMock()
        mock_locator.all = AsyncMock(return_value=[mock_element])

        mock_page = MagicMock()
        mock_page.locator.return_value = mock_locator
        mock_get_page.return_value = mock_page

        test_locator_ids = [uuid4()]
        mock_create_locators.return_value = test_locator_ids

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 1 element(s)" in result.content
        assert f"Locator IDs: {test_locator_ids}" in result.content
        mock_page.locator.assert_called_once_with(query)
        mock_create_locators.assert_called_once_with(page_id, [mock_element])

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.create_new_locators_for_page')
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_label_query_success(self, mock_get_page, mock_create_locators):
        """Test querying by label successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "Username"
        query_by = "label"

        mock_element = MagicMock()
        mock_element.is_visible = AsyncMock(return_value=True)

        mock_locator = MagicMock()
        mock_locator.all = AsyncMock(return_value=[mock_element])

        mock_page = MagicMock()
        mock_page.get_by_label.return_value = mock_locator
        mock_get_page.return_value = mock_page

        test_locator_ids = [uuid4()]
        mock_create_locators.return_value = test_locator_ids

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 1 element(s)" in result.content
        assert f"Locator IDs: {test_locator_ids}" in result.content
        mock_page.get_by_label.assert_called_once_with(query)
        mock_create_locators.assert_called_once_with(page_id, [mock_element])

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.create_new_locators_for_page')
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_text_query_success(self, mock_get_page, mock_create_locators):
        """Test querying by text successfully."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "Login"
        query_by = "text"

        mock_element1 = MagicMock()
        mock_element1.is_visible = AsyncMock(return_value=True)
        mock_element2 = MagicMock()
        mock_element2.is_visible = AsyncMock(return_value=True)

        mock_locator = MagicMock()
        mock_locator.all = AsyncMock(return_value=[mock_element1, mock_element2])

        mock_page = MagicMock()
        mock_page.get_by_text.return_value = mock_locator
        mock_get_page.return_value = mock_page

        test_locator_ids = [uuid4(), uuid4()]
        mock_create_locators.return_value = test_locator_ids

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is True
        assert "Found 2 element(s)" in result.content
        assert f"Locator IDs: {test_locator_ids}" in result.content
        mock_page.get_by_text.assert_called_once_with(query)
        mock_create_locators.assert_called_once_with(page_id, [mock_element1, mock_element2])

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_element_not_found(self, mock_get_page):
        """Test when no elements match the query."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#nonexistent"
        query_by = "css"

        mock_locator = MagicMock()
        mock_locator.all = AsyncMock(return_value=[])

        mock_page = MagicMock()
        mock_page.locator.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "No element found" in result.content

    @pytest.mark.asyncio
    @patch('agent_backend.tools.playwright_functions.get_page_by_id')
    async def test_element_exists_but_not_visible(self, mock_get_page):
        """Test when elements match but none are visible."""
        # Arrange
        context_id = uuid4()
        page_id = uuid4()
        query = "#hidden-button"
        query_by = "css"

        mock_element = MagicMock()
        mock_element.is_visible = AsyncMock(return_value=False)

        mock_locator = MagicMock()
        mock_locator.all = AsyncMock(return_value=[mock_element])

        mock_page = MagicMock()
        mock_page.locator.return_value = mock_locator
        mock_get_page.return_value = mock_page

        # Act
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

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
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

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
        result = await get_visible_elements_by(context_id, page_id, query, query_by)

        # Assert
        assert isinstance(result, ToolResponse)
        assert result.success is False
        assert "Unexpected error" in result.content


class TestGetVisibleElementsByTool:
    """Tests for get_visible_elements_by_tool definition."""

    def test_tool_definition(self):
        """Test that the tool is properly defined."""
        assert get_visible_elements_by_tool.name == "get_visible_elements_by"
        assert get_visible_elements_by_tool.type == "function"
        assert "page_id" in get_visible_elements_by_tool.parameters.properties
        assert "query" in get_visible_elements_by_tool.parameters.properties
        assert "query_by" in get_visible_elements_by_tool.parameters.properties
        assert get_visible_elements_by_tool.parameters.required == ["page_id", "query", "query_by"]

    def test_tool_registered_in_dictionaries(self):
        """Test that the tool is registered in the function mappings."""
        from agent_backend.tools.playwright_functions import (
            playwright_function_names_to_functions,
            playwright_function_names_to_tools
        )

        assert "get_visible_elements_by" in playwright_function_names_to_functions
        assert "get_visible_elements_by" in playwright_function_names_to_tools
        assert playwright_function_names_to_functions["get_visible_elements_by"] == get_visible_elements_by
        assert playwright_function_names_to_tools["get_visible_elements_by"] == get_visible_elements_by_tool
