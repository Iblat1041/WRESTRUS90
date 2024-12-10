"""Параметры проекта"""

from enum import Enum, IntEnum


class Limits(IntEnum):
    # Максимальная длина строковых полей моделей в приложении "competition"
    MAX_LEN_COMPETITION_CHARFIELD = 255
    # Максимальная длинна слаговых полей в модели в приложении "competition"
    MAX_LEN_COMPETITION_SLAGFIELD = 255
    # Длинна поля name модели CategoryCompetition связь many-to-one к модели Comprtition
    MAX_LEN_CAT_COMPETITION_CHARFIELD = 100
    #Длинна поля slug модели CategoryCompetition связь many-to-one к модели Comprtition
    MAX_LEN_CAT_COMPETITION_SLAGFIELD = 255
    # Максимальная длина строковых полей моделей в приложении "event"
    MAX_LEN_EVENT_CHARFIELD = 255
    # Максимальная длинна слаговых полей в модели в приложении "event"
    MAX_LEN_EVENT_SLAGFIELD = 255
    # Длинна поля name модели CategoryEvent связь many-to-one к модели 'event'
    MAX_LEN_CAT_EVENT_CHARFIELD = 100
    #Длинна поля slug модели CategoryEvent связь many-to-one к модели 'event'
    MAX_LEN_CAT_EVENT_SLAGFIELD = 255
