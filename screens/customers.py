"""Page 2 — Customer entry form."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Length, Regex
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from .base import BaseScreen

TIERS = [("Bronze", "bronze"), ("Silver", "silver"), ("Gold", "gold")]
EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class CustomersScreen(BaseScreen):
    SCREEN_NAME = "customers"
    PAGE_TITLE = "New Customer"

    def compose_body(self) -> ComposeResult:
        yield Static("Fields marked * are required. Submit sends JSON to demo_api_submit().", classes="hint")
        with Horizontal(classes="form-row"):
            yield Label("Name *")
            yield Input(placeholder="Ada Lovelace", id="name", validators=[Length(minimum=2)])
        with Horizontal(classes="form-row"):
            yield Label("Email *")
            yield Input(placeholder="ada@example.com", id="email",
                        validators=[Regex(EMAIL_RE, failure_description="Not a valid email")])
        with Horizontal(classes="form-row"):
            yield Label("Phone")
            yield Input(placeholder="+1 555 0100", id="phone", type="text")
        with Horizontal(classes="form-row"):
            yield Label("Tier")
            yield Select(TIERS, id="tier", value="bronze", allow_blank=False)
        with Horizontal(classes="form-row"):
            yield Label("")
            yield Checkbox("Subscribe to newsletter", id="newsletter")
        with Horizontal(classes="actions"):
            yield Button("Submit", id="submit", variant="success")
            yield Button("Clear", id="clear")
        yield Static("No submission yet.", id="result")

    @on(Button.Pressed, "#submit")
    @on(Input.Submitted)
    def _submit(self) -> None:
        name, email = self.query_one("#name", Input), self.query_one("#email", Input)
        problems = self.check_inputs(name, email)
        if problems:
            self.notify("\n".join(problems), title="Fix the form", severity="warning")
            return
        self.submit_to_api("customers", {
            "name": name.value.strip(),
            "email": email.value.strip(),
            "phone": self.query_one("#phone", Input).value.strip(),
            "tier": self.query_one("#tier", Select).value,
            "newsletter": self.query_one("#newsletter", Checkbox).value,
        })
        self._clear()

    @on(Button.Pressed, "#clear")
    def _clear(self) -> None:
        for field in self.query(Input):
            field.clear()
        self.query_one("#tier", Select).value = "bronze"
        self.query_one("#newsletter", Checkbox).value = False
        self.query_one("#name", Input).focus()
