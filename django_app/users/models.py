from django.db import models
import json


class Admin(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('moderator', 'Moderator')], default='admin')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admins'

    def __str__(self):
        return f"Admin {self.user.name}"


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)  # Увеличьте max_length, если нужно
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255, null=True)  # Увеличьте max_length, если нужно
    created_at = models.DateTimeField(auto_now_add=True)  # Добавьте auto_now_add

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name


class ChildRegistration(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    age = models.IntegerField()
    parent_contact = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'child_registrations'

    def __str__(self):
        return f"Registration for {self.child_name}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.title


class News(models.Model):
    vk_post_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    images = models.JSONField(null=True, default=dict)  # JSONField доступен с Django 3.1+
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'news'

    def __str__(self):
        return self.title
