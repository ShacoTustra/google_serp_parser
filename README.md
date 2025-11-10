# Google AI Overview Parser

Парсер для извлечения AI Overview блока из результатов поиска Google с использованием Playwright.

## Описание

Этот парсер позволяет программно извлекать текст из блока AI Overview (ранее известного как SGE - Search Generative Experience), который Google показывает в результатах поиска. Парсер использует Playwright для автоматизации браузера и поддерживает различные конфигурации.

## Установка

```bash
npm install
```

После установки необходимо установить браузеры для Playwright:

```bash
npx playwright install chromium
```

## Использование

### Базовый пример

```typescript
import { parseAIOverview } from './src/index';

const result = await parseAIOverview('What is artificial intelligence?');

if (result.found) {
  console.log('AI Overview:', result.text);
  console.log('Sources:', result.metadata?.sources);
} else {
  console.log('AI Overview not found');
}
```

### С настройками

```typescript
import { parseAIOverview } from './src/index';

const result = await parseAIOverview('How does machine learning work?', {
  headless: false,        // Показать браузер
  timeout: 30000,         // Таймаут 30 секунд
  language: 'en',         // Язык поиска
  userAgent: 'custom-ua'  // Пользовательский User Agent
});

console.log(result.text);
```

### Пакетная обработка с переиспользованием браузера

```typescript
import { chromium } from 'playwright';
import { parseAIOverviewWithBrowser } from './src/index';

const browser = await chromium.launch({ headless: true });

const queries = [
  'What is AI?',
  'How does blockchain work?',
  'Explain quantum computing'
];

for (const query of queries) {
  const result = await parseAIOverviewWithBrowser(browser, query);
  console.log(`${query}:`, result.found ? result.text : 'Not found');
}

await browser.close();
```

## API

### `parseAIOverview(query, options?)`

Основная функция для парсинга AI Overview.

**Параметры:**

- `query` (string) - Поисковый запрос
- `options` (ParserOptions, optional) - Опции конфигурации

**Возвращает:** `Promise<AIOverviewResult>`

### `ParserOptions`

```typescript
interface ParserOptions {
  headless?: boolean;      // Headless режим (по умолчанию: true)
  timeout?: number;        // Таймаут в миллисекундах (по умолчанию: 30000)
  userAgent?: string;      // User Agent строка
  language?: string;       // Язык поиска (по умолчанию: 'en')
}
```

### `AIOverviewResult`

```typescript
interface AIOverviewResult {
  text: string;           // Текст AI Overview
  found: boolean;         // Найден ли AI Overview
  query: string;          // Использованный запрос
  metadata?: {
    sources?: string[];   // Источники (если доступны)
    timestamp?: string;   // Временная метка
  };
}
```

### `parseAIOverviewWithBrowser(browser, query, options?)`

Функция для использования с существующим экземпляром браузера.

**Параметры:**

- `browser` (Browser) - Экземпляр браузера Playwright
- `query` (string) - Поисковый запрос
- `options` (Omit<ParserOptions, 'headless'>) - Опции конфигурации (без headless)

**Возвращает:** `Promise<AIOverviewResult>`

## Запуск примеров

### С использованием ts-node

```bash
npm run example
```

### Сборка и запуск

```bash
npm run build
npm start
```

## Важные замечания

1. **Доступность AI Overview**: AI Overview может быть недоступен для всех запросов или регионов. Это зависит от политики Google.

2. **Селекторы**: Google может изменять HTML структуру своих страниц. Парсер использует несколько различных селекторов для максимальной надежности.

3. **Rate Limiting**: Google может ограничивать частоту запросов. Рекомендуется добавлять задержки между запросами при пакетной обработке.

4. **User Agent**: Использование реалистичного User Agent может улучшить надежность парсинга.

5. **Headless режим**: В некоторых случаях Google может определять headless браузеры. Если возникают проблемы, попробуйте использовать `headless: false`.

## Структура проекта

```
google_serp_parser/
├── src/
│   ├── index.ts        # Основной парсер
│   └── example.ts      # Примеры использования
├── dist/               # Скомпилированные файлы (после npm run build)
├── package.json
├── tsconfig.json
└── README.md
```

## Разработка

### Сборка проекта

```bash
npm run build
```

### Тестирование

```bash
npm test
```

## Лицензия

MIT

## Примечания

Этот инструмент предназначен для образовательных и исследовательских целей. Убедитесь, что ваше использование соответствует условиям использования Google.
