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
- Redis
- gunicorn  
- docker  
- Celery 
- aiogram
- VK API
- GitHub Actions

<h2 align='center'> Инструкция по локальному запуску проекта с использованием Polling </h2>
<h3 align='center'> Запуск Docker-контейнера с базой данных PostgreSQL, redis, pgadmin </h3>

### 1. Перейдите в папку `infra`:
```bash
cd infra
```

### 2. Запустите Docker-контейнер `docker-compose.local.yml`:
```bash
docker-compose -f docker-compose.local.yml up -d
```

### 3. Дождитесь полного запуска контейнера (это может занять несколько секунд).

### 4. Проверьте статус контейнеров:
```bash
docker-compose -f docker-compose.local.yml ps
```

### 5. При необходимости проверьте лог контейнера:
```bash
docker-compose -f docker-compose.local.yml logs
```

> **<u>Важно</u>**: контейнер с базой данных PostgreSQL должен быть запущен и полностью готов к работе перед запуском проекта.

<h3 align='center'>Запуск проекта:</h3>

### 1. Клонируйте репозиторий:
```bash
git clone git clone git@github.com:Iblat1041/WRESTRUS90.git
```

### 2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
```

### 3. Активируйте виртуальное окружение:
- Для macOS/Linux:
```bash
source venv/bin/activate
```
- Для Windows:
```bash
venv\Scripts\activate
```

### 4. Установите зависимости:
```bash
pip install -r src/requirements.txt
```

### 5. Создайте файл `.env` в папке `infra` с переменными из `.env.example`:


### 6. Перейдите в папку `fastapi_app`:
```bash
cd fastapi_app
```
### 7. Создайте новые миграции (миграции необходимо создавать при каждом изменении моделей):
```bash
alembic -c db/alembic.ini revision --autogenerate -m "init"
```

### 8. Примените миграции к базе данных:
```bash
alembic -c db/alembic.ini upgrade head
```

### 9. Запустите проект:
```bash
python main.py
```
После этого введите в Telegram-бот команду `/start` для активации бота.


<h2 align='center'>Celery локальный запуск</h2>

Запуск из /WRESTRUS90/fastapi_app:

Celery Worker — рабочий процесс, который выполняет задачи, отправленные в очередь через Redis. Worker "слушает" очередь задач и выполняет их, когда они поступают от Celery Beat

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && celery -A fastapi_app.vk.celery_app.celery_app worker --loglevel=DEBUG
```
Эта команда запускает Celery Beat — планировщик задач, который отвечает за запуск периодических задач по расписанию, определённому в конфигурации Celery

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/.. && celery -A vk.celery_app.celery_app beat --loglevel=DEBUG

```

<h2 align='center'> Подключение к базе данных в pgAdmin </h2>

##Подключитесь к базе данных в pgAdmin

Откройте pgAdmin в браузере перейдите по адресу:

```bash
http://localhost:5050
```

Войдите с учетными данными настройка в .env:
```bash
Email: admin@example.com
Password: admin
```
Настройка подключения :

```bash
В левой панели щелкните правой кнопкой мыши на Servers > Register > Server.
Введите имя сервера, например, dbwrest.
Вкладка Connection:
Host name/address: db (имя сервиса PostgreSQL в Docker-сети).
Port: 5432.
Maintenance database: dbwrest.
Username: wrest.
Password: wrest.
Нажмите Save.
```


<h2 align='center'> Развертыванию проекта с контейнерами FastAPI, PostgreSQL, Redis, Celery на сервере</h2>

<h3 align='center'> Предварительные требования</h3
>
- Сервер с установленными Docker и Docker Compose
- SSH-доступ к серверу с использованием SSH-ключа
- Файлы `.env` (образец файла есть в директории `infra` репозитории проекта на GitHub) и `docker-compose.production.yml` 
(есть в директории `infra` в репозитории проекта на GitHub)

### 1. Подключение к серверу

```bash
ssh user@111.111.111.11
```

(здесь и далее по тексту замените *user* на Ваше имя пользователя на сервере, *111.111.111.11* на IP-адрес Вашего сервера)

### 2. Подготовка окружения

Перейдите в директорию `infra` на сервере:

```bash
cd ~/infra
```

### 3. Копирование необходимых файлов

Скопируйте файлы `.env` и `docker-compose.production.yml` в папку `infra` на сервере.<br>
Если файлы находятся на вашем локальном компьютере, используйте команду:

```bash
scp .env docker-compose.production.yml user@111.111.111.11:~/infra/
```

### 4. Настройка переменных окружения

Перед запуском убедитесь, что в файле `.env`:
1. Указан корректный токен для Вашего Telegram бота
1. Заданы правильные данные для суперпользователя
1. Установлены корректные параметры для PostgreSQL

### 5. Запуск проекта
Выполните следующую команду в директории `infra`:<br>
```bash
docker compose -f docker-compose.production.yml up -d
```

Эта команда:
- Создаст volume для базы данных PostgreSQL
- Запустит контейнер с базой данных PostgreSQL
- Запустит контейнер с приложением FastAPI
- Настроит сеть между контейнерами

### 6. Проверка работы
Убедитесь, что контейнеры запущены:<br>
```bash
docker compose -f docker-compose.production.yml ps
```

Проверьте логи контейнера с приложением FastAPI:<br>
```bash
docker compose -f docker-compose.production.yml logs backend
```

Проверьте логи контейнера с базой данных PostgreSQL:<br>
```bash
docker compose -f docker-compose.production.yml logs db
```

После этого введите в Telegram-бот команду ```/start``` для активации бота.

### 7. Доступ к приложению
Приложение FastAPI будет доступно по адресу/порту: https://111.111.111.11:8000<br>
(также можно настроить Nginx на сервере на переадресацию всех запросов по IP-адресу или доменному имени сервера на 8000 порт).

Панель администрирования будет доступна по адресу: https://111.111.111.11/admin/<br>
Используйте данные суперпользователя из файла `.env` для входа в панель администрирования.

База данных PostgreSQL будет доступна по следующим параметрам:
- Хост: db (внутри docker-сети)
- Порт: 5432
- Пользователь, пароль и имя базы данных будут установлены в соответствии с файлом .env

### 8. Полезные команды
Остановить контейнеры:<br>
```bash
docker compose -f docker-compose.production.yml down
```

Перезапустить контейнеры:<br>
```bash
docker compose -f docker-compose.production.yml restart
```

Обновить контейнеры (после обновления образа):
```
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d
```

### 9. Дополнительная информация
- При первом запуске будет создан суперпользователь с указанными в файле .env данными
- Все данные базы данных PostgreSQL при перезапуске контейнера с базой данных сохраняются в volume pgdata
- Приложение FastAPI автоматически перезапускается при падении контейнера или сервера
- Для обновления кода на сервере необходимо создать коммит с изменениями и сделать push в ветку main в репозитории 
GitHub – все изменения автоматически будут применены к Docker-образу в Docker Hub, и изменённый образ будет использован 
для создания и перезапуска контейнера с приложением FastAPI на сервере (реализовано на базе GitHub Actions workflow). 
Для корректного обновления необходимо убедиться, что в настройках репозитория GitHub указаны необходимые secrets, см. 
файл ***main.yml*** в директории ***.github/workflows***.
