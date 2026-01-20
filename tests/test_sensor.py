"""Tests for Calendar backed Alarm Clock sensor platform."""
import pytest
from unittest.mock import Mock, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.calendar_alarm_clock.sensor import (
    async_setup_entry,
    AlarmSensor,
)
from custom_components.calendar_alarm_clock.const import DOMAIN


@pytest.fixture
def hass():
    """Create a mock Home Assistant instance."""
    return Mock(spec=HomeAssistant)


@pytest.fixture
def config_entry():
    """Create a mock config entry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {}
    return entry


@pytest.mark.asyncio
async def test_async_setup_entry(hass, config_entry):
    """Test sensor platform setup."""
    async_add_entities = AsyncMock()

    await async_setup_entry(hass, config_entry, async_add_entities)

    async_add_entities.assert_called_once()
    sensors = async_add_entities.call_args[0][0]
    assert len(sensors) == 1
    assert isinstance(sensors[0], AlarmSensor)


def test_sensor_initialization(config_entry):
    """Test sensor initialization."""
    sensor = AlarmSensor(config_entry, "example")

    assert sensor._entry == config_entry
    assert sensor._sensor_type == "example"
    assert sensor._attr_name == "Calendar backed Alarm Clock Example"
    assert sensor._attr_unique_id == f"{config_entry.entry_id}_example"
    assert sensor._attr_native_value is None


def test_sensor_device_info(config_entry):
    """Test sensor device info."""
    sensor = AlarmSensor(config_entry, "example")

    device_info = sensor.device_info

    assert device_info["identifiers"] == {(DOMAIN, config_entry.entry_id)}
    assert device_info["name"] == "Calendar backed Alarm Clock"
    assert device_info["manufacturer"] == "Custom"
    assert device_info["model"] == "Calendar backed Alarm Clock"


@pytest.mark.asyncio
async def test_sensor_update(config_entry):
    """Test sensor update method."""
    sensor = AlarmSensor(config_entry, "example")

    # Should not raise any errors
    await sensor.async_update()

    # Native value should still be None (no actual implementation yet)
    assert sensor._attr_native_value is None


def test_sensor_multiple_types(config_entry):
    """Test creating sensors with different types."""
    sensor1 = AlarmSensor(config_entry, "type1")
    sensor2 = AlarmSensor(config_entry, "type2")

    assert sensor1._attr_name == "Calendar backed Alarm Clock Type1"
    assert sensor2._attr_name == "Calendar backed Alarm Clock Type2"
    assert sensor1._attr_unique_id != sensor2._attr_unique_id

