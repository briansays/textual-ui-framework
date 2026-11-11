"""Page 4 — Records browser: reads back whatever the backend has stored."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Label, Select, Static

from .base import BaseScreen

ENTITIES = [("Customers", "customers"), ("Orders", "orders"), ("Settings", "settings")]


class RecordsScreen(BaseScreen):
    SCREEN_NAME = "records"
    PAGE_TITLE = "Stored Records"

    def compose_body(self) -> ComposeResult:
        with Horizontal(classes="form-row"):
            yield Label("Entity")
            yield Select(ENTITIES, id="entity", value="customers", allow_blank=False)
        yield DataTable(id="table", zebra_stripes=True, cursor_type="row")
        with Horizontal(classes="actions"):
            yield Button("Refresh", id="refresh", variant="primary")
        yield Static(id="result")

    def on_screen_resume(self) -> None:
        self.refresh_table()

    @on(Select.Changed, "#entity")
    @on(Button.Pressed, "#refresh")
    def refresh_table(self) -> None:
        entity = self.query_one("#entity", Select).value
        table = self.query_one("#table", DataTable)
        table.clear(columns=True)

        result = self.api.list(str(entity))
        if not result.ok:
            self.show_result(f"Error: {result.error}")
            return
        records = result.data.get("records", [])

        # Build columns from the union of keys across all records.
        keys: list[str] = []
        for r in records:
            keys += [k for k in r["data"] if k not in keys]
        table.add_columns("id", *keys)
        for r in records:
            table.add_row(str(r["id"]), *(str(r["data"].get(k, "")) for k in keys))
        self.show_result(f"{len(records)} record(s) in '{entity}' · {self.api.backend_name}")
