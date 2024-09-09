Проектом «Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Стек используемых технологий:
Python, Django, Django Rest Framework, Postgres, Docker, Docker-compose, Gunicorn, Nginx, Workflow, React

### Чтобы посмотреть спецификацию API:

Перейдите в папку infra, выполните команду ```docker-compose up```. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу ```http://localhost``` будет доступен фронтенд веб-приложения, а по адресу ```http://localhost/api/docs/``` — спецификацию API.


Чтобы собрать проект локально, выполните из директории FOODGRAM команду ```docker compose up```. Удостоверьтесь, что DEBUG = True.
Проект будет доступен на ```http://localhost:7777/```

### В проекте должен быть .env файл с данными:

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram

DB_HOST=db
DB_PORT=5432

DEBUG=True

ALLOWED_HOSTS=127.0.0.1,localhost
```

## Информацию о API проекта

### Создание виртуального окружения:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Tanya794/foodgram.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3.9 -m venv venv
```

```
source venv/bin/activate
```

### Запросы:

##### Пользователи
###### ```/api/users/```: (GET) Список пользователей / (POST) Регистрация пользователя
###### ```/api/users/{id}/```: (GET) Профиль пользователя
###### ```/api/users/me/```: (GET) Текущий пользователь
###### ```/api/users/me/avatar/```: (PUT) Добавление аватара / (DEL) Удаление аватара
###### ```/api/users/set_passwort/```: (POST) Изменение пароля
###### ```/api/auth/token/login/```: (POST) Получить токен авторизации
###### ```/api/auth/token/logout/```: (POST) Удаление токена

##### Теги
###### ```/api/tags/```: (GET) Cписок тегов
###### ```/api/tags/{id}/```: (GET) Получение тега

##### Рецепты
###### ```/api/recipes/```: (GET) Список рецептов / (POST) Создание рецепта
###### ```/api/recipes/{id}/```: (GET) Получение рецепта / (PATCH) Обновление рецепта / (DEL) Удаление рецепта
###### ```/api/recipes/{id}/get-link/```: (GET) Получить короткую ссылку на рецепт

##### Список покупок
###### ```/api/recipes/download_shopping_cart/```: (GET) Скачать список покупок
###### ```/api/recipes/{id}/shopping_cart/```: (POST) Добавить рецепт в список покупок / (DEL) Удалить рецепт из списка покупок

##### Избранное
###### ```/api/recipes/{id}/favorite/```: (POST) Добавить рецепт в избранное / (DEL) Удалить рецепт из избранного

##### Подписки
###### ```/api/users/subscriptions/```: (GET) Мои подписки (Возвращает пользователей, на которых подписан текущий пользователь.)
###### ```/api/users/{id}/subscribe/```: (POST) Подписаться на пользователя / (DEL) Отписаться от пользователя

##### Ингредиенты
###### ```/api/ingredients/```: (GET) Список ингредиентов
###### ```/api/ingredients/{id}/```: (GET) Получение ингредиента

#### Сайт:
```http://158.160.65.231:7007```

#### Вход в админ-зону:
email: ```admin@admin.ru```
password: ```Aa12345678```


Проект выполнила Татьяна Маркелова
