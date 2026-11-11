"""Page 5 — Settings: configures the backend through demo_api_init()."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Number
from textual.widgets import Button, Input, Label, Select, Static, Switch

from .base import BaseScreen

LOG_LEVELS = [(lvl.title(), lvl) for lvl in ("debug", "info", "warning", "error")]


class SettingsScreen(BaseScreen):
    SCREEN_NAME = "settings"
    PAGE_TITLE = "Settings"

    def compose_body(self) -> ComposeResult:
        yield Static("Apply calls demo_api_init(config) and also stores a copy as a record.", classes="hint")
        with Horizontal(classes="form-row"):
            yield Label("Endpoint *")
            yield Input("localhost:9000", id="endpoint")
        with Horizontal(classes="form-row"):
            yield Label("Timeout (s) *")
            yield Input("30", id="timeout", type="number", validators=[Number(minimum=1, maximum=600)])
        with Horizontal(classes="form-row"):
            yield Label("Log level")
            yield Select(LOG_LEVELS, id="log_level", value="info", allow_blank=False)
        with Horizontal(classes="form-row"):
            yield Label("Dark mode")
            yield Switch(value=True, id="dark")
        with Horizontal(classes="actions"):
            yield Button("Apply", id="submit", variant="success")
            yield Button("Back to Menu", id="back")
        yield Static("Not applied yet.", id="result")

    @on(Switch.Changed, "#dark")
    def _toggle_theme(self, event: Switch.Changed) -> None:
        self.app.theme = "textual-dark" if event.value else "textual-light"

    @on(Button.Pressed, "#back")
    def _back(self) -> None:
        self.action_goto("menu")

    @on(Button.Pressed, "#submit")
    def _submit(self) -> None:
        endpoint, timeout = self.query_one("#endpoint", Input), self.query_one("#timeout", Input)
        if problems := self.check_inputs(endpoint, timeout):
            self.notify("\n".join(problems), title="Fix the form", severity="warning")
            return
        config = {
            "endpoint": endpoint.value.strip(),
            "timeout": float(timeout.value),
            "log_level": self.query_one("#log_level", Select).value,
            "dark_mode": self.query_one("#dark", Switch).value,
        }
        result = self.api.configure(config)
        if not result.ok:
            self.notify(result.error or "configure failed", title="API error", severity="error")
            self.show_result(f"Error: {result.error}")
            return
        self.submit_to_api("settings", config)
