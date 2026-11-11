# Textual Demo Framework

A stock-looking [Textual](https://textual.textualize.io) TUI with five linked
screens, data-entry forms and a generic C++ backend reached through a C ABI.

```
app.py                 App entry; registers screens, owns the API object
app.tcss               Shared layout styles (stock theme colours)
screens/
  base.py              BaseScreen: header, side nav menu, footer, F-keys, API/validation helpers
  main_menu.py   (1)   Landing page with a selectable menu
  customers.py   (2)   Customer form: Input + validators, Select, Checkbox
  orders.py      (3)   Order form: Select fed from backend, RadioSet, TextArea
  records.py     (4)   DataTable browser of everything stored in the backend
  settings.py    (5)   Config form → demo_api_init(); Switch toggles theme
api/bridge.py          ctypes wrapper (falls back to a Python mock if lib not built)
cpp/demo_api.h/.cpp    Generic JSON-in/JSON-out C API, in-memory C++ implementation
tests/test_app.py      Headless end-to-end test of every screen
```

## Run

```bash
pip install -r requirements.txt
make          # builds build/libdemoapi.dylib (.so on Linux)
python3 app.py    # or: make run
python3 tests/test_app.py
```

The header subtitle shows which backend is active: `C++ (libdemoapi.dylib)`
or `Python mock` if you skipped `make`.

## Navigation

- Side menu buttons on every page
- F1 Menu · F2 Customers · F3 Orders · F4 Records · F5 Settings
- Esc returns to the main menu; Ctrl+Q quits; Ctrl+P opens the command palette

## The C++ API

`cpp/demo_api.h` is the whole contract:

| Function | Purpose |
|---|---|
| `demo_api_version()` | static version string |
| `demo_api_init(config_json)` | configure; returns 0 on success |
| `demo_api_submit(entity, payload_json)` | → `{"ok":true,"id":N}` / `{"ok":false,"error":...}` |
| `demo_api_list(entity)` | → `{"ok":true,"records":[{"id":N,"data":{...}}]}` |
| `demo_api_free(ptr)` | free any returned `char*` |
| `demo_api_shutdown()` | clear state |

Everything crosses the boundary as JSON text, so you can replace the bodies in
`demo_api.cpp` with calls into a real system without touching Python.

## Adding a screen

1. Create `screens/foo.py` with a `BaseScreen` subclass that sets
   `SCREEN_NAME = "foo"` and implements `compose_body()`.
2. Register it in `screens/__init__.py` `SCREENS`.
3. Add `("foo", "Foo", "f6")` to `NAV_ITEMS` in `screens/base.py`. It then
   appears in the side menu, main menu, footer and key bindings.

Use `self.submit_to_api("entity", payload_dict)` from a submit handler; it
calls the backend, shows a toast and updates any `#result` widget.
