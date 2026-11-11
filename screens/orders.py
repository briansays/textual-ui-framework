"""Page 3 — Order entry form. The customer list is fetched from the backend."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Number
from textual.widgets import Button, Input, Label, RadioButton, RadioSet, Select, Static, TextArea

from .base import BaseScreen

PRODUCTS = [("Widget — $4.00", "widget"), ("Gadget — $12.50", "gadget"), ("Gizmo — $30.00", "gizmo")]


class OrdersScreen(BaseScreen):
    SCREEN_NAME = "orders"
    PAGE_TITLE = "New Order"

    def compose_body(self) -> ComposeResult:
        yield Static("Customers are loaded live from demo_api_list('customers').", classes="hint")
        with Horizontal(classes="form-row"):
            yield Label("Customer *")
            yield Select([], id="customer", prompt="Select a customer")
        with Horizontal(classes="form-row"):
            yield Label("Product *")
            yield Select(PRODUCTS, id="product", prompt="Select a product")
        with Horizontal(classes="form-row"):
            yield Label("Quantity *")
            yield Input("1", id="quantity", type="integer",
                        validators=[Number(minimum=1, maximum=999)])
        with Horizontal(classes="form-row"):
            yield Label("Priority")
            with RadioSet(id="priority"):
                yield RadioButton("Standard", value=True, id="standard")
                yield RadioButton("Express", id="express")
                yield RadioButton("Overnight", id="overnight")
        with Horizontal(classes="form-row"):
            yield Label("Notes")
            yield TextArea(id="notes")
        with Horizontal(classes="actions"):
            yield Button("Place Order", id="submit", variant="success")
            yield Button("Clear", id="clear")
        yield Static("No submission yet.", id="result")

    def on_screen_resume(self) -> None:
        """Refresh the customer dropdown each time this page is shown."""
        result = self.api.list("customers")
        records = result.data.get("records", []) if result.ok else []
        select = self.query_one("#customer", Select)
        select.set_options((f"#{r['id']} {r['data'].get('name', '?')}", r["id"]) for r in records)
        if not records:
            self.show_result("No customers yet — add one on the Customers page (F2).")

    @on(Button.Pressed, "#submit")
    def _submit(self) -> None:
        customer = self.query_one("#customer", Select)
        product = self.query_one("#product", Select)
        quantity = self.query_one("#quantity", Input)

        problems = self.check_inputs(quantity)
        if customer.value is Select.BLANK:
            problems.insert(0, "customer: required")
        if product.value is Select.BLANK:
            problems.insert(1, "product: required")
        if problems:
            self.notify("\n".join(problems), title="Fix the form", severity="warning")
            return

        priority = self.query_one("#priority", RadioSet).pressed_button
        self.submit_to_api("orders", {
            "customer_id": customer.value,
            "product": product.value,
            "quantity": int(quantity.value),
            "priority": priority.id if priority else "standard",
            "notes": self.query_one("#notes", TextArea).text,
        })
        self._clear()

    @on(Button.Pressed, "#clear")
    def _clear(self) -> None:
        self.query_one("#customer", Select).clear()
        self.query_one("#product", Select).clear()
        self.query_one("#quantity", Input).value = "1"
        self.query_one("#standard", RadioButton).value = True
        self.query_one("#notes", TextArea).clear()
