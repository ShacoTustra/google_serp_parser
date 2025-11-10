# Google AI Overview Parser (Python)

Парсер для извлечения AI Overview блока из результатов поиска Google с использованием Playwright для Python.

## Описание

Этот парсер позволяет программно извлекать текст из блока AI Overview (ранее известного как SGE - Search Generative Experience), который Google показывает в результатах поиска. Парсер использует Playwright для автоматизации браузера и поддерживает различные конфигурации.

## Установка

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Установите браузеры для Playwright

```bash
playwright install chromium
```

Если нужны системные зависимости (Linux):

```bash
playwright install --with-deps chromium
```

## Использование

### Базовый пример

```python
from parser import parse_ai_overview

# Простой вызов
result = parse_ai_overview('What is artificial intelligence?')

if result.found:
    print(f"AI Overview: {result.text}")
    print(f"Sources: {result.sources}")
else:
    print("AI Overview не найден")
```

### С настройками

```python
from parser import parse_ai_overview

result = parse_ai_overview(
    query='How does machine learning work?',
    headless=False,        # Показать браузер
    timeout=30000,         # Таймаут 30 секунд
    language='en',         # Язык поиска
    user_agent='custom-ua' # Пользовательский User Agent
)

print(result.text)
```

### Использование класса парсера

```python
from parser import GoogleAIOverviewParser

# Создаем экземпляр парсера
parser = GoogleAIOverviewParser(
    headless=True,
    timeout=30000,
    language='en'
)

# Парсим несколько запросов
queries = [
    'What is AI?',
    'How does blockchain work?',
    'Explain quantum computing'
]

for query in queries:
    result = parser.parse(query)
    if result.found:
        print(f"\n{query}:")
        print(f"{result.text[:200]}...")
```

### Работа с результатом

```python
from parser import parse_ai_overview

result = parse_ai_overview('What is climate change?')

# Получить данные как словарь
data = result.to_dict()
print(data)

# Доступ к атрибутам
print(f"Текст: {result.text}")
print(f"Найден: {result.found}")
print(f"Запрос: {result.query}")
print(f"Источники: {result.sources}")
print(f"Время: {result.timestamp}")
```

## API

### Функция `parse_ai_overview()`

```python
def parse_ai_overview(
    query: str,
    headless: bool = True,
    timeout: int = 30000,
    user_agent: Optional[str] = None,
    language: str = 'en'
) -> AIOverviewResult
```

**Параметры:**

- `query` (str) - Поисковый запрос
- `headless` (bool) - Запускать браузер в headless режиме (по умолчанию: True)
- `timeout` (int) - Таймаут для операций в миллисекундах (по умолчанию: 30000)
- `user_agent` (str, optional) - Пользовательский User Agent
- `language` (str) - Язык поиска (по умолчанию: 'en')

**Возвращает:** `AIOverviewResult`

### Класс `GoogleAIOverviewParser`

```python
class GoogleAIOverviewParser:
    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
        language: str = 'en'
    )

    def parse(self, query: str) -> AIOverviewResult
```

### Класс `AIOverviewResult`

```python
@dataclass
class AIOverviewResult:
    text: str                      # Текст AI Overview
    found: bool                    # Найден ли AI Overview
    query: str                     # Использованный запрос
    sources: Optional[List[str]]   # Источники (если доступны)
    timestamp: Optional[str]       # Временная метка

    def to_dict(self) -> Dict[str, Any]
```

## Запуск примеров

### Базовый тест

```bash
python3 parser.py
```

### Примеры использования

```bash
python3 example.py
```

### Тест с mock данными

```bash
python3 test_parser_mock.py
```

## Структура проекта

```
google_serp_parser/
├── parser.py              # Основной парсер
├── example.py             # Примеры использования
├── test_parser_mock.py    # Тест с mock HTML
├── requirements.txt       # Python зависимости
├── README_PYTHON.md       # Документация Python версии
└── README.md              # Общая документация
```

## Важные замечания

### 1. Доступность AI Overview

AI Overview может быть недоступен для всех запросов или регионов. Это зависит от:
- Типа запроса (информационные запросы работают лучше)
- Географического региона
- Языка поиска
- Политики Google

### 2. Селекторы

Парсер использует множество селекторов для поиска AI Overview:

- `div[data-attrid="SGEAIOverview"]` - основной селектор
- `div[data-attrid="AIOverview"]` - альтернативный
- `div[jsname="yp1CPe"]` - JavaScript имя контейнера
- И другие...

Google может изменять HTML структуру. Парсер автоматически пробует разные варианты.

### 3. Rate Limiting

Google может ограничивать частоту запросов. Рекомендации:

- Добавляйте задержки между запросами (3-5 секунд)
- Используйте разные User Agents
- Не делайте слишком много запросов подряд

### 4. Headless режим

В некоторых случаях Google может определять headless браузеры. Если возникают проблемы:

```python
result = parse_ai_overview(query, headless=False)
```

### 5. Отладка

Для отладки запустите с видимым браузером:

```python
parser = GoogleAIOverviewParser(headless=False, timeout=60000)
result = parser.parse('your query')
```

Браузер останется открытым на 5 секунд если AI Overview не найден.

## Примеры запросов, которые обычно имеют AI Overview

```python
queries = [
    'What is artificial intelligence?',
    'How does machine learning work?',
    'Explain quantum computing',
    'What is climate change?',
    'How does blockchain work?',
    'What is the theory of relativity?',
    'How do vaccines work?',
    'What is photosynthesis?',
]
```

## Устранение неполадок

### Браузер не запускается

```bash
# Переустановите браузеры
playwright install --force chromium
```

### AI Overview не найден

1. Проверьте, что запрос на английском языке (или измените `language`)
2. Попробуйте информационные запросы ("What is...", "How does...")
3. Запустите с `headless=False` для визуальной проверки
4. Проверьте доступ к интернету

### Timeout ошибки

```python
# Увеличьте таймаут
result = parse_ai_overview(query, timeout=60000)  # 60 секунд
```

### Проблемы с сетью

```python
try:
    result = parse_ai_overview(query)
except Exception as e:
    print(f"Error: {e}")
```

## Требования к системе

- Python 3.7+
- Playwright 1.40.0+
- Интернет соединение
- ~200 MB для браузера Chromium

## Производительность

- Один запрос: ~5-10 секунд
- С кешированием браузера: ~3-5 секунд
- Зависит от скорости интернета

## Лицензия

MIT

## Примечания

Этот инструмент предназначен для образовательных и исследовательских целей. Убедитесь, что ваше использование соответствует условиям использования Google.

## Поддержка

Если AI Overview не находится:
1. Проверьте логи (парсер выводит подробную информацию)
2. Запустите mock-тест: `python3 test_parser_mock.py`
3. Попробуйте разные запросы
4. Проверьте регион и язык

## Примеры вывода

### Успешный результат

```
Query: What is artificial intelligence?

✅ AI Overview found!

Text length: 450 characters

AI Overview Text:
--------------------------------------------------------------------------------
Artificial Intelligence (AI) is a branch of computer science that aims to
create intelligent machines that work and react like humans. AI systems can
perform tasks such as visual perception, speech recognition, decision-making,
and language translation...
--------------------------------------------------------------------------------

Sources (3):
  1. https://en.wikipedia.org/wiki/Artificial_intelligence
  2. https://www.ibm.com/cloud/learn/what-is-artificial-intelligence
  3. https://www.britannica.com/technology/artificial-intelligence

Timestamp: 2025-11-10T12:00:00.000000
```

### Когда не найден

```
Query: some random query

❌ AI Overview not found for this query
Note: AI Overview may not be available for all queries or regions
```
