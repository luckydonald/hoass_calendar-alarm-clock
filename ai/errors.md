

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
