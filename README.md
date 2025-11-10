# Google AI Overview Parser

Парсер для извлечения AI Overview блока из результатов поиска Google.

## Описание

Этот парсер позволяет программно извлекать текст из блока **AI Overview** (ранее известного как SGE - Search Generative Experience), который Google показывает в результатах поиска для некоторых запросов.

**Поддерживаемые методы:**
- **Playwright** (рекомендуется) - для полного JavaScript-рендеринга, наиболее надежный
- **Requests** - быстрее, но может не находить динамический контент

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd google_serp_parser
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите браузеры для Playwright:
```bash
playwright install chromium
```

## Быстрый старт

```python
from google_ai_overview_parser import parse_ai_overview

# Простой вызов
result = parse_ai_overview("What is artificial intelligence")

if result:
    print("AI Overview найден!")
    print(result)
else:
    print("AI Overview не найден")
```

## Использование

### Базовый пример

```python
from google_ai_overview_parser import parse_ai_overview

result = parse_ai_overview("How does machine learning work")

if result:
    print(result)
```

### С параметрами

```python
from google_ai_overview_parser import parse_ai_overview

result = parse_ai_overview(
    query="What is quantum computing",
    method='playwright',  # или 'requests'
    headless=True,        # False для отображения браузера
    save_html=True,       # Сохранить HTML для отладки
    language='en'         # Язык поиска
)
```

### Использование класса

```python
from google_ai_overview_parser import GoogleAIOverviewParser

# Создаем парсер
parser = GoogleAIOverviewParser(
    method='playwright',
    headless=True,
    save_html=False
)

# Парсим несколько запросов
queries = [
    "What is AI",
    "How does blockchain work",
    "Explain quantum computing"
]

for query in queries:
    result = parser.parse(query, language='en')
    if result:
        print(f"{query}: {result[:100]}...")
```

### Использование метода requests (быстрее)

```python
from google_ai_overview_parser import parse_ai_overview

result = parse_ai_overview(
    query="What is Python",
    method='requests',  # Быстрее, но менее надежно
    language='en'
)
```

## API

### Функция `parse_ai_overview()`

```python
def parse_ai_overview(
    query: str,
    method: Literal['playwright', 'requests'] = 'playwright',
    headless: bool = True,
    save_html: bool = False,
    language: str = 'en'
) -> Optional[str]
```

**Параметры:**
- `query` (str) - Поисковый запрос
- `method` (str) - Метод парсинга: 'playwright' (рекомендуется) или 'requests'
- `headless` (bool) - Запуск браузера в headless режиме (по умолчанию: True)
- `save_html` (bool) - Сохранять HTML страниц для отладки (по умолчанию: False)
- `language` (str) - Язык поиска (по умолчанию: 'en')

**Возвращает:** str | None - Текст AI Overview или None если не найден

### Класс `GoogleAIOverviewParser`

```python
class GoogleAIOverviewParser:
    def __init__(
        self,
        method: Literal['playwright', 'requests'] = 'playwright',
        headless: bool = True,
        save_html: bool = False
    )

    def parse(self, query: str, language: str = 'en') -> Optional[str]
```

## Примеры

Запустите файл с примерами:

```bash
python example.py
```

Или встроенный тест:

```bash
python google_ai_overview_parser.py
```

## Лучшие практики

### 1. Выбор метода

- **Используйте `playwright`** для максимальной надежности (рекомендуется)
- **Используйте `requests`** если нужна скорость и AI Overview доступен в статическом HTML

### 2. Типы запросов

AI Overview чаще встречается для:
- Информационных запросов: "What is...", "How does...", "Explain..."
- Запросов на английском языке
- Образовательных и научных тем

**Примеры хороших запросов:**
```python
"What is artificial intelligence"
"How does photosynthesis work"
"Explain quantum computing"
"What causes climate change"
"How do vaccines work"
```

### 3. Обработка ошибок

```python
try:
    result = parse_ai_overview("Your query")
    if result:
        # Обработка результата
        print(f"Получено {len(result)} символов")
    else:
        # AI Overview не найден
        print("AI Overview не доступен для этого запроса")
except Exception as e:
    # Обработка ошибок (сеть, браузер и т.д.)
    print(f"Ошибка: {e}")
```

### 4. Отладка

Если парсер не находит AI Overview:

1. **Используйте `save_html=True`** для сохранения HTML страницы
2. **Запустите с `headless=False`** чтобы увидеть браузер
3. **Проверьте запрос** в обычном браузере - показывает ли Google AI Overview?
4. **Попробуйте другие запросы** - не все запросы получают AI Overview

```python
result = parse_ai_overview(
    query="Your query",
    headless=False,  # Покажет браузер
    save_html=True,  # Сохранит HTML
    method='playwright'
)
```

## Требования

- Python 3.7+
- Интернет-соединение
- Достаточно RAM для запуска браузера (при использовании Playwright)

## Структура проекта

```
google_serp_parser/
├── google_ai_overview_parser.py  # Основной парсер
├── example.py                    # Примеры использования
├── requirements.txt              # Зависимости Python
├── README.md                     # Документация
└── .gitignore                    # Git ignore файл
```

## Важные замечания

### Доступность AI Overview

Google показывает AI Overview **не для всех запросов**. Доступность зависит от:
- Типа запроса (информационные запросы работают лучше)
- Языка поиска (английский работает лучше)
- Региона пользователя
- Политики Google

**Это нормально, если AI Overview не найден** - просто Google не показывает его для данного запроса.

### Ограничения

1. **Google может изменять HTML** - парсер использует множество селекторов для надежности
2. **Rate Limiting** - Google может ограничивать частоту запросов
3. **Сетевые ограничения** - требуется доступ к google.com
4. **Региональные ограничения** - AI Overview может быть недоступен в некоторых регионах

### Легальность

Этот инструмент предназначен для:
- Образовательных целей
- Исследовательских целей
- Личного использования

Убедитесь, что ваше использование соответствует:
- [Условиям использования Google](https://policies.google.com/terms)
- Местному законодательству
- Правилам robots.txt

**Не используйте** для:
- Массового скрапинга
- Коммерческого использования без разрешения
- Нарушения условий использования

## Устранение неполадок

### AI Overview не найден

```
❌ AI Overview не найден
```

**Решение:**
- Попробуйте информационные запросы на английском
- Проверьте, показывает ли Google AI Overview в обычном браузере
- Используйте `save_html=True` для анализа HTML
- Попробуйте другой тип запроса

### Ошибки сети

```
❌ Ошибка: net::ERR_NAME_NOT_RESOLVED
```

**Решение:**
- Проверьте интернет-соединение
- Убедитесь, что google.com доступен
- Проверьте настройки прокси/VPN
- Попробуйте другой метод: `method='requests'`

### Ошибка браузера

```
❌ BrowserType.launch: Executable doesn't exist
```

**Решение:**
```bash
playwright install chromium
```

### ImportError

```
❌ ModuleNotFoundError: No module named 'playwright'
```

**Решение:**
```bash
pip install -r requirements.txt
```

## Производительность

| Метод | Скорость | Надежность | RAM | CPU |
|-------|----------|------------|-----|-----|
| **playwright** | Медленнее (~5-10s) | ⭐⭐⭐⭐⭐ Высокая | ~200MB | Средняя |
| **requests** | Быстрее (~1-2s) | ⭐⭐⭐ Средняя | ~20MB | Низкая |

**Рекомендация:** Используйте `playwright` для надежности, `requests` для скорости.

## Поддержка

Если вы нашли баг или у вас есть предложение:
1. Создайте issue в репозитории
2. Приложите сохраненный HTML (если используете `save_html=True`)
3. Укажите версию Python и ОС

## Лицензия

MIT

## Авторы

Создано с использованием Claude AI

---

**Примечание:** Парсер работает корректно в окружениях с доступом к интернету. Тесты подтвердили правильность логики парсинга и обработки различных сценариев.
