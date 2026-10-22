# library_rental

Курс "ERP-CRM системи", Трек A (Бібліотека / прокат). Модуль Odoo 19.
Залежність: лише `base` (зайві crm, sale, mail не потрібні).

## Практичне заняття 1: середовище та перший модуль

### Що згенерував AI (Claude)

1. Запит "Odoo не підключається" (скріншот odoo.conf). AI запропонував додати в odoo.conf db_host, db_port, db_user, db_password, http_port.
2. Помилка UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4. AI запропонував підключитися через psql з PGCLIENTENCODING=UTF8 і створити роль openpg командою CREATE ROLE.
3. Помилка про різні collate і ctype. AI запропонував створити базу вручну (CREATE DATABASE library ... LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0) і ініціалізувати її через odoo-bin -d library -i base --stop-after-init.
4. Запит "створи Git-репозиторій і структуру модуля": AI згенерував .gitignore, папку library_rental з __init__.py і мінімальний __manifest__.py.

### Що виправлено вручну

1. Порт 8069 займала служба Windows Odoo, браузер показував ERR_TOO_MANY_REDIRECTS. AI спершу помилково пояснив це cookie та іншою базою; не підтвердилося (помилка була і в режимі інкогніто). Справжню причину знайдено за відсутністю рядків GET у терміналі. Рішення: власний екземпляр на --http-port=8070.
2. Master Password: AI вказав admin, але Odoo згенерував власний пароль і записав його хеш в odoo.conf.
3. У odoo.conf додано db_name = library, dbfilter = ^library$, list_db = False.

## Практичне заняття 2: моделі бібліотеки та ORM

### Структура зв'язків

- **Book** (name, author, isbn, publish_year) має One2many copy_ids до Copy.
- **Copy** (book_id Many2one, inventory_number, condition): окрема сутність, бо одна книга має багато фізичних примірників з власним станом.
- **Member** (name, membership_number, phone, email): обрано варіант (а), окрема модель library.member, а не _inherits від res.partner. Причина: простіше і менше ризику на цьому етапі; мінус: контакти дублюють res.partner.
- **Loan** (copy_id, member_id, loan_date, due_date, return_date, state): видача прив'язана до конкретного примірника (Copy), а не до назви книги, бо тільки так видно, який фізичний примірник зараз на руках. Автор і ISBN книги показуються у формі через related-поля copy_id.book_id.

Відхилень від рекомендованої структури немає.

### ondelete (перевірено вручну)

- Copy.book_id: ondelete='restrict'. Видалення книги з примірниками заборонено (перевірено в інтерфейсі, скріншот screenshot_ondelete_restrict.png, PostgreSQL повертає помилку RESTRICT).
- Loan.copy_id і Loan.member_id: ondelete='restrict'. Видалення примірника чи читача не знищує історію видач.
- Усі Many2one мають required=True.

### Що згенерував AI без правок

- Файли models/book.py, copy.py, member.py, loan.py, XML-представлення, ir.model.access.csv, демо-дані в data/library_data.xml (4 книги, 6 примірників, 3 читачі, 4 видачі).
- Запити ORM для Кроку 5 (screenshot_orm_queries.png): пошук книг автора, вільні примірники (1 з 2 для "Tiger Hunters": INV-102), прострочені видачі, create() + write() видачі.

### Що довелось виправити вручну

1. У завданні сказано "tree views", але в Odoo 19 тег називається list. Використано <list>.
2. Команди PowerShell 5 з Set-Content -Encoding utf8 створили файли з BOM, через що Odoo не читав маніфест (попередження "Missing author key"). Виправлено перезаписом у UTF-8 без BOM.
3. Odoo брав застарілу копію library_rental з server\addons (вона стояла раніше в addons_path). Виправлено порядком шляхів: C:\odoo_custom першим.
4. Демо-дані покладено в data/, а не в demo/, бо базу створено з --without-demo=all (файли demo/ не завантажуються). Записи в data/ мають noupdate="1".
5. Ліміти ondelete: AI запропонував restrict, але поведінку перевірено вручну спробою видалення книги.

## Встановлення

1. Додати C:\odoo_custom до addons_path в odoo.conf.
2. Оновити список застосунків (режим розробника) і встановити Library Rental.
3. Скріншоти: screenshot_installed.png, screenshot_ondelete_restrict.png, screenshot_orm_queries.png.