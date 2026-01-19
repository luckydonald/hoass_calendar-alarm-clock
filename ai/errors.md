# A log of errors given to the AI during processing.

It doesn't appear as integration to add?
There i would assume the following flow:
- Add integration
- Choose calendar to load/save events to
- Setup defaults (snooze, timeout)

————————

Give me steps to troubleshoot why the integration is not shown when I search for alarm or anything which should match the name.

————————

Logs: nothing.

File structure: `/homeassistant/custom_components/calendar_alarm_clock/calendar_alarm_clock/` containing `__init__.py`, `alarm_manager.py`, more .py files and the other listed stuff, and the folders `translations/` and `www/`

————————

Error: src/main.ts(252,3): error TS2353: Object literal may only specify known properties, and 'documentationURL' does not exist in type '{ type: string; name: string; description: string; preview?: boolean | undefined; }'.

————————

the hacs test fails with `Error:  <Validation brands> failed:  The repository has not been added as a custom domain to the brands repo (More info: https://hacs.xyz/docs/publish/include#check-brands )`
I do not plan to add a icon to their repo, can I somehow mute that one check specifically?

————————

Log details (ERROR)   Logger: homeassistant.setup Source: setup.py:425 First occurred: 19:24:23 (1 occurrence) Last logged: 19:24:23  Error during setup of component calendar_alarm_clock: 'HomeAssistantHTTP' object has no attribute 'register_static_path' Traceback (most recent call last):   File "/usr/src/homeassistant/homeassistant/setup.py", line 425, in _async_setup_component     result = await task              ^^^^^^^^^^   File "/config/custom_components/calendar_alarm_clock/__init__.py", line 41, in async_setup     hass.http.register_static_path(     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ AttributeError: 'HomeAssistantHTTP' object has no attribute 'register_static_path'. Did you mean: 'async_register_static_paths'?

————————

Hassfest fails with:
Integration calendar_alarm_clock - /github/workspace/custom_components/calendar_alarm_clock: Error: R] [DEPENDENCIES] Using component http but it's not in 'dependencies' or 'after_dependencies' Error: R] [DEPENDENCIES] Using component lovelace but it's not in 'dependencies' or 'after_dependencies' Warning: G] [CONFIG_SCHEMA] Integrations which implement 'async_setup' or 'setup' must define either 'CONFIG_SCHEMA', 'PLATFORM_SCHEMA' or 'PLATFORM_SCHEMA_BASE'. If the integration has no configuration parameters, can only be set up from platforms or can only be set up from config entries, one of the helpers cv.empty_config_schema, cv.platform_only_config_schema or cv.config_entry_only_config_schema can be used.

————————

- zsh: command not found: ruff

Add a full development setup/execution section to the end of the readme.

————————

Logger: aiohttp.server
Source: /usr/local/lib/python3.13/site-packages/aiohttp/web_protocol.py:481
First occurred: 20:37:37 (1 occurrence)
Last logged: 20:37:37

Error handling request from fe80::1864:f828:c67a:7e6
Traceback (most recent call last):
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_protocol.py", line 510, in _handle_request
    resp = await request_handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_app.py", line 569, in _handle
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/site-packages/aiohttp/web_middlewares.py", line 117, in impl
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/security_filter.py", line 92, in security_filter_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/forwarded.py", line 87, in forwarded_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/request_context.py", line 26, in request_context_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/ban.py", line 86, in ban_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/auth.py", line 242, in auth_middleware
    return await handler(request)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/headers.py", line 41, in headers_middleware
    response = await handler(request)
               ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/http.py", line 73, in handle
    result = await handler(request, **request.match_info)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/decorators.py", line 83, in with_admin
    return await func(self, request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/config/config_entries.py", line 272, in post
    return await super().post(request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/components/http/data_validator.py", line 74, in wrapper
    return await method(view, request, data, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/data_entry_flow.py", line 76, in post
    return await self._post_impl(request, data)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/helpers/data_entry_flow.py", line 83, in _post_impl
    result = await self._flow_mgr.async_init(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "/usr/src/homeassistant/homeassistant/data_entry_flow.py", line 316, in async_init
    flow = await self.async_create_flow(handler, context=context, data=data)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/src/homeassistant/homeassistant/config_entries.py", line 3701, in async_create_flow
    return handler.async_get_options_flow(entry)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "/config/custom_components/calendar_alarm_clock/config_flow.py", line 80, in async_get_options_flow
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/config/custom_components/calendar_alarm_clock/config_flow.py", line 171, in __init__
AttributeError: property 'config_entry' of 'OptionsFlowHandler' object has no setter

—————————

Log details (ERROR)
This error originated from a custom integration.
Logger: custom_components.calendar_alarm_clock.alarm_manager
Source: custom_components/calendar_alarm_clock/alarm_manager.py:150
integration: Calendar backed Alarm Clock (documentation, issues)
First occurred: 20:43:32 (4 occurrences)
Last logged: 20:45:02

Error updating alarms from calendar: Action calendar.list_events not found

—————————

Log details (ERROR)
Logger: homeassistant.helpers.entity
Source: helpers/entity.py:961
First occurred: 20:44:23 (6 occurrences)
Last logged: 20:45:23

Update for sensor.calendar_alarm_next_alarm fails
Update for sensor.calendar_alarm_previous_alarm fails
Traceback (most recent call last):
  File "/usr/src/homeassistant/homeassistant/helpers/entity.py", line 961, in async_update_ha_state
    await self.async_device_update()
  File "/usr/src/homeassistant/homeassistant/helpers/entity.py", line 1312, in async_device_update
    await self.async_update()
TypeError: object NoneType can't be used in 'await' expression

—————————

Log details (ERROR)
This error originated from a custom integration.
Logger: custom_components.calendar_alarm_clock.alarm_manager
Source: custom_components/calendar_alarm_clock/alarm_manager.py:150
integration: Calendar backed Alarm Clock (documentation, issues)
First occurred: 20:54:00 (13 occurrences)
Last logged: 21:00:02

Error updating alarms from calendar: Action calendar.list_events not found

—————————

Logger: homeassistant.helpers.entity
Source: helpers/entity.py:961
First occurred: January 15, 2026 at 20:54:41 (846 occurrences)
Last logged: 00:25:42

Update for sensor.calendar_alarm_next_alarm fails
Update for sensor.calendar_alarm_previous_alarm fails
Traceback (most recent call last):
  File "/usr/src/homeassistant/homeassistant/helpers/entity.py", line 961, in async_update_ha_state
    await self.async_device_update()
  File "/usr/src/homeassistant/homeassistant/helpers/entity.py", line 1312, in async_device_update
    await self.async_update()
TypeError: object NoneType can't be used in 'await' expression

—————————

./scripts/commit.sh: line 103: declare: -A: invalid option
declare: usage: declare [-afFirtx] [-p] [name[=value] ...]
make: *** [commit] Error 2

—————————

Log details (ERROR)


Logger: homeassistant.config_entries
Source: config_entries.py:762
First occurred: 21:04:39 (1 occurrence)
Last logged: 21:04:39

Error setting up entry Calendar Alarm Clock (Auto-Discovery) for calendar_alarm_clock
Traceback (most recent call last):
  File "/usr/src/homeassistant/homeassistant/config_entries.py", line 762, in __async_setup_with_context
    result = await component.async_setup_entry(hass, self)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/config/custom_components/calendar_alarm_clock/__init__.py", line 114, in async_setup_entry
    calendar_entity: str = entry.data[CONF_CALENDAR_ENTITY]
                           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'calendar_entity'

———

In version 20 uppon installation it immedly spammed integration recommendations for all calendars it found. I then tried to change it to first have an integration which will show a checkbox, asking you if you want that (it's spammy with 40+ calendars).
However, with that change somehow I broke it, and it no longer auto-discovers anything...


———

The flow is:
1. Install
2. Autodiscovery triggers (with no prior config)
  - Realizes that there is no auto_discovery entity created
  - Creates a auto-discovery request with id auto_discovery
3. auto_discovery is configured by a user (either via the suggestion, or via [+ Integration] -> Calendar Alram Clock
  - Checkbox if calendar auto discovery
4. User saves if or if no auto discovery.
5. Secondary flows/autodiscovery suggestions:
  - Now that the `auto_discovery` one exists, have ` [+ Integration] -> Calendar Alram Clock`  give you the gui with entity_id selector for calendars.
  - If discovery is on, now scan all calendars and generate suggestions for those elements.
