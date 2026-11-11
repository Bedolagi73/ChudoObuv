# Чудо Обувь

Учебный каталог обуви: Python, PySide6, SQLAlchemy и PostgreSQL.

## Запуск

Из корня репозитория в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/TufliBatinkoKrosovki"
.\.venv\Scripts\python.exe widget.py
```

Замените USER, PASSWORD и HOST своими параметрами. База данных должна существовать; приложение создаёт таблицы при запуске. Без DATABASE_URL используется PostgreSQL на localhost с базой TufliBatinkoKrosovki. `.env.example` показывает формат настройки; автоматически файл .env не загружается.

Для первоначального импорта таблиц из `import/` в подготовленную базу:

```powershell
.\.venv\Scripts\python.exe import_data.py
```

## Последние правки интерфейса

В `preview/` сохранены последние изменения от 05.11.2026 13:06: скидка 25% на товары без заказов в прошлом месяце, подсветка малого остатка и обновлённое оформление. Там же находятся скриншоты.

Чтобы применить эту версию в своей копии, скопируйте `widget.py`, `tovar.py`, `form.ui`, `tovar.ui` из `preview/` в корень с заменой, затем пересоздайте Python-код формы:

```powershell
.\.venv\Scripts\pyside6-uic.exe form.ui -o ui_form.py
.\.venv\Scripts\python.exe widget.py
```

Изображения товаров и логотипа отсутствуют в сохранённых исходниках. Каталог показывает «Нет фото», если изображения не найдены.

## Проверка публикации

Проверены синтаксис Python и XML форм. Приложение при публикации не запускалось: сохранённое виртуальное окружение ссылается на Python с другого компьютера, а в текущем Python зависимости не установлены.
