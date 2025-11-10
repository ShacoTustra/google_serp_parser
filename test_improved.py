#!/usr/bin/env python3
"""Улучшенный тест с более реалистичными настройками"""

import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_google_with_improved_headers(query):
    """Тест с улучшенными headers и cookies"""

    encoded_query = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded_query}&hl=en'

    # Более реалистичные headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    # Cookies для более реалистичной сессии
    cookies = {
        'CONSENT': 'YES+',
        'NID': '511=test'
    }

    print(f"\n{'='*80}")
    print(f"Запрос: {query}")
    print(f"URL: {url}")
    print('='*80)

    try:
        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)

        response = session.get(url, timeout=15)
        response.raise_for_status()

        print(f"✓ Статус: {response.status_code}")
        print(f"✓ Размер ответа: {len(response.text)} символов")

        # Сохраняем HTML
        filename = f'google_improved_{query[:30].replace(" ", "_")}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ HTML сохранен в: {filename}")

        # Проверяем наличие антибот защиты
        if 'var o9=function' in response.text or 'var AA=function' in response.text:
            print("\n⚠️  Обнаружена антибот-защита Google!")
            print("Google детектирует автоматические запросы.")
            return None

        # Ищем результаты поиска
        soup = BeautifulSoup(response.text, 'lxml')

        # Проверяем основные элементы страницы
        search_div = soup.find('div', {'id': 'search'})
        if search_div:
            print("✓ Найден основной div с результатами поиска")
        else:
            print("✗ Основной div с результатами не найден")

        # Ищем AI Overview селекторы
        ai_selectors = [
            'div[data-attrid*="AI"]',
            'div[data-attrid="SGEAIOverview"]',
            'div[data-attrid="AIOverview"]',
        ]

        for selector in ai_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n✓ Найден элемент с селектором: {selector}")
                for elem in elements[:1]:
                    text = elem.get_text(separator=' ', strip=True)
                    if len(text) > 100:
                        print(f"\nТекст ({len(text)} символов):")
                        print("-" * 80)
                        print(text[:500])
                        print("-" * 80)
                        return text

        # Проверяем заголовки страницы
        title = soup.find('title')
        if title:
            print(f"\n📄 Заголовок страницы: {title.get_text()}")

        # Ищем знак, что мы получили настоящую страницу результатов
        result_stats = soup.find('div', {'id': 'result-stats'})
        if result_stats:
            print(f"✓ Статистика результатов: {result_stats.get_text()}")

        print("\n❌ AI Overview не найден в результатах")

        # Показываем первые div'ы для анализа
        print("\nПервые 3 div элемента:")
        for i, div in enumerate(soup.find_all('div')[:3], 1):
            attrs = ' '.join([f'{k}={v}' for k, v in (div.attrs.items() if div.attrs else [])])
            print(f"  {i}. <div {attrs[:100]}...")

        return None

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка сети: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("\n" + "="*80)
    print("Улучшенный тест парсера Google AI Overview")
    print("="*80)

    queries = [
        "What is artificial intelligence",
        "Python programming language",
    ]

    for query in queries:
        result = test_google_with_improved_headers(query)
        if result:
            print(f"\n✅ Успешно получен AI Overview!")
            break

    print("\n" + "="*80)
    print("Тест завершен")
    print("="*80)
