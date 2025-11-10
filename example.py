#!/usr/bin/env python3
"""
Примеры использования Google AI Overview Parser
"""

from google_ai_overview_parser import parse_ai_overview, GoogleAIOverviewParser


def example_1_simple():
    """Простой пример использования"""
    print("=" * 80)
    print("Пример 1: Простое использование")
    print("=" * 80)

    query = "What is machine learning"
    result = parse_ai_overview(query)

    if result:
        print(f"\n✅ AI Overview найден для запроса '{query}':\n")
        print(result)
    else:
        print(f"\n❌ AI Overview не найден для запроса '{query}'")

    print("\n")


def example_2_with_options():
    """Пример с дополнительными опциями"""
    print("=" * 80)
    print("Пример 2: С дополнительными опциями")
    print("=" * 80)

    query = "How does blockchain work"

    # С сохранением HTML для анализа
    result = parse_ai_overview(
        query=query,
        method='playwright',  # Используем Playwright
        headless=True,        # Headless режим
        save_html=True,       # Сохранить HTML
        language='en'         # Английский язык
    )

    if result:
        print(f"\n✅ AI Overview найден (длина: {len(result)} символов):\n")
        print(result[:300] + "..." if len(result) > 300 else result)
    else:
        print(f"\n❌ AI Overview не найден")

    print("\n")


def example_3_multiple_queries():
    """Пример с множественными запросами"""
    print("=" * 80)
    print("Пример 3: Обработка нескольких запросов")
    print("=" * 80)

    queries = [
        "What is artificial intelligence",
        "How does photosynthesis work",
        "Explain quantum computing",
        "What causes climate change"
    ]

    # Создаем парсер один раз
    parser = GoogleAIOverviewParser(
        method='playwright',
        headless=True,
        save_html=False
    )

    results = {}

    for query in queries:
        print(f"\nОбрабатываю: {query}")
        result = parser.parse(query, language='en')

        results[query] = result

        if result:
            print(f"  ✅ Найдено ({len(result)} символов)")
        else:
            print(f"  ❌ Не найдено")

    # Выводим результаты
    print("\n" + "=" * 80)
    print("Результаты:")
    print("=" * 80)

    for query, result in results.items():
        print(f"\n📝 {query}")
        if result:
            print(f"   {result[:150]}...")
        else:
            print(f"   Не найдено")

    print("\n")


def example_4_requests_method():
    """Пример использования метода requests (быстрее, но менее надежно)"""
    print("=" * 80)
    print("Пример 4: Использование метода requests")
    print("=" * 80)

    query = "What is Python programming"

    # Используем requests вместо Playwright (быстрее, но может не найти JS-контент)
    result = parse_ai_overview(
        query=query,
        method='requests',  # Используем requests + BeautifulSoup
        save_html=False,
        language='en'
    )

    if result:
        print(f"\n✅ AI Overview найден:\n")
        print(result)
    else:
        print(f"\n❌ AI Overview не найден")
        print("\nПримечание: Метод 'requests' может не находить AI Overview,")
        print("если он рендерится через JavaScript. Попробуйте метод 'playwright'.")

    print("\n")


def example_5_error_handling():
    """Пример с обработкой ошибок"""
    print("=" * 80)
    print("Пример 5: Обработка ошибок")
    print("=" * 80)

    query = "test query"

    try:
        result = parse_ai_overview(
            query=query,
            method='playwright',
            headless=True,
            save_html=False,
            language='en'
        )

        if result:
            print(f"\n✅ Результат получен")
            print(f"Длина текста: {len(result)} символов")
            print(f"Превью: {result[:200]}...")
        else:
            print(f"\n⚠️  AI Overview не найден для запроса '{query}'")
            print("\nВозможные причины:")
            print("  • AI Overview недоступен для данного запроса")
            print("  • Ограничения по региону")
            print("  • Google изменил структуру страницы")
            print("  • Нет интернет-соединения")

    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("\nПроверьте:")
        print("  • Интернет-соединение")
        print("  • Установлены ли все зависимости (playwright install chromium)")

    print("\n")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "Google AI Overview Parser - Примеры" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    print("Внимание: Для работы парсера требуется интернет-соединение!")
    print("Если вы видите ошибки сети - это нормально в изолированных окружениях.")
    print("\n")

    # Запускаем примеры
    example_1_simple()
    # example_2_with_options()
    # example_3_multiple_queries()
    # example_4_requests_method()
    # example_5_error_handling()

    print("=" * 80)
    print("Примеры завершены!")
    print("=" * 80)
    print("\nДля использования в реальных условиях:")
    print("  1. Убедитесь, что есть интернет-соединение")
    print("  2. Используйте метод 'playwright' для надежности")
    print("  3. Попробуйте информационные запросы на английском")
    print("  4. При проблемах используйте save_html=True для отладки")
    print("\n")
