
## Запуск без docker-compose
1) Создать миграции приложения
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

2) Запуск redis. Env `REDIS_URL=redis://0.0.0.0:6379`
    ```
    sudo  docker run -d --name redis_l -p 6379:6379 -p 8001:8001 redis/redis-stack:latest --rm
    ```
    Если выдает ошибку, что контейнер есть, то запустить 
    ```commandline
    sudo docker start redis_l
    ```

3) Запуск celery

    ```
    celery -A base worker --loglevel=INFO
    ```
4) Создать суперюзера `python manage.py createsuperuser`
5) Запустить проект `python manage.py runserver`