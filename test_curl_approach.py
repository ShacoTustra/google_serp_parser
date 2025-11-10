#!/usr/bin/env python3
"""
Подход с использованием curl через subprocess
Мы знаем что curl работает в этом окружении
"""

import subprocess
import urllib.parse
from bs4 import BeautifulSoup
import re

print("=" * 80)
print("ТЕСТ С CURL (через subprocess)")
print("=" * 80)

def fetch_with_curl(url):
    """Получить страницу используя curl"""
    try:
        # Выполняем curl с нужными заголовками
        result = subprocess.run(
            [
                'curl',
                '-s',  # Silent mode
                '-L',  # Follow redirects
                '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                '-H', 'Accept-Language: en-US,en;q=0.9',
                '-H', 'Accept-Encoding: identity',  # Отключаем сжатие!
                '--compressed',  # Но разрешаем curl обрабатывать сжатие
                url
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"❌ curl завершился с кодом: {result.returncode}")
            print(f"stderr: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Ошибка при выполнении curl: {e}")
        return None

def parse_ai_overview(html):
    """Парсинг AI Overview из HTML"""
    soup = BeautifulSoup(html, 'lxml')

    # Селекторы для AI Overview
    selectors = [
        'div[data-attrid*="AI"]',
        'div[data-attrid*="SGE"]',
        'div[jsname="yp1CPe"]',
        'div[data-sgrd="true"]',
        'div[data-attrid="SGEAIOverview"]',
        'div[data-attrid="AIOverview"]',
    ]

    print("🔎 Поиск AI Overview в HTML...")

    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator=' ', strip=True)

            if text and len(text) > 100:
                # Очищаем текст
                text = re.sub(r'\s+', ' ', text).strip()

                # Проверка на признаки AI Overview
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

                if len(sentences) >= 2:
                    print(f"✓ Найдено с селектором: {selector}")
                    return text

    return None

# Тест 1: Простой curl google.com
print("\n" + "=" * 80)
print("ТЕСТ 1: Проверка доступности Google")
print("=" * 80)

result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'https://www.google.com'],
                       capture_output=True, text=True)
print(f"HTTP код ответа от Google: {result.stdout}")

if result.stdout == '200':
    print("✅ Google доступен через curl!")
else:
    print(f"⚠️  Неожиданный код ответа: {result.stdout}")

# Тест 2: Получение страницы поиска
print("\n" + "=" * 80)
print("ТЕСТ 2: Получение страницы поиска")
print("=" * 80)

queries = [
    "What is artificial intelligence",
    "How does machine learning work"
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Запрос: {query}")
    print('='*80)

    # Формируем URL
    encoded_query = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded_query}&hl=en'

    print(f"📡 URL: {url}")
    print(f"🌐 Получение страницы через curl...")

    html = fetch_with_curl(url)

    if html:
        print(f"✅ Получено! Размер: {len(html)} символов")

        # Сохраняем
        filename = f"google_curl_{query.replace(' ', '_')[:30]}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Сохранено в: {filename}")

        # Быстрая проверка содержимого
        soup = BeautifulSoup(html, 'lxml')
        all_divs = soup.find_all('div')
        print(f"📊 Найдено div элементов: {len(all_divs)}")

        if len(all_divs) > 0:
            print("✅ HTML валиден! BeautifulSoup может его парсить")

            # Пробуем найти AI Overview
            ai_overview = parse_ai_overview(html)

            if ai_overview:
                print(f"\n🎉 AI OVERVIEW НАЙДЕН!")
                print("=" * 80)
                print(ai_overview[:500])
                if len(ai_overview) > 500:
                    print(f"\n... и еще {len(ai_overview) - 500} символов")
                print("=" * 80)
            else:
                print("\n⚠️  AI Overview не найден в HTML")
                print("Возможно Google не показывает AI Overview для этого запроса")
        else:
            print("❌ HTML поврежден - 0 div элементов")
            # Проверяем первые 200 символов
            print("\nПервые 200 символов:")
            print(html[:200])
    else:
        print("❌ Не удалось получить HTML")

    print()

print("=" * 80)
print("Тест curl завершен!")
print("=" * 80)
