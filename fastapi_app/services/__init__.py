# Импорт с псевдонимами при необходимости
from .admin import AdminAdmin as AdminAdmin
from .admin import ChildRegistrationAdmin as ChildRegistrationAdmin
from .admin import EventAdmin as EventAdmin
from .admin import UserAdmin as UserAdmin

from .admin_handl.handlers import admin_router
from .child_handl.handlers import child_router
from .event_handl.handlers import event_router

from services.models import User