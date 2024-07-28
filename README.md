# Проект парсинга pep

### Запуск парсера
1. Клонируйте рекозиторий командой `git clone git@github.com:r1kenpy/bs4_parser_pep.git`;
2. Перейдите в папку bs4_parser_pep `cd bs4_parser_pep`;
3. Установите виртуальное окружение для Linux или MacOS `python3 -m venv vevn`, для Windows `python -m venv vevn`;
4. Активируйте виртуальное окружение для Linux или MacOS `source venv/bin/activate`, для Windows `source venv/Scripts/activate`;
5. Установите зависимости `pip install -r requirements.txt`;
6. Чтобы посмотреть доступные команды парсера введите `python src/main.py -h`.

### Доступные функции
Для запуска парсера нужно указать обязательный агрумент(positional arguments) `python src/main.py [positional arguments] [optional arguments]`. 

Обязательные аргументы:
- аргумент `download` - скачивания последней версии документации;
- аргумент `latest-versions` - вывод в консоль или сохранение в отдельный файл ссылок на документацию, версию и статус Python;
- аргумент `whats-new` - вывод в консоль или сохранение в отдельный файл ссылок на обновления Python;
- аргумент `pep` - сверки статусов pep на общей странице и на cтранице конкретного pep.

Так же есть необязательные(optional arguments) аргументы: 
- `-c, --clear-cache`- Очистка кеша;
- `-o {pretty,file}` или  `--output {pretty,file}` - Дополнительные способы вывода данных. Доступен только `latest-versions` и `whats-new`.
  - `pretty` - вывод в таблицу в консоле;
  - `file` - создается файл с результатом парсинга.

Автор [Молчанов Владимир](https://t.me/r1ken0)