"""
Simple debug test to verify pytest-asyncio is working.
"""

import pytest

@pytest.mark.asyncio
async def test_async_works():
    """Test that async tests run at all."""
    print("\n✅ Async test is running!")
    assert True


@pytest.fixture
async def simple_fixture():
    """Test that async fixtures work."""
    print("\n✅ Async fixture is running!")
    yield "fixture_value"
    print("\n✅ Async fixture cleanup running!")


@pytest.mark.asyncio
async def test_with_fixture(simple_fixture):
    """Test that async fixtures are called."""
    print(f"\n✅ Test got fixture value: {simple_fixture}")
    assert simple_fixture == "fixture_value"
