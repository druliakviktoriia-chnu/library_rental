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


## Практичне заняття 3: бізнес-логіка

### Параметри

- Термін видачі: 14 днів (константа LOAN_PERIOD_DAYS).
- Ставка штрафу: 5 грн за день прострочення (константа FINE_PER_DAY).
- Обидві величини задані константами на початку models/loan.py і використовуються лише через них, не зашиті в кількох місцях.

### Обчислювані поля

- due_date: compute + store=True, @api.depends('loan_date'), значення loan_date + 14 днів.
- fine_amount: compute + store=True, @api.depends('return_date', 'due_date'). Рахується лише якщо return_date заповнено і воно пізніше за due_date: днів прострочення * 5. В інших випадках 0.
- is_overdue: compute БЕЗ store, @api.depends('state', 'due_date'). Істина для активних видач з due_date раніше за сьогодні. Використовується лише для червоного підсвічування рядків у списку (decoration-danger).

### onchange

@api.onchange('copy_id') лише повертає попередження (warning), якщо вибраний примірник уже має активну видачу. Збереження він не блокує: це тільки підказка в UI.

### Обмеження @api.constrains

1. Один примірник не може мати дві активні видачі одночасно (copy_id, state). Запобігає ситуації, коли один фізичний примірник записаний одразу на двох читачів. Пошук конфліктів явно виключає поточний запис (id != loan.id), інакше кожна активна видача конфліктувала б сама з собою.
2. due_date має бути пізніше loan_date (loan_date, due_date). Запобігає видачі з нелогічним терміном.
3. return_date, якщо задано, не може бути раніше loan_date (loan_date, return_date). Запобігає даті повернення до дати видачі.

У всіх трьох випадках піднімається ValidationError з повідомленням українською.

### Що згенерував AI

models/loan.py цілком (compute-методи, onchange, три constrains) і оновлений loan_views.xml (колонки Due Date і Fine, підсвічування прострочених видач).

### Що перевірено і виправлено вручну

1. Перевірено @api.depends вручну: fine_amount залежить від двох полів (return_date і due_date), обидва перелічені (типова помилка AI: залишити лише одне з них). Результат перевірено на записах: INV-101 з Loan Date Sep 1 і Return Date Sep 20 має Due Date Sep 15 і Fine 25.0 (5 днів * 5 грн), а видача, повернена до терміну, має Fine 0.0.
2. Перевірено, що store=True стоїть на due_date і fine_amount, а is_overdue навмисно без store.
3. Перевірено, що метод заборони дублювання виключає self.id, а onchange повертає лише warning і не піднімає ValidationError.
4. Демо-дані (data/library_data.xml) містили значення due_date для обчислюваного поля. Їх видалено, бо тепер due_date рахується з loan_date.

Скріншот: screenshot_fine_amount.png (форма видачі зі штрафом 25.0).