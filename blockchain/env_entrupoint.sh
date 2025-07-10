#!/bin/sh
set -e

# Путь к .env файлу внутри контейнера
ENV_FILE="/app/.env"

# Создаем .env, если он отсутствует
if [ ! -f "$ENV_FILE" ]; then
  touch "$ENV_FILE"
  
  # Записываем переменные окружения в файл
  if [ -n "$(env)" ]; then
    echo "Создание .env из переменных окружения..."
    env | while IFS= read -r line; do
      # Игнорируем служебные переменные Docker и пустые строки
      case $line in
        PATH=*|PWD=*|HOME=*|TERM=*|SHLVL=*|_=*) continue ;;
        *) ;;
      esac
      echo "$line" >> "$ENV_FILE"
    done
  fi
fi

# Запуск основной команды (например, Node.js, Python и т.д.)
exec "$@"