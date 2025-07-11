# VoteMate
#### Команда - Хакатоновые монстры
<a href="https://vote.vickz.ru/#/"><img src="https://github.com/asdfrewqha/blockchain-test/blob/readme/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2017.13.10.png"></img></a>
# Запуск проекта

> Чтобы запустить отдельно бэкенд (FastAPI приложение) достаточно установить все нужные библиотеки из `requirements.txt`, зайти в папку `backend` и прописать команду `uvicorn backend.main:app --reload`. Полностью это выглядит так:
> ```shell
> pip install -r backend/requirements.txt
> uvicorn backend.main:app --reload
> ```
> Скачивание библиотек может занять какое-то небольшое количество времени, если некоторые из них не скачаны.

> Чтобы запустить отдельно frontend часть, необходимо установить нужные модули, войти в папку и прописать `npm start`, по итогу это выглядит примерно так:
> ```shell
> cd frontend
> npm start
> ```
> Запуск frontend тоже может занимать какое-то количество времени в зависимости от устройства.

> Чтобы запустить весь проект целиком можно воспользоваться специальным `docker-compose.yml`, предназначенном для локального запуска - он находиться в папке `/local-config` (лежащей в корне проекта).
> Перед запуском вам нужно настроить и положить в эту папку файл с переменными окружения (`.env`).  Вот список его настроек (также его можно получить в папке `/config/.env.example`):
> ```.env
> RANDOM_SECRET=
> FASTAPI_HOST=
> FASTAPI_PORT=
> POSTGRES_USER=
> POSTGRES_PASSWORD=
> POSTGRES_HOST=
> POSTGRES_PORT=
> POSTGRES_DBNAME=
> DEFAULT_AVATAR_URL=
> REDIS_HOST=
> REDIS_PORT=
> REDIS_PASSWORD=
> REDIS_DB=
> REDIS_ARQ=
> BOT_TOKEN=
> BUCKET_NAME=
> S3_ACCESS_KEY=
> S3_SECRET_KEY=
> S3_ENDPOINT_URL=
> FRONTEND_URL=
> ```

> После настройки переменных окружения для запуска всей системы из корня проекта достаточно выполнить буквально две комманды:
> ```shell
>  cd local-config
>  docker compose up --build
> ```
> (опционально можете добавить флаг `-d` чтобы не выводить логи в реальном времени)


> Для запуска системы контейнеров docker необходимо сначала скачать образы, поэтому для выполнения комманды потребуется стабильный интернет и немного времени.
> После запуска всех контейнеров, документация бэкенда будет доступна по ссылке [http://localhost](http://localhost)


> ### Основной docker-compose - для автоматической сборки на сервере с помощью CI/CD
> Для его запуска нужно все так же записать переменные окружения в `.env`, но переместить его на сервер, а также дописать необходимую информацию в секреты репозитория. После такой настройки вы сможете любым пушем в `main` запустить автоматическую загрузку приложения на сервер.
> <img width="1539" height="353" alt="brave_screenshot_github com" src="https://github.com/user-attachments/assets/c843bb7f-4e52-4f79-8b40-a29149e02bf6" />
> После успешного деплоя приложения появится зеленая галочка около значка коммита и если перейти туда, то будет видно вот такое окошко.

# Задача VoteMate

> В мире сейчас растет всеобщая неуверенность в честности подсчетов голосований, из-за чего люди и люди все реже и реже участвуют в публичных голосованиях. Также многие боятся того, что организаторы голосований сольют персональные данные участника, поэтому многие переживают за свою анонимность.
Мы решаем эти две проблемы и считаем, что благодаря своему сервису мы можем обратно вернуть веру людей в честные и анонимные голосования.

# Преимущества

> Существуют разные методы проголосовать, но мы сделали ставку на новой технологии, которая значительно повышает безопасность - блокчейне. Хоть такие голосования уже делались, мы решили сделать более обобщенный вариант, чтобы на нашей платформе были голосования на любой вкус

# Регистрация
#### [Зарегистрироваться](https://vote.vickz.ru/#/signup)
> Уже сейчас реализована регистрация через мессенджер Телеграм - [@SecureVoteBlockchainBot](t.me/SecureVoteBlockchainBot)
> Чтобы успешно зарегистрироваться на нашем сайте нужно:
> 1. Перейти на [https://vote.vickz.ru/#/signup](https://vote.vickz.ru/#/signup)
> 2. Введите свое имя
> 3. Логин
> 4. Пароль
> 5. После перейти в нашего [бота](t.me/SecureVoteBlockchainBot) и прописать `/start`
<img width="60%" src="https://github.com/asdfrewqha/blockchain-test/blob/main/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2017.42.24.png"></img>
> 6. Вы получите код, его надо вставить в окно на сайте
<img width="60%" src="https://github.com/asdfrewqha/blockchain-test/blob/main/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2014.09.34.jpg"></img>
<img width="60%" src="https://github.com/asdfrewqha/blockchain-test/blob/main/Readme-photos/photo_2025-07-10_17-45-56.jpg"></img>
> 7. **Успешно!**
> 8. Теперь оформите свой профиль)
<img width="75%" src="https://github.com/asdfrewqha/blockchain-test/blob/main/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2017.47.12.png"></img>

# Возможности на сайте
## Создание собственных голосований
> Перейдите на страницу `Home` - [Home](https://vote.vickz.ru/#/home)
> Нажмите `Create Poll`
<img src='https://github.com/asdfrewqha/blockchain-test/blob/readme/Readme-photos/photo_2025-07-10_18-41-56.jpg'></img>
> Вы можете сделать его как `Публичным`, так и `Приватным`

## Голосование
> Перейдите на страницу `Search` - [Search](https://vote.vickz.ru/#/search)
<img src='https://github.com/asdfrewqha/blockchain-test/blob/readme/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2018.50.40.png'></img>
> Выберите любое голосование
>
> <img src='https://github.com/asdfrewqha/blockchain-test/blob/readme/Readme-photos/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202025-07-10%20%D0%B2%2019.06.37.png'></img>
> Вы можете поставить галочку `Notify me about this poll's result`, чтобы при окончании голосования вам пришло уведомление в телеграмм [бота](t.me/SecureVoteBlockchainBot)
