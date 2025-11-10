#!/usr/bin/env python3
"""Тестирование различных способов решения DNS проблемы в Playwright"""

import sys
from playwright.sync_api import sync_playwright
import time

def test_chromium_with_dns_args():
    """Тест 1: Chromium с дополнительными DNS аргументами"""
    print("\n" + "="*80)
    print("ТЕСТ 1: Chromium с DNS аргументами")
    print("="*80)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE localhost',
                ]
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()

            print("Попытка загрузить google.com...")
            page.goto('https://www.google.com', timeout=15000)

            title = page.title()
            print(f"✅ Успех! Заголовок: {title}")

            browser.close()
            return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_firefox():
    """Тест 2: Firefox вместо Chromium"""
    print("\n" + "="*80)
    print("ТЕСТ 2: Firefox")
    print("="*80)

    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(
                headless=True,
                firefox_user_prefs={
                    'network.dns.disableIPv6': False,
                }
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()

            print("Попытка загрузить google.com...")
            page.goto('https://www.google.com', timeout=15000)

            title = page.title()
            print(f"✅ Успех! Заголовок: {title}")

            browser.close()
            return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_with_ip_address():
    """Тест 3: Использование IP адреса напрямую"""
    print("\n" + "="*80)
    print("ТЕСТ 3: Прямой IP адрес")
    print("="*80)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()

            # Получаем IP Google через curl
            import subprocess
            result = subprocess.run(
                ['curl', '-s', '-I', 'https://www.google.com'],
                capture_output=True,
                text=True,
                timeout=10
            )

            print(f"Curl статус код: {result.returncode}")
            if result.returncode == 0:
                print("✓ Curl работает!")

            # Пробуем через HTTP (не HTTPS)
            print("\nПопытка загрузить через HTTP...")
            page.goto('http://www.google.com', timeout=15000, wait_until='domcontentloaded')

            title = page.title()
            print(f"✅ Успех! Заголовок: {title}")

            browser.close()
            return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_with_simple_site():
    """Тест 4: Простой сайт для проверки базовой связи"""
    print("\n" + "="*80)
    print("ТЕСТ 4: Простой тестовый сайт")
    print("="*80)

    sites = [
        'http://example.com',
        'https://httpbin.org/html',
    ]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            context = browser.new_context()
            page = context.new_page()

            for site in sites:
                try:
                    print(f"\nПопытка загрузить {site}...")
                    page.goto(site, timeout=10000)
                    title = page.title()
                    print(f"✅ Успех! Заголовок: {title}")

                    browser.close()
                    return True
                except Exception as e:
                    print(f"❌ Ошибка для {site}: {e}")
                    continue

            browser.close()
            return False

    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False


def test_with_localhost_proxy():
    """Тест 5: Через локальный HTTP прокси"""
    print("\n" + "="*80)
    print("ТЕСТ 5: Через HTTP прокси (curl)")
    print("="*80)

    # Запускаем простой HTTP прокси на базе curl
    import subprocess
    import threading

    print("Информация: Этот тест использует subprocess для создания прокси")
    print("В данном окружении может не работать из-за ограничений")

    return False


if __name__ == '__main__':
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "ТЕСТИРОВАНИЕ DNS В PLAYWRIGHT" + " "*28 + "║")
    print("╚" + "="*78 + "╝")

    tests = [
        ("Chromium с DNS аргументами", test_chromium_with_dns_args),
        ("Firefox", test_firefox),
        ("Прямой IP/HTTP", test_with_ip_address),
        ("Простой сайт", test_with_simple_site),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))

            if success:
                print(f"\n🎉 УСПЕХ! Тест '{name}' прошел!")
                print("Этот метод можно использовать для парсера!")
                break

        except KeyboardInterrupt:
            print("\n\nПрервано пользователем")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Критическая ошибка в тесте '{name}': {e}")
            results.append((name, False))

    print("\n" + "="*80)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("="*80)

    for name, success in results:
        status = "✅ РАБОТАЕТ" if success else "❌ НЕ РАБОТАЕТ"
        print(f"{name:40} {status}")

    print("\n" + "="*80)

    if any(success for _, success in results):
        print("✅ Найден работающий метод!")
    else:
        print("❌ Ни один метод не сработал")
        print("\nРекомендации:")
        print("1. Проверьте сетевые настройки окружения")
        print("2. Возможно требуется настройка DNS в системе")
        print("3. Рассмотрите использование внешнего прокси")
