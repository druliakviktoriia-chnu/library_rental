# library_rental

Практичне заняття 1 (ERP-CRM системи, Трек A: Бібліотека / прокат).
Мінімальний модуль Odoo 19, що встановлюється без помилок. Залежність лише `base`.

## Що згенерував AI

Використовувався Claude (Anthropic). Конкретні запити:

1. "У мене не підключається Odoo" (скріншот VS Code з odoo.conf, де був лише addons_path). AI запропонував додати в odoo.conf параметри db_host, db_port, db_user, db_password, http_port.
2. Запит на діагностику помилки UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4. AI запропонував підключитися через psql з PGCLIENTENCODING=UTF8 і створити роль openpg командою CREATE ROLE ... PASSWORD.
3. Запит після помилки "параметри сортування з різними значеннями collate і ctype не підтримуються на цій платформі". AI запропонував створити базу вручну: CREATE DATABASE library ... LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0, і ініціалізувати її командою odoo-bin -d library -i base --without-demo=all --stop-after-init.
4. Запит "створи Git-репозиторій і структуру модуля". AI згенерував .gitignore, папку library_rental з __init__.py та мінімальний __manifest__.py (depends: base).
5. Запит на підключення модуля: AI запропонував дописати C:\odoo_custom в addons_path і оновити список застосунків (Update Apps List, режим debug).

## Що виправлено вручну

1. Порт 8069 уже займала служба Windows Odoo, тому браузер показував ERR_TOO_MANY_REDIRECTS. Рішення: запуск власного екземпляра з --http-port=8070 (перевірено в браузері: 127.0.0.1:8070).
2. AI спочатку помилково пояснив цикл редиректів cookie та базою db_vika. Це не підтвердилося (помилка була і в режимі інкогніто), справжня причина знайдена за відсутністю рядків GET у терміналі.
3. Master Password: AI вказав admin, але Odoo згенерував власний пароль і записав хеш в odoo.conf. Використано пароль, який показав Odoo.
4. У odoo.conf додано db_name = library, dbfilter = ^library$, list_db = False, щоб Odoo однозначно вибирав базу.
5. Пароль адміністратора бази замінено на власний, стандартний admin/admin не залишено.

## Залежності

У __manifest__.py вказано лише `base`: модуль поки не використовує функціонал crm, sale чи mail.

## Встановлення

1. Додати C:\odoo_custom до addons_path в odoo.conf.
2. Оновити список застосунків (режим розробника) і встановити Library Rental.
3. Скріншот встановленого модуля: screenshot_installed.png.
