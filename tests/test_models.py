"""Tests for Calendar backed Alarm Clock data models."""
from custom_components.calendar_alarm_clock.models import Alarm


def test_plugin_data_creation():
    """Test creating a PluginData instance."""
    data = Alarm()

    # Since it's an empty dataclass, just verify it exists
    assert data is not None
    assert isinstance(data, Alarm)


def test_plugin_data_is_dataclass():
    """Test that PluginData is a dataclass."""
    import dataclasses

    assert dataclasses.is_dataclass(Alarm)

