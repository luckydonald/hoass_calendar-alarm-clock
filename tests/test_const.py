"""Tests for Calendar backed Alarm Clock constants."""
from custom_components.calendar_alarm_clock.const import DOMAIN, LOG_NAME


def test_domain_constant():
    """Test that DOMAIN is set correctly."""
    assert DOMAIN == "calendar_alarm_clock"
    assert isinstance(DOMAIN, str)


def test_log_name_constant():
    """Test that LOG_NAME is set correctly."""
    assert LOG_NAME == "custom-components.calendar_alarm_clock"
    assert isinstance(LOG_NAME, str)
    assert DOMAIN in LOG_NAME


def test_constants_are_final():
    """Test that constants appear to be final (by convention)."""
    # This is more of a documentation test
    # Python doesn't enforce Final at runtime
    assert DOMAIN is not None
    assert LOG_NAME is not None

