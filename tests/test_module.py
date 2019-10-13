"""Test that the persistent_structures imports as expected."""

import persistent_structures


def test_module() -> None:
    """Test that the module behaves as expected."""
    assert persistent_structures.__version__ is not None
