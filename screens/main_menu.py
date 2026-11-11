"""Page 1 — Main menu: landing page linking to every other screen."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView, Static

from .base import NAV_ITEMS, BaseScreen

DESCRIPTIONS = {
    "customers": "Add a customer record (text inputs, select, checkbox).",
    "orders": "Place an order against an existing customer.",
    "records": "Browse everything stored in the C++ backend.",
    "settings": "Push configuration to the backend via demo_api_init().",
}


class MainMenuScreen(BaseScreen):
    SCREEN_NAME = "menu"
    PAGE_TITLE = "Main Menu"

    def compose_body(self) -> ComposeResult:
        yield Static("Choose a page with ↑/↓ and Enter, the side menu, or F1–F5.", classes="hint")
        yield ListView(
            *(
                ListItem(Label(f"{label:<12} {DESCRIPTIONS.get(name, '')}"), id=f"menu-{name}")
                for name, label, _ in NAV_ITEMS
                if name != self.SCREEN_NAME
            ),
            id="menu-list",
        )
        yield Static(id="backend-info", classes="hint")

    def on_mount(self) -> None:
        self.query_one("#menu-list").focus()

    def on_screen_resume(self) -> None:
        self.query_one("#backend-info", Static).update(
            f"\nBackend: {self.api.backend_name}  ·  {self.api.version()}"
        )

    @on(ListView.Selected, "#menu-list")
    def _open(self, event: ListView.Selected) -> None:
        self.action_goto(event.item.id.removeprefix("menu-"))
