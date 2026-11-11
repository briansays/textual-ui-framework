"""BaseScreen: shared header, nav menu, footer, key bindings and API helper.

Every page subclasses this and only implements `compose_body()`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

if TYPE_CHECKING:
    from api import ApiResult, DemoApi

# (screen name, menu label, hot key). Order defines the nav menu.
NAV_ITEMS: list[tuple[str, str, str]] = [
    ("menu", "Main Menu", "f1"),
    ("customers", "Customers", "f2"),
    ("orders", "Orders", "f3"),
    ("records", "Records", "f4"),
    ("settings", "Settings", "f5"),
]


class BaseScreen(Screen):
    SCREEN_NAME = ""
    PAGE_TITLE = ""

    BINDINGS = [
        *(Binding(key, f"goto('{name}')", label) for name, label, key in NAV_ITEMS),
        Binding("escape", "goto('menu')", "Back", show=False),
        Binding("ctrl+q", "app.quit", "Quit"),
    ]

    @property
    def api(self) -> DemoApi:
        return self.app.api  # type: ignore[attr-defined]

    # ---- layout -----------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="layout"):
            with Vertical(id="nav"):
                yield Static("NAVIGATE", classes="nav-title")
                for name, label, key in NAV_ITEMS:
                    yield Button(
                        label,
                        id=f"nav-{name}",
                        classes="nav-btn",
                        variant="primary" if name == self.SCREEN_NAME else "default",
                    )
            with VerticalScroll(id="body"):
                yield Static(self.PAGE_TITLE, classes="page-title")
                yield from self.compose_body()
        yield Footer()

    def compose_body(self) -> ComposeResult:
        yield from ()

    # ---- navigation -------------------------------------------------------
    @on(Button.Pressed, ".nav-btn")
    def _nav_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.action_goto(event.button.id.removeprefix("nav-"))

    def action_goto(self, name: str) -> None:
        if name != self.SCREEN_NAME:
            self.app.switch_screen(name)

    # ---- form helpers -----------------------------------------------------
    @staticmethod
    def check_inputs(*required: Input) -> list[str]:
        """Return a message per required Input that is empty or fails its validators."""
        problems = []
        for field in required:
            if not field.value.strip():
                problems.append(f"{field.id}: required")
                continue
            result = field.validate(field.value)
            if result is not None and not result.is_valid:
                problems.append(f"{field.id}: {'; '.join(result.failure_descriptions)}")
        return problems

    # ---- API helper used by every form -------------------------------------
    def submit_to_api(self, entity: str, payload: dict[str, Any]) -> ApiResult:
        result = self.api.submit(entity, payload)
        if result.ok:
            msg = f"Saved to '{entity}' as id {result.data.get('id')}"
            self.notify(msg, title="Submitted")
        else:
            msg = f"Error: {result.error}"
            self.notify(msg, title="API error", severity="error")
        self.show_result(msg)
        return result

    def show_result(self, text: str) -> None:
        for widget in self.query("#result"):
            widget.update(text)  # type: ignore[attr-defined]
