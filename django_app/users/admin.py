from django.contrib import admin
from .models import Admin, ChildRegistration, Event, News, User

admin.site.register(Admin)
admin.site.register(ChildRegistration)
admin.site.register(Event)
admin.site.register(News)
admin.site.register(User)
