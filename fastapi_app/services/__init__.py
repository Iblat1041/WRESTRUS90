# Импорт с псевдонимами при необходимости
from .admin import AdminAdmin as AdminAdmin
from .admin import ChildRegistrationAdmin as ChildRegistrationAdmin
from .admin import EventAdmin as EventAdmin
from .admin import NewsAdmin as NewsAdmin
from .admin import UserAdmin as UserAdmin

# Экспорт только нужных классов
__all__ = [
    'AdminAdmin',
    'ChildRegistrationAdmin',
    'EventAdmin',
    'NewsAdmin',
    'UserAdmin',
    ]
