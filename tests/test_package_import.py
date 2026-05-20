"""Basic package import test for the TwinAgent AI repository skeleton."""

import twinagent


def test_package_metadata() -> None:
    """Verify that the package imports and exposes basic project metadata."""
    assert twinagent.__version__ == "0.1.0"
    assert twinagent.PROJECT_NAME == "TwinAgent AI"
    assert twinagent.PROJECT_SUBTITLE == "Agentic Copilot for Industrial Digital Twins"
