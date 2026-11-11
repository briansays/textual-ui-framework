"""Headless smoke test: drives every screen through the real UI.

Run with:  python3 tests/test_app.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.widgets import DataTable, Input, Select  # noqa: E402

from app import DemoApp  # noqa: E402


async def main() -> None:
    app = DemoApp()
    async with app.run_test(size=(120, 40)) as pilot:
        print("backend:", app.api.backend_name)
        assert app.screen.SCREEN_NAME == "menu"

        # Menu list -> Customers
        await pilot.press("enter")
        assert app.screen.SCREEN_NAME == "customers", app.screen

        # Invalid submit is rejected
        await pilot.click("#submit")
        assert not app.api.list("customers").data["records"]

        # Fill and submit (digits typed into an Input must not trigger nav)
        app.screen.query_one("#name", Input).focus()
        await pilot.press(*"Ada 123")
        app.screen.query_one("#email", Input).value = "ada@example.com"
        await pilot.click("#submit")
        await pilot.pause()
        recs = app.api.list("customers").data["records"]
        assert recs and recs[0]["data"]["name"] == "Ada 123", recs

        # F3 -> Orders; customer dropdown populated from the backend
        await pilot.press("f3")
        await pilot.pause()
        assert app.screen.SCREEN_NAME == "orders"
        s = app.screen
        s.query_one("#customer", Select).value = recs[0]["id"]
        s.query_one("#product", Select).value = "gadget"
        s.query_one("#quantity", Input).value = "3"
        await pilot.click("#express")
        await pilot.click("#submit")
        await pilot.pause()
        order = app.api.list("orders").data["records"][0]["data"]
        assert order == {"customer_id": 1, "product": "gadget", "quantity": 3,
                         "priority": "express", "notes": ""}, order

        # Side-menu nav button -> Records
        await pilot.click("#nav-records")
        await pilot.pause()
        assert app.screen.SCREEN_NAME == "records"
        assert app.screen.query_one(DataTable).row_count == 1

        # Settings -> Apply
        await pilot.press("f5")
        await pilot.pause()
        await pilot.click("#submit")
        await pilot.pause()
        assert app.api.list("settings").data["records"]

        # Back to menu via Escape
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen.SCREEN_NAME == "menu"
        app.save_screenshot("menu.svg", path=sys.argv[1] if len(sys.argv) > 1 else ".")
    print("ALL OK")


asyncio.run(main())
