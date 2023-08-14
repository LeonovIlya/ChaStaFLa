Веб-приложение для отображения статистики и графиков на [Flask](https://flask.palletsprojects.com/en/2.2.x/).

Есть авторизация и регистрация. Данных пользователя хранятся в [PostgreSQL](https://www.postgresql.org/).

В качестве входных данных - xls/xlsx файлы.

В качестве выходных данных - png с графиками.

Обработка Excel файла через [Pandas](https://pandas.pydata.org/). Построение графиков - [Matplotlib](https://matplotlib.org/).

Есть возможность загружать файлы на сервер, смотреть список загруженных файлов, выбирать файл для построения графиков.

### Для запуска проекта необходимо:

Установить зависимости:

```bash
pip install -r requirements.txt
```

Сделать миграции
```
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

Выполнить команду:

```bash
python app.py
```

Для работы по протоколу https нужен SSL сертификат.
В корневой папке (где app.py) запускаем bash, выполняем следующую команду
```
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
```
В самом app.py добавляем строчку
```
context = (r"./certificate.pem", r"./key.pem")
```
В app.run добавляем параметр
```
ssl_context=context
```
