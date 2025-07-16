<h1 align='center'>
Проект "Telegram-бот для взаимодействия с пользователями"
</h1>

<h2 align='center'>
Ключевые компоненты системы
</h2>

<h3>Сервис интеграции с VK:</h3>

- Автоматическая загрузка постов из группы ВКонтакте (ежечасный парсинг)
- Парсинг текста, изображений и метаданных
- Сохранение новостей в базу данных с тегами статусов (на модерации/опубликовано/архив)
- Автоматические уведомления модераторов в Telegram о новых постах

<h3>Telegram-бот (aiogram):</h3>

- Пользовательский интерфейс: регистрация, запись в секции, просмотр мероприятий
- Административные функции: модерация контента, управление расписанием
- Система уведомлений о статусе заявок

<h3>API (FastAPI):</h3>

- RESTful endpoints для взаимодействия с ботом
- Интеграция с VK API и Telegram Bot API
- JWT-аутентификация и ролевой доступ

<h3>FastAdmin-панель:</h3>

CRUD-интерфейс для управления:
 
- Пользователями (фильтрация по ролям)
- Новостями (одобрение/редактирование постов)
- Записями в секции
- Мероприятиями

- Кастомные actions (массовые операции, экспорт данных)
- Логирование действий администраторов

<h3>База данных (PostgreSQL):</h3>

-Оптимизированная схема для:

- Пользователей (родители/тренеры/админы)
- Новостей (с привязкой к VK-постам)
- Записей в секции (со статусами обработки)
- Регулярные бэкапы

<h3>Фоновые задачи (Celery + Redis):</h3>

- Периодические задачи: парсинг VK, напоминания
- Асинхронная обработка тяжелых операций
- Мониторинг через Flower

<h3>Особенности реализации:</h3>

- Все компоненты развернуты в Docker-контейнерах
- Prometheus-метрики для API и Celery
- Автоматическое тестирование CI/CD (GitHub Actions)

<h2 align='center'>
Технологии
</h2>

- Python  
- FastAPI
- PostgreSQL
- FastAdmin 
- Redis
- gunicorn  
- docker  
- Celery 
- aiogram
- VK API
- GitHub Actions

<h1 align='center'> ДАЛЕЕ ИНФОРМАЦИЯ ДЛЯ РАЗРАБОТКИ </h1>

# Запуск PostgreSQL в Docker

1. Перейдите в папку `infra`:
```bash
cd infra
```
2. Запустите (app, celery_worker, celery_beat) обращаются к redis (для Celery и FSM) и db `docker-compose.production.yml`:
```bash
docker-compose -f docker-compose.production.yml up -d
```

2. Запустите PostgreSQL в Docker, используя файл `docker-compose.yml`:
```bash
docker-compose -f docker-compose.yml up -d
```

3. Дождитесь полного запуска контейнеров (это может занять несколько секунд).

4. Проверьте статус контейнеров:
```bash
docker-compose -f docker-compose.yml pss
```

5. Проверьте логи (если необходимо):
```bash
docker-compose -f docker-compose.yml logs
```

> **Важно**: PostgreSQL должен быть запущен и полностью готов к работе перед запуском проекта.

## Запуск проекта:

## Клонирование репозитория и настройка окружения

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd smena_collective_team2
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
```

3. Активируйте виртуальное окружение:
- Для macOS/Linux:
```bash
source venv/bin/activate
```
- Для Windows:
```bash
venv\Scripts\activate
```

4. Установите зависимости:
```bash
pip install -r src/requirements.txt
```

5. Создайте файл `.env` в папке `infra` с переменными из `.env.example`:


## Запуск проекта

1. Перейдите в папку `src`:
```bash
cd src
```

2. Создайте новые миграции (также при изменении моделей применять):
```bash
alembic -c db/alembic.ini revision --autogenerate -m "init"
```

3. Выполните миграции базы данных:
```bash
alembic -c db/alembic.ini upgrade head
```

4. Запустите проект:
```bash
python main.py
```

## Запуск админ MAin

1. Перейдите в папку `django_app`:
```bash
cd django_app
```


4. Запустите админки:
```bash
http://localhost:8443/admin/
```

# Подключитесь к базе данных в pgAdmin

Шаг 2: Подключитесь к базе данных в pgAdmin

Откройте pgAdmin в браузере перейдите по адресу:

```bash
http://localhost:5050
```

Войдите с учетными данными:
```bash
Email: admin@example.com
Password: admin
```
Настройте подключение (если еще не настроено):

```bash
В левой панели щелкните правой кнопкой мыши на Servers > Register > Server.
Введите имя сервера, например, dbwrest.
Вкладка Connection:
Host name/address: db (имя сервиса PostgreSQL в Docker-сети).
Port: 5432 (внутренний порт PostgreSQL).
Maintenance database: dbwrest.
Username: wrest.
Password: wrest.
Нажмите Save.
```

# Celery локальный запуск

Запуск из /WRESTRUS90/fastapi_app:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
```

Celery Worker — рабочий процесс, который выполняет задачи, отправленные в очередь через Redis. Worker "слушает" очередь задач и выполняет их, когда они поступают от Celery Beat
``` bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && celery -A fastapi_app.vk.celery_app.celery_app worker --loglevel=DEBUG
```
Эта команда запускает Celery Beat — планировщик задач, который отвечает за запуск периодических задач по расписанию, определённому в конфигурации Celery
``` bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && celery -A vk.celery_app.celery_app beat --loglevel=DEBUG
```

## Вход в панель администрирования

Откройте в браузере: сгенерированный URL + /admin/ (например, https://ваш_субдомен.loca.lt/admin/)

Используйте данные суперпользователя из файла `.env` для входа.

```bash
https://id.vk.com/about/business/go/accounts/230078/apps/53825466/edit
```

Обновление записей
```bash
celery -A fastapi_app.vk.celery_app.celery_app call fetch_and_save_news_task
```
