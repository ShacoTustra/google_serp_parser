#!/usr/bin/env python3
"""
Гибридный подход: requests для получения HTML + Playwright для парсинга
"""

import requests
from playwright.sync_api import sync_playwright
import urllib.parse
import time

def get_google_page_with_requests(query):
    """Получаем страницу Google через requests"""
    print(f"\n🔍 Получение страницы Google через requests...")

    encoded_query = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded_query}&hl=en'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    cookies = {
        'CONSENT': 'YES+',
    }

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)

        response = session.get(url, timeout=15)
        response.raise_for_status()

        print(f"✓ Статус: {response.status_code}")
        print(f"✓ Размер: {len(response.text)} символов")

        # Сохраняем для анализа
        filename = f'google_hybrid_{int(time.time())}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ Сохранено в: {filename}")

        return response.text, filename

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, None


def parse_with_playwright(html_content, query):
    """Парсим HTML через Playwright"""
    print(f"\n🔎 Парсинг HTML через Playwright...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            context = browser.new_context()
            page = context.new_page()

            # Загружаем HTML напрямую
            page.set_content(html_content, wait_until='domcontentloaded')

            print("✓ HTML загружен в Playwright")

            # Ищем AI Overview
            selectors = [
                'div[data-attrid*="AI"]',
                'div[data-attrid="SGEAIOverview"]',
                'div[data-attrid="AIOverview"]',
                'div[jsname="yp1CPe"]',
            ]

            found = False
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        if text and len(text) > 100:
                            print(f"\n✅ AI Overview найден с селектором: {selector}")
                            print(f"Длина: {len(text)} символов")
                            print("\nПервые 500 символов:")
                            print("-" * 80)
                            print(text[:500])
                            print("-" * 80)

                            browser.close()
                            return text
                except Exception as e:
                    continue

            # Если не нашли, пробуем общий поиск
            print("\n🔎 Пробуем общий поиск по div элементам...")

            divs = page.query_selector_all('div[data-hveid], div[jscontroller]')
            print(f"Найдено {len(divs)} потенциальных блоков")

            for i, div in enumerate(divs[:20]):
                try:
                    text = div.inner_text()
                    if text and 150 < len(text) < 3000:
                        # Проверяем на признаки AI Overview
                        if 'AI' in text or len(text.split('.')) > 3:
                            print(f"\n✓ Потенциальный AI Overview в блоке {i}")
                            print(f"Длина: {len(text)} символов")
                            print(f"Первые 300 символов:\n{text[:300]}...")

                            # Проверяем что это не навигация
                            nav_count = sum(1 for kw in ['Sign in', 'Images', 'Videos'] if kw in text)
                            if nav_count < 2:
                                print("✓ Похоже на контент (не навигация)")
                                browser.close()
                                return text
                except:
                    continue

            print("\n❌ AI Overview не найден")

            # Показываем что вообще на странице
            print("\nПроверка контента страницы:")
            search_div = page.query_selector('div#search')
            if search_div:
                print("✓ Найден div#search (основной контейнер результатов)")
            else:
                print("✗ div#search не найден")

            result_stats = page.query_selector('div#result-stats')
            if result_stats:
                stats_text = result_stats.inner_text()
                print(f"✓ Статистика результатов: {stats_text}")
            else:
                print("✗ Статистика результатов не найдена")

            # Проверяем на антибот
            page_text = page.content()[:1000]
            if 'var o9=function' in page_text or 'var AA=function' in page_text:
                print("\n⚠️  Обнаружена антибот-защита!")

            browser.close()
            return None

    except Exception as e:
        print(f"\n❌ Ошибка Playwright: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("\n" + "="*80)
    print("ГИБРИДНЫЙ ПОДХОД: Requests + Playwright")
    print("="*80)

    queries = [
        "What is artificial intelligence",
        "Python programming language",
    ]

    for query in queries:
        print(f"\n{'='*80}")
        print(f"ЗАПРОС: {query}")
        print('='*80)

        # Шаг 1: Получаем HTML через requests
        html_content, filename = get_google_page_with_requests(query)

        if not html_content:
            print("❌ Не удалось получить HTML")
            continue

        # Шаг 2: Парсим через Playwright
        result = parse_with_playwright(html_content, query)

        if result:
            print(f"\n🎉 УСПЕХ! AI Overview извлечен!")
            return True

        time.sleep(2)

    print("\n" + "="*80)
    print("Тест завершен")
    print("="*80)

    return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
