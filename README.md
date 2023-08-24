# **BlogPost - площадка для публикации статей**

### Оглавление
<ol>
 <li><a href="#description">Описание проекта</a></li>
 <li><a href="#stack">Используемые технологии</a></li>
 <li><a href="#architecture">Архитектура проекта</a></li>
 <li><a href="#docker">Как запустить проект в Docker?</a></li>
 <li><a href="#start_project">Как развернуть проект локально?</a></li>
 <li><a href="#author">Авторы проекта</a></li>
</ol>

___
### Описание проекта:<a name="description"></a>
Площадка предназначена для публикации авторами статей. На площадке реализована система 
регистрации/восстановления пароля, есть возможность комментировать публикации,
подписываться на интересных авторов, просматривать список своих подписчиков.

___
### **Используемые технологии**<a name="stack"></a>
![](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=jinja&logoColor=white)
![](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![](https://img.shields.io/badge/HTML-red?style=for-the-badge)
![](https://img.shields.io/badge/CSS-2CA5E0?style=for-the-badge)
![](https://img.shields.io/badge/Jinja-red?style=for-the-badge&logo=jinja&logoColor=black)
![](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
___
### Архитектура проекта<a name="architecture"></a>


| Директория | Описание                                                           |
|------------|--------------------------------------------------------------------|
| `yatube`   | Содержит файлы Django приложения, разбитые на маленькие приложения |
| `tests`    | Директория с тестами проекта                                       |
| `infra`    | Файлы для запуска с помощью Docker, настройки Nginx                |

___
### Как запустить проект в Docker?<a name="docker"></a>
* Запустите терминал и клонируйте репозиторий 
    ```
    git clone https://github.com/FakaFakaYeah/BlogPost.git
    ```
    
* Создайте .env файл и заполните его по шаблону
  ```
  USE_POSTGRESQL=True # Если флаг стоит False, будет использована sqlite3
  SECRET_KEY=  #укажите свой SECRET_KEY
  DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
  DB_NAME=  # имя базы данных
  POSTGRES_USER= # логин для подключения к базе данных
  POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)
  DB_HOST=  # название сервиса (контейнера)
  DB_PORT=  # порт для подключения к БД
  ```
  
* Установите Docker по ссылке https://www.docker.com/products/docker-desktop

* Перейдите в директорию с Docker-compose.yaml
    ```
    cd infra
    ```

* Выполните команду по разворачиванию docker-compose
    ```
    docker-compose up -d
    ``` 
  
* Будет проведена сборка образа по Dockerfile и запуск проекта в трех контейнерах

* Выполните миграции по следующей команде:
    ```
    docker-compose exec web python manage.py migrate
    ```
* Выполните сбор статики проекта по следующей команде:
    ```
    docker-compose exec web python manage.py collectstatic --no-input
    ```
* Cоздайте суперпользователя
  ```
  docker-compose exec web python manage.py createsuperuser
  ```
  укажите имя пользователя, почту и пароль
  
* Проект будет доступен по следующим адресам:
  ```
  http://localhost/ - главня страница проекта
  http://localhost/admin/ - админ зона
  ```

___
### Как развернуть проект локально?<a name="start_project"></a>
* Запустите терминал и клонируйте репозиторий 
  ```
  git clone https://github.com/FakaFakaYeah/BlogPost.git
  ```

* Создайте и активируйте виртуальное окружение
  ```
  python3 -m venv venv
  ```

  Если у вас Linux/macOS

  ```
    source venv/bin/activate
  ```
  
  Если у вас windows

  ```
  source venv/scripts/activate
  ```
  
* Установите зависимости из файла requirements.txt:
  ```
  python3 -m pip install --upgrade pip
  ```

  ```
  pip install -r requirements.txt
  ```

* Перейдите в директорию с файлами проекта
  ```
  cd yatube
  ```

* Выполните миграции по следующей команде:
  ```
  python manage.py migrate
  ```

* Создайте суперпользователя
  ```
  python manage.py createsuperuser
  ```
  укажите имя пользователя, почту и пароль
  
* Запустите проект
  ```
  python manage.py runserver
  ```
  
* Проект будет доступен по следующим адресам:
  ```
  http://127.0.0.1:8000/ - главня страница проекта
  http://127.0.0.1:8000/admin/ - админ зона
  ```
___
### Авторы проекта:<a name="author"></a>
Смирнов Степан
<div>
  <a href="https://github.com/FakaFakaYeah">
    <img src="https://github.com/FakaFakaYeah/FakaFakaYeah/blob/main/files/images/GitHub.png" title="GitHub" alt="Github" width="39" height="39"/>&nbsp
  </a>
  <a href="https://t.me/s_smirnov_work" target="_blank">
      <img src="https://github.com/FakaFakaYeah/FakaFakaYeah/blob/main/files/images/telegram.png" title="Telegram" alt="Telegram" width="40" height="40"/>&nbsp
  </a>
</div>