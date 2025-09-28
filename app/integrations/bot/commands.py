"""Команды бота для приватных и групповых чатов."""

from __future__ import annotations

from aiogram.types import BotCommand

private_commands = [
    BotCommand(command="start", description="Начать взаимодействие с ботом"),
    BotCommand(command="menu", description="Открыть главное меню"),
]

group_commands = [
    BotCommand(command="menu", description="Открыть меню бота в группе"),
]
