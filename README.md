# QRKot
>Приложение Благотворительного фонда поддержки котиков **QRKot**.
>
>Фонд собирает пожертвования на различные целевые проекты: на медицинское обслуживание нуждающихся хвостатых, на обустройство кошачьей колонии в подвале, на корм оставшимся без попечения кошкам — на любые цели, связанные с поддержкой кошачьей популяции

## Автор 
- Кобелев Андрей Андреевич  
    - [email](mailto:andrey.pydev@gmail.com)
  
## Технологии  
- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
- [aiosqlite](https://aiosqlite.omnilib.dev/en/stable/index.html)
- [Uvicorn](https://www.uvicorn.org/)

## Как запустить проект: 
  
Клонировать репозиторий и перейти в него в командной строке:  
  
```  
git clone https://github.com/andrey-kobelev/cat_charity_fund.git
```  
  
```  
cd cat_charity_fund
```  
  
Cоздать и активировать виртуальное окружение:  
  
```  
python3 -m venv env  
```  
  
```  
source env/bin/activate  
```  
  
Установить зависимости из файла requirements.txt:  
  
```  
python3 -m pip install --upgrade pip  
```  
  
```  
pip install -r requirements.txt  
```
### Настройка базы данных

Выполните все не применённые миграции:

```bash
alembic upgrade head
```

### Команда запуска приложения

В корневой директории проекта выполните команду запуска проекта

```
uvicorn app.main:app --reload
```


## Справка

После запуска сервера Uvicorn будет  доступна документация в двух форматах:
- [документация Swagger](http://127.0.0.1:8000/docs)
- [документация ReDoc](http://127.0.0.1:8000/redoc)

