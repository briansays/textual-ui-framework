"""Screen registry. Names here are what `app.switch_screen(name)` accepts."""

from .customers import CustomersScreen
from .main_menu import MainMenuScreen
from .orders import OrdersScreen
from .records import RecordsScreen
from .settings import SettingsScreen

SCREENS = {
    "menu": MainMenuScreen,
    "customers": CustomersScreen,
    "orders": OrdersScreen,
    "records": RecordsScreen,
    "settings": SettingsScreen,
}
