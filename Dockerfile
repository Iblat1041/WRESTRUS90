FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./fastapi_app /app/fastapi_app

EXPOSE 8000
CMD alembic -c db/alembic.ini revision --autogenerate -m 'init' ; alembic -c db/alembic.ini upgrade head ; python main.py