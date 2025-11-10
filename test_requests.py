#!/usr/bin/env python3
"""Тест парсера с методом requests"""

from google_ai_overview_parser import parse_ai_overview

print("=" * 80)
print("Тест парсера с методом requests")
print("=" * 80)

queries = [
    "What is artificial intelligence",
    "How does machine learning work",
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Запрос: {query}")
    print('='*80)

    result = parse_ai_overview(
        query=query,
        method='requests',  # Используем requests вместо playwright
        save_html=True,     # Сохраним HTML для анализа
        language='en'
    )

    if result:
        print(f"\n✅ AI Overview найден! Длина: {len(result)} символов\n")
        print("Первые 500 символов:")
        print("-" * 80)
        print(result[:500])
        print("-" * 80)
        if len(result) > 500:
            print(f"\n... и еще {len(result) - 500} символов")
    else:
        print("\n❌ AI Overview не найден")

    print("\n")

    # Пауза между запросами
    import time
    time.sleep(2)

print("=" * 80)
print("Тест завершен!")
print("=" * 80)
