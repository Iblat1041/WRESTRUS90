# Хост веб-сервера FastAPI (0.0.0.0 позволяет принимать соединения со всех интерфейсов).
WEB_SERVER_HOST=0.0.0.0
# Порт веб-сервера FastAPI (8888 соответствует порту в docker-compose.yml).
WEB_SERVER_PORT=8888
# Токен Telegram-бота для инициализации Bot в main.py и celery_app.py.
TELEGRAM_BOT_TOKEN=7369567804:AAEqOM3QQkl_UDjbEeJfpBRIFUbQ4RgAfVE

# Данные первого суперпользователя для fastadmin.
FIRST_SUPERUSER_FIRST_NAME=Ivan        # Имя суперпользователя.
FIRST_SUPERUSER_LAST_NAME=Ivanov       # Фамилия суперпользователя.
FIRST_SUPERUSER_MIDDLE_NAME=Ivanovich  # Отчество суперпользователя.
FIRST_SUPERUSER_TELEGRAM_ID=830208061  # Telegram ID суперпользователя для уведомлений.
FIRST_SUPERUSER_ROLE=ADMIN             # Роль суперпользователя (ADMIN для полного доступа).
FIRST_SUPERUSER_EMAIL=example@email.com  # Email суперпользователя.
FIRST_SUPERUSER_PHONE=+79999999999     # Телефон суперпол
ьзователя.
FIRST_SUPERUSER_ADDITIONAL_INFO=Moscow # Дополнительная информация о суперпользователе.
FIRST_SUPERUSER_PASSWORD=admin         # Пароль суперпользователя для fastadmin.

# Настройки подключения к базе данных PostgreSQL.
POSTGRES_USER=wrest                    # Имя пользователя PostgreSQL.
POSTGRES_PASSWORD=wrest                # Пароль пользователя PostgreSQL.
POSTGRES_DB=dbwrest                    # Имя базы данных.
POSTGRES_SERVER=db                     # Хост базы данных (имя сервиса db в docker-compose.yml). 
                                       # Docker контейнерах сервисы общаются по именам (db:5432)
                                       # Локально нужно подключаться через localhost:5000, настройка в comfig.py

POSTGRES_PORT_PROD=5432                     # Порт PostgreSQL внутри контейнера 5432, локально переключается на 5000. настройка в comfig.py.
POSTGRES_PORT_LOCAL=5000

# Настройки подключения к Redis.
REDIS_HOST=redis                       # Хост Redis (имя сервиса redis в docker-compose.yml).
REDIS_PORT=6379                        # Порт Redis.

# Настройки VK API для получения новостей.
VK_ACCESS_TOKEN=ce136ae6ce136ae6ce136ae671cd262548cce13ce136ae6a64ccb5b5bdd091895cf343c
VK_GROUP_ID=17967058                 # ID группы VK.
