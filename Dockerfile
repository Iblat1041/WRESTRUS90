FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./fastapi_app/ .

EXPOSE 8000

CMD ["/bin/bash", "-c", "alembic -c db/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]