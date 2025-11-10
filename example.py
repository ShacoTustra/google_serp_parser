"""
Примеры использования Google AI Overview Parser
"""

from parser import parse_ai_overview, GoogleAIOverviewParser


def example_1_basic():
    """Пример 1: Базовое использование"""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)

    query = "What is artificial intelligence?"
    print(f"\nQuery: {query}\n")

    result = parse_ai_overview(query, headless=True)

    if result.found:
        print("✅ AI Overview found!")
        print(f"\nText length: {len(result.text)} characters")
        print("\nAI Overview Text:")
        print("-" * 80)
        print(result.text)
        print("-" * 80)

        if result.sources:
            print(f"\nSources ({len(result.sources)}):")
            for i, source in enumerate(result.sources, 1):
                print(f"  {i}. {source}")

        print(f"\nTimestamp: {result.timestamp}")
    else:
        print("❌ AI Overview not found for this query")
        print("Note: AI Overview may not be available for all queries or regions")


def example_2_multiple_queries():
    """Пример 2: Несколько запросов"""
    print("\n\n" + "=" * 80)
    print("Example 2: Multiple Queries")
    print("=" * 80)

    queries = [
        "How does machine learning work?",
        "What is quantum computing?",
        "Explain blockchain technology"
    ]

    parser = GoogleAIOverviewParser(headless=True, timeout=30000)

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 80)

        result = parser.parse(query)

        if result.found:
            print(f"✅ Found ({len(result.text)} chars)")
            print(f"Preview: {result.text[:200]}...")
        else:
            print("❌ Not found")


def example_3_custom_settings():
    """Пример 3: С настройками"""
    print("\n\n" + "=" * 80)
    print("Example 3: Custom Settings")
    print("=" * 80)

    query = "What is Python programming language?"
    print(f"\nQuery: {query}\n")

    # Используем не-headless режим для отладки
    result = parse_ai_overview(
        query=query,
        headless=True,  # Установите False чтобы увидеть браузер
        timeout=30000,
        language='en'
    )

    if result.found:
        print("✅ AI Overview found!")
        print(f"\n{result.text[:300]}...")
    else:
        print("❌ AI Overview not found")


def example_4_result_dict():
    """Пример 4: Работа с результатом как словарем"""
    print("\n\n" + "=" * 80)
    print("Example 4: Result as Dictionary")
    print("=" * 80)

    query = "What is climate change?"
    print(f"\nQuery: {query}\n")

    result = parse_ai_overview(query)

    # Преобразуем в словарь
    result_dict = result.to_dict()

    print("Result as dictionary:")
    for key, value in result_dict.items():
        if key == 'text' and value:
            print(f"  {key}: {value[:100]}... ({len(value)} chars)")
        elif key == 'sources' and value:
            print(f"  {key}: {len(value)} sources")
        else:
            print(f"  {key}: {value}")


if __name__ == '__main__':
    # Запускаем все примеры
    try:
        example_1_basic()
        # example_2_multiple_queries()
        # example_3_custom_settings()
        # example_4_result_dict()

        print("\n\n" + "=" * 80)
        print("Examples completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
