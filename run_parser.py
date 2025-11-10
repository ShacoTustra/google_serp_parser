#!/usr/bin/env python3
"""
Скрипт для запуска парсера из командной строки
Usage: python3 run_parser.py "Your search query"
"""

import sys
import argparse
from parser import parse_ai_overview


def main():
    parser = argparse.ArgumentParser(
        description='Parse Google AI Overview for a search query'
    )

    parser.add_argument(
        'query',
        type=str,
        help='Search query to parse'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=30000,
        help='Timeout in milliseconds (default: 30000)'
    )

    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='Search language (default: en)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Google AI Overview Parser")
    print("=" * 80)
    print(f"\nQuery: {args.query}")
    print(f"Language: {args.language}")
    print(f"Headless: {not args.no_headless}")
    print(f"Timeout: {args.timeout}ms\n")
    print("-" * 80)

    try:
        result = parse_ai_overview(
            query=args.query,
            headless=not args.no_headless,
            timeout=args.timeout,
            language=args.language
        )

        if result.found:
            print("\n✅ AI Overview найден!\n")
            print(f"Длина текста: {len(result.text)} символов\n")

            if args.verbose or len(result.text) < 500:
                print("Текст AI Overview:")
                print("-" * 80)
                print(result.text)
                print("-" * 80)
            else:
                print("Текст AI Overview (первые 500 символов):")
                print("-" * 80)
                print(result.text[:500] + '...')
                print("-" * 80)
                print(f"\n(Используйте --verbose для полного текста)")

            if result.sources:
                print(f"\n📚 Источники ({len(result.sources)}):")
                for i, source in enumerate(result.sources, 1):
                    print(f"  {i}. {source}")

            print(f"\n⏰ Время: {result.timestamp}")

        else:
            print("\n❌ AI Overview не найден для этого запроса")
            print("\nВозможные причины:")
            print("  • AI Overview недоступен для данного типа запросов")
            print("  • Ограничения по региону или языку")
            print("  • Google изменил структуру страницы")
            print("  • Проблемы с сетевым подключением")
            print("\nПопробуйте:")
            print(f"  • Информационные запросы: 'What is...', 'How does...'")
            print(f"  • Запуск с видимым браузером: --no-headless")
            print(f"  • Другой язык: --language ru")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}\n")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: python3 run_parser.py \"Your search query\"")
        print("Example: python3 run_parser.py \"What is artificial intelligence?\"")
        print("\nFor more options: python3 run_parser.py --help")
        sys.exit(1)

    main()
