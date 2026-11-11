"""Python <-> C++ bridge.

Loads build/libdemoapi.{dylib,so,dll} with ctypes. If the library has not been
built, falls back to a pure-Python mock that speaks the same JSON protocol, so
the UI is always runnable. Screens only ever talk to `DemoApi`.
"""

from __future__ import annotations

import ctypes
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LIB_NAME = {"darwin": "libdemoapi.dylib", "win32": "demoapi.dll"}.get(sys.platform, "libdemoapi.so")
DEFAULT_LIB = ROOT / "build" / LIB_NAME


@dataclass
class ApiResult:
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class _NativeBackend:
    """Thin ctypes wrapper around the C ABI in cpp/demo_api.h."""

    def __init__(self, path: Path) -> None:
        lib = ctypes.CDLL(str(path))
        lib.demo_api_version.restype = ctypes.c_char_p
        lib.demo_api_init.argtypes = [ctypes.c_char_p]
        lib.demo_api_init.restype = ctypes.c_int
        # Returned strings are library-owned heap memory: take them as raw
        # pointers so we can copy, then hand them back to demo_api_free.
        for name in ("demo_api_submit", "demo_api_list"):
            getattr(lib, name).restype = ctypes.c_void_p
        lib.demo_api_submit.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        lib.demo_api_list.argtypes = [ctypes.c_char_p]
        lib.demo_api_free.argtypes = [ctypes.c_void_p]
        lib.demo_api_free.restype = None
        self._lib = lib
        self.name = f"C++ ({path.name})"

    def _take(self, ptr: int | None) -> str:
        if not ptr:
            return '{"ok":false,"error":"null response from library"}'
        try:
            return ctypes.string_at(ptr).decode("utf-8")
        finally:
            self._lib.demo_api_free(ptr)

    def version(self) -> str:
        return self._lib.demo_api_version().decode()

    def init(self, config_json: str) -> int:
        return self._lib.demo_api_init(config_json.encode())

    def submit(self, entity: str, payload_json: str) -> str:
        return self._take(self._lib.demo_api_submit(entity.encode(), payload_json.encode()))

    def list(self, entity: str) -> str:
        return self._take(self._lib.demo_api_list(entity.encode()))


class _MockBackend:
    """Pure-Python stand-in with identical JSON responses."""

    name = "Python mock (library not built)"

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._next_id = 1

    def version(self) -> str:
        return "demo-api mock 1.0.0"

    def init(self, config_json: str) -> int:
        return 0 if config_json.strip().startswith("{") else 1

    def submit(self, entity: str, payload_json: str) -> str:
        if not entity:
            return json.dumps({"ok": False, "error": "entity name is required"})
        record = {"id": self._next_id, "data": json.loads(payload_json)}
        self._store.setdefault(entity, []).append(record)
        self._next_id += 1
        return json.dumps({"ok": True, "id": record["id"]})

    def list(self, entity: str) -> str:
        return json.dumps({"ok": True, "records": self._store.get(entity, [])})


class DemoApi:
    """The single object screens use to reach the backend."""

    def __init__(self, lib_path: Path | None = None) -> None:
        path = lib_path or DEFAULT_LIB
        try:
            self._backend: _NativeBackend | _MockBackend = _NativeBackend(path)
        except OSError:
            self._backend = _MockBackend()

    @property
    def backend_name(self) -> str:
        return self._backend.name

    @property
    def is_native(self) -> bool:
        return isinstance(self._backend, _NativeBackend)

    def version(self) -> str:
        return self._backend.version()

    def configure(self, config: dict[str, Any]) -> ApiResult:
        rc = self._backend.init(json.dumps(config))
        return ApiResult(ok=True) if rc == 0 else ApiResult(ok=False, error=f"init returned {rc}")

    def submit(self, entity: str, payload: dict[str, Any]) -> ApiResult:
        return self._parse(self._backend.submit(entity, json.dumps(payload)))

    def list(self, entity: str) -> ApiResult:
        return self._parse(self._backend.list(entity))

    @staticmethod
    def _parse(raw: str) -> ApiResult:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return ApiResult(ok=False, error=f"bad JSON from backend: {exc}")
        return ApiResult(ok=bool(data.get("ok")), data=data, error=data.get("error"))
