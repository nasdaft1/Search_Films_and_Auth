# Описание

## Элементы скрипта
- `Worker` - класс для хранения состояния и взаимодействия с базами.
- `UpdatesExtractor(Worker)` - класс для взаимодействия с postgres и получения записей, которые обновились.
- `MoviesExtractor(Worker)` - класс для взаимодействия с postgres и получения фильмов, которые нужно обновить.
- `UpdatesExtractorsManager` - класс для объединения `UpdatesExtractor` в одну сущность, чтобы выполнять одинаковые 
команды сразу со всеми `UpdatesExtractor`, а не отдельно.
- `Extractor` - класс для объединения `MoviesExtractor` и `UpdatesExtractorsManager`, чтобы сократить код и разделить 
логику.
- `PostgresController` - класс для создания соединения с postgres и отправки запросов с функцией backoff.
- `ElasticsearchController` - класс для отправки запросов в elasticsearch с функцией backoff.
- `backoff` - декоратор для повторного выполнения функции через некоторое время, если возникла ошибка.

## Логика работы
- Из таблиц `genre`, `person`, `film_work`, по очереди, с учётом сохранённого состояния получаем по N записей, 
которые были обновлены.
- Пока есть записи, которые нужно обновить, выполняется следующее:
  - Из таблицы `film_work` получаем N записей, которые нужно обновить.
    - Выполняется подзапрос на получение id N записей на основе сохранённого состояния и фильтра с записями, 
    которые были обновлены.
    - Выполняется запрос на получение полной информации по фильмам из первого запроса в формате схемы индекса 
    Elasticsearch.
  - Выполняется запрос в Elasticsearch для обновления информации.
  - Сохраняется последний обновлённый фильм на случай прерывания скрипта.
- Сохраняется состояние с последними используемыми для обновления записями в каждой таблице, чтобы следующий цикл их 
пропускал.

## Комментарии
- Задание и реализация не учитывают изменение связей между таблицами. 
- Скрипт хранит состояние обновлённых записей на основе времени изменения и идентификатора последней обновлённой записи, 
а состояние обновлённых фильмов хранится на основе состояний трёх таблиц и id последнего обновлённого фильма.
- Скрипт получает список фильмов, которые нужно обновить, в подзапросе, а не отдельным запросом, 
так как в отдельном запросе нет смысла, а если пытаться получить идентификаторы фильмов в моменте получения обновлённых 
записей, то сложно реализовать итерацию N-го количества фильмов, удаление дублей, а так же сохранение состояния.
- Использование `fechmany` вместо `fetchall` считаю неоправданным:
  - У меня не применяется OFFSET.
  - Для запросов списка обновлённых записей в таблицах `genre`, `person`, `film_work` нужно будет либо реализовывать 
  генераторы, возвращая yield внутри контекстного менеджера курсора, либо запоминать курсор для каждой таблице где-то 
  отдельно. Оба варианта усложняют использование `backoff`. Нужно будет отслеживать ошибки, и во время их возникновения 
  менять в запросе WHERE, чтобы не получать всё ещё раз, либо добавлять OFFSET. Мне кажется, всё это значительно 
  усложнит понимание кода.
  - При запросе фильмов, которые нужно обновить, используется подзапрос идентификаторов с указанием LIMIT, а основной 
  запрос выполняется без него. Если делить это на два отдельных запроса, то это повышает нагрузку на клиента и сеть, 
  в связи с необходимостью сначала получать идентификаторы, а потом их передать. Применение лимита во втором запросе, 
  а не в первом, тоже кажется менее выгодным по производительности в связи с неопределённым количеством фильмов и 
  связанных записей, а в первом подзапросе получаются только идентификаторы.
- Сократил дублирование кода, добавив `UpdatesExtractorsManager`. Теперь даже можно просто в конфиге добавлять 
дополнительные таблицы, в которых нужно следить за обновлениями.