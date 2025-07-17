#!/bin/bash

# Количество строк логов для вывода
TAIL_LINES=200

# Получаем список ID всех запущенных контейнеров
container_ids=$(docker ps -q)

# Проверяем, есть ли запущенные контейнеры
if [ -z "$container_ids" ]; then
  echo "Нет запущенных контейнеров."
  exit 1
fi

# Перебираем каждый ID контейнера и выводим ограниченные логи
for id in $container_ids; do
  # Получаем имя контейнера
  container_name=$(docker inspect --format '{{.N
ame}}' "$id" | sed 's/^\///')
  echo "======================================"
  echo "Логи для контейнера: $container_name ($id) [Последние $TAIL_LINES строк]"
  echo "======================================"
  docker logs --tail "$TAIL_LINES" "$id"
  echo -e "\n"
done