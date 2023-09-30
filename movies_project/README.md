# Запуск
- Установить Docker и Docker Compose
- Клонировать проект
- Перейти в папку `./movies_project`
- Создать и заполнить файл `.env` на примере файла `.env.example`
- Запустить контейнеры через docker-compose:
  - **Linux**: `sudo docker-compose --env-file ./.env up --build`
  - **Windows**: `docker compose --env-file ./.env up --build`

# Запуск тестов
- Создать и заполнить файл `.env.test` на примере файла `.env.test.example`
- Перейти в папку `./movies_project/tests/functional`
- Запустить контейнеры через docker-compose:
  - **Linux**: `sudo docker-compose --env-file ./.env.test up --build`
  - **Windows**: `docker compose --env-file ./.env.test up --build`
- В консоли отобразятся результаты тестирования
- Далее можно запускать тесты либо повторным запуском контейнера `api_tests_1`, либо командой `pytest` в терминале

## Если БД postgres пустая
- Остановить контейнер, обновляющий данные в elasticsearch:
  - **Linux**: `sudo docker stop movies_project-etl-1`
  - **Windows**: `docker stop movies_project-etl-1`
- Заполнить её одним из вариантов ниже
- Запустить контейнер, обновляющий данные в elasticsearch:
  - **Linux**: `sudo docker start movies_project-etl-1`
  - **Windows**: `docker start movies_project-etl-1`

### Миграция данных из первого спринта
- Клонировать проект первого спринта `git clone https://github.com/resegr/new_admin_panel_sprint_1.git`
- Перейти в папку `./new_admin_panel_sprint_1/sqlite_to_postgres`
- Создать и заполнить файл `.env` на примере файла `.env.example`
- Создать виртуальное окружение `python3 -m venv venv`
- Активировать виртуальное окружение `. venv/bin/activate`
- Установить зависимости `pip install -r requirements.txt`
- Запустить скрипт `python main.py`, дождаться выполнения

### Восстановление из дампа
- При использовании Windows выполнять команды нужно в каталоге bin установленного PostgreSQL, 
например: `C:\Program Files\PostgreSQL\15\bin`, либо добавить его в переменную среды `PATH`
- Создать БД `createdb -U app movies_project`
- Восстановить БД из дампа `pg_restore -U app -d movies_project /path/to/your/dumpfile.dump`

# Результат
- Swagger: `http://127.0.0.1/api/openapi`
- OpenAPI файл: `movies_project/async_api/openapi.json`
