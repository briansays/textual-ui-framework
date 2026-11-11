"""Entry point: python app.py"""

from __future__ import annotations

from textual.app import App

from api import DemoApi
from screens import SCREENS


class DemoApp(App):
    TITLE = "Textual Demo Framework"
    CSS_PATH = "app.tcss"
    SCREENS = SCREENS

    def __init__(self) -> None:
        super().__init__()
        self.api = DemoApi()
        self.sub_title = self.api.backend_name

    def on_mount(self) -> None:
        self.push_screen("menu")


if __name__ == "__main__":
    DemoApp().run()
